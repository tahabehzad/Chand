"""Fail-closed, versioned statutory rule-set loader.

Authority
---------
``docs/PISH_HESABDARI_HOLY_BIBLE.md`` §10.5 (versioning), §10.6 (fail-closed
loader behaviour) and §5.11 (verified seed inspection);
``docs/specs/STATUTORY_INGESTION.md`` §7 (activation criteria A1–A8);
``docs/EXECUTION_PLAN.md`` §7.2 rule 6.
Decision:
    ADR-008 — the only loadable year is the verified 1404 baseline; 1405 is
    transcribed, unverified and inactive and must raise on request.
Related:
    WBS P1-T01 — statutory rule-set loader (versioned, fail-closed).

Contract notes
--------------
* The loader is the only component that touches the seed YAML files; the
  calculation engines receive a :class:`StatutoryRuleSet` value and never
  read the filesystem themselves.
* Fail-closed semantics: the 1405 placeholder (``is_verified_and_active:
  false`` plus null parameters) raises :class:`StatutoryParameterUnavailable`
  — never a coercion of null to zero and never a silent 1404 fallback.
* YAML float nodes are constructed as exact ``Decimal`` values from their
  scalar text, so no binary float ever enters a rate.
* Known seed defects are deliberately **not** loaded: ``eydi_tax_excess_rate``
  (the rejected flat-10 % rule, HB-GAP-005) and
  ``sanavat_monthly_accrual_rate`` (the inexact 1/12 literal, HB-GAP-017) are
  absent from :class:`StatutoryRuleSet`, so no engine can consume them.  The
  correction path for the seeds themselves remains the future ``1404.2``
  revision; the immutable files are never edited.
* ``standard_monthly_attendance_hours`` (176 h) is intentionally **not**
  exposed: it is an attendance-proration figure, never an overtime divisor
  (``FIND-LEG-03``; ``1.docx`` Defect 3).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from functools import lru_cache
from pathlib import Path
from typing import cast

import yaml

from app.engines.errors import RuleSetNotActive, StatutoryParameterUnavailable

__all__ = (
    "StatutoryRuleSet",
    "TaxBracket",
    "load_rule_set",
    "validate_invariants",
)

#: The only year whose seed may be loaded (ADR-008; PROJECT_STATUS §4).
ACTIVE_STATUTORY_YEARS: frozenset[int] = frozenset({1404})

#: Version label mandated for outputs by ``docs/EXECUTION_PLAN.md`` §3.5.
_STATUTORY_VERSION_TEMPLATE = "{year}.1"

#: Seed directory resolved from this module: ``backend/data/seeds``.
_SEEDS_DIR = Path(__file__).resolve().parents[2] / "data" / "seeds"

#: Permitted month lengths (Holy Bible §10.5 — never assume a 30-day month).
_VALID_MONTH_LENGTHS: frozenset[int] = frozenset({29, 30, 31})


def _seed_code(year: int) -> str:
    """Return the categorical seed identifier used in error codes."""
    return f"STATUTORY_SEED_{year}"


class _DecimalYamlLoader(yaml.SafeLoader):
    """A SafeLoader that constructs YAML floats as exact ``Decimal`` scalars."""


def _construct_decimal(loader: yaml.SafeLoader, node: yaml.ScalarNode) -> Decimal:
    """Build a ``Decimal`` from the node's scalar text (no float round trip)."""
    return Decimal(str(loader.construct_scalar(node)))


_DecimalYamlLoader.add_constructor("tag:yaml.org,2002:float", _construct_decimal)


@dataclass(frozen=True, slots=True)
class TaxBracket:
    """One progressive salary-tax slab (DTA Arts. 82–92; Budget Law)."""

    slab: int
    min_rial: int
    max_rial: int | None
    rate: Decimal


