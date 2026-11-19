"""API tests for the CTC breakdown simulation endpoint.

Authority:
    docs/SALARY_ESTIMATION_SPEC.md; REMEDIATED_TECHNICAL_SPECIFICATION_V2.md Module 6;
    AGENTS.md §2 Financial invariants.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app

ENDPOINT = "/api/v1/simulations/salary-ctc-breakdown"


@pytest.fixture
def client() -> Iterator[TestClient]:
    """Return a TestClient over the FastAPI application."""
    application = create_app(Settings(_env_file=None))
    with TestClient(application) as test_client:
        yield test_client


def test_ctc_breakdown_happy_path(client: TestClient) -> None:
    """A valid 450M Rial gross salary returns exact integer CTC breakdowns and reconciles."""
    response = client.post(
        ENDPOINT,
        json={
            "gross_salary_rial": 450_000_000,
            "year": 1404,
            "month_days": 30,
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["gross_salary_rial"] == 450_000_000
    assert data["rule_version"] == "1404.1"
    assert len(data["calculation_hash"]) == 64

    deductions = data["deductions"]
    assert deductions["employee_sso_rial"] > 0
    assert deductions["income_tax_rial"] > 0
    assert deductions["total_deductions_rial"] == (
        deductions["employee_sso_rial"] + deductions["income_tax_rial"]
    )

    # Net reconciliation: Gross - Deductions = Net
    assert data["net_salary_rial"] == data["gross_salary_rial"] - deductions["total_deductions_rial"]

    employer_costs = data["employer_costs"]
    assert employer_costs["employer_sso_rial"] > 0
    assert employer_costs["unemployment_rial"] > 0
    assert employer_costs["monthly_severance_rial"] > 0
    assert employer_costs["monthly_eydi_rial"] > 0
    assert employer_costs["total_employer_costs_rial"] == (
        employer_costs["employer_sso_rial"]
        + employer_costs["unemployment_rial"]
        + employer_costs["monthly_severance_rial"]
        + employer_costs["monthly_eydi_rial"]
    )

    # CTC reconciliation: Gross + Employer Overhead = CTC
    assert data["total_cost_to_employer_rial"] == (
        data["gross_salary_rial"] + employer_costs["total_employer_costs_rial"]
    )
    assert data["annual_cost_to_employer_rial"] == data["total_cost_to_employer_rial"] * 12

    # Deterministic hash: calling again with identical parameters yields identical calculation_hash
    response2 = client.post(
        ENDPOINT,
        json={
            "gross_salary_rial": 450_000_000,
            "year": 1404,
            "month_days": 30,
        },
    )
    assert response2.status_code == 200
    assert response2.json()["calculation_hash"] == data["calculation_hash"]


def test_ctc_breakdown_forbids_extra_fields(client: TestClient) -> None:
    """An unknown field is rejected with 422 under extra='forbid'."""
    response = client.post(
        ENDPOINT,
        json={
            "gross_salary_rial": 300_000_000,
            "unknown_bonus": 10_000_000,
        },
    )
    assert response.status_code == 422
    assert "error" in response.json()


def test_ctc_breakdown_refuses_unverified_year(client: TestClient) -> None:
    """Requesting an unverified statutory year (e.g. 1406) fails closed."""
    response = client.post(
        ENDPOINT,
        json={
            "gross_salary_rial": 300_000_000,
            "year": 1406,
            "month_days": 30,
        },
    )
    assert response.status_code == 422
    data = response.json()
    assert "error" in data


def test_ctc_breakdown_accepts_verified_1404_year(client: TestClient) -> None:
    """Requesting active baseline year 1404 succeeds."""
    response = client.post(
        ENDPOINT,
        json={
            "gross_salary_rial": 400_000_000,
            "year": 1404,
            "month_days": 30,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "1404" in data["rule_version"]
    assert data["net_salary_rial"] > 0


def test_ctc_breakdown_zero_gross(client: TestClient) -> None:
    """A zero gross salary evaluates to zero deductions and zero CTC."""
    response = client.post(
        ENDPOINT,
        json={
            "gross_salary_rial": 0,
            "year": 1404,
            "month_days": 30,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["gross_salary_rial"] == 0
    assert data["net_salary_rial"] == 0
    assert data["total_cost_to_employer_rial"] == 0
    assert data["deductions"]["total_deductions_rial"] == 0
    assert data["employer_costs"]["total_employer_costs_rial"] == 0
