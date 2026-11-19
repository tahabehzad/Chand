"""Pydantic v2 schemas for Total Cost to Employer (CTC) breakdown.

Authority
---------
``docs/SALARY_ESTIMATION_SPEC.md``; ``docs/PISH_HESABDARI_HOLY_BIBLE.md`` §2.3;
``REMEDIATED_TECHNICAL_SPECIFICATION_V2.md`` Module 6; ``AGENTS.md`` §2 Financial invariants.

Contract notes
--------------
* Every monetary field is a whole-Rial JSON integer.
* Request strictly forbids unknown fields (extra="forbid").
* Calculations must be exact, reproducible, and verifiable.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

__all__ = (
    "CtcBreakdownRequest",
    "CtcBreakdownResponse",
    "CtcDeductions",
    "CtcEmployerCosts",
)


class CtcDeductions(BaseModel):
    """Breakdown of employee-side deductions from monthly gross salary."""

    model_config = ConfigDict(extra="forbid")

    employee_sso_rial: int = Field(
        ...,
        ge=0,
        description="Employee SSO contribution (7% on insurable wage) in Rial",
    )
    income_tax_rial: int = Field(
        ...,
        ge=0,
        description="Employee progressive income tax (Article 137 conservative) in Rial",
    )
    total_deductions_rial: int = Field(
        ...,
        ge=0,
        description="Total employee deductions (SSO + Tax) in Rial",
    )


class CtcEmployerCosts(BaseModel):
    """Breakdown of employer overhead costs beyond gross salary."""

    model_config = ConfigDict(extra="forbid")

    employer_sso_rial: int = Field(
        ...,
        ge=0,
        description="Employer SSO contribution (20% on insurable wage) in Rial",
    )
    unemployment_rial: int = Field(
        ...,
        ge=0,
        description="Employer unemployment insurance contribution (3% on insurable wage) in Rial",
    )
    monthly_severance_rial: int = Field(
        ...,
        ge=0,
        description="Monthly severance (Sanavat) accrual (Gross / 12) in Rial",
    )
    monthly_eydi_rial: int = Field(
        ...,
        ge=0,
        description="Monthly bonus (Eydi) accrual (Annual Eydi / 12) in Rial",
    )
    total_employer_costs_rial: int = Field(
        ...,
        ge=0,
        description="Total employer overhead expenses in Rial",
    )


class CtcBreakdownRequest(BaseModel):
    """Request payload for monthly CTC and net salary calculation."""

    model_config = ConfigDict(extra="forbid")

    gross_salary_rial: int = Field(
        ...,
        ge=0,
        description="Monthly gross salary in whole Rial",
    )
    year: int = Field(
        default=1405,
        description="Statutory rule year (Shamsi calendar, default: 1405)",
    )
    month_days: int = Field(
        default=30,
        ge=29,
        le=31,
        description="Days in the payroll month (29, 30, or 31; default: 30)",
    )


class CtcBreakdownResponse(BaseModel):
    """Response payload containing comprehensive CTC and net salary breakdown."""

    model_config = ConfigDict(extra="forbid")

    gross_salary_rial: int = Field(
        ...,
        ge=0,
        description="Agreed gross salary in Rial",
    )
    net_salary_rial: int = Field(
        ...,
        ge=0,
        description="Net take-home pay to employee in Rial (Gross - Employee SSO - Tax)",
    )
    deductions: CtcDeductions = Field(
        ...,
        description="Itemized employee deductions",
    )
    employer_costs: CtcEmployerCosts = Field(
        ...,
        description="Itemized employer overhead costs",
    )
    total_cost_to_employer_rial: int = Field(
        ...,
        ge=0,
        description="Total monthly Cost to Employer (CTC) in Rial",
    )
    annual_cost_to_employer_rial: int = Field(
        ...,
        ge=0,
        description="Total 12-month annual Cost to Employer in Rial (Monthly CTC * 12)",
    )
    rule_version: str = Field(
        ...,
        description="Statutory rule set version used for calculation",
    )
    engine_version: str = Field(
        ...,
        description="Version string of the statutory calculation engine",
    )
    calculation_hash: str = Field(
        ...,
        description="SHA-256 fingerprint of the canonical calculation payload",
    )
    generated_at: str = Field(
        ...,
        description="ISO-8601 UTC timestamp of calculation issuance",
    )
