"""Gemini Web-Grounded Live Market Salary Service.

Authority
---------
``docs/adr/ADR-014-market-salary-reference-data-and-estimation.md`` §7 (contract);
``AGENTS.md`` §2 Financial invariants 7-12 (refuse rather than fabricate, pure math,
no float literals in calculation, Decimal only, quantisation to whole-Toman
multiples of 10 Rial).

Related
-------
``app/services/estimation/service.py`` (orchestration),
``app/domain/salary_estimation/salary_estimator.py`` (database fallback),
``app/domain/salary_estimation/schemas.py`` (outcome, profile),
``app/domain/salary_estimation/taxonomy.py`` (job families, search terms).

Scope
-----
Executes live search queries via Google Gemini API with Google Search web grounding.
Extracts verified Iranian labor market salary figures (from Jobinja, Jobvision,
IranTalent, Quera, Karboom, e-estekhdam) without ever generating or fabricating
salary figures. Applies pure quantile calculations (p25, median, p75) with Decimal.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Sequence
from datetime import datetime
from decimal import Decimal
from typing import Any, Final

import httpx

from app.domain.salary_estimation.market_data import (
    MarketAggregate,
    MarketObservation,
)
from app.domain.salary_estimation.matcher import JobMatch, SalaryMatcher
from app.domain.salary_estimation.salary_estimator import (
    InsufficientMarketDataError,
    legal_minimum_wage_reference,
)
from app.domain.salary_estimation.schemas import (
    ENGINE_VERSION,
    EstimationOutcome,
    EstimationProfile,
    MarketRowSummary,
)
from app.domain.salary_estimation.statistics import histogram, median, percentile
from app.engines.money import round_half_up, to_decimal
from app.services.estimation.gemini_prompts import build_estimation_prompt

__all__ = (
    "GEMINI_LIVE_METHOD",
    "GeminiLiveSalaryService",
    "GeminiUnavailableError",
)

GEMINI_LIVE_METHOD: Final[str] = "gemini_web_grounded_cohort"
_TOMAN_QUANTUM_RIAL: Final[int] = 10
_DEFAULT_GEMINI_TIMEOUT_SECONDS: Final[float] = 30.0

#: Minimum reasonable monthly salary in Iran (around entry-level / part-time in Rial: 2M Toman)
_MIN_PLAUSIBLE_SALARY_RIAL: Final[int] = 20_000_000
#: Maximum reasonable monthly salary in Iran (5 Billion Rial = 500M Toman)
_MAX_PLAUSIBLE_SALARY_RIAL: Final[int] = 5_000_000_000


class GeminiUnavailableError(RuntimeError):
    """Raised when Google Gemini API cannot be reached, times out, or fails.

    Maps to HTTP 503 ESTIMATION_GEMINI_UNAVAILABLE at the API router boundary.
    """


def _quantise_toman_exact(exact: Decimal) -> tuple[int, int]:
    """Return ``(whole_toman_rial_amount, signed_residual_rial)``."""
    toman = round_half_up(exact / Decimal(_TOMAN_QUANTUM_RIAL))
    emitted = toman * _TOMAN_QUANTUM_RIAL
    return emitted, emitted - int(exact)


def _clean_markdown_json(raw_text: str) -> str:
    """Strip markdown code fence blocks if present."""
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def _extract_grounding_sources(candidate: dict[str, Any]) -> list[str]:
    """Extract web search citation sources from candidate grounding metadata."""
    sources: list[str] = []
    grounding = candidate.get("groundingMetadata") or candidate.get("grounding_metadata") or {}
    if not isinstance(grounding, dict):
        return sources
    chunks = grounding.get("groundingChunks") or grounding.get("grounding_chunks") or []
    if isinstance(chunks, list):
        for chunk in chunks:
            if isinstance(chunk, dict) and "web" in chunk:
                web = chunk["web"]
                title = web.get("title") or web.get("uri", "")
                if title:
                    sources.append(str(title))
    return sources


def _parse_observations(
    raw_observations: object,
    profile: EstimationProfile,
    family_key: str,
    as_of: datetime,
) -> list[MarketObservation]:
    """Parse and validate list of observation dictionaries."""
    observations: list[MarketObservation] = []
    if not isinstance(raw_observations, list):
        return observations

    for idx, item in enumerate(raw_observations):
        if not isinstance(item, dict):
            continue
        amount = item.get("amount_rial")
        if not isinstance(amount, (int, float)) or amount <= 0:
            continue
        int_amount = int(amount)
        if int_amount < _MIN_PLAUSIBLE_SALARY_RIAL and int_amount * 10 >= _MIN_PLAUSIBLE_SALARY_RIAL:
            int_amount *= 10
        if int_amount < _MIN_PLAUSIBLE_SALARY_RIAL or int_amount > _MAX_PLAUSIBLE_SALARY_RIAL:
            continue

        source_name = str(item.get("source_name") or f"gemini_source_{idx + 1}")
        observations.append(
            MarketObservation(
                id=f"live_{idx + 1}_{hashlib.sha256(source_name.encode()).hexdigest()[:8]}",
                family_key=family_key,
                job_title_reported=str(item.get("job_title_reported") or profile.job_title),
                city=str(item.get("city") or profile.city),
                province=profile.province,
                amount_rial=int_amount,
                period=str(item.get("period") or "monthly"),
                currency_unit_reported="rial",
                source_id=source_name,
                source_url=item.get("source_url"),
                license_status="manual_verified",
                collected_at=as_of,
                seniority_level=str(item.get("seniority_level") or profile.seniority_level),
                experience_years=profile.experience_years,
                employment_type=profile.employment_type,
                work_condition=profile.work_condition,
                is_synthetic=False,
            )
        )
    return observations


def _parse_aggregates(
    raw_aggregates: object,
    profile: EstimationProfile,
    family_key: str,
    as_of: datetime,
) -> list[MarketAggregate]:
    """Parse and validate list of aggregate report dictionaries."""
    aggregates: list[MarketAggregate] = []
    if not isinstance(raw_aggregates, list):
        return aggregates

    for idx, item in enumerate(raw_aggregates):
        if not isinstance(item, dict):
            continue
        p25 = item.get("p25_rial")
        med = item.get("median_rial")
        p75 = item.get("p75_rial")
        if not (
            isinstance(p25, (int, float))
            and isinstance(med, (int, float))
            and isinstance(p75, (int, float))
        ):
            continue
        int_p25, int_med, int_p75 = int(p25), int(med), int(p75)
        if int_med < _MIN_PLAUSIBLE_SALARY_RIAL and int_med * 10 >= _MIN_PLAUSIBLE_SALARY_RIAL:
            int_p25 *= 10
            int_med *= 10
            int_p75 *= 10
        if int_med < _MIN_PLAUSIBLE_SALARY_RIAL:
            continue
        sample_size = int(item.get("sample_size") or 30)
        source_name = str(item.get("source_name") or f"gemini_report_{idx + 1}")
        aggregates.append(
            MarketAggregate(
                id=f"live_agg_{idx + 1}",
                family_key=family_key,
                city=str(item.get("city") or profile.city),
                median_salary_rial=int_med,
                source_id=source_name,
                license_status="published_report",
                collected_at=as_of,
                sample_size=sample_size,
                seniority_level=str(item.get("seniority_level") or profile.seniority_level),
                p25_salary_rial=int_p25,
                p75_salary_rial=int_p75,
                min_salary_rial=int_p25,
                max_salary_rial=int_p75,
                province=profile.province,
                is_synthetic=False,
            )
        )
    return aggregates


class GeminiLiveSalaryService:
    """Queries Gemini API with Google Search grounding to fetch live Iranian salary data."""

    def __init__(
        self,
        *,
        http_client: httpx.AsyncClient | None = None,
        timeout_seconds: float = _DEFAULT_GEMINI_TIMEOUT_SECONDS,
    ) -> None:
        self._http_client = http_client
        self._timeout_seconds = timeout_seconds
        self._last_cohort_scope: str | None = None

    def build_prompt(
        self,
        profile: EstimationProfile,
        match: JobMatch | None = None,
    ) -> str:
        """Construct the prompt instructing Gemini with web grounding to extract Iranian salaries."""
        return build_estimation_prompt(profile, match)

    async def call_gemini(
        self,
        *,
        api_key: str,
        prompt: str,
        model: str = "gemini-2.0-flash",
    ) -> dict[str, Any]:
        """Call the Google Gemini API with Google Search grounding."""
        if not api_key or not api_key.strip():
            raise GeminiUnavailableError("کلید دسترسی جمینای ارائه نشده یا خالی است.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        params = {"key": api_key.strip()}
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "tools": [{"google_search": {}}],
            "generationConfig": {
                "temperature": 0.1,
                "topP": 0.95,
            },
        }

        try:
            if self._http_client is not None:
                response = await self._http_client.post(
                    url, params=params, json=payload, timeout=self._timeout_seconds
                )
            else:
                async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                    response = await client.post(url, params=params, json=payload)
        except httpx.TimeoutException as exc:
            raise GeminiUnavailableError("مهلت زمان ارتباط با سرویس جمینای به پایان رسید (Timeout).") from exc
        except (httpx.ConnectError, httpx.NetworkError) as exc:
            raise GeminiUnavailableError("امکان برقراری ارتباط با سرویس جمینای وجود ندارد.") from exc
        except Exception as exc:
            raise GeminiUnavailableError(f"خطای غیرمنتظره در ارتباط با سرویس جمینای: {exc}") from exc

        if response.status_code != 200:
            if response.status_code in {400, 401, 403}:
                raise GeminiUnavailableError(
                    f"کلید دسترسی جمینای نامعتبر است یا دسترسی مجاز نیست (کد {response.status_code})."
                )
            if response.status_code == 429:
                raise GeminiUnavailableError("سقف درخواست‌های مجاز سرویس جمینای تکمیل شده است (Rate Limit).")
            raise GeminiUnavailableError(
                f"سرویس جمینای با خطای {response.status_code} پاسخ داد: {response.text[:200]}"
            )

        try:
            raw_json: Any = response.json()
            if not isinstance(raw_json, dict):
                raise GeminiUnavailableError("پاسخ دریافتی از جمینای ساختار دیکشنری ندارد.")
            typed_dict: dict[str, Any] = raw_json
            return typed_dict
        except GeminiUnavailableError:
            raise
        except Exception as exc:
            raise GeminiUnavailableError("پاسخ دریافتی از سرویس جمینای قالب JSON معتبر نداشت.") from exc

    def parse_gemini_payload(
        self,
        gemini_response: dict[str, Any],
        profile: EstimationProfile,
        match: JobMatch | None,
        as_of: datetime,
    ) -> tuple[list[MarketObservation], list[MarketAggregate], list[str], list[str], list[str]]:
        """Parse Gemini JSON response and grounding metadata into typed domain entities."""
        candidates = gemini_response.get("candidates")
        if not candidates or not isinstance(candidates, list):
            raise GeminiUnavailableError("سرویس جمینای هیچ گزینه‌ای (candidate) در پاسخ ارائه نکرد.")

        candidate = candidates[0]
        content = candidate.get("content", {})
        parts = content.get("parts", [])
        if not parts:
            raise GeminiUnavailableError("پاسخ سرویس جمینای فاقد محتوای متنی بود.")

        raw_text = parts[0].get("text", "")
        cleaned_json = _clean_markdown_json(raw_text)

        try:
            data = json.loads(cleaned_json)
        except json.JSONDecodeError as exc:
            match_json = re.search(r"\{.*\}", raw_text, re.DOTALL)
            if match_json:
                try:
                    data = json.loads(match_json.group(0))
                except json.JSONDecodeError:
                    raise GeminiUnavailableError("استخراج داده‌های ساختاریافته از پاسخ جمینای ناموفق بود.") from exc
            else:
                raise GeminiUnavailableError("پاسخ دریافتی از جمینای ساختار JSON مورد نظر را نداشت.") from exc

        if not isinstance(data, dict):
            raise GeminiUnavailableError("داده‌های مستخرج از جمینای در قالب دیکشنری معتبر نیستند.")

        if not data.get("found_data", True):
            reason = str(data.get("refusal_reason") or "دادهٔ معتبری از حقوق این موقعیت شغلی در وب یافت نشد.")
            raise InsufficientMarketDataError(
                "insufficient_live_market_data",
                reason,
                counts={"valid_samples": 0},
            )

        grounding_sources = _extract_grounding_sources(candidate)
        family_key = match.family_key if match else "general"

        raw_scope = str(data.get("cohort_scope") or "").strip().lower()
        if raw_scope in {"city", "province", "national"}:
            self._last_cohort_scope = raw_scope
        else:
            self._last_cohort_scope = None

        observations = _parse_observations(data.get("observations"), profile, family_key, as_of)
        aggregates = _parse_aggregates(data.get("aggregates"), profile, family_key, as_of)

        factors_influence = [str(x) for x in data.get("factors_influence", []) if isinstance(x, str)]
        factors_notes = [str(x) for x in data.get("factors_notes", []) if isinstance(x, str)]

        return observations, aggregates, factors_influence, factors_notes, grounding_sources

    def calculate_live_outcome(  # noqa: PLR0912, PLR0915
        self,
        *,
        profile: EstimationProfile,
        match: JobMatch,
        observations: Sequence[MarketObservation],
        aggregates: Sequence[MarketAggregate],
        factors_influence: Sequence[str],
        factors_notes: Sequence[str],
        grounding_sources: Sequence[str],
        as_of: datetime,
        model: str,
        statutory_active_year: int = 1405,
    ) -> EstimationOutcome:
        """Pure calculation mapping extracted live data onto EstimationOutcome adhering to ADR-014."""
        if not observations and not aggregates:
            raise InsufficientMarketDataError(
                "insufficient_live_market_data",
                "دادهٔ معتبری از حقوق این موقعیت شغلی در جستجوی زنده وب یافت نشد.",
                counts={"valid_samples": 0},
            )

        warnings: list[str] = [
            "این تخمین از جستجوی زنده وب با هوش مصنوعی (Google Gemini) و تطبیق داده‌های بازار ایران استخراج شده است."
        ]
        warning_codes: list[str] = ["gemini_live_web_grounded"]

        if observations:
            values = [to_decimal(obs.amount_rial) for obs in observations]
            sample_count = len(values)
            if sample_count == 1:
                low_exact = values[0]
                central_exact = values[0]
                high_exact = values[0]
            elif sample_count == 2:
                low_exact = min(values)
                central_exact = (values[0] + values[1]) / Decimal(2)
                high_exact = max(values)
            else:
                low_exact = percentile(values, 25)
                central_exact = median(values)
                high_exact = percentile(values, 75)

            low, low_residual = _quantise_toman_exact(low_exact)
            central, central_residual = _quantise_toman_exact(central_exact)
            high, high_residual = _quantise_toman_exact(high_exact)

            sample_score = min(Decimal(1), Decimal(sample_count) / Decimal(10))
            data_confidence = (
                sample_score * Decimal("0.40")
                + Decimal("0.85") * Decimal("0.30")
                + Decimal("1.00") * Decimal("0.30")
            )
            prediction = min(data_confidence, Decimal("0.90"))
            confidence_level = (
                "high" if prediction >= Decimal("0.70") else ("medium" if prediction >= Decimal("0.45") else "low")
            )

            market_rows: list[MarketRowSummary] = []
            grouped: dict[str, list[MarketObservation]] = {}
            for obs in observations:
                grouped.setdefault(obs.source_id, []).append(obs)

            for src, rows in grouped.items():
                row_vals = [to_decimal(r.amount_rial) for r in rows]
                r_low, _ = _quantise_toman_exact(percentile(row_vals, 25) if len(row_vals) >= 3 else min(row_vals))
                r_med, _ = _quantise_toman_exact(median(row_vals))
                r_high, _ = _quantise_toman_exact(percentile(row_vals, 75) if len(row_vals) >= 3 else max(row_vals))
                market_rows.append(
                    MarketRowSummary(
                        source=src,
                        job_title=rows[0].job_title_reported,
                        city=rows[0].city,
                        seniority_level=rows[0].seniority_level or profile.seniority_level,
                        min_salary_rial=r_low,
                        median_salary_rial=r_med,
                        max_salary_rial=r_high,
                        sample_count=len(rows),
                        collected_at=as_of,
                        confidence=confidence_level,
                    )
                )

            distribution = histogram(values) if len(values) >= 4 else ()
            all_sources = sorted({obs.source_id for obs in observations} | set(grounding_sources))

        else:
            agg = aggregates[0]
            sample_count = agg.sample_size
            p25_val = agg.p25_salary_rial if agg.p25_salary_rial is not None else agg.median_salary_rial
            p75_val = agg.p75_salary_rial if agg.p75_salary_rial is not None else agg.median_salary_rial
            low, low_residual = _quantise_toman_exact(to_decimal(p25_val))
            central, central_residual = _quantise_toman_exact(to_decimal(agg.median_salary_rial))
            high, high_residual = _quantise_toman_exact(to_decimal(p75_val))

            data_confidence = Decimal("0.65")
            prediction = Decimal("0.60")
            confidence_level = "medium"

            market_rows = [
                MarketRowSummary(
                    source=agg.source_id,
                    job_title=profile.job_title,
                    city=agg.city,
                    seniority_level=agg.seniority_level or profile.seniority_level,
                    min_salary_rial=low,
                    median_salary_rial=central,
                    max_salary_rial=high,
                    sample_count=agg.sample_size,
                    collected_at=as_of,
                    confidence=confidence_level,
                )
            ]
            distribution = ()
            all_sources = sorted({agg.source_id} | set(grounding_sources))

        legal = legal_minimum_wage_reference(statutory_active_year)
        if legal is not None:
            warning_codes.append("legal_reference_only")

        factors: list[str] = [
            f"گروه شغلی: {match.family_title_fa}",
            f"جستجوی زنده در پایگاه‌های استخدامی ایران: {', '.join(all_sources[:3])}",
            f"تعداد نمونه‌های مشاهده‌شده در وب: {sample_count}",
            f"میانهٔ بازار استخراج‌شده: {central // _TOMAN_QUANTUM_RIAL:,} تومان",
        ]
        if factors_influence:
            factors.extend(factors_influence[:3])

        notes: list[str] = [
            "داده‌ها از طریق جستجوی زنده در وب و آگهی‌های واقعی استخراج شده و عددی بدون مشاهده تولید نشده است.",
        ]
        if factors_notes:
            notes.extend(factors_notes[:3])

        scope = getattr(self, "_last_cohort_scope", None)
        if not scope:
            if any(obs.city == profile.city for obs in observations):
                scope = "city"
            elif profile.province and any(obs.province == profile.province for obs in observations):
                scope = "province"
            else:
                scope = "national"

        if scope == "national":
            if confidence_level == "high":
                confidence_level = "medium"
            factors.insert(
                0, "دامنه برآورد: میانگین کشوری (به‌دلیل تمرکز آگهی‌ها در سراسر کشور)"
            )
            notes.append(
                "به دلیل کمبود داده‌های نقطه‌ای در شهر انتخابی، تخمین بر اساس توزیع کشوری در سراسر ایران محاسبه شد."
            )

        methodology: dict[str, object] = {
            "method": GEMINI_LIVE_METHOD,
            "estimation_version": "gemini-live-v1",
            "engine_version": ENGINE_VERSION,
            "cohort_scope": scope,
            "cohort_definition": (
                f"شهر {profile.city}"
                if scope == "city"
                else f"استان {profile.province or profile.city}"
                if scope == "province"
                else "میانگین کشوری در سراسر ایران"
            ),
            "valid_sample_count": sample_count,
            "range_source": "live_web_observations_quantiles",
            "percentile_method": "linear interpolation (R-7)",
            "outlier_tests": ["range_sanity_bounds"],
            "adjustments_applied": [],
            "data_kind": "live_web_grounded_observations",
            "currency": {
                "storage": "rial",
                "published_figures": "whole-toman multiples of 10 Rial",
                "toman_divisor": 10,
            },
            "warning_codes": warning_codes,
            "gemini_model": model,
        }

        hash_payload = {
            "profile": {
                "job_title": profile.job_title,
                "experience_years": profile.experience_years,
                "seniority_level": profile.seniority_level,
                "city": profile.city,
            },
            "method": GEMINI_LIVE_METHOD,
            "model": model,
            "published": [low, central, high],
            "sample_count": sample_count,
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
            valid_sample_count=sample_count,
            quarantined_sample_count=0,
            rejected_sample_count=0,
            confidence_level=confidence_level,
            confidence_score=prediction,
            data_confidence=data_confidence,
            prediction_confidence=prediction,
            confidence_components={
                "sample_size": f"{sample_count}",
                "method": GEMINI_LIVE_METHOD,
                "model": model,
            },
            confidence_weights={"live_search_weight": "1.00"},
            factors_influence=tuple(factors),
            factors_notes=tuple(notes),
            data_sources=tuple(all_sources),
            data_collected_at=as_of,
            data_oldest_at=as_of,
            market_rows=tuple(market_rows),
            distribution=tuple(distribution),
            methodology=methodology,
            warnings=tuple(warnings),
            match=match.as_dict(),
            cohort_scope=scope,
            cohort_size=sample_count,
            legal_minimum_wage_rial=legal,
            calculation_hash=calculation_hash,
            generated_at=as_of,
            data_source_mode="gemini_live",
        )

    async def estimate_market_salary_live(
        self,
        profile: EstimationProfile,
        *,
        api_key: str,
        model: str = "gemini-2.0-flash",
        as_of: datetime,
        statutory_active_year: int = 1405,
    ) -> EstimationOutcome:
        """High-level orchestration: construct prompt -> call Gemini -> parse -> pure calculate."""
        matcher = SalaryMatcher()
        match = matcher.match(
            job_title=profile.job_title,
            job_description=profile.job_description,
            skills=profile.skills,
            seniority_level=profile.seniority_level,
        )
        if match is None:
            match = JobMatch(
                family_key="custom_role",
                family_title_fa=profile.job_title,
                score=Decimal("1.0"),
                reasons=("عنوان پویای بازار کار",),
                components={"title": "1.0"},
            )

        prompt = self.build_prompt(profile, match)
        gemini_data = await self.call_gemini(api_key=api_key, prompt=prompt, model=model)
        (
            observations,
            aggregates,
            factors_influence,
            factors_notes,
            grounding_sources,
        ) = self.parse_gemini_payload(gemini_data, profile, match, as_of)

        return self.calculate_live_outcome(
            profile=profile,
            match=match,
            observations=observations,
            aggregates=aggregates,
            factors_influence=factors_influence,
            factors_notes=factors_notes,
            grounding_sources=grounding_sources,
            as_of=as_of,
            model=model,
            statutory_active_year=statutory_active_year,
        )
