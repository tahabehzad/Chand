"""Unit tests for the Total Cost to Employer (CTC) breakdown endpoint.

Authority:
    docs/SALARY_ESTIMATION_SPEC.md; docs/PISH_HESABDARI_HOLY_BIBLE.md §2.3;
    AGENTS.md §2 Financial invariants (exact integer Rial, Decimal only, round once).
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.engines.money import round_half_up
from app.engines.rules import load_rule_set
from app.main import create_app

ENDPOINT = "/api/v1/simulations/salary-ctc-breakdown"


@pytest.fixture
def client() -> TestClient:
    """Return a TestClient over the FastAPI application."""
    application = create_app(Settings(_env_file=None, estimation_allow_sample_data=False))
    return TestClient(application)


class TestCtcBreakdownCalculations:
    """Verify exact integer Rial arithmetic for SSO, Tax, Severance, and Eydi."""

    def test_low_salary_below_tax_ceiling(self, client: TestClient) -> None:
        """A 100M Rial gross salary has 0 tax, exact 7%/20%/3% SSO, and verified accruals."""
        gross = 100_000_000
        response = client.post(
            ENDPOINT,
            json={"gross_salary_rial": gross, "year": 1404, "month_days": 30},
        )
        assert response.status_code == 200, response.text
        data = response.json()

        # Invariants: all monetary figures are integer Rial
        assert isinstance(data["gross_salary_rial"], int)
        assert isinstance(data["net_salary_rial"], int)
        assert isinstance(data["total_cost_to_employer_rial"], int)
        assert isinstance(data["annual_cost_to_employer_rial"], int)

        deductions = data["deductions"]
        assert isinstance(deductions["employee_sso_rial"], int)
        assert isinstance(deductions["income_tax_rial"], int)
        assert isinstance(deductions["total_deductions_rial"], int)

        employer_costs = data["employer_costs"]
        assert isinstance(employer_costs["employer_sso_rial"], int)
        assert isinstance(employer_costs["unemployment_rial"], int)
        assert isinstance(employer_costs["monthly_severance_rial"], int)
        assert isinstance(employer_costs["monthly_eydi_rial"], int)
        assert isinstance(employer_costs["total_employer_costs_rial"], int)

        # SSO: 7% employee, 20% employer, 3% unemployment (uncapped at 100M)
        assert deductions["employee_sso_rial"] == 7_000_000
        assert employer_costs["employer_sso_rial"] == 20_000_000
        assert employer_costs["unemployment_rial"] == 3_000_000

        # Tax: 100M is below the 120M monthly exemption floor in 1404
        assert deductions["income_tax_rial"] == 0
        assert deductions["total_deductions_rial"] == 7_000_000
        assert data["net_salary_rial"] == 93_000_000

        # Severance: 100,000,000 / 12 = 8,333,333.333... -> 8,333,333
        expected_severance = int(round_half_up(Decimal(gross) / Decimal(12)))
        assert employer_costs["monthly_severance_rial"] == expected_severance
        assert employer_costs["monthly_severance_rial"] == 8_333_333

        # Eydi: 2 * 100M = 200M (under the 3x minimum wage cap ~214.98M in 1404)
        # Monthly accrual: 200,000,000 / 12 = 16,666,666.666... -> 16,666,667
        expected_eydi = int(round_half_up(Decimal(200_000_000) / Decimal(12)))
        assert employer_costs["monthly_eydi_rial"] == expected_eydi
        assert employer_costs["monthly_eydi_rial"] == 16_666_667

        # Total reconciliation
        expected_total_employer = 20_000_000 + 3_000_000 + 8_333_333 + 16_666_667
        assert employer_costs["total_employer_costs_rial"] == expected_total_employer
        assert data["total_cost_to_employer_rial"] == gross + expected_total_employer
        assert data["annual_cost_to_employer_rial"] == data["total_cost_to_employer_rial"] * 12

    def test_high_salary_exceeding_sso_ceiling_and_eydi_cap(self, client: TestClient) -> None:
        """An 800M Rial salary tests SSO 7x cap and Eydi 3x minimum wage cap."""
        gross = 800_000_000
        rule_set = load_rule_set(1404)
        daily_min = rule_set.daily_minimum_wage_rial
        month_days = 30
        sso_ceiling = daily_min * 7 * month_days

        response = client.post(
            ENDPOINT,
            json={"gross_salary_rial": gross, "year": 1404, "month_days": month_days},
        )
        assert response.status_code == 200, response.text
        data = response.json()

        deductions = data["deductions"]
        employer_costs = data["employer_costs"]

        # Capped SSO values at 7x minimum daily wage
        expected_ee_sso = int(round_half_up(Decimal(sso_ceiling) * Decimal("0.07")))
        expected_er_sso = int(round_half_up(Decimal(sso_ceiling) * Decimal("0.20")))
        expected_unemp = int(round_half_up(Decimal(sso_ceiling) * Decimal("0.03")))

        assert deductions["employee_sso_rial"] == expected_ee_sso
        assert employer_costs["employer_sso_rial"] == expected_er_sso
        assert employer_costs["unemployment_rial"] == expected_unemp

        # High salary pays substantial progressive income tax
        assert deductions["income_tax_rial"] > 50_000_000

        # Eydi is capped at 3x minimum monthly wage (3 * monthly_minimum_wage_30days_rial)
        max_annual_eydi = rule_set.monthly_minimum_wage_30days_rial * 3
        expected_eydi = int(round_half_up(Decimal(max_annual_eydi) / Decimal(12)))
        assert employer_costs["monthly_eydi_rial"] == expected_eydi

        # Severance is 1/12 of gross salary (uncapped)
        expected_severance = int(round_half_up(Decimal(gross) / Decimal(12)))
        assert employer_costs["monthly_severance_rial"] == expected_severance

        # Check net identity and CTC identity
        assert data["net_salary_rial"] == gross - deductions["total_deductions_rial"]
        assert data["total_cost_to_employer_rial"] == gross + employer_costs["total_employer_costs_rial"]
        assert data["annual_cost_to_employer_rial"] == data["total_cost_to_employer_rial"] * 12

    def test_progressive_tax_brackets(self, client: TestClient) -> None:
        """Salaries in different brackets pay progressively higher tax rates."""
        # 200M: 0 tax (under 240M exemption floor)
        r200 = client.post(ENDPOINT, json={"gross_salary_rial": 200_000_000, "year": 1404}).json()
        assert r200["deductions"]["income_tax_rial"] == 0

        # 280M: enters 10% bracket (taxable amount above 240M after SSO allowance)
        r280 = client.post(ENDPOINT, json={"gross_salary_rial": 280_000_000, "year": 1404}).json()
        tax_280 = r280["deductions"]["income_tax_rial"]
        assert tax_280 > 0

        # 450M: enters higher bracket (20%)
        r450 = client.post(ENDPOINT, json={"gross_salary_rial": 450_000_000, "year": 1404}).json()
        tax_450 = r450["deductions"]["income_tax_rial"]
        assert tax_450 > tax_280 * 3  # Progressive ladder effect

    def test_forbids_extra_fields(self, client: TestClient) -> None:
        """Pydantic extra='forbid' rejects undocumented fields with 422."""
        response = client.post(
            ENDPOINT,
            json={"gross_salary_rial": 200_000_000, "unauthorized_extra": "hacked"},
        )
        assert response.status_code == 422
        assert "error" in response.json()

    def test_refuses_unverified_statutory_year(self, client: TestClient) -> None:
        """Requesting an unverified year (e.g. 1406) is rejected with 422 fail-closed."""
        response = client.post(
            ENDPOINT,
            json={"gross_salary_rial": 200_000_000, "year": 1406},
        )
        assert response.status_code == 422
        assert "error" in response.json()

    def test_accepts_verified_1404_statutory_year(self, client: TestClient) -> None:
        """Requesting active baseline year 1404 succeeds with 200 OK and accurate calculations."""
        response = client.post(
            ENDPOINT,
            json={"gross_salary_rial": 500_000_000, "year": 1404},
        )
        assert response.status_code == 200
        data = response.json()
        assert "1404" in data["rule_version"]
        assert data["net_salary_rial"] > 0

    def test_deterministic_calculation_hash(self, client: TestClient) -> None:
        """Calculation hash is deterministic and changes when inputs change."""
        payload1 = {"gross_salary_rial": 300_000_000, "year": 1404, "month_days": 30}
        payload2 = {"gross_salary_rial": 400_000_000, "year": 1404, "month_days": 30}

        r1 = client.post(ENDPOINT, json=payload1).json()
        r1_repeat = client.post(ENDPOINT, json=payload1).json()
        r2 = client.post(ENDPOINT, json=payload2).json()

        assert r1["calculation_hash"] == r1_repeat["calculation_hash"]
        assert len(r1["calculation_hash"]) == 64
        # Different gross produces different hash
        assert r1["calculation_hash"] != r2["calculation_hash"]
