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
    "ErrorResponse",
    "GrossToNetRequest",
    "PayrollResponse",
    "ProvenanceEntry",
    "SsoView",
    "TaxPostureValue",
)

TaxPostureValue = Literal["conservative_inta", "court_precedent"]


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
    """One taxed slab band."""

    slab: int
    taxed_amount_rial: int
    tax_rial: int


class PostureTaxView(BaseModel):
    """One Article 137 posture's tax result (both are always emitted)."""

    posture: TaxPostureValue
    art137_deduction_rial: int
    welfare_allowances_taxable: bool
    taxable_income_rial: int
    income_tax_rial: int
    tax_slabs_applied: list[str]
    slab_breakdown: list[SlabLine]
    net_rial: int


class PayrollResponse(BaseModel):
    """The complete hashed payslip snapshot with the provenance envelope.

    ``generated_at`` is injected by the API layer only — the calculation
    itself is a pure function of the inputs and the rule-set version.
    """

    statutory_version: str
    rule_set_status: str
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
    tax_postures: dict[str, PostureTaxView]
    net_rial: int
    alternate_posture_net_rial: int
    employee_deductions: dict[str, int]
    severance_sanavat: dict[str, int]
    eydi: dict[str, object]
    employer_cost: dict[str, object]
    rounding_residual_rial: int
    provenance: dict[str, ProvenanceEntry]
    termination_liability: dict[str, object] | None = None


class ErrorResponse(BaseModel):
    """The single error shape: a stable code, never a monetary amount."""

    error: dict[str, str]
