"""Dynamic Regulatory Sync Service for Iranian statutory payroll rules.

Authority
---------
ADR-007 (statutory repository); ADR-008 (statutory rule versioning);
ADR-014 (search grounding & refuse rather than fabricate);
``AGENTS.md`` §2 Invariants 7-12; ``financial-data-integrity`` §16.

Monitored Official Sources
--------------------------
1. ``rrk.ir`` — روزنامه رسمی جمهوری اسلامی ایران (قوانین بودجه، مصوبات هیأت وزیران)
2. ``divan-edalat.ir`` — دیوان عدالت اداری (دادنامه‌های وحدت رویه پیرامون معافیت مالیاتی و بیمه)
3. ``intamedia.ir`` — سازمان امور مالیاتی کشور (بخشنامه‌های مالیات بر درآمد حقوق مواد ۸۲ تا ۹۲)
4. ``mcls.gov.ir`` — وزارت تعاون، کار و رفاه اجتماعی (بخشنامه‌های دستمزد شورای عالی کار)
5. ``tamin.ir`` — سازمان تأمین اجتماعی (بخشنامه‌های دستمزد مقطوع و سقف بیمه)
"""

from __future__ import annotations

import datetime
import json
import os
from dataclasses import dataclass
from typing import Any, Final

import httpx

from app.engines.rules import (
    StatutoryRuleSet,
    build_rule_set_from_parameters,
    register_active_rule_set,
    rule_set_from_record,
)
from app.repositories.statutory_repository import (
    StatutoryRepository,
    StatutoryRuleSetRecord,
    bootstrap_baseline_record,
    get_default_statutory_repository,
)

__all__ = (
    "OFFICIAL_MONITORED_DOMAINS",
    "OFFICIAL_SOURCES_DESCRIPTIONS",
    "DiscoveredRegulatoryUpdate",
    "RegulatorySyncService",
    "SyncOutcome",
    "get_regulatory_sync_service",
)

OFFICIAL_MONITORED_DOMAINS: Final[tuple[str, ...]] = (
    "rrk.ir",
    "divan-edalat.ir",
    "intamedia.ir",
    "mcls.gov.ir",
    "tamin.ir",
)

OFFICIAL_SOURCES_DESCRIPTIONS: Final[tuple[str, ...]] = (
    "روزنامه رسمی جمهوری اسلامی ایران (rrk.ir)",
    "دیوان عدالت اداری (divan-edalat.ir)",
    "سازمان امور مالیاتی کشور (intamedia.ir)",
    "وزارت تعاون، کار و رفاه اجتماعی (mcls.gov.ir)",
    "سازمان تأمین اجتماعی (tamin.ir)",
)

DEFAULT_OFFICIAL_URLS: Final[tuple[str, ...]] = (
    "https://rrk.ir",
    "https://divan-edalat.ir",
    "https://intamedia.ir",
    "https://mcls.gov.ir",
    "https://tamin.ir",
)

_DEFAULT_GEMINI_TIMEOUT_SECONDS: Final[float] = 30.0


@dataclass(frozen=True, slots=True)
class DiscoveredRegulatoryUpdate:
    """Parsed parameters extracted from official sources."""

    found_update: bool
    refusal_reason: str | None
    year_shamsi: int
    daily_minimum_wage_rial: int
    monthly_housing_allowance_rial: int
    monthly_grocery_allowance_rial: int
    monthly_tax_exemption_rial: int
    tax_brackets: tuple[dict[str, Any], ...]
    max_daily_insurable_wage_rial: int
    court_precedent_active: bool
    source_circular_reference: str
    effective_date: str
    source_urls: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SyncOutcome:
    """Result of a regulatory sync run."""

    status: str  # "success", "no_change", "refused", "unavailable"
    previous_version: str
    active_version: str
    year_shamsi: int
    has_changes: bool
    message: str
    last_synced_at: str
    source_urls: list[str]
    discovered_record: StatutoryRuleSetRecord | None = None


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