@dataclass(frozen=True, slots=True)
class StatutoryRuleSet:
    """An immutable, validated snapshot of one statutory rule-set version.

    All monetary parameters are whole-Rial ``int`` values; all rates and
    factors are exact ``Decimal`` values.  No ``float`` can be stored here.
    """

    statutory_version: str
    rule_year_shamsi: int
    rule_set_status: str
    is_verified: bool
    effective_date: str
    source_circular_reference: str

    daily_minimum_wage_rial: int
    monthly_minimum_wage_29days_rial: int
    monthly_minimum_wage_30days_rial: int
    monthly_minimum_wage_31days_rial: int

    monthly_housing_allowance_rial: int
    monthly_grocery_allowance_rial: int
    monthly_marriage_allowance_rial: int
    child_allowance_per_child_rial: int

    daily_seniority_base_rial: int
    monthly_seniority_base_30days_rial: int

    employee_sso_rate: Decimal
    employer_sso_rate: Decimal
    employer_unemployment_rate: Decimal

    max_daily_insurable_wage_rial: int

    @property
    def max_monthly_insurable_wage_30days_rial(self) -> int:
        """Return the 30-day insurable ceiling (invariant R-01 cross-check)."""
        return self.max_daily_insurable_wage_rial * 30

    standard_weekly_hours: Decimal
    overtime_multiplier: Decimal
    night_shift_multiplier: Decimal

    monthly_tax_exemption_rial: int
    annual_tax_exemption_rial: int
    tax_brackets: tuple[TaxBracket, ...]

    eydi_min_days: int
    eydi_max_days_min_wage: int
    max_annual_eydi_rial: int
    eydi_tax_exemption_rial: int
    non_cash_benefit_annual_tax_exemption_rial: int

    def monthly_minimum_wage_rial(self, days_in_month: int) -> int:
        """Return the statutory monthly minimum wage for *days_in_month*."""
        _require_month_length(days_in_month)
        if days_in_month == 29:
            return self.monthly_minimum_wage_29days_rial
        if days_in_month == 31:
            return self.monthly_minimum_wage_31days_rial
        return self.monthly_minimum_wage_30days_rial

    def insurable_ceiling_rial(self, days_in_month: int) -> int:
        """Return the SSO insurable ceiling for *days_in_month*.

        Social Security Law Art. 39 and SSO circular S4 item 13: the ceiling
        is 7 × the daily minimum wage **per calendar day**, applied over the
        actual month length (29/30/31).
        """
        _require_month_length(days_in_month)
        return self.max_daily_insurable_wage_rial * days_in_month

    def overtime_divisor(self, days_in_month: int) -> Decimal:
        """Return the paid-hours divisor for *days_in_month*.

        Labour Law Art. 51: 44 hours over 6 working days, so the monthly
        paid-calendar-hours divisor is ``44 × days / 6`` (220.00 for a
        30-day month; 227.33… for 31 days).  The 176-hour attendance figure
        is never used here.
        """
        _require_month_length(days_in_month)
        return self.standard_weekly_hours * days_in_month / Decimal(6)

    def bracket_for_rate(self, rate: Decimal) -> TaxBracket | None:
        """Return the first bracket carrying *rate*, if any."""
        for bracket in self.tax_brackets:
            if bracket.rate == rate:
                return bracket
        return None


def _require_month_length(days_in_month: int) -> None:
    """Reject any month length outside {29, 30, 31}."""
    if days_in_month not in _VALID_MONTH_LENGTHS:
        raise RuleSetNotActive(
            "PAYROLL_MONTH_LENGTH_INVALID: days_in_month must be 29, 30 or 31"
        )


def _mapping(value: object, key: str) -> dict[object, object]:
    """Return *value* as a plain mapping or raise categorically."""
    if not isinstance(value, dict):
        raise StatutoryParameterUnavailable(f"{key}_NOT_MAPPING: seed is malformed")
    return cast(dict[object, object], value)


def _seed_int(data: dict[object, object], key: str, year: int) -> int:
    """Return a required non-null whole-Rial parameter."""
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise StatutoryParameterUnavailable(
            f"{_seed_code(year)}_PARAMETER_UNAVAILABLE: required parameter is null or missing"
        )
    return value


def _seed_decimal(data: dict[object, object], key: str, year: int) -> Decimal:
    """Return a required non-null rate/factor parameter as an exact Decimal."""
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, Decimal):
        raise StatutoryParameterUnavailable(
            f"{_seed_code(year)}_PARAMETER_UNAVAILABLE: required parameter is null or missing"
        )
    if not value.is_finite():
        raise StatutoryParameterUnavailable(
            f"{_seed_code(year)}_PARAMETER_UNAVAILABLE: required parameter is not finite"
        )
    return value


def _seed_str(data: dict[object, object], key: str, year: int) -> str:
    """Return a required non-null string parameter."""
    value = data.get(key)
    if not isinstance(value, str):
        raise StatutoryParameterUnavailable(
            f"{_seed_code(year)}_PARAMETER_UNAVAILABLE: required parameter is null or missing"
        )
    return value


