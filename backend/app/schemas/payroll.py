"""Pydantic v2 contracts for the gross-to-net payroll simulation endpoint.

Authority
---------
ADR-008 (single minimal endpoint; provenance envelope);
``docs/EXECUTION_PLAN.md`` §7.2 rule 4 (five provenance fields) and §7.3;
financial-data-integrity rules 25-27 (integer Rial JSON, rates as strings).

Contract notes
--------------
* Every monetary field is a JSON **integer** in Rial; every rate or factor
  is a **string** so a JavaScript client cannot silently coerce it into a
  binary float.
* ``rule_year`` is pinned explicitly (never "latest"); only the verified
  1404 baseline loads — any other year fails closed at the loader.
* The request forbids unknown fields so a typo cannot silently change the
  meaning of a calculation.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

__all__ = (
    "AllowancesInput",
    "EmployerCostView",
    "ErrorResponse",
    "EydiView",
    "GrossToNetRequest",
    "InsurableBaseView",
    "PayrollResponse",
    "ProvenanceEntry",
    "SeveranceView",
    "SsoView",
    "StatutoryReferenceView",
    "TaxPostureValue",
)

TaxPostureValue = Literal["conservative_inta", "court_precedent"]
TerminationScenarioValue = Literal[
    "probation_employer_initiated",
    "probation_employee_initiated",
    "ordinary_termination",
]


class AllowancesInput(BaseModel):
    """Monthly fixed allowances, in whole Rial (defaults: none paid)."""

    model_config = ConfigDict(extra="forbid")

    housing: int = Field(default=0, ge=0)
    grocery: int = Field(default=0, ge=0)
    marriage: int = Field(default=0, ge=0)
    child: int = Field(default=0, ge=0)
    continuous_attraction: int = Field(default=0, ge=0)


class GrossToNetRequest(BaseModel):
    """One month's gross-to-net calculation request."""

    model_config = ConfigDict(extra="forbid")

    gross_monthly_rial: int = Field(gt=0, description="Contractual monthly gross, Rial")
    rule_year: int = Field(default=1404, description="Statutory rule year (only 1404 loads)")
    days_in_month: Literal[29, 30, 31] = 30
    tax_posture: TaxPostureValue = "conservative_inta"
    allowances: AllowancesInput = AllowancesInput()
    overtime_hours: int = Field(default=0, ge=0)
    night_hours: int = Field(default=0, ge=0)
    continuous_attraction_taxable: bool = False
    probation_months: int | None = Field(default=None, ge=1, le=3)
    tenure_months: int | None = Field(default=None, ge=0)
    accumulated_unused_leave_days: int | None = Field(default=None, ge=0)
    probation_days_worked: int | None = Field(default=None, ge=0)
    termination_scenario: TerminationScenarioValue | None = Field(
        default=None,
        description=(
            "Which Art. 11 line applies when probation data is supplied. "
            "Defaults to employer-initiated for backward compatibility."
        ),
    )
    recognised_service_years: int | None = Field(
        default=None,
        ge=0,
        description="Whole recognised service years used for the reference seniority block.",
    )


class ProvenanceEntry(BaseModel):
    """Field-level provenance: the rule behind one emitted figure."""

    rule_id: str
    rule_year_shamsi: int
    formula_ref: str


class SsoView(BaseModel):
    """The SSO contribution block."""

    insurable_wage_rial: int
    insurable_ceiling_rial: int
    sso_insurable_ceiling_applied: bool
    employee_share_7pct_rial: int
    employer_share_20pct_rial: int
    unemployment_fund_3pct_rial: int


class SlabLine(BaseModel):
    """One taxed slab band.

    ``rate`` is a **string** so a JavaScript client cannot coerce it into a
    binary float (financial-data-integrity rule 26).
    """

    slab: int
    rate: str
    taxed_amount_rial: int
    tax_rial: int


class PostureTaxView(BaseModel):
    """One Article 137 posture's tax result (both are always emitted)."""

    posture: TaxPostureValue
    art137_deduction_rial: int
    welfare_allowances_taxable: bool
    taxable_income_rial: int
    taxable_base_clamped: bool
    income_tax_rial: int
    income_tax_exact_total_rial: int
    tax_rounding_residual_rial: int
    tax_slabs_applied: list[str]
    slab_breakdown: list[SlabLine]
    net_rial: int


class InsurableBaseView(BaseModel):
    """The audited SSO base note (B-3 conflict is published, not resolved)."""

    basis: str
    conflict_ref: str


class SeveranceView(BaseModel):
    """The monthly Sanavat accrual block."""

    base_rial: int
    accrual_basis: str
    includes_overtime_premiums: bool
    conflict_ref: str
    monthly_accrual_rial: int


class EydiView(BaseModel):
    """The annual Eydi block and its tax reconciliation."""

    annual_gross_rial: int
    at_cap: bool
    cap_basis: str
    excess_tax_method: str
    includes_overtime_premiums: bool
    monthly_accrual_rial: int
    annual_tax_rial: int
    annual_tax_exact_total_rial: int
    tax_rounding_residual_rial: int
    annual_net_rial: int
    conflict_refs: str


class EmployerCostView(BaseModel):
    """The monthly and annual total cost to employer (CTC)."""

    total_monthly_employer_cost_rial: int
    annual_ctc_12month_rial: int
    includes_26day_leave_reserve: bool


class StatutoryReferenceView(BaseModel):
    """Reference-only statutory floors and seniority (not applied to net)."""

    monthly_minimum_wage_rial: int
    daily_minimum_wage_rial: int
    housing_allowance_floor_rial: int
    grocery_allowance_floor_rial: int
    marriage_allowance_floor_rial: int
    child_allowance_per_child_rial: int
    allowance_floor_excluding_child_rial: int
    declared_child_allowance_rial: int
    declared_child_allowance_below_floor: bool
    total_gross_below_minimum_wage: bool
    daily_seniority_base_rial: int
    monthly_seniority_base_rial: int
    recognised_service_years: int
    monthly_seniority_increment_rial: int
    applied_to_net: bool
    reference_only_reason: str


class PayrollResponse(BaseModel):
    """The complete hashed payslip snapshot with the provenance envelope.

    ``generated_at`` is injected by the API layer only — the calculation
    itself is a pure function of the inputs and the rule-set version.
    """

    statutory_version: str
    rule_set_status: str
    rule_set_status_source: str
    rule_set_fingerprint: str
    is_verified: bool
    engine_version: str
    calculation_hash: str
    generated_at: str
    rule_year_shamsi: int
    days_in_month: int
    primary_tax_posture: TaxPostureValue
    inputs: dict[str, object]
    bases: dict[str, object]
    sso: SsoView
    insurable_base: InsurableBaseView
    tax_postures: dict[str, PostureTaxView]
    net_rial: int
    alternate_posture_net_rial: int
    employee_deductions: dict[str, int]
    severance_sanavat: SeveranceView
    eydi: EydiView
    employer_cost: EmployerCostView
    statutory_reference: StatutoryReferenceView
    statutory_parameter_usage: dict[str, str]
    rounding_residual_rial: int
    rounding_residual_scope: str
    provenance: dict[str, ProvenanceEntry]
    termination_liability: dict[str, object] | None = None


class ErrorResponse(BaseModel):
    """The single error shape: a stable code, never a monetary amount."""

    error: dict[str, str]
