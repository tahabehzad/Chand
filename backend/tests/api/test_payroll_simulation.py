"""API tests for the gross-to-net simulation endpoint (P1-T19).

Authority:
    ADR-008 (the single minimal endpoint; the provenance envelope);
    ``docs/EXECUTION_PLAN.md`` §7.2 rule 4 (the five provenance fields) and
    §7.3; ``docs/specs/TESTING.md`` §5 (the contract layer).
Related:
    WBS P1-T19 - Simulation API (ADR-008 v1 scope).
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app

VALID_REQUEST = {
    "gross_monthly_rial": 341_850_120,
    "rule_year": 1404,
    "days_in_month": 30,
    "tax_posture": "conservative_inta",
    "allowances": {
        "housing": 9_000_000,
        "grocery": 22_000_000,
        "marriage": 5_000_000,
        "child": 10_390_968,
        "continuous_attraction": 40_000_000,
    },
    "overtime_hours": 0,
    "night_hours": 0,
    "continuous_attraction_taxable": False,
}

ENDPOINT = "/api/v1/simulations/gross-to-net"


@pytest.fixture
def client() -> Iterator[TestClient]:
    """Return a client over a local-configured application."""
    application = create_app(Settings(_env_file=None))
    with TestClient(application) as test_client:
        yield test_client


# ---------------------------------------------------------------------------
# The happy path
# ---------------------------------------------------------------------------


def test_the_endpoint_answers_200(client: TestClient) -> None:
    response = client.post(ENDPOINT, json=VALID_REQUEST)
    assert response.status_code == 200


def test_the_response_carries_the_five_provenance_fields(client: TestClient) -> None:
    body = client.post(ENDPOINT, json=VALID_REQUEST).json()
    assert body["statutory_version"] == "1404.1"
    assert body["rule_set_status"] == "VERIFIED"
    assert body["is_verified"] is True
    assert body["engine_version"]
    assert len(body["calculation_hash"]) == 64
    assert body["generated_at"]


def test_the_response_carries_both_postures(client: TestClient) -> None:
    body = client.post(ENDPOINT, json=VALID_REQUEST).json()
    assert set(body["tax_postures"]) == {"conservative_inta", "court_precedent"}
    assert body["primary_tax_posture"] == "conservative_inta"


def test_the_net_identity_holds_in_the_response(client: TestClient) -> None:
    body = client.post(ENDPOINT, json=VALID_REQUEST).json()
    total_gross = body["bases"]["total_gross_rial"]
    employee_sso = body["sso"]["employee_share_7pct_rial"]
    tax = body["employee_deductions"]["income_tax_rial"]
    assert total_gross - employee_sso - tax == body["net_rial"]


def test_the_provenance_map_covers_every_emitted_figure(client: TestClient) -> None:
    body = client.post(ENDPOINT, json=VALID_REQUEST).json()
    for figure, entry in body["provenance"].items():
        assert figure
        assert entry["rule_id"]
        assert entry["rule_year_shamsi"] == 1404
        assert entry["formula_ref"]


def test_every_monetary_value_is_a_json_integer(client: TestClient) -> None:
    """financial-data-integrity rule 26: money is an integer in Rial."""
    body = client.post(ENDPOINT, json=VALID_REQUEST).json()

    def walk(node: object, path: str) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                walk(value, f"{path}.{key}")
        elif isinstance(node, list):
            for index, value in enumerate(node):
                walk(value, f"{path}[{index}]")
        elif isinstance(node, float):
            raise AssertionError(f"a float reached the response at {path}: {node!r}")

    walk(body, "$")


def test_the_calculation_is_reproducible(client: TestClient) -> None:
    first = client.post(ENDPOINT, json=VALID_REQUEST).json()
    second = client.post(ENDPOINT, json=VALID_REQUEST).json()
    assert first["calculation_hash"] == second["calculation_hash"]
    assert first["net_rial"] == second["net_rial"]


def test_the_correlation_id_is_echoed(client: TestClient) -> None:
    response = client.post(ENDPOINT, json=VALID_REQUEST, headers={"X-Request-Id": "req-9"})
    assert response.headers["X-Request-Id"] == "req-9"


def test_the_termination_block_appears_when_probation_is_supplied(
    client: TestClient,
) -> None:
    payload = dict(VALID_REQUEST)
    payload["probation_months"] = 3
    payload["tenure_months"] = 24
    payload["accumulated_unused_leave_days"] = 12
    body = client.post(ENDPOINT, json=payload).json()
    assert body["termination_liability"]["employer_initiated_probation_liability_rial"] == (
        1_025_550_360
    )


# ---------------------------------------------------------------------------
# The fail-closed paths
# ---------------------------------------------------------------------------


def test_an_unverified_rule_year_is_refused_with_the_stable_error_shape(
    client: TestClient,
) -> None:
    payload = dict(VALID_REQUEST)
    payload["rule_year"] = 1405
    response = client.post(ENDPOINT, json=payload)
    assert response.status_code == 422
    body = response.json()
    assert set(body) == {"error"}
    assert body["error"]["code"] == "STATUTORY_PARAMETER_UNAVAILABLE"
    assert "140" not in body["error"]["detail"].replace("1405", "")


def test_a_year_without_a_rule_set_is_refused(client: TestClient) -> None:
    payload = dict(VALID_REQUEST)
    payload["rule_year"] = 1403
    response = client.post(ENDPOINT, json=payload)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "RULE_SET_NOT_ACTIVE"


def test_an_unknown_field_is_refused(client: TestClient) -> None:
    """A typo must never silently change the meaning of a calculation."""
    payload = dict(VALID_REQUEST)
    payload["gross_monthly_rialial"] = 1
    response = client.post(ENDPOINT, json=payload)
    assert response.status_code == 422


def test_a_negative_gross_is_refused(client: TestClient) -> None:
    payload = dict(VALID_REQUEST)
    payload["gross_monthly_rial"] = -1
    response = client.post(ENDPOINT, json=payload)
    assert response.status_code == 422


def test_a_zero_gross_is_refused(client: TestClient) -> None:
    payload = dict(VALID_REQUEST)
    payload["gross_monthly_rial"] = 0
    response = client.post(ENDPOINT, json=payload)
    assert response.status_code == 422


def test_an_impossible_month_length_is_refused(client: TestClient) -> None:
    payload = dict(VALID_REQUEST)
    payload["days_in_month"] = 28
    response = client.post(ENDPOINT, json=payload)
    assert response.status_code == 422


def test_an_unknown_posture_is_refused(client: TestClient) -> None:
    payload = dict(VALID_REQUEST)
    payload["tax_posture"] = "some_other_reading"
    response = client.post(ENDPOINT, json=payload)
    assert response.status_code == 422


def test_a_probation_period_beyond_the_statutory_maximum_is_refused(
    client: TestClient,
) -> None:
    payload = dict(VALID_REQUEST)
    payload["probation_months"] = 4
    response = client.post(ENDPOINT, json=payload)
    assert response.status_code == 422


def test_a_gross_that_does_not_cover_the_allowances_is_refused(
    client: TestClient,
) -> None:
    payload = dict(VALID_REQUEST)
    payload["gross_monthly_rial"] = 1_000_000
    response = client.post(ENDPOINT, json=payload)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "PAYROLL_INPUT_INVALID"


def test_no_error_response_carries_a_monetary_amount(client: TestClient) -> None:
    """The error shape carries a stable code, never an amount."""
    payload = dict(VALID_REQUEST)
    payload["rule_year"] = 1405
    body = client.post(ENDPOINT, json=payload).json()
    detail = body["error"]["detail"]
    assert not any(character.isdigit() for character in detail.replace("1405", ""))


def test_the_error_shape_is_the_same_for_every_refusal(client: TestClient) -> None:
    """A validation refusal must use the documented error envelope too."""
    payload = dict(VALID_REQUEST)
    payload["gross_monthly_rial"] = -1
    body = client.post(ENDPOINT, json=payload).json()
    assert set(body) == {"error"}
    assert set(body["error"]) == {"code", "detail"}


def test_the_openapi_contract_declares_the_endpoint() -> None:
    application = create_app(Settings(_env_file=None, app_debug=True))
    schema = application.openapi()
    assert ENDPOINT in schema["paths"]
    operation = schema["paths"][ENDPOINT]["post"]
    assert "requestBody" in operation
    assert "200" in operation["responses"]
