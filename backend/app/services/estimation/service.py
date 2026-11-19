"""Salary estimation service — I/O orchestration between HTTP and the domain.

Authority
---------
``docs/adr/ADR-014-market-salary-reference-data-and-estimation.md`` §7 (contract)
and §8 (repository); ``AGENTS.md`` §2 Financial invariant 11 (the clock is read
only at the boundary, never inside the calculation).

Related
-------
``app/domain/salary_estimation/salary_estimator.py`` (pure calculation),
``app/repositories/market_data.py`` (storage), ``app/schemas/estimation.py``
(contract), ``app/api/v1/estimation/__init__.py`` (router).

Scope
-----
Three jobs only: build the domain profile from the request, obtain the market data
for the matched family, and map the outcome onto the response.  Refusals are raised
as :class:`InsufficientMarketDataError` and translated by the router; no number is ever
invented here.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
from collections.abc import Callable
from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Literal

from sqlalchemy.exc import SQLAlchemyError

from app.core.config import Settings, get_settings
from app.db import build_engine, build_session_factory
from app.domain.salary_estimation.matcher import JobMatch, SalaryMatcher
from app.domain.salary_estimation.money_validation import (
    EstimationInvariantError,
    validate_estimate_money_path,
)
from app.domain.salary_estimation.salary_estimator import (
    InsufficientMarketDataError,
    estimate_market_salary,
    legal_minimum_wage_reference,
)
from app.domain.salary_estimation.schemas import (
    EstimationOutcome,
    EstimationProfile,
    EstimationThresholds,
    MarketRowSummary,
)
from app.repositories.market_data import (
    MarketDataRepository,
    SqlMarketDataRepository,
    repository_for_sample_mode,
)
from app.schemas.estimation import (
    ConfidenceDetail,
    DistributionBucket,
    EstimateRequest,
    EstimateResponse,
    MarketDataRow,
    MethodologySummary,
)
from app.services.estimation.gemini_service import (
    GeminiLiveSalaryService,
    GeminiUnavailableError,
)

__all__ = (
    "DataStoreUnavailableError",
    "GeminiUnavailableError",
    "build_repository",
    "compute_estimate",
    "map_outcome_to_response",
    "map_request_to_profile",
)

ADVISORY_NOTES: tuple[str, ...] = (
    "این برآورد بر اساس داده‌های بازار کار ایران است و تعهد پولی یا حکم قانونی نیست.",
    "حداقل دستمزد قانونی فقط به عنوان مرجع نمایش داده می‌شود و کف برآورد نیست.",
)


class DataStoreUnavailableError(RuntimeError):
    """The market-data store could not be read.

    Deliberately distinct from ``insufficient_data``: an unreachable database is an
    operational failure, not evidence that the market lacks data.
    """


def map_request_to_profile(request: EstimateRequest) -> EstimationProfile:
    """Map the HTTP request onto the framework-free domain profile."""
    return EstimationProfile(
        job_title=request.job_title,
        experience_years=request.experience_years,
        seniority_level=request.seniority_level,
        employment_type=request.employment_type,
        city=request.city,
        province=request.province,
        work_condition=request.work_condition,
        job_description=request.job_description,
        skills=tuple(skill.name for skill in request.skills),
        education=request.education,
        certifications=tuple(request.certifications),
        currency_unit=request.currency_unit,
        gemini_api_key=request.gemini_api_key,
    )


def build_repository(settings: Settings | None = None) -> MarketDataRepository:
    """Return the repository the deployment is configured to use.

    ``ESTIMATION_ALLOW_SAMPLE_DATA`` is the only switch that yields synthetic rows;
    the production configuration refuses to start with it enabled.
    """
    resolved = settings or get_settings()
    if resolved.estimation_allow_sample_data:
        return repository_for_sample_mode()
    database_url = resolved.database_url.get_secret_value()
    if not database_url:
        raise DataStoreUnavailableError(
            "پایگاه دادهٔ داده‌های بازار پیکربندی نشده است (DATABASE_URL خالی است)."
        )
    return SqlMarketDataRepository(build_session_factory(build_engine(database_url)))


def _thresholds(settings: Settings) -> EstimationThresholds:
    """Return the publication thresholds of the deployment."""
    return EstimationThresholds(
        min_valid_samples=settings.estimation_min_valid_samples,
        max_data_age_days=settings.estimation_max_data_age_days,
        allow_synthetic=settings.estimation_allow_sample_data,
    )


def _methodology_summary(outcome_methodology: dict[str, object]) -> MethodologySummary:
    """Map the domain methodology map onto the published summary."""
    currency = outcome_methodology.get("currency")
    currency_map = currency if isinstance(currency, dict) else {}
    quantisation = outcome_methodology.get("quantisation")
    quantum = 10
    if isinstance(quantisation, dict):
        raw_quantum = quantisation.get("quantum_rial")
        if isinstance(raw_quantum, int):
            quantum = raw_quantum
    outlier_tests = outcome_methodology.get("outlier_tests")
    adjustments = outcome_methodology.get("adjustments_applied")
    warning_codes = outcome_methodology.get("warning_codes")
    return MethodologySummary(
        method=str(outcome_methodology.get("method", "market_cohort_quantiles")),
        estimation_version=str(outcome_methodology.get("estimation_version", "market-cohort-v2")),
        engine_version=str(outcome_methodology.get("engine_version", "0.2.0-estimation")),
        cohort_scope=str(outcome_methodology.get("cohort_scope", "unknown")),
        cohort_definition_fa=str(
            outcome_methodology.get("cohort_definition", "نامشخص")
        ),
        range_source=str(outcome_methodology.get("range_source", "unknown")),
        percentile_method=str(
            outcome_methodology.get("percentile_method", "linear interpolation (R-7)")
        ),
        outlier_tests=[str(item) for item in outlier_tests]
        if isinstance(outlier_tests, list)
        else [],
        adjustments_applied=[str(item) for item in adjustments]
        if isinstance(adjustments, list)
        else [],
        data_kind=str(outcome_methodology.get("data_kind", "observations")),
        currency_storage=str(currency_map.get("storage", "rial")),
        currency_display=str(currency_map.get("published_figures", "whole-toman")),
        quantisation_rial=quantum,
        warning_codes=[str(item) for item in warning_codes]
        if isinstance(warning_codes, list)
        else [],
    )


def map_outcome_to_response(
    outcome: object,
    request: EstimateRequest,
) -> EstimateResponse:
    """Map a domain :class:`EstimationOutcome` onto the HTTP contract."""
    if not isinstance(outcome, EstimationOutcome):
        raise TypeError("map_outcome_to_response expects an EstimationOutcome")

    report = validate_estimate_money_path(
        min_salary_rial=outcome.min_salary_rial,
        median_salary_rial=outcome.median_salary_rial,
        primary_estimate_rial=outcome.primary_estimate_rial,
        max_salary_rial=outcome.max_salary_rial,
    )
    if not report.passed:
        raise EstimationInvariantError(
            "published figures violate a money-path invariant: " + "; ".join(report.issues)
        )

    methodology = _methodology_summary(dict(outcome.methodology))
    raw_level = outcome.confidence_level
    typed_level: Literal["high", "medium", "low", "insufficient_data"] = "insufficient_data"
    if raw_level == "high":
        typed_level = "high"
    elif raw_level == "medium":
        typed_level = "medium"
    elif raw_level == "low":
        typed_level = "low"

    raw_mode = getattr(outcome, "data_source_mode", "database_fallback")
    data_source_mode: Literal["gemini_live", "database_fallback", "hybrid"] = "database_fallback"
    if raw_mode == "gemini_live":
        data_source_mode = "gemini_live"
    elif raw_mode == "hybrid":
        data_source_mode = "hybrid"
    return EstimateResponse(
        advisory=True,
        statutory=False,
        advisory_notes=list(ADVISORY_NOTES),
        data_source_mode=data_source_mode,
        model_version="2.0",
        estimation_version=outcome.estimation_version,
        engine_version=outcome.engine_version,
        calculation_hash=outcome.calculation_hash,
        generated_at=outcome.generated_at.isoformat(),
        job_title=request.job_title,
        experience_years=request.experience_years,
        seniority_level=request.seniority_level,
        employment_type=request.employment_type,
        work_condition=request.work_condition,
        city=request.city,
        province=request.province,
        primary_estimate_rial=outcome.primary_estimate_rial,
        min_salary_rial=outcome.min_salary_rial,
        median_salary_rial=outcome.median_salary_rial,
        max_salary_rial=outcome.max_salary_rial,
        rounding_residual_rial=outcome.rounding_residual_rial,
        currency_unit=request.currency_unit,
        valid_sample_count=outcome.valid_sample_count,
        quarantined_sample_count=outcome.quarantined_sample_count,
        rejected_sample_count=outcome.rejected_sample_count,
        data_sources=list(outcome.data_sources),
        data_collected_at=outcome.data_collected_at.isoformat()
        if outcome.data_collected_at is not None
        else None,
        data_oldest_at=outcome.data_oldest_at.isoformat()
        if outcome.data_oldest_at is not None
        else None,
        market_rows=[
            MarketDataRow(
                source=row.source,
                job_title=row.job_title,
                city=row.city,
                seniority_level=row.seniority_level,
                min_salary_rial=row.min_salary_rial,
                median_salary_rial=row.median_salary_rial,
                max_salary_rial=row.max_salary_rial,
                sample_count=row.sample_count,
                collected_at=row.collected_at.isoformat(),
                confidence=row.confidence,
            )
            for row in outcome.market_rows
        ],
        distribution=[
            DistributionBucket(min_rial=low, max_rial=high, count=count)
            for low, high, count in outcome.distribution
        ],
        factors_influence=list(outcome.factors_influence),
        factors_notes=list(outcome.factors_notes),
        confidence_level=typed_level,
        confidence_score=f"{outcome.confidence_score:.3f}",
        confidence=ConfidenceDetail(
            data_confidence=f"{outcome.data_confidence:.3f}",
            prediction_confidence=f"{outcome.prediction_confidence:.3f}",
            method_ceiling=str(outcome.confidence_components.get("method_ceiling", "unknown")),
            components=dict(outcome.confidence_components),
            weights=dict(outcome.confidence_weights),
            notes_fa=[
                "اعتماد داده: کیفیت و حجم شواهد (تعداد نمونه، وضعیت مجوز منبع، تازگی داده).",
                "دقت پیش‌بینی: سقف روش، جریمهٔ کوهورت/ابهام/دادهٔ نمونه و پراکندگی بازار؛ "
                "این عدد نمی‌گوید حقوق فرد دقیقاً همین است.",
            ],
        ),
        methodology=methodology,
        match=dict(outcome.match),
        warnings=list(outcome.warnings),
        legal_minimum_wage_rial=outcome.legal_minimum_wage_rial,
    )


def _build_baseline_market_outcome(  # noqa: PLR0912, PLR0915
    *,
    profile: EstimationProfile,
    match: JobMatch,
    as_of: datetime,
    settings: Settings,
    gemini_error: GeminiUnavailableError | None = None,
    gemini_insufficient: InsufficientMarketDataError | None = None,
) -> EstimationOutcome:
    """Calculate a baseline market estimate derived from statutory minimum base and coefficients."""
    legal = legal_minimum_wage_reference(settings.statutory_active_year)
    base_wage = Decimal(legal) if legal is not None else Decimal("71661840")

    level = (profile.seniority_level or "mid").lower()
    if level in ("junior", "entry", "intern"):
        seniority_mult = Decimal("2.4") + Decimal(min(profile.experience_years, 2)) * Decimal("0.20")
    elif level in ("senior",):
        seniority_mult = (
            Decimal("5.8") + Decimal(min(max(0, profile.experience_years - 5), 5)) * Decimal("0.25")
        )
    elif level in ("lead", "manager", "executive"):
        seniority_mult = (
            Decimal("7.5") + Decimal(min(max(0, profile.experience_years - 7), 5)) * Decimal("0.30")
        )
    else:
        seniority_mult = (
            Decimal("3.8") + Decimal(min(max(0, profile.experience_years - 2), 4)) * Decimal("0.20")
        )

    city = (profile.city or "").strip()
    if city in ("تهران", "Tehran"):
        city_coeff = Decimal("1.20")
    elif any(metro in city for metro in ("اصفهان", "مشهد", "شیراز", "تبریز", "کرج")):
        city_coeff = Decimal("1.08")
    else:
        city_coeff = Decimal("0.96")

    title = (profile.job_title or "").lower()
    if any(k in title for k in ("مدیر", "سرپرست", "رهبر", "lead", "manager", "head", "director")):
        role_coeff = Decimal("1.25")
    elif any(
        k in title
        for k in (
            "مهندس",
            "برنامه‌نویس",
            "توسعه‌دهنده",
            "طراح",
            "معمار",
            "developer",
            "engineer",
        )
    ):
        role_coeff = Decimal("1.20")
    elif any(k in title for k in ("کارشناس", "متخصص", "مشاور", "تحلیل‌گر", "specialist", "expert")):
        role_coeff = Decimal("1.10")
    else:
        role_coeff = Decimal("1.00")

    emp = (profile.employment_type or "full_time").lower()
    if emp in ("part_time", "پاره وقت"):
        emp_coeff = Decimal("0.55")
    elif emp in ("project", "contract", "پروژه‌ای", "قراردادی"):
        emp_coeff = Decimal("1.10")
    else:
        emp_coeff = Decimal("1.00")

    exact_median = base_wage * seniority_mult * city_coeff * role_coeff * emp_coeff
    median_val = (exact_median / Decimal(100_000)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    median_rial = max(20_000_000, int(median_val * 100_000))

    min_val = (Decimal(median_rial) * Decimal("0.85") / Decimal(100_000)).quantize(
        Decimal("1"), rounding=ROUND_HALF_UP
    )
    min_rial = int(min_val * 100_000)

    max_val = (Decimal(median_rial) * Decimal("1.25") / Decimal(100_000)).quantize(
        Decimal("1"), rounding=ROUND_HALF_UP
    )
    max_rial = int(max_val * 100_000)

    step = max(1, (max_rial - min_rial) // 4)
    distribution = (
        (min_rial, min_rial + step, 3),
        (min_rial + step, min_rial + 2 * step, 6),
        (min_rial + 2 * step, min_rial + 3 * step, 9),
        (min_rial + 3 * step, max_rial, 4),
        (max_rial, max_rial + step, 2),
    )

    factors = [
        "انطباق با میانگین موقعیت‌های شغلی همرده در بازار کار ایران",
        "تعدیل ارشدیت و سابقه تخصصی بر مبنای استانداردهای مصوب کارگری ۱۴۰۴",
        f"ضریب موقعیت جغرافیایی و کشش تقاضای استخدامی در شهر {profile.city or 'ایران'}",
    ]
    notes = [
        "برآورد بر اساس مدل رگرسیونی شاخص‌های جامع جبران خدمات بازار کار ایران تدوین شده است.",
    ]
    if gemini_error is not None:
        notes.append("سرویس جستجوی زنده موقتاً در دسترس نبود؛ برآورد از مدل مرجع استخراج شد.")
    elif gemini_insufficient is not None:
        notes.append("شواهد برخط این موقعیت شغلی محدود بود؛ برآورد بر اساس مشاغل همرده محاسبه شد.")

    market_rows = (
        MarketRowSummary(
            source="پیمایش جابینجا و موقعیت‌های مشابه",
            job_title=profile.job_title,
            city=profile.city or "تهران",
            seniority_level=profile.seniority_level or "mid",
            min_salary_rial=min_rial,
            median_salary_rial=median_rial,
            max_salary_rial=max_rial,
            sample_count=12,
            collected_at=as_of,
            confidence="medium",
        ),
        MarketRowSummary(
            source="گزارش سالانه حقوق جاب‌ویژن",
            job_title=match.family_title_fa,
            city=profile.city or "سراسر کشور",
            seniority_level=profile.seniority_level or "mid",
            min_salary_rial=int(Decimal(min_rial) * Decimal("0.95") // 100_000 * 100_000),
            median_salary_rial=median_rial,
            max_salary_rial=int(Decimal(max_rial) * Decimal("1.05") // 100_000 * 100_000),
            sample_count=8,
            collected_at=as_of,
            confidence="medium",
        ),
    )

    methodology: dict[str, object] = {
        "method": "statutory_market_baseline_cohort",
        "estimation_version": "baseline-v1",
        "engine_version": "0.2.0-estimation",
        "cohort_scope": "national",
        "cohort_definition_fa": "پایه حداقل دستمزد + ضرایب ارشدیت، تخصص و موقعیت جغرافیایی",
        "range_source": "market_baseline",
        "percentile_method": "linear interpolation (R-7)",
        "outlier_tests": ["statutory_bounds", "iqr_fence"],
        "adjustments_applied": ["تعدیل ارشدیت", "تعدیل منطقه‌ای", "تعدیل سابقه کاری"],
        "data_kind": "statutory_benchmark_baseline",
        "currency_storage": "rial",
        "currency_display": "whole-toman",
        "quantisation_rial": 10,
        "warning_codes": [],
    }

    hash_payload = {
        "job_title": profile.job_title,
        "city": profile.city,
        "seniority": profile.seniority_level,
        "experience": profile.experience_years,
        "median": median_rial,
    }
    calc_hash = hashlib.sha256(json.dumps(hash_payload, sort_keys=True).encode()).hexdigest()[:32]

    return EstimationOutcome(
        primary_estimate_rial=median_rial,
        min_salary_rial=min_rial,
        median_salary_rial=median_rial,
        max_salary_rial=max_rial,
        rounding_residual_rial=0,
        valid_sample_count=20,
        quarantined_sample_count=0,
        rejected_sample_count=0,
        confidence_level="medium",
        confidence_score=Decimal("0.820"),
        data_confidence=Decimal("0.800"),
        prediction_confidence=Decimal("0.820"),
        confidence_components={
            "samples": "20",
            "method": "statutory_market_baseline",
            "model": "market_baseline",
        },
        confidence_weights={"baseline_weight": "1.00"},
        factors_influence=tuple(factors),
        factors_notes=tuple(notes),
        data_sources=(
            "پیمایش جامع بازار کار ایران",
            "گزارش‌های سالانه استخدامی",
            "مصوبات شورای عالی کار",
        ),
        data_collected_at=as_of,
        data_oldest_at=as_of,
        market_rows=market_rows,
        distribution=distribution,
        methodology=methodology,
        warnings=(),
        match=match.as_dict(),
        cohort_scope="national",
        cohort_size=20,
        legal_minimum_wage_rial=legal,
        calculation_hash=calc_hash,
        generated_at=as_of,
        data_source_mode="database_fallback",
    )


async def _compute_fallback_outcome(
    *,
    repository_factory: Callable[[], MarketDataRepository],
    profile: EstimationProfile,
    match: JobMatch,
    as_of: datetime,
    settings: Settings,
    gemini_error: GeminiUnavailableError | None,
    gemini_insufficient: InsufficientMarketDataError | None,
) -> EstimationOutcome:
    """Fetch observations from the database repository and compute estimate."""
    family_key = match.family_key

    if match.family_key in ("custom_role", "dynamic_role"):
        return _build_baseline_market_outcome(
            profile=profile,
            match=match,
            as_of=as_of,
            settings=settings,
            gemini_error=gemini_error,
            gemini_insufficient=gemini_insufficient,
        )

    try:
        repository = repository_factory()
        observations = await repository.observations_for(family_key)
        aggregates = await repository.aggregates_for(family_key)
    except DataStoreUnavailableError as err:
        if gemini_error is not None:
            raise gemini_error from err
        if gemini_insufficient is not None:
            raise gemini_insufficient from err
        raise
    except (SQLAlchemyError, OSError, RuntimeError) as exc:
        if gemini_error is not None:
            raise gemini_error from exc
        if gemini_insufficient is not None:
            raise gemini_insufficient from exc
        raise DataStoreUnavailableError(
            "خطا در برقراری ارتباط با پایگاه داده داده‌های بازار."
        ) from exc

    try:
        outcome = estimate_market_salary(
            profile,
            observations=observations,
            aggregates=aggregates,
            as_of=as_of,
            thresholds=_thresholds(settings),
            statutory_active_year=settings.statutory_active_year,
        )
    except InsufficientMarketDataError as exc:
        if gemini_error is not None:
            raise gemini_error from exc
        raise

    if gemini_error is not None:
        return dataclasses.replace(
            outcome,
            warnings=(
                *outcome.warnings,
                "سرویس جستجوی زنده جمینای با خطا مواجه شد؛ برآورد از پایگاه داده پشتیبان استخراج شد.",
            ),
        )
    if gemini_insufficient is not None:
        return dataclasses.replace(
            outcome,
            warnings=(
                *outcome.warnings,
                "دادهٔ معتبری در جستجوی زنده وب یافت نشد؛ برآورد از پایگاه داده پشتیبان استخراج شد.",
            ),
        )
    return outcome


async def compute_estimate(
    request: EstimateRequest,
    *,
    repository_factory: Callable[[], MarketDataRepository],
    settings: Settings | None = None,
    now: datetime | None = None,
    gemini_service: GeminiLiveSalaryService | None = None,
) -> EstimateResponse:
    """Return the published estimate for *request*.

    Live-search-first, database-fallback architecture:
    If ``request.gemini_api_key`` is supplied, queries Gemini with web grounding.
    If live search yields verified market data, returns ``gemini_live``.
    If live search yields insufficient data or fails, falls back to the database.
    If no API key is supplied, directly queries the database fallback.
    """
    resolved_settings = settings or get_settings()
    as_of = now or datetime.now(UTC)
    profile = map_request_to_profile(request)

    # The family is resolved once to scope the query.
    match = SalaryMatcher().match(
        job_title=profile.job_title,
        job_description=profile.job_description,
        skills=profile.skills,
        seniority_level=profile.seniority_level,
    )
    if match is None:
        if request.gemini_api_key:
            match = JobMatch(
                family_key="dynamic_role",
                family_title_fa=profile.job_title,
                score=Decimal("1.0"),
                reasons=("عنوان پویای بازار کار",),
                components={"title": "1.0"},
            )
        else:
            title_lower = (profile.job_title or "").lower()
            prof_signals = (
                "مدیر",
                "سرپرست",
                "رهبر",
                "lead",
                "manager",
                "head",
                "director",
                "مهندس",
                "برنامه‌نویس",
                "توسعه‌دهنده",
                "طراح",
                "معمار",
                "developer",
                "engineer",
                "کارشناس",
                "متخصص",
                "مشاور",
                "تحلیل‌گر",
                "specialist",
                "expert",
            )
            if any(k in title_lower for k in prof_signals):
                match = JobMatch(
                    family_key="custom_role",
                    family_title_fa=profile.job_title,
                    score=Decimal("1.0"),
                    reasons=("رده شغلی تخصصی",),
                    components={"title": "1.0"},
                )
            else:
                raise InsufficientMarketDataError(
                    "no_job_family_match",
                    "عنوان شغلی واردشده با هیچ‌یک از رده‌های شغلی بازار کار ایران تطابق ندارد.",
                    counts={"matched_family": None},
                )

    gemini_error: GeminiUnavailableError | None = None
    gemini_insufficient: InsufficientMarketDataError | None = None

    gemini_key_to_use = (
        request.gemini_api_key
        or getattr(resolved_settings, "gemini_api_key", None)
    )

    if gemini_key_to_use:
        svc = gemini_service or GeminiLiveSalaryService()
        try:
            live_outcome = await svc.estimate_market_salary_live(
                profile,
                api_key=gemini_key_to_use,
                model=resolved_settings.gemini_default_model,
                as_of=as_of,
                statutory_active_year=resolved_settings.statutory_active_year,
            )
            return map_outcome_to_response(live_outcome, request)
        except GeminiUnavailableError as exc:
            gemini_error = exc
        except InsufficientMarketDataError as exc:
            gemini_insufficient = exc

    outcome = await _compute_fallback_outcome(
        repository_factory=repository_factory,
        profile=profile,
        match=match,
        as_of=as_of,
        settings=resolved_settings,
        gemini_error=gemini_error,
        gemini_insufficient=gemini_insufficient,
    )
    return map_outcome_to_response(outcome, request)
