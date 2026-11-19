"""Market salary estimation from validated observations.

Authority
---------
``docs/adr/ADR-014-market-salary-reference-data-and-estimation.md`` §4 (estimation
method), §5 (matching), §6 (confidence), §7 (publishing rules);
``docs/SALARY_ESTIMATION_SPEC.md`` (revisions R-01…R-09);
``AGENTS.md`` §2 Financial invariants 7-11.

Related
-------
``market_data.py`` (records), ``validation.py`` (classification),
``statistics.py`` (quantiles), ``matcher.py`` (job family), ``schemas.py``
(outcome), ``app/services/estimation/service.py`` (I/O orchestration).

Scope
-----
Pure function: ``(profile, observations, aggregates, as_of, thresholds)`` in,
:class:`EstimationOutcome` out.  No database, network, clock or environment read.

What changed from the previous engine, and why
---------------------------------------------
* The median is the real median (mean of the two central values for even n); the
  previous ``values[len // 2]`` biased every even sample upward.
* The published range is the market's own ``p25…p75``, not ``median x (1 ± 15/25/40 %)``.
* City, seniority and employment type are **cohort selectors**.  They are never
  multiplied on top of a cohort that already encodes them, which is what removed
  the double counting.
* Experience, education and skills carry **no monetary multiplier**.  No
  statistically defensible coefficient exists in the corpus, so they inform the
  match and the explanation instead of silently moving the figure.
* Nothing is published below the sample floor; the estimator refuses instead of
  producing a precise-looking number.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime
from decimal import Decimal

from app.engines.money import round_half_up, to_decimal
from app.engines.rules import load_rule_set

from .market_data import (
    MarketAggregate,
    MarketObservation,
    ValidationOutcome,
)
from .matcher import JobMatch, SalaryMatcher
from .schemas import (
    ENGINE_VERSION,
    ESTIMATION_VERSION,
    EstimationOutcome,
    EstimationProfile,
    EstimationThresholds,
    MarketRowSummary,
)
from .statistics import histogram, interquartile_range, median, percentile
from .taxonomy import normalize_text
from .validation import ValidationPolicy, classify_observations

__all__ = (
    "InsufficientMarketDataError",
    "estimate_market_salary",
    "legal_minimum_wage_reference",
)

#: Quality of a source tier, in ``[0, 1]``.  A licence-backed publication ranks
#: above a manager-typed figure; a sample ranks last and is capped anyway.
_SOURCE_QUALITY: Mapping[str, Decimal] = {
    "licensed": Decimal("1"),
    "published_report": Decimal("0.80"),
    "manual_verified": Decimal("0.55"),
    "synthetic_dev": Decimal("0.20"),
}

#: Confidence weights.  Data confidence answers "how good is the evidence";
#: prediction confidence answers "how far should this figure be trusted".
_DATA_WEIGHTS: Mapping[str, Decimal] = {
    "sample_size": Decimal("0.40"),
    "source_quality": Decimal("0.30"),
    "recency": Decimal("0.30"),
}

#: A cohort wider than city+seniority is a weaker comparison.
_SCOPE_PENALTY: Mapping[str, Decimal] = {
    "city_seniority_employment": Decimal("1"),
    "city_seniority": Decimal("0.97"),
    "city": Decimal("0.90"),
    "province": Decimal("0.82"),
    "national": Decimal("0.68"),
}

#: Method ceiling: an observation-based cohort can never be claimed as certain,
#: and a published aggregate is weaker still because its raw sample is unseen.
_METHOD_CEILING: Mapping[str, Decimal] = {
    "observations": Decimal("0.90"),
    "published_aggregate": Decimal("0.55"),
}

#: A synthetic sample can never look trustworthy, whatever its volume: the penalty
#: is large enough that a sample cohort can only ever publish as ``low``.
_SYNTHETIC_PENALTY = Decimal("0.55")

#: Persian labels for the cohort scope, used in the explanation.
_SCOPE_LABEL_FA: Mapping[str, str] = {
    "city_seniority_employment": "شهر + سطح تخصص + نوع استخدام",
    "city_seniority": "شهر + سطح تخصص",
    "city": "شهر (بدون تفکیک سطح)",
    "province": "استان",
    "national": "کل کشور (بدون تفکیک جغرافیایی)",
}

#: Anything at or above this is shown as a high-confidence estimate.
_HIGH_CONFIDENCE = Decimal("0.70")
_MEDIUM_CONFIDENCE = Decimal("0.45")
_LOW_CONFIDENCE = Decimal("0.20")

#: Published figures are quantised to a whole Toman so the Persian UI can render
#: Toman exactly (ADR-013 currency convention) without rounding in the display
#: layer.  The quantisation is at most 5 Rial per figure and is reported.
_TOMAN_QUANTUM_RIAL = 10


class InsufficientMarketDataError(Exception):
    """Raised when no defensible figure can be published.

    ``reason`` is a stable machine code; ``detail`` is the Persian explanation the
    API returns.  Both are part of the refusal contract.
    """

    def __init__(
        self,
        reason: str,
        detail: str,
        *,
        counts: Mapping[str, int | None] | None = None,
    ) -> None:
        super().__init__(f"{reason}: {detail}")
        self.reason = reason
        self.detail = detail
        self.counts: dict[str, int | None] = dict(counts or {})


def _quantise_toman_exact(exact: Decimal) -> tuple[int, int]:
    """Return ``(whole_toman_rial_amount, signed_residual_rial)``."""
    toman = round_half_up(exact / Decimal(_TOMAN_QUANTUM_RIAL))
    emitted = toman * _TOMAN_QUANTUM_RIAL
    return emitted, emitted - int(exact)


def _recency_score(values: Sequence[datetime], as_of: datetime) -> Decimal:
    """Return ``[0, 1]`` for how recent the sample is (median age in days)."""
    ages: list[int] = []
    for value in values:
        moment = value if value.tzinfo is not None else value.replace(tzinfo=as_of.tzinfo)
        ages.append(max(0, (as_of - moment).days))
    if not ages:
        return Decimal(0)
    central = median(ages)
    if central <= 180:
        return Decimal(1)
    remaining = Decimal(730) - central
    if remaining <= 0:
        return Decimal(0)
    return remaining / Decimal(550)


def _source_quality(values: Sequence[MarketObservation]) -> Decimal:
    """Return the mean source-quality tier of the sample."""
    if not values:
        return Decimal(0)
    total = sum(
        (_SOURCE_QUALITY.get(row.license_status, Decimal("0.10")) for row in values),
        Decimal(0),
    )
    return total / Decimal(len(values))


def _dispersion_score(values: Sequence[Decimal]) -> Decimal:
    """Return ``[0, 1]``: 1 means a tight market, 0 a very wide one."""
    central = median(values)
    if central <= 0:
        return Decimal(0)
    spread = interquartile_range(values)
    coefficient = spread / central
    score = Decimal(1) - coefficient * Decimal("2")
    return max(Decimal(0), min(Decimal(1), score))


def _completeness_score(profile: EstimationProfile) -> Decimal:
    """Return the share of optional profile fields the manager supplied."""
    optional = (
        bool(profile.job_description),
        bool(profile.skills),
        bool(profile.education),
        bool(profile.province),
        bool(profile.employment_type),
        bool(profile.seniority_level),
    )
    supplied = sum(1 for value in optional if value)
    return Decimal(supplied) / Decimal(len(optional))


def _confidence_level(score: Decimal) -> str:
    """Map a numeric confidence to the published four-level vocabulary."""
    if score >= _HIGH_CONFIDENCE:
        return "high"
    if score >= _MEDIUM_CONFIDENCE:
        return "medium"
    if score >= _LOW_CONFIDENCE:
        return "low"
    return "insufficient_data"


def _scope_predicates(
    profile: EstimationProfile,
) -> tuple[tuple[str, Callable[[MarketObservation], bool]], ...]:
    """Return the cohort scopes, narrowest first."""
    city = normalize_text(profile.city)
    province = normalize_text(profile.province or "")
    seniority = normalize_text(profile.seniority_level)
    employment = normalize_text(profile.employment_type)

    def matches_city(row: MarketObservation) -> bool:
        return normalize_text(row.city) == city

    def matches_seniority(row: MarketObservation) -> bool:
        return normalize_text(row.seniority_level or "") == seniority

    def matches_employment(row: MarketObservation) -> bool:
        return normalize_text(row.employment_type or "") == employment

    scopes: list[tuple[str, Callable[[MarketObservation], bool]]] = [
        (
            "city_seniority_employment",
            lambda row: matches_city(row) and matches_seniority(row) and matches_employment(row),
        ),
        ("city_seniority", lambda row: matches_city(row) and matches_seniority(row)),
        ("city", matches_city),
    ]
    if province:
        scopes.append(
            (
                "province",
                lambda row: normalize_text(row.province or "") == province,
            )
        )
    scopes.append(("national", lambda _row: True))
    return tuple(scopes)


def _select_cohort(
    rows: Sequence[MarketObservation],
    profile: EstimationProfile,
    minimum: int,
) -> tuple[str, tuple[MarketObservation, ...]] | None:
    """Return the narrowest cohort that clears the sample floor."""
    for scope, predicate in _scope_predicates(profile):
        subset = tuple(row for row in rows if predicate(row))
        if len(subset) >= minimum:
            return scope, subset
    return None


def _market_rows(
    outcome: ValidationOutcome,
    *,
    confidence_level: str,
) -> tuple[MarketRowSummary, ...]:
    """Summarise the valid sample per source (the ``market_rows`` contract)."""
    grouped: dict[str, list[MarketObservation]] = {}
    for row in outcome.valid:
        grouped.setdefault(row.source_id, []).append(row)

    summaries: list[MarketRowSummary] = []
    for source, rows in sorted(grouped.items()):
        values = [outcome.monthly_by_id[row.id] for row in rows]
        low, central, high = (
            round_half_up(percentile(values, 25)),
            round_half_up(median(values)),
            round_half_up(percentile(values, 75)),
        )
        summaries.append(
            MarketRowSummary(
                source=source,
                job_title=rows[0].job_title_reported,
                city=rows[0].city,
                seniority_level=rows[0].seniority_level or "",
                min_salary_rial=low,
                median_salary_rial=central,
                max_salary_rial=high,
                sample_count=len(rows),
                collected_at=max(row.collected_at for row in rows),
                confidence=confidence_level,
            )
        )
    return tuple(summaries)


def legal_minimum_wage_reference(statutory_active_year: int) -> int | None:
    """Return the monthly legal minimum wage, or ``None`` when unavailable.

    A missing statutory reference must never stop a market estimate: the minimum
    wage is a *reference* (ADR-013 D-07), not an input to the calculation.  The
    loader is wrapped here so a missing or unverified rule set degrades to "no
    reference" instead of failing the estimate.
    """
    try:
        return int(load_rule_set(statutory_active_year).monthly_minimum_wage_30days_rial)
    except Exception:
        return None


def _aggregate_outcome(
    aggregate: MarketAggregate,
    *,
    profile: EstimationProfile,
    match: JobMatch,
    as_of: datetime,
    thresholds: EstimationThresholds,
    statutory_active_year: int = 1405,
) -> EstimationOutcome:
    """Build an outcome from a published aggregate (no raw sample available)."""
    if aggregate.min_salary_rial is None or aggregate.max_salary_rial is None:
        raise InsufficientMarketDataError(
            "aggregate_missing_range",
            "گزارش تجمیعی موجود، بازهٔ حقوق را منتشر نکرده است و بدون بازه، تخمین ارائه نمی‌شود.",
            counts={"valid_samples": aggregate.sample_size, "aggregate_rows": 1},
        )

    identity = (aggregate.p25_salary_rial, aggregate.median_salary_rial, aggregate.p75_salary_rial)
    low_exact = to_decimal(identity[0] if identity[0] is not None else aggregate.min_salary_rial)
    central_exact = to_decimal(aggregate.median_salary_rial)
    high_exact = to_decimal(identity[2] if identity[2] is not None else aggregate.max_salary_rial)

    low, low_residual = _quantise_toman_exact(low_exact)
    central, central_residual = _quantise_toman_exact(central_exact)
    high, high_residual = _quantise_toman_exact(high_exact)

    recency = _recency_score([aggregate.collected_at], as_of)
    quality = _SOURCE_QUALITY.get(aggregate.license_status, Decimal("0.10"))
    sample_component = min(Decimal(1), Decimal(aggregate.sample_size) / Decimal(60))
    data_confidence = (
        sample_component * Decimal("0.40")
        + quality * Decimal("0.30")
        + recency * Decimal("0.30")
    )
    prediction = min(data_confidence, _METHOD_CEILING["published_aggregate"])
    if aggregate.is_synthetic:
        prediction = prediction * _SYNTHETIC_PENALTY
    level = _confidence_level(prediction)

    warnings: list[str] = []
    warning_codes: list[str] = []
    if aggregate.is_synthetic:
        warnings.append("دادهٔ نمونهٔ توسعه (ساختگی) استفاده شده است؛ این عدد داده بازار نیست.")
        warning_codes.append("sample_data_in_use")
    warnings.append(
        "این تخمین از یک گزارش تجمیعی منتشرشده ساخته شده است؛ داده خام در دسترس نیست "
        "و آزمون‌های پرت‌یابی روی آن اجرا نشده است."
    )
    warning_codes.append("published_aggregate_source")

    legal = legal_minimum_wage_reference(statutory_active_year)
    if legal is None:
        warnings.append("مرجع حداقل دستمزد قانونی در دسترس نبود؛ تخمین بدون آن ارائه شده است.")
    warning_codes.append("legal_minimum_wage_unavailable" if legal is None else "legal_reference_only")

    methodology: dict[str, object] = {
        "method": "published_aggregate",
        "estimation_version": ESTIMATION_VERSION,
        "engine_version": ENGINE_VERSION,
        "cohort_scope": "published_report",
        "valid_sample_count": aggregate.sample_size,
        "publish_floor": thresholds.min_valid_samples,
        "range_source": "published_min_max",
        "adjustments_applied": [],
        "currency": {
            "storage": "rial",
            "published_figures": "whole-toman multiples of 10 Rial",
            "toman_divisor": 10,
        },
        "warning_codes": warning_codes,
        "data_kind": "aggregate",
    }

    hash_payload = {
        "profile": {
            "job_title": profile.job_title,
            "experience_years": profile.experience_years,
            "seniority_level": profile.seniority_level,
            "employment_type": profile.employment_type,
            "city": profile.city,
            "province": profile.province,
            "work_condition": profile.work_condition,
            "skills": list(profile.skills),
            "education": profile.education,
        },
        "aggregate_id": aggregate.id,
        "published": [low, central, high],
        "engine_version": ENGINE_VERSION,
    }
    calculation_hash = hashlib.sha256(
        json.dumps(hash_payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()[:32]

    return EstimationOutcome(
        primary_estimate_rial=central,
        min_salary_rial=low,
        median_salary_rial=central,
        max_salary_rial=high,
        rounding_residual_rial=low_residual + central_residual + high_residual,
        valid_sample_count=aggregate.sample_size,
        quarantined_sample_count=0,
        rejected_sample_count=0,
        confidence_level=level,
        confidence_score=prediction,
        data_confidence=data_confidence,
        prediction_confidence=prediction,
        confidence_components={
            "sample_size": f"{sample_component:.3f}",
            "source_quality": f"{quality:.3f}",
            "recency": f"{recency:.3f}",
            "method_ceiling": f"{_METHOD_CEILING['published_aggregate']:.3f}",
        },
        confidence_weights={key: f"{value:.2f}" for key, value in _DATA_WEIGHTS.items()},
        factors_influence=(
            f"گروه شغلی: {match.family_title_fa}",
            "منبع: گزارش تجمیعی منتشرشده",
            f"حجم نمونهٔ گزارش: {aggregate.sample_size}",
        ),
        data_sources=(aggregate.source_id,),
        data_collected_at=aggregate.collected_at,
        data_oldest_at=aggregate.collected_at,
        market_rows=(),
        distribution=(),
        methodology=methodology,
        warnings=tuple(warnings),
        match=match.as_dict(),
        cohort_scope="published_report",
        cohort_size=aggregate.sample_size,
        legal_minimum_wage_rial=legal,
        calculation_hash=calculation_hash,
        generated_at=as_of,
    )


def estimate_market_salary(  # noqa: PLR0912, PLR0915 - one guard per cohort decision
    profile: EstimationProfile,
    *,
    observations: Sequence[MarketObservation],
    aggregates: Sequence[MarketAggregate] = (),
    matcher: SalaryMatcher | None = None,
    as_of: datetime,
    thresholds: EstimationThresholds | None = None,
    statutory_active_year: int = 1405,
) -> EstimationOutcome:
    """Return a defensible market estimate for *profile*.

    Raises
    ------
    InsufficientMarketDataError
        When the title matches no family, the sample is below the floor, the
        matched cohort holds only quarantined rows, or the confidence is too low
        to publish.  The refusal carries the counts, so the UI can say what is
        missing instead of showing a number.
    """
    resolved = thresholds or EstimationThresholds()
    resolved_matcher = matcher or SalaryMatcher()

    match = resolved_matcher.match(
        job_title=profile.job_title,
        job_description=profile.job_description,
        skills=profile.skills,
        seniority_level=profile.seniority_level,
    )
    if match is None:
        raise InsufficientMarketDataError(
            "no_job_family_match",
            "عنوان شغلی واردشده با هیچ‌یک از خانواده‌های شغلی شناخته‌شده تطابق ندارد.",
            counts={"matched_family": None},
        )

    family_rows = tuple(row for row in observations if row.family_key == match.family_key)
    outcome = classify_observations(
        family_rows,
        as_of=as_of,
        policy=ValidationPolicy(
            max_age_days=resolved.max_data_age_days,
            allow_synthetic=resolved.allow_synthetic,
        ),
    )

    cohort = _select_cohort(outcome.valid, profile, resolved.min_valid_samples)
    if cohort is None:
        family_aggregates = [
            aggregate
            for aggregate in aggregates
            if aggregate.family_key == match.family_key
            and normalize_text(aggregate.city) == normalize_text(profile.city)
            and (aggregate.is_synthetic is False or resolved.allow_synthetic)
        ]
        if family_aggregates and resolved.allow_aggregate_fallback:
            chosen = max(family_aggregates, key=lambda item: item.collected_at)
            return _aggregate_outcome(
                chosen,
                profile=profile,
                match=match,
                as_of=as_of,
                thresholds=resolved,
                statutory_active_year=statutory_active_year,
            )
        raise InsufficientMarketDataError(
            "insufficient_valid_samples",
            "برای این شغل، شهر و سطح تخصص، دادهٔ معتبر کافی برای تخمین وجود ندارد.",
            counts={
                "valid_samples": len(outcome.valid),
                "suspicious_samples": len(outcome.suspicious),
                "rejected_samples": len(outcome.rejected),
                "required_samples": resolved.min_valid_samples,
            },
        )

    scope, cohort_rows = cohort
    cohort_ids = {row.id for row in cohort_rows}
    values = [to_decimal(outcome.monthly_by_id[row.id]) for row in cohort_rows]

    low_exact = percentile(values, 25)
    central_exact = median(values)
    high_exact = percentile(values, 75)
    low, low_residual = _quantise_toman_exact(low_exact)
    central, central_residual = _quantise_toman_exact(central_exact)
    high, high_residual = _quantise_toman_exact(high_exact)

    sample_component = min(Decimal(1), Decimal(len(values)) / Decimal(30))
    quality = _source_quality(cohort_rows)
    recency = _recency_score([row.collected_at for row in cohort_rows], as_of)
    data_confidence = (
        sample_component * _DATA_WEIGHTS["sample_size"]
        + quality * _DATA_WEIGHTS["source_quality"]
        + recency * _DATA_WEIGHTS["recency"]
    )
    dispersion = _dispersion_score(values)
    completeness = _completeness_score(profile)
    prediction = min(data_confidence, _METHOD_CEILING["observations"])
    prediction = prediction * _SCOPE_PENALTY.get(scope, Decimal("0.5"))
    prediction = prediction * (Decimal("0.85") + Decimal("0.15") * dispersion)
    prediction = prediction * (Decimal("0.90") + Decimal("0.10") * completeness)
    if match.is_ambiguous:
        prediction = prediction * Decimal("0.90")
    if any(row.is_synthetic for row in cohort_rows):
        prediction = prediction * _SYNTHETIC_PENALTY

    if prediction < resolved.confidence_publish_floor:
        raise InsufficientMarketDataError(
            "confidence_below_publish_floor",
            "اطمینان تخمین از حد قابل انتشار کمتر است؛ به‌جای عددی ظاهراً دقیق، عددی ارائه نمی‌شود.",
            counts={
                "valid_samples": len(outcome.valid),
                "confidence_permille": int(prediction * 1000),
            },
        )

    level = _confidence_level(prediction)
    quarantine = outcome.quarantine_reasons

    warnings: list[str] = []
    warning_codes: list[str] = []
    if any(row.is_synthetic for row in cohort_rows):
        warnings.append(
            "دادهٔ نمونهٔ توسعه (ساختگی) استفاده شده است؛ این عدد داده بازار نیست و نباید نقل شود."
        )
        warning_codes.append("sample_data_in_use")
    if outcome.suspicious or outcome.rejected:
        warnings.append(
            f"{len(outcome.suspicious) + len(outcome.rejected)} نمونهٔ مشکوک یا رد‌شده از محاسبه خارج شد."
        )
        warning_codes.append("quarantined_rows_excluded")
    if scope != "city_seniority_employment":
        warnings.append(
            f"کوهورت مقایسه «{_SCOPE_LABEL_FA.get(scope, scope)}» است؛ "
            "تفکیک دقیق‌تر ممکن نبود و اطمینان کاهش یافت."
        )
        warning_codes.append(f"cohort_fallback_{scope}")
    if match.is_ambiguous:
        warnings.append("عنوان شغلی به بیش از یک گروه نزدیک بود؛ گروه با بالاترین امتیاز انتخاب شد.")
        warning_codes.append("ambiguous_job_family")
    if recency < 1:
        warnings.append("تازگی داده کمتر از حد مطلوب است؛ اطمینان کاهش یافت.")
        warning_codes.append("data_not_fresh")
    if len(values) < 8:
        warnings.append("حجم نمونه برای آزمون‌های آماری مقاوم (IQR/MAD) کم است.")
        warning_codes.append("small_sample")

    legal = legal_minimum_wage_reference(statutory_active_year)
    if legal is None:
        warnings.append("مرجع حداقل دستمزد قانونی در دسترس نبود؛ تخمین بدون آن ارائه شده است.")
        warning_codes.append("legal_minimum_wage_unavailable")
    else:
        warning_codes.append("legal_reference_only")

    central_toman = central // _TOMAN_QUANTUM_RIAL
    factors: list[str] = [
        f"گروه شغلی: {match.family_title_fa} (اطمینان تطبیق {match.score:.0%})",
        f"کوهورت مقایسه: {_SCOPE_LABEL_FA.get(scope, scope)}",
        f"تعداد نمونهٔ معتبر: {len(values)}",
        f"پراکندگی بازار (فاصلهٔ بین‌چارکی): {round_half_up(interquartile_range(values))} ریال",
        f"میانهٔ بازار: {central_toman} تومان",
    ]
    if quarantine:
        top = sorted(quarantine.items(), key=lambda item: (-item[1], item[0]))[:3]
        factors.append(
            "داده‌های خارج‌شده: "
            + "، ".join(f"{code} ({count})" for code, count in top)
        )

    notes: list[str] = [
        "سابقه، تحصیلات و مهارت‌ها فقط در تطبیق شغلی و توضیح نتیجه اثر دارند؛ "
        "ضریب پولی برای آن‌ها اعمال نشد چون مبنای آماری مستند ندارد.",
        "شهر، سطح تخصص و نوع استخدام از طریق انتخاب کوهورت اثر می‌کنند، نه با ضریب جداگانه؛ "
        "این کار دوباره‌شماری را حذف می‌کند.",
    ]
    if profile.experience_years >= 15 and normalize_text(profile.seniority_level) != "senior":
        notes.append(
            "سابقهٔ اعلام‌شده با سطح تخصص انتخاب‌شده هم‌خوان نیست؛ سطح تخصص تعیین‌کنندهٔ کوهورت است."
        )
        warning_codes.append("experience_seniority_mismatch")

    methodology: dict[str, object] = {
        "method": "market_cohort_quantiles",
        "estimation_version": ESTIMATION_VERSION,
        "engine_version": ENGINE_VERSION,
        "cohort_scope": scope,
        "cohort_definition": _SCOPE_LABEL_FA.get(scope, scope),
        "valid_sample_count": len(values),
        "quarantined_sample_count": len(outcome.suspicious) + len(outcome.rejected),
        "range_source": "p25_p50_p75_of_valid_observations",
        "percentile_method": "linear interpolation (R-7)",
        "outlier_tests": ["iqr_fence_3x", "modified_z_score_3_5", "p1_p99", "peer_ratio"],
        "adjustments_applied": [],
        "included_row_ids": sorted(cohort_ids),
        "data_kind": "observations",
        "dispatch": "toman",
        "quantisation": {
            "quantum_rial": _TOMAN_QUANTUM_RIAL,
            "reason": "figures are published as whole-Toman multiples so the UI never rounds",
        },
        "currency": {
            "storage": "rial",
            "published_figures": "whole-toman multiples of 10 Rial",
            "toman_divisor": 10,
        },
        "confidence_weights": {key: f"{value:.2f}" for key, value in _DATA_WEIGHTS.items()},
        "warning_codes": list(dict.fromkeys(warning_codes)),
    }

    hash_payload = {
        "profile": {
            "job_title": profile.job_title,
            "experience_years": profile.experience_years,
            "seniority_level": profile.seniority_level,
            "employment_type": profile.employment_type,
            "city": profile.city,
            "province": profile.province,
            "work_condition": profile.work_condition,
            "skills": list(profile.skills),
            "education": profile.education,
        },
        "family_key": match.family_key,
        "cohort": scope,
        "rows": sorted(cohort_ids),
        "published": [low, central, high],
        "engine_version": ENGINE_VERSION,
    }
    calculation_hash = hashlib.sha256(
        json.dumps(hash_payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()[:32]

    return EstimationOutcome(
        primary_estimate_rial=central,
        min_salary_rial=low,
        median_salary_rial=central,
        max_salary_rial=high,
        rounding_residual_rial=low_residual + central_residual + high_residual,
        valid_sample_count=len(values),
        quarantined_sample_count=len(outcome.suspicious),
        rejected_sample_count=len(outcome.rejected),
        confidence_level=level,
        confidence_score=prediction,
        data_confidence=data_confidence,
        prediction_confidence=prediction,
        confidence_components={
            "sample_size": f"{sample_component:.3f}",
            "source_quality": f"{quality:.3f}",
            "recency": f"{recency:.3f}",
            "dispersion": f"{dispersion:.3f}",
            "completeness": f"{completeness:.3f}",
            "cohort_penalty": f"{_SCOPE_PENALTY.get(scope, Decimal('0.5')):.2f}",
            "method_ceiling": f"{_METHOD_CEILING['observations']:.2f}",
        },
        confidence_weights={key: f"{value:.2f}" for key, value in _DATA_WEIGHTS.items()},
        factors_influence=tuple(factors),
        factors_notes=tuple(notes),
        data_sources=tuple(sorted({row.source_id for row in cohort_rows})),
        data_collected_at=max(row.collected_at for row in cohort_rows),
        data_oldest_at=min(row.collected_at for row in cohort_rows),
        market_rows=_market_rows(
            ValidationOutcome(
                valid=cohort_rows,
                monthly_by_id=outcome.monthly_by_id,
            ),
            confidence_level=level,
        ),
        distribution=histogram(values),
        methodology=methodology,
        warnings=tuple(warnings),
        match=match.as_dict(),
        cohort_scope=scope,
        cohort_size=len(values),
        legal_minimum_wage_rial=legal,
        calculation_hash=calculation_hash,
        generated_at=as_of,
    )