def _seed_year(data: dict[object, object], key: str, year: int) -> int:
    """Return the seed's own rule year, rejecting a mismatched label."""
    value = _seed_int(data, key, year)
    if value != year:
        raise StatutoryParameterUnavailable(
            f"{_seed_code(year)}_YEAR_MISMATCH: seed year does not match the requested year"
        )
    return value


def _seed_brackets(data: dict[object, object], year: int) -> tuple[TaxBracket, ...]:
    """Return the progressive slabs as typed, ordered tuples."""
    raw = data.get("tax_brackets")
    if not isinstance(raw, list) or not raw:
        raise StatutoryParameterUnavailable(
            f"{_seed_code(year)}_PARAMETER_UNAVAILABLE: tax_brackets is null or empty"
        )
    brackets: list[TaxBracket] = []
    for index, entry in enumerate(raw):
        row = _mapping(entry, f"tax_brackets[{index}]")
        slab = _seed_int(row, "slab", year)
        min_rial = _seed_int(row, "min_rial", year)
        raw_max = row.get("max_rial")
        max_rial: int | None
        if raw_max is None:
            max_rial = None
        elif isinstance(raw_max, int) and not isinstance(raw_max, bool):
            max_rial = raw_max
        else:
            raise StatutoryParameterUnavailable(
                f"{_seed_code(year)}_PARAMETER_UNAVAILABLE: slab maximum is invalid"
            )
        rate = _seed_decimal(row, "rate", year)
        brackets.append(
            TaxBracket(slab=slab, min_rial=min_rial, max_rial=max_rial, rate=rate)
        )
    return tuple(brackets)


def validate_invariants(rule_set: StatutoryRuleSet) -> dict[str, bool]:
    """Verify the offline-checkable subset of invariants R-01…R-10.

    R-08 is structural by construction: the Sanavat accrual is computed as
    ``Mozd-e Saabet ÷ 12`` in :mod:`app.engines.severance`; the seed's
    inexact ``sanavat_monthly_accrual_rate`` literal is never loaded
    (HB-GAP-017).  Any failed invariant raises
    :class:`StatutoryParameterUnavailable`.
    """
    results: dict[str, bool] = {
        "R-01": rule_set.max_monthly_insurable_wage_30days_rial
        == rule_set.max_daily_insurable_wage_rial * 30,
        "R-02": rule_set.annual_tax_exemption_rial
        == rule_set.monthly_tax_exemption_rial * 12,
        "R-03": rule_set.eydi_tax_exemption_rial
        == rule_set.annual_tax_exemption_rial // 12,
        "R-04": rule_set.non_cash_benefit_annual_tax_exemption_rial
        == (rule_set.annual_tax_exemption_rial * 2) // 12,
        "R-05": rule_set.child_allowance_per_child_rial
        == rule_set.daily_minimum_wage_rial * 3,
        "R-06": rule_set.max_annual_eydi_rial
        == rule_set.monthly_minimum_wage_30days_rial * 3,
        "R-07": rule_set.monthly_minimum_wage_31days_rial
        == rule_set.daily_minimum_wage_rial * 31,
        "R-08": True,
        "R-09": rule_set.tax_brackets[0].max_rial == rule_set.monthly_tax_exemption_rial,
        "R-10": rule_set.monthly_seniority_base_30days_rial
        == rule_set.daily_seniority_base_rial * 30,
    }
    failed = sorted(name for name, passed in results.items() if not passed)
    if failed:
        raise StatutoryParameterUnavailable(
            "STATUTORY_INVARIANT_VIOLATION: seed failed "
            + ",".join(failed)
        )
    return results


