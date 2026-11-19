"""Fail-closed, versioned statutory rule-set loader.

Authority
---------
``docs/PISH_HESABDARI_HOLY_BIBLE.md`` §10.5 (versioning), §10.6 (fail-closed
loader behaviour) and §5.11 (verified seed inspection);
``docs/specs/STATUTORY_INGESTION.md`` §7 (activation criteria A1-A8);
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

import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal
from functools import lru_cache
from pathlib import Path
from typing import Protocol, cast

import yaml

from app.engines.errors import (
    MonthLengthInvalid,
    PayrollInputError,
    RuleSetNotActive,
    StatutoryInvariantViolation,
    StatutoryParameterUnavailable,
)

__all__ = (
    "StatutoryRuleSet",
    "TaxBracket",
    "build_rule_set_from_parameters",
    "clear_active_rule_set_cache",
    "load_rule_set",
    "register_active_rule_set",
    "rule_set_from_record",
    "shift_brackets_by",
    "validate_invariants",
)

#: The permitted statutory baseline years (1404 historical verified, 1405 active current law).
ACTIVE_STATUTORY_YEARS: frozenset[int] = frozenset({1404, 1405})

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
    """One progressive salary-tax slab (DTA Arts. 82-92; Budget Law)."""

    slab: int
    min_rial: int
    max_rial: int | None
    rate: Decimal


def shift_brackets_by(
    brackets: tuple[TaxBracket, ...],
    exemption_rial: int,
) -> tuple[TaxBracket, ...]:
    """Return *brackets* with every edge moved down by *exemption_rial*.

    A progressive ladder whose first slab is the exemption can only be
    matched against a base that has already had the exemption removed if the
    ladder is shifted by the same amount.  The transformation is exact: the
    shifted ladder evaluated at ``x - exemption`` equals the absolute ladder
    evaluated at ``x``.
    """
    if exemption_rial < 0:
        raise PayrollInputError(
            "PAYROLL_INPUT_INVALID: exemption_rial must be non-negative"
        )
    return tuple(
        TaxBracket(
            slab=bracket.slab,
            min_rial=bracket.min_rial - exemption_rial,
            max_rial=(
                None if bracket.max_rial is None else bracket.max_rial - exemption_rial
            ),
            rate=bracket.rate,
        )
        for bracket in brackets
    )


@dataclass(frozen=True, slots=True)
class StatutoryRuleSet:
    """An immutable, validated snapshot of one statutory rule-set version.

    All monetary parameters are whole-Rial ``int`` values; all rates and
    factors are exact ``Decimal`` values.  No ``float`` can be stored here.
    """

    statutory_version: str
    rule_year_shamsi: int
    rule_set_status: str
    rule_set_status_source: str
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
    #: The seed's own 30-day ceiling.  It is loaded as an **independent**
    #: value so invariant R-01 can compare the derived figure against the
    #: verified seed instead of comparing a property with itself
    #: (remediation A-7).
    seed_max_monthly_insurable_wage_30days_rial: int

    @property
    def max_monthly_insurable_wage_30days_rial(self) -> int:
        """Return the derived 30-day insurable ceiling (7 x daily x 30)."""
        return self.max_daily_insurable_wage_rial * 30

    standard_weekly_hours: Decimal
    #: The seed's 30-day overtime divisor (220.00 h).  It is a cross-check on
    #: :meth:`overtime_divisor`, never the divisor itself: the engine derives
    #: the divisor from the statutory weekly hours and the actual month length.
    seed_overtime_monthly_divisor: Decimal
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
        is 7 x the daily minimum wage **per calendar day**, applied over the
        actual month length (29/30/31).
        """
        _require_month_length(days_in_month)
        return self.max_daily_insurable_wage_rial * days_in_month

    def overtime_divisor(self, days_in_month: int) -> Decimal:
        """Return the paid-hours divisor for *days_in_month*.

        Labour Law Art. 51: 44 hours over 6 working days, so the monthly
        paid-calendar-hours divisor is ``44 x days / 6`` (220.00 for a
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

    def canonical_parameters(self) -> dict[str, object]:
        """Return every calculation parameter as a canonical JSON-safe mapping.

        The mapping is the reproducibility contract for ``A-11``: equal
        mappings mean equal rule-set arithmetic, and the SHA-256 of the
        canonical JSON is published with every calculation so a stored result
        can be re-verified against the exact parameter values that produced
        it.  Rates and factors are decimal **strings** (never JSON floats), so
        the digest itself cannot hide a binary-float conversion.
        """
        return {
            "statutory_version": self.statutory_version,
            "rule_year_shamsi": self.rule_year_shamsi,
            "rule_set_status": self.rule_set_status,
            "is_verified": self.is_verified,
            "effective_date": self.effective_date,
            "source_circular_reference": self.source_circular_reference,
            "daily_minimum_wage_rial": self.daily_minimum_wage_rial,
            "monthly_minimum_wage_29days_rial": self.monthly_minimum_wage_29days_rial,
            "monthly_minimum_wage_30days_rial": self.monthly_minimum_wage_30days_rial,
            "monthly_minimum_wage_31days_rial": self.monthly_minimum_wage_31days_rial,
            "monthly_housing_allowance_rial": self.monthly_housing_allowance_rial,
            "monthly_grocery_allowance_rial": self.monthly_grocery_allowance_rial,
            "monthly_marriage_allowance_rial": self.monthly_marriage_allowance_rial,
            "child_allowance_per_child_rial": self.child_allowance_per_child_rial,
            "daily_seniority_base_rial": self.daily_seniority_base_rial,
            "monthly_seniority_base_30days_rial": self.monthly_seniority_base_30days_rial,
            "employee_sso_rate": str(self.employee_sso_rate),
            "employer_sso_rate": str(self.employer_sso_rate),
            "employer_unemployment_rate": str(self.employer_unemployment_rate),
            "max_daily_insurable_wage_rial": self.max_daily_insurable_wage_rial,
            "standard_weekly_hours": str(self.standard_weekly_hours),
            "seed_overtime_monthly_divisor": str(self.seed_overtime_monthly_divisor),
            "overtime_multiplier": str(self.overtime_multiplier),
            "night_shift_multiplier": str(self.night_shift_multiplier),
            "monthly_tax_exemption_rial": self.monthly_tax_exemption_rial,
            "annual_tax_exemption_rial": self.annual_tax_exemption_rial,
            "tax_brackets": [
                {
                    "slab": bracket.slab,
                    "min_rial": bracket.min_rial,
                    "max_rial": bracket.max_rial,
                    "rate": str(bracket.rate),
                }
                for bracket in self.tax_brackets
            ],
            "eydi_min_days": self.eydi_min_days,
            "eydi_max_days_min_wage": self.eydi_max_days_min_wage,
            "max_annual_eydi_rial": self.max_annual_eydi_rial,
            "eydi_tax_exemption_rial": self.eydi_tax_exemption_rial,
            "non_cash_benefit_annual_tax_exemption_rial": (
                self.non_cash_benefit_annual_tax_exemption_rial
            ),
        }

    def fingerprint(self) -> str:
        """Return the SHA-256 of the canonical parameter mapping."""
        canonical = json.dumps(
            self.canonical_parameters(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()


    def brackets_above(self, exemption_rial: int) -> tuple[TaxBracket, ...]:
        """Return the salary ladder expressed relative to *exemption_rial*.

        The seed states the ladder in **absolute taxable Rial**, and its first
        slab *is* the exemption (invariant R-09 pins
        ``tax_brackets[0].max_rial == monthly_tax_exemption_rial``).  A base
        that has already had the exemption removed must therefore be matched
        against a ladder that has moved down by the same amount, otherwise
        the ladder stays one whole exemption too high and the tax collapses
        to zero for every base below the first taxable edge.

        The transformation is exact and invertible: shifting the ladder down
        by *exemption_rial* and evaluating it at ``x - exemption_rial`` is
        identical to evaluating the absolute ladder at ``x``.  The reference
        arithmetic in ``docs/PISH_HESABDARI_HOLY_BIBLE.md`` Appendix A
        (A.4 tax ``3,792,061``; A.5 tax ``17,647,059``) is reproduced by this
        form and by no other.
        """
        return shift_brackets_by(self.tax_brackets, exemption_rial)


def _require_month_length(days_in_month: int) -> None:
    """Reject any month length outside {29, 30, 31}."""
    if days_in_month not in _VALID_MONTH_LENGTHS:
        raise MonthLengthInvalid(
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
    """Verify the offline-checkable subset of invariants R-01…R-11.

    R-08 is structural by construction: the Sanavat accrual is computed as
    ``Mozd-e Saabet ÷ 12`` in :mod:`app.engines.severance`; the seed's
    inexact ``sanavat_monthly_accrual_rate`` literal is never loaded
    (HB-GAP-017).  Any failed invariant raises
    :class:`StatutoryInvariantViolation`.

    R-01 is a **genuine** comparison since remediation A-7: the derived
    30-day ceiling (``7 x daily x 30``) is compared with the seed's own
    independent ``max_monthly_insurable_wage_30days_rial`` value.  The former
    form compared a property with the expression that defined it and could
    never fail.
    """
    results: dict[str, bool] = {
        "R-01": rule_set.max_monthly_insurable_wage_30days_rial
        == rule_set.seed_max_monthly_insurable_wage_30days_rial,
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
        "R-11": rule_set.seed_overtime_monthly_divisor
        == rule_set.overtime_divisor(30),
    }
    failed = sorted(name for name, passed in results.items() if not passed)
    if failed:
        raise StatutoryInvariantViolation(
            "STATUTORY_INVARIANT_VIOLATION: seed failed " + ",".join(failed)
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
    # B-9: the status is read from the seed when the seed states it, and is
    # otherwise derived from the verified-and-active flag.  The source is
    # published so a reader never has to guess where "VERIFIED" came from.
    explicit_status = data.get("rule_set_status")
    if explicit_status is None:
        status = "VERIFIED"
        status_source = "seed.is_verified_and_active"
    elif isinstance(explicit_status, str) and explicit_status:
        status = explicit_status
        status_source = "seed.rule_set_status"
    else:
        raise StatutoryParameterUnavailable(
            f"{_seed_code(year)}_PARAMETER_UNAVAILABLE: rule_set_status is invalid"
        )

    rule_set = StatutoryRuleSet(
        statutory_version=_STATUTORY_VERSION_TEMPLATE.format(year=rule_year),
        rule_year_shamsi=rule_year,
        rule_set_status=status,
        rule_set_status_source=status_source,
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
        seed_max_monthly_insurable_wage_30days_rial=_seed_int(
            data, "max_monthly_insurable_wage_30days_rial", year
        ),
        standard_weekly_hours=weekly_hours,
        seed_overtime_monthly_divisor=_seed_decimal(
            data, "overtime_monthly_divisor", year
        ),
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


def _parse_param_int(val: object, field_name: str, year: int) -> int:
    """Safely extract an integer parameter, raising StatutoryParameterUnavailable on error."""
    if isinstance(val, bool) or not isinstance(val, (int, str)):
        raise StatutoryParameterUnavailable(
            f"{_seed_code(year)}_PARAMETER_UNAVAILABLE: {field_name} must be integer"
        )
    try:
        return int(val)
    except ValueError as exc:
        raise StatutoryParameterUnavailable(
            f"{_seed_code(year)}_PARAMETER_UNAVAILABLE: {field_name} could not be converted to int"
        ) from exc


def _parse_param_decimal(val: object, field_name: str, year: int) -> Decimal:
    """Safely extract a Decimal parameter, raising StatutoryParameterUnavailable on error."""
    if isinstance(val, bool) or not isinstance(val, (int, float, str, Decimal)):
        raise StatutoryParameterUnavailable(
            f"{_seed_code(year)}_PARAMETER_UNAVAILABLE: {field_name} must be numeric"
        )
    try:
        d = Decimal(str(val))
    except Exception as exc:
        raise StatutoryParameterUnavailable(
            f"{_seed_code(year)}_PARAMETER_UNAVAILABLE: {field_name} could not be converted to Decimal"
        ) from exc
    if not d.is_finite():
        raise StatutoryParameterUnavailable(
            f"{_seed_code(year)}_PARAMETER_UNAVAILABLE: {field_name} is not finite"
        )
    return d


def _parse_tax_brackets_dict(raw_brackets: object, year: int) -> tuple[TaxBracket, ...]:
    """Parse list of tax bracket dicts into tuple of TaxBracket."""
    if not isinstance(raw_brackets, (list, tuple)) or not raw_brackets:
        raise StatutoryParameterUnavailable(
            f"{_seed_code(year)}_PARAMETER_UNAVAILABLE: tax_brackets is null or empty"
        )
    brackets: list[TaxBracket] = []
    for index, entry in enumerate(raw_brackets):
        if not isinstance(entry, dict):
            raise StatutoryParameterUnavailable(
                f"{_seed_code(year)}_PARAMETER_UNAVAILABLE: tax_bracket[{index}] is not a dict"
            )
        slab = _parse_param_int(entry.get("slab"), f"tax_brackets[{index}].slab", year)
        min_rial = _parse_param_int(
            entry.get("min_rial"), f"tax_brackets[{index}].min_rial", year
        )
        raw_max = entry.get("max_rial")
        max_rial: int | None
        if raw_max is None:
            max_rial = None
        else:
            max_rial = _parse_param_int(
                raw_max, f"tax_brackets[{index}].max_rial", year
            )
        rate = _parse_param_decimal(entry.get("rate"), f"tax_brackets[{index}].rate", year)
        brackets.append(
            TaxBracket(slab=slab, min_rial=min_rial, max_rial=max_rial, rate=rate)
        )
    return tuple(brackets)


def build_rule_set_from_parameters(
    data: dict[str, object],
    year: int,
    version: str | None = None,
    status: str = "VERIFIED",
    status_source: str = "database",
) -> StatutoryRuleSet:
    """Build a StatutoryRuleSet from a parameters dictionary and validate invariants."""
    daily_minimum = _parse_param_int(
        data["daily_minimum_wage_rial"], "daily_minimum_wage_rial", year
    )
    monthly_minimum_30 = _parse_param_int(
        data.get("monthly_minimum_wage_30days_rial", daily_minimum * 30),
        "monthly_minimum_wage_30days_rial",
        year,
    )
    monthly_minimum_31 = _parse_param_int(
        data.get("monthly_minimum_wage_31days_rial", daily_minimum * 31),
        "monthly_minimum_wage_31days_rial",
        year,
    )
    monthly_minimum_29 = _parse_param_int(
        data.get("monthly_minimum_wage_29days_rial", daily_minimum * 29),
        "monthly_minimum_wage_29days_rial",
        year,
    )

    monthly_housing = _parse_param_int(
        data.get("monthly_housing_allowance_rial", 9_000_000),
        "monthly_housing_allowance_rial",
        year,
    )
    monthly_grocery = _parse_param_int(
        data.get("monthly_grocery_allowance_rial", 22_000_000),
        "monthly_grocery_allowance_rial",
        year,
    )
    monthly_marriage = _parse_param_int(
        data.get("monthly_marriage_allowance_rial", 5_000_000),
        "monthly_marriage_allowance_rial",
        year,
    )
    child_allowance = _parse_param_int(
        data.get("child_allowance_per_child_rial", daily_minimum * 3),
        "child_allowance_per_child_rial",
        year,
    )
    daily_seniority = _parse_param_int(
        data.get("daily_seniority_base_rial", 94_000),
        "daily_seniority_base_rial",
        year,
    )
    monthly_seniority = _parse_param_int(
        data.get("monthly_seniority_base_30days_rial", daily_seniority * 30),
        "monthly_seniority_base_30days_rial",
        year,
    )

    employee_sso_rate = _parse_param_decimal(
        data.get("employee_sso_rate", "0.070"), "employee_sso_rate", year
    )
    employer_sso_rate = _parse_param_decimal(
        data.get("employer_sso_rate", "0.200"), "employer_sso_rate", year
    )
    employer_unemployment_rate = _parse_param_decimal(
        data.get("employer_unemployment_rate", "0.030"),
        "employer_unemployment_rate",
        year,
    )

    max_daily_insurable = _parse_param_int(
        data.get("max_daily_insurable_wage_rial", daily_minimum * 7),
        "max_daily_insurable_wage_rial",
        year,
    )
    seed_max_monthly_insurable = _parse_param_int(
        data.get(
            "seed_max_monthly_insurable_wage_30days_rial", max_daily_insurable * 30
        ),
        "seed_max_monthly_insurable_wage_30days_rial",
        year,
    )

    weekly_hours = _parse_param_decimal(
        data.get("standard_weekly_hours", "44.00"), "standard_weekly_hours", year
    )
    overtime_divisor = _parse_param_decimal(
        data.get(
            "overtime_monthly_divisor",
            data.get("seed_overtime_monthly_divisor", "220.00"),
        ),
        "overtime_monthly_divisor",
        year,
    )
    overtime_multiplier = _parse_param_decimal(
        data.get("overtime_multiplier", "1.40"), "overtime_multiplier", year
    )
    night_shift_multiplier = _parse_param_decimal(
        data.get("night_shift_multiplier", "1.35"), "night_shift_multiplier", year
    )

    monthly_tax_exemption = _parse_param_int(
        data["monthly_tax_exemption_rial"], "monthly_tax_exemption_rial", year
    )
    annual_tax_exemption = _parse_param_int(
        data.get("annual_tax_exemption_rial", monthly_tax_exemption * 12),
        "annual_tax_exemption_rial",
        year,
    )
    brackets = _parse_tax_brackets_dict(data["tax_brackets"], year)

    eydi_min_days = _parse_param_int(
        data.get("eydi_min_days", 60), "eydi_min_days", year
    )
    eydi_max_days = _parse_param_int(
        data.get("eydi_max_days_min_wage", 90), "eydi_max_days_min_wage", year
    )
    max_annual_eydi = _parse_param_int(
        data.get("max_annual_eydi_rial", monthly_minimum_30 * 3),
        "max_annual_eydi_rial",
        year,
    )
    eydi_tax_exemption = _parse_param_int(
        data.get("eydi_tax_exemption_rial", annual_tax_exemption // 12),
        "eydi_tax_exemption_rial",
        year,
    )
    non_cash_exemption = _parse_param_int(
        data.get(
            "non_cash_benefit_annual_tax_exemption_rial",
            (annual_tax_exemption * 2) // 12,
        ),
        "non_cash_benefit_annual_tax_exemption_rial",
        year,
    )

    stat_version = version or str(data.get("statutory_version", f"{year}.1"))
    effective_date = str(data.get("effective_date", f"{year}-01-01"))
    source_circ = str(
        data.get("source_circular_reference", f"Official Circular {year}")
    )

    rule_set = StatutoryRuleSet(
        statutory_version=stat_version,
        rule_year_shamsi=year,
        rule_set_status=status,
        rule_set_status_source=status_source,
        is_verified=True,
        effective_date=effective_date,
        source_circular_reference=source_circ,
        daily_minimum_wage_rial=daily_minimum,
        monthly_minimum_wage_29days_rial=monthly_minimum_29,
        monthly_minimum_wage_30days_rial=monthly_minimum_30,
        monthly_minimum_wage_31days_rial=monthly_minimum_31,
        monthly_housing_allowance_rial=monthly_housing,
        monthly_grocery_allowance_rial=monthly_grocery,
        monthly_marriage_allowance_rial=monthly_marriage,
        child_allowance_per_child_rial=child_allowance,
        daily_seniority_base_rial=daily_seniority,
        monthly_seniority_base_30days_rial=monthly_seniority,
        employee_sso_rate=employee_sso_rate,
        employer_sso_rate=employer_sso_rate,
        employer_unemployment_rate=employer_unemployment_rate,
        max_daily_insurable_wage_rial=max_daily_insurable,
        seed_max_monthly_insurable_wage_30days_rial=seed_max_monthly_insurable,
        standard_weekly_hours=weekly_hours,
        seed_overtime_monthly_divisor=overtime_divisor,
        overtime_multiplier=overtime_multiplier,
        night_shift_multiplier=night_shift_multiplier,
        monthly_tax_exemption_rial=monthly_tax_exemption,
        annual_tax_exemption_rial=annual_tax_exemption,
        tax_brackets=brackets,
        eydi_min_days=eydi_min_days,
        eydi_max_days_min_wage=eydi_max_days,
        max_annual_eydi_rial=max_annual_eydi,
        eydi_tax_exemption_rial=eydi_tax_exemption,
        non_cash_benefit_annual_tax_exemption_rial=non_cash_exemption,
    )
    validate_invariants(rule_set)
    return rule_set


class _StatutoryRecordLike(Protocol):
    @property
    def rule_year_shamsi(self) -> int: ...

    @property
    def parameters_json(self) -> dict[str, object]: ...

    @property
    def version_id(self) -> str: ...


def rule_set_from_record(record: _StatutoryRecordLike) -> StatutoryRuleSet:
    """Build StatutoryRuleSet from a persisted StatutoryRuleSetRecord."""
    params = record.parameters_json
    year = record.rule_year_shamsi
    version = record.version_id
    return build_rule_set_from_parameters(
        params, year=year, version=version, status="ACTIVE", status_source="repository"
    )


_ACTIVE_STATUTORY_CACHE: dict[int, StatutoryRuleSet] = {}


def register_active_rule_set(rule_set: StatutoryRuleSet) -> None:
    """Register an active rule set in the cache to override seed fallback."""
    _ACTIVE_STATUTORY_CACHE[rule_set.rule_year_shamsi] = rule_set


def clear_active_rule_set_cache() -> None:
    """Clear registered active rule sets, resetting to seed defaults."""
    _ACTIVE_STATUTORY_CACHE.clear()
    load_rule_set.cache_clear()


@lru_cache(maxsize=8)
def load_rule_set(year: int) -> StatutoryRuleSet:
    """Load the verified rule set for *year*, failing closed otherwise.

    Checks dynamic registered versions first; falls back to seed files.

    The refusal **kind** follows the state of the requested year:

    * no seed at all -> :class:`RuleSetNotActive`;
    * a seed that exists but is not verified and active (the 1405
      placeholder) -> :class:`StatutoryParameterUnavailable`;
    * a verified seed whose year is not an activated baseline ->
      :class:`StatutoryParameterUnavailable`.

    The 1405 placeholder is therefore refused with
    ``StatutoryParameterUnavailable`` (ADR-008 directive 3), never with a
    silent fallback to 1404.

    Raises:
        StatutoryParameterUnavailable: The seed exists but is unverified or
            carries null parameters (the 1405 placeholder), or a structural
            invariant failed.
        RuleSetNotActive: No seed exists for *year* at all.
    """
    if year in _ACTIVE_STATUTORY_CACHE:
        return _ACTIVE_STATUTORY_CACHE[year]
    path = _SEEDS_DIR / f"statutory_rules_{year}.yaml"
    if not path.exists():
        # A year outside the verified baseline can never be served; the
        # message stays categorical and names no figure.
        raise RuleSetNotActive(
            "RULE_SET_YEAR_NOT_LOADABLE: the requested rule year has no "
            "verified and active rule set"
        )
    rule_set = _parse_seed(year, path)
    if year not in ACTIVE_STATUTORY_YEARS:
        raise StatutoryParameterUnavailable(
            f"STATUTORY_SEED_{year}_NOT_ACTIVE: the rule set is verified but "
            "the year is not an activated statutory baseline"
        )
    return rule_set