def _extract_grounding_urls(gemini_response: dict[str, Any]) -> list[str]:
    """Extract grounding URLs from Gemini response candidates."""
    urls: list[str] = []
    candidates = gemini_response.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        return urls

    for cand in candidates:
        if not isinstance(cand, dict):
            continue
        grounding = cand.get("groundingMetadata") or cand.get("grounding_metadata") or {}
        if not isinstance(grounding, dict):
            continue
        chunks = grounding.get("groundingChunks") or grounding.get("grounding_chunks") or []
        if isinstance(chunks, list):
            for chunk in chunks:
                if isinstance(chunk, dict) and "web" in chunk:
                    web = chunk["web"]
                    uri = web.get("uri")
                    if uri and isinstance(uri, str):
                        urls.append(uri)
    return urls


class RegulatorySyncService:
    """Orchestrates dynamic search grounding and versioned statutory updates."""

    def __init__(
        self,
        repository: StatutoryRepository | None = None,
        http_client: httpx.AsyncClient | None = None,
        timeout_seconds: float = _DEFAULT_GEMINI_TIMEOUT_SECONDS,
    ) -> None:
        self._repository_override = repository
        self._http_client = http_client
        self._timeout_seconds = timeout_seconds
        self._last_synced_at: datetime.datetime = datetime.datetime.now(datetime.UTC)

    @property
    def repository(self) -> StatutoryRepository:
        if self._repository_override is not None:
            return self._repository_override
        return get_default_statutory_repository()

    @property
    def last_synced_at(self) -> datetime.datetime:
        return self._last_synced_at

    def build_query_prompt(self, active_rule_set: StatutoryRuleSet) -> str:
        """Formulate targeted Iranian legal queries against official portals."""
        active_year = active_rule_set.rule_year_shamsi
        return (
            "You are an expert Iranian legal researcher and statutory payroll auditor.\n"
            "Search verified Iranian official governmental portals ONLY:\n"
            "- rrk.ir (روزنامه رسمی جمهوری اسلامی ایران)\n"
            "- divan-edalat.ir (دیوان عدالت اداری)\n"
            "- intamedia.ir (سازمان امور مالیاتی کشور)\n"
            "- mcls.gov.ir (وزارت تعاون، کار و رفاه اجتماعی)\n"
            "- tamin.ir (سازمان تأمین اجتماعی)\n\n"
            "TARGET REGULATORY QUERIES TO RESEARCH:\n"
            '1. "آخرین مصوبه حداقل دستمزد شورای عالی کار و حق مسکن و بن کارگری"\n'
            '2. "سقف معافیت مالیات بر حقوق سالانه و ماهانه و پلههای مالیاتی بودجه کشور"\n'
            '3. "آخرین آرای وحدت رویه و دادنامههای دیوان عدالت اداری درباره معافیت مالیاتی مزایای رفاهی و انگیزه کار و ماده ۱۳۷"\n\n'
            f"CURRENT ACTIVE BASELINE (Year {active_year} Shamsi):\n"
            f"- Daily Minimum Wage: {active_rule_set.daily_minimum_wage_rial:,} Rial\n"
            f"- Monthly Housing Allowance: {active_rule_set.monthly_housing_allowance_rial:,} Rial\n"
            f"- Monthly Grocery Allowance: {active_rule_set.monthly_grocery_allowance_rial:,} Rial\n"
            f"- Monthly Tax Exemption: {active_rule_set.monthly_tax_exemption_rial:,} Rial\n"
            f"- Max Daily Insurable Wage: {active_rule_set.max_daily_insurable_wage_rial:,} Rial\n\n"
            "INVARIANT (Refuse Rather Than Fabricate):\n"
            "- If NO official new law, budget act, or circular has been officially gazetted, set found_update = false.\n"
            "- NEVER fabricate, hallucinate or guess statutory parameters.\n"
            "- Return amounts in whole Iranian RIAL (not Toman). (1 Toman = 10 Rial).\n"
            "- Daily insurable ceiling is strictly 7x daily minimum wage.\n\n"
            "RESPONSE JSON FORMAT:\n"
            "{\n"
            '  "found_update": false,\n'
            '  "refusal_reason": "هیچ مصوبه جدیدی در روزنامه رسمی یا تارنماهای مراجع رسمی برای سال جدید درج نشده است",\n'
            '  "year_shamsi": 1404,\n'
            '  "daily_minimum_wage_rial": 3463656,\n'
            '  "monthly_housing_allowance_rial": 9000000,\n'
            '  "monthly_grocery_allowance_rial": 22000000,\n'
            '  "monthly_tax_exemption_rial": 240000000,\n'
            '  "tax_brackets": [\n'
            '    {"slab": 1, "min_rial": 0, "max_rial": 240000000, "rate": "0.00"},\n'
            '    {"slab": 2, "min_rial": 240000001, "max_rial": 300000000, "rate": "0.10"},\n'
            '    {"slab": 3, "min_rial": 300000001, "max_rial": 380000000, "rate": "0.15"},\n'
            '    {"slab": 4, "min_rial": 380000001, "max_rial": 500000000, "rate": "0.20"},\n'
            '    {"slab": 5, "min_rial": 500000001, "max_rial": 666666667, "rate": "0.25"},\n'
            '    {"slab": 6, "min_rial": 666666668, "max_rial": null, "rate": "0.30"}\n'
            "  ],\n"
            '  "max_daily_insurable_wage_rial": 24245592,\n'
            '  "court_precedent_active": true,\n'
            '  "source_circular_reference": "عنوان بخشنامه رسمی یا شماره دادنامه",\n'
            '  "effective_date": "1404-01-01",\n'
            '  "source_urls": ["https://rrk.ir/..."]\n'
            "}"
        )

    async def call_gemini_grounding(
        self,
        *,
        api_key: str,
        prompt: str,
        model: str = "gemini-2.0-flash",
    ) -> dict[str, Any]:
        """Call Google Gemini API with Google Search Grounding."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        params = {"key": api_key.strip()}
        payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "tools": [{"google_search": {}}],
            "generationConfig": {
                "temperature": 0.0,
                "topP": 0.95,
            },
        }

        if self._http_client is not None:
            res = await self._http_client.post(
                url, params=params, json=payload, timeout=self._timeout_seconds
            )
        else:
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                res = await client.post(url, params=params, json=payload)

        if res.status_code != 200:
            raise RuntimeError(
                f"Gemini API returned error code {res.status_code}: {res.text[:200]}"
            )

        data = res.json()
        if not isinstance(data, dict):
            raise RuntimeError("Gemini API response is not a valid JSON dictionary")
        return data

    def parse_gemini_response(
        self,
        response_data: dict[str, Any],
        fallback_year: int = 1404,
    ) -> DiscoveredRegulatoryUpdate:
        """Parse, validate, and enforce invariants on the grounded response."""
        candidates = response_data.get("candidates")
        if not isinstance(candidates, list) or not candidates:
            return DiscoveredRegulatoryUpdate(
                found_update=False,
                refusal_reason="پاسخی از مدل استخراج نشد",
                year_shamsi=fallback_year,
                daily_minimum_wage_rial=0,
                monthly_housing_allowance_rial=0,
                monthly_grocery_allowance_rial=0,
                monthly_tax_exemption_rial=0,
                tax_brackets=(),
                max_daily_insurable_wage_rial=0,
                court_precedent_active=True,
                source_circular_reference="",
                effective_date=f"{fallback_year}-01-01",
                source_urls=(),
            )

        cand = candidates[0]
        content = cand.get("content", {})
        parts = content.get("parts", [])
        text = ""
        for p in parts:
            if isinstance(p, dict) and "text" in p:
                text += p["text"]

        cleaned = _clean_markdown_json(text)
        try:
            parsed = json.loads(cleaned)
        except Exception:
            return DiscoveredRegulatoryUpdate(
                found_update=False,
                refusal_reason="پاسخ مدل ساختار JSON معتبر نداشت",
                year_shamsi=fallback_year,
                daily_minimum_wage_rial=0,
                monthly_housing_allowance_rial=0,
                monthly_grocery_allowance_rial=0,
                monthly_tax_exemption_rial=0,
                tax_brackets=(),
                max_daily_insurable_wage_rial=0,
                court_precedent_active=True,
                source_circular_reference="",
                effective_date=f"{fallback_year}-01-01",
                source_urls=(),
            )

        grounding_urls = _extract_grounding_urls(response_data)
        response_urls = parsed.get("source_urls", [])
        if isinstance(response_urls, list):
            for u in response_urls:
                if isinstance(u, str) and u not in grounding_urls:
                    grounding_urls.append(u)

        found_update = bool(parsed.get("found_update", False))
        refusal_reason = parsed.get("refusal_reason")
        year_shamsi = int(parsed.get("year_shamsi", fallback_year))
        daily_min = int(parsed.get("daily_minimum_wage_rial", 0))
        monthly_housing = int(parsed.get("monthly_housing_allowance_rial", 0))
        monthly_grocery = int(parsed.get("monthly_grocery_allowance_rial", 0))
        monthly_tax_exemp = int(parsed.get("monthly_tax_exemption_rial", 0))
        max_daily_insurable = int(
            parsed.get("max_daily_insurable_wage_rial", daily_min * 7)
        )
        court_precedent = bool(parsed.get("court_precedent_active", True))
        source_ref = str(parsed.get("source_circular_reference", ""))
        effective_date = str(parsed.get("effective_date", f"{year_shamsi}-01-01"))

        raw_brackets = parsed.get("tax_brackets", [])
        brackets_list: list[dict[str, Any]] = [
            dict(item) for item in raw_brackets if isinstance(item, dict)
        ] if isinstance(raw_brackets, list) else []

        # Enforce statutory rule: insurable daily wage must equal 7 * daily_minimum_wage
        if daily_min > 0:
            max_daily_insurable = daily_min * 7

        return DiscoveredRegulatoryUpdate(
            found_update=found_update,
            refusal_reason=str(refusal_reason) if refusal_reason else None,
            year_shamsi=year_shamsi,
            daily_minimum_wage_rial=daily_min,
            monthly_housing_allowance_rial=monthly_housing,
            monthly_grocery_allowance_rial=monthly_grocery,
            monthly_tax_exemption_rial=monthly_tax_exemp,
            tax_brackets=tuple(brackets_list),
            max_daily_insurable_wage_rial=max_daily_insurable,
            court_precedent_active=court_precedent,
            source_circular_reference=source_ref,
            effective_date=effective_date,
            source_urls=tuple(grounding_urls),
        )

    def _has_changes(
        self,
        active_record: StatutoryRuleSetRecord,
        update: DiscoveredRegulatoryUpdate,
    ) -> bool:
        """Check if discovered parameters differ from the active rule set."""
        p = active_record.parameters_json
        if update.daily_minimum_wage_rial != p.get("daily_minimum_wage_rial"):
            return True
        if update.monthly_housing_allowance_rial != p.get("monthly_housing_allowance_rial"):
            return True
        if update.monthly_grocery_allowance_rial != p.get("monthly_grocery_allowance_rial"):
            return True
        if update.monthly_tax_exemption_rial != p.get("monthly_tax_exemption_rial"):
            return True
        return update.year_shamsi != active_record.rule_year_shamsi

    async def sync(
        self,
        api_key: str | None = None,
        force: bool = False,
    ) -> SyncOutcome:
        """Execute the sync pipeline, comparing discovered rules against active ones."""
        self._last_synced_at = datetime.datetime.now(datetime.UTC)
        resolved_key = api_key or os.environ.get("GEMINI_API_KEY", "")

        active_record = await self.repository.get_active_rule_set_record()
        if active_record is None:
            active_record = bootstrap_baseline_record()

        active_rule_set = rule_set_from_record(active_record)

        if not resolved_key or not resolved_key.strip():
            # If no API key is supplied, keep existing active rule set without fabricating
            return SyncOutcome(
                status="no_change",
                previous_version=active_record.version_id,
                active_version=active_record.version_id,
                year_shamsi=active_record.rule_year_shamsi,
                has_changes=False,
                message="کلید جستجوی وب ارائه نشد؛ نسخهٔ فعال قوانین جاری معتبر حفظ شد.",
                last_synced_at=self._last_synced_at.isoformat(),
                source_urls=list(active_record.source_urls) or list(DEFAULT_OFFICIAL_URLS),
            )

        try:
            prompt = self.build_query_prompt(active_rule_set)
            gemini_data = await self.call_gemini_grounding(
                api_key=resolved_key, prompt=prompt
            )
            discovered = self.parse_gemini_response(
                gemini_data, fallback_year=active_record.rule_year_shamsi
            )
        except Exception as exc:
            return SyncOutcome(
                status="unavailable",
                previous_version=active_record.version_id,
                active_version=active_record.version_id,
                year_shamsi=active_record.rule_year_shamsi,
                has_changes=False,
                message=f"بررسی برخط قوانین با خطا مواجه شد: {exc}",
                last_synced_at=self._last_synced_at.isoformat(),
                source_urls=list(active_record.source_urls) or list(DEFAULT_OFFICIAL_URLS),
            )

        if not discovered.found_update and not force:
            # INVARIANT: Refuse rather than fabricate
            return SyncOutcome(
                status="no_change",
                previous_version=active_record.version_id,
                active_version=active_record.version_id,
                year_shamsi=active_record.rule_year_shamsi,
                has_changes=False,
                message=(
                    discovered.refusal_reason
                    or "بررسی مراجع رسمی انجام شد؛ مصوبه جدیدی برای جایگزینی وجود ندارد."
                ),
                last_synced_at=self._last_synced_at.isoformat(),
                source_urls=list(discovered.source_urls) or list(active_record.source_urls),
            )

        # Check if actual changes exist
        if not self._has_changes(active_record, discovered) and not force:
            return SyncOutcome(
                status="no_change",
                previous_version=active_record.version_id,
                active_version=active_record.version_id,
                year_shamsi=active_record.rule_year_shamsi,
                has_changes=False,
                message="مقادیر استخراج‌شده با نسخهٔ فعال فعلی یکسان است؛ نیازی به ایجاد نسخه جدید نیست.",
                last_synced_at=self._last_synced_at.isoformat(),
                source_urls=list(discovered.source_urls) or list(active_record.source_urls),
            )

        # Formulate new version id:
        # Same year -> increment revision e.g. 1404.1 -> 1404.2
        # New year -> 1405.1
        if discovered.year_shamsi == active_record.rule_year_shamsi:
            new_rev = active_record.revision + 1
            new_version_id = f"{discovered.year_shamsi}.{new_rev}"
        else:
            new_version_id = f"{discovered.year_shamsi}.1"

        daily_min = discovered.daily_minimum_wage_rial
        monthly_min_30 = daily_min * 30
        annual_tax_exemp = discovered.monthly_tax_exemption_rial * 12

        new_params = dict(active_record.parameters_json)
        new_params["rule_year_shamsi"] = discovered.year_shamsi
        new_params["daily_minimum_wage_rial"] = daily_min
        new_params["monthly_minimum_wage_30days_rial"] = monthly_min_30
        new_params["monthly_minimum_wage_31days_rial"] = daily_min * 31
        new_params["monthly_minimum_wage_29days_rial"] = daily_min * 29
        new_params["child_allowance_per_child_rial"] = daily_min * 3
        new_params["max_annual_eydi_rial"] = monthly_min_30 * 3

        new_params["monthly_housing_allowance_rial"] = (
            discovered.monthly_housing_allowance_rial
        )
        new_params["monthly_grocery_allowance_rial"] = (
            discovered.monthly_grocery_allowance_rial
        )
        new_params["monthly_tax_exemption_rial"] = discovered.monthly_tax_exemption_rial
        new_params["annual_tax_exemption_rial"] = annual_tax_exemp
        new_params["eydi_tax_exemption_rial"] = annual_tax_exemp // 12
        new_params["non_cash_benefit_annual_tax_exemption_rial"] = (
            annual_tax_exemp * 2
        ) // 12

        new_params["max_daily_insurable_wage_rial"] = (
            discovered.max_daily_insurable_wage_rial
        )
        new_params["seed_max_monthly_insurable_wage_30days_rial"] = (
            discovered.max_daily_insurable_wage_rial * 30
        )
        new_params["court_precedent_active"] = discovered.court_precedent_active
        new_params["source_circular_reference"] = discovered.source_circular_reference
        new_params["effective_date"] = discovered.effective_date

        if discovered.tax_brackets:
            new_params["tax_brackets"] = [dict(b) for b in discovered.tax_brackets]

        # Invariant check: try building StatutoryRuleSet to ensure invariants pass
        rule_set = build_rule_set_from_parameters(
            new_params,
            year=discovered.year_shamsi,
            version=new_version_id,
            status="ACTIVE",
        )

        persisted_record = await self.repository.save_new_version(
            version_id=new_version_id,
            effective_from=datetime.date.fromisoformat("2025-03-21"),
            source_reference=discovered.source_circular_reference,
            source_urls=discovered.source_urls,
            parameters_json=new_params,
            is_active=True,
            supersedes_id=active_record.id,
        )

        # Register active in memory cache
        register_active_rule_set(rule_set)

        return SyncOutcome(
            status="success",
            previous_version=active_record.version_id,
            active_version=new_version_id,
            year_shamsi=discovered.year_shamsi,
            has_changes=True,
            message=f"نسخه جدید {new_version_id} با موفقیت استخراج، اعتبارسنجی و در پایگاه داده ثبت شد.",
            last_synced_at=self._last_synced_at.isoformat(),
            source_urls=list(discovered.source_urls),
            discovered_record=persisted_record,
        )

    async def get_status(self) -> dict[str, Any]:
        """Return the current regulatory synchronization status."""
        active_record = await self.repository.get_active_rule_set_record()
        if active_record is None:
            active_record = bootstrap_baseline_record()

        effective_date_str = str(
            active_record.parameters_json.get(
                "effective_date", active_record.effective_from.isoformat()
            )
        )

        urls = list(active_record.source_urls) if active_record.source_urls else list(
            DEFAULT_OFFICIAL_URLS
        )

        return {
            "active_version": active_record.version_id,
            "year_shamsi": active_record.rule_year_shamsi,
            "effective_date": effective_date_str,
            "last_synced_at": self._last_synced_at.isoformat(),
            "sources": list(OFFICIAL_SOURCES_DESCRIPTIONS),
            "source_urls": urls,
        }


class _SyncServiceContainer:
    instance: RegulatorySyncService | None = None


def get_regulatory_sync_service() -> RegulatorySyncService:
    """Return singleton instance of RegulatorySyncService."""
    if _SyncServiceContainer.instance is None:
        _SyncServiceContainer.instance = RegulatorySyncService()
    return _SyncServiceContainer.instance


def clear_regulatory_sync_service() -> None:
    """Clear singleton instance of RegulatorySyncService."""
    _SyncServiceContainer.instance = None