def _parse_seed(year: int, path: Path) -> StatutoryRuleSet:
    """Parse and validate one seed file into a :class:`StatutoryRuleSet`."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RuleSetNotActive(
            f"STATUTORY_SEED_UNREADABLE: no loadable rule set for the requested year ({year})"
        ) from exc
    loaded: object = yaml.load(text, Loader=_DecimalYamlLoader)  # noqa: S506
    data = _mapping(loaded, "seed")

    flag = data.get("is_verified_and_active")
    if flag is not True:
        # The 1405 placeholder: null parameters must never be coerced and no
        # silent fallback to 1404 may occur (Holy Bible §10.6; ADR-008).
        raise StatutoryParameterUnavailable(
            f"{_seed_code(year)}_NOT_VERIFIED: the rule set is not verified and active; "
            "null statutory parameters are never coerced and fallback is refused"
        )

    rule_year = _seed_year(data, "rule_year_shamsi", year)
    daily_minimum = _seed_int(data, "daily_minimum_wage_rial", year)
    monthly_minimum_30 = _seed_int(data, "monthly_minimum_wage_30days_rial", year)
    monthly_minimum_31 = _seed_int(data, "monthly_minimum_wage_31days_rial", year)
    weekly_hours = _seed_decimal(data, "standard_weekly_hours", year)
    brackets = _seed_brackets(data, year)

    rule_set = StatutoryRuleSet(
        statutory_version=_STATUTORY_VERSION_TEMPLATE.format(year=rule_year),
        rule_year_shamsi=rule_year,
        rule_set_status="VERIFIED",
        is_verified=True,
        effective_date=_seed_str(data, "effective_date", year),
        source_circular_reference=_seed_str(data, "source_circular_reference", year),
        daily_minimum_wage_rial=daily_minimum,
        monthly_minimum_wage_29days_rial=daily_minimum * 29,
        monthly_minimum_wage_30days_rial=monthly_minimum_30,
        monthly_minimum_wage_31days_rial=monthly_minimum_31,
        monthly_housing_allowance_rial=_seed_int(
            data, "monthly_housing_allowance_rial", year
        ),
        monthly_grocery_allowance_rial=_seed_int(
            data, "monthly_grocery_allowance_rial", year
        ),
        monthly_marriage_allowance_rial=_seed_int(
            data, "monthly_marriage_allowance_rial", year
        ),
        child_allowance_per_child_rial=_seed_int(
            data, "child_allowance_per_child_rial", year
        ),
        daily_seniority_base_rial=_seed_int(data, "daily_seniority_base_rial", year),
        monthly_seniority_base_30days_rial=_seed_int(
            data, "monthly_seniority_base_30days_rial", year
        ),
        employee_sso_rate=_seed_decimal(data, "employee_sso_rate", year),
        employer_sso_rate=_seed_decimal(data, "employer_sso_rate", year),
        employer_unemployment_rate=_seed_decimal(
            data, "employer_unemployment_rate", year
        ),
        max_daily_insurable_wage_rial=_seed_int(
            data, "max_daily_insurable_wage_rial", year
        ),
        standard_weekly_hours=weekly_hours,
        overtime_multiplier=_seed_decimal(data, "overtime_multiplier", year),
        night_shift_multiplier=_seed_decimal(data, "night_shift_multiplier", year),
        monthly_tax_exemption_rial=_seed_int(data, "monthly_tax_exemption_rial", year),
        annual_tax_exemption_rial=_seed_int(data, "annual_tax_exemption_rial", year),
        tax_brackets=brackets,
        eydi_min_days=_seed_int(data, "eydi_min_days", year),
        eydi_max_days_min_wage=_seed_int(data, "eydi_max_days_min_wage", year),
        max_annual_eydi_rial=_seed_int(data, "max_annual_eydi_rial", year),
        eydi_tax_exemption_rial=_seed_int(data, "eydi_tax_exemption_rial", year),
        non_cash_benefit_annual_tax_exemption_rial=_seed_int(
            data, "non_cash_benefit_annual_tax_exemption_rial", year
        ),
    )
    validate_invariants(rule_set)
    return rule_set


@lru_cache(maxsize=8)
def load_rule_set(year: int) -> StatutoryRuleSet:
    """Load the verified rule set for *year*, failing closed otherwise.

    Raises:
        StatutoryParameterUnavailable: The seed exists but is unverified or
            carries null parameters (the 1405 placeholder), or a structural
            invariant failed.
        RuleSetNotActive: No seed exists for *year* at all.
    """
    if year not in ACTIVE_STATUTORY_YEARS:
        # A year outside the verified baseline can never be served; the
        # message stays categorical and names no figures.
        raise RuleSetNotActive(
            "RULE_SET_YEAR_NOT_LOADABLE: the requested rule year has no "
            "verified and active rule set"
        )
    return _parse_seed(year, _SEEDS_DIR / f"statutory_rules_{year}.yaml")
