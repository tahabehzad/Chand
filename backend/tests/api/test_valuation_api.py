"""API evidence for the advisory compensation proposal (ADR-009, P5-T02).

Authority:
    ADR-009; ``docs/EXECUTION_PLAN.md`` §7.2 rule 4 and §7.3;
    ``docs/specs/TESTING.md`` §5 (the contract layer).
Contract notes:
    Every figure in the statutory blocks must be reproducible by the existing
    simulation endpoint; the suite therefore replays one costing rather than
    trusting the valuation response.
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app

ENDPOINT = "/api/v1/valuations/compensation-proposal"
SIMULATION = "/api/v1/simulations/gross-to-net"

VALID_REQUEST: dict[str, object] = {
    "total_experience_months": 60,
    "relevant_experience_months": 42,
    "skill_level": 3,
    "education_level": "bachelor",
    "band_min_gross_rial": 100_000_000,
    "band_max_gross_rial": 200_000_000,
}


@pytest.fixture
def client() -> Iterator[TestClient]:
    """Return a client over a local-configured application."""
    application = create_app(Settings(_env_file=None))
    with TestClient(application) as test_client:
        yield test_client


def _post(client: TestClient, **overrides: object) -> dict[str, object]:
    body = dict(VALID_REQUEST)
    body.update(overrides)
    response = client.post(ENDPOINT, json=body)
    assert response.status_code == 200, response.text
    payload: dict[str, object] = response.json()
    return payload


def _floats(node: object) -> list[object]:
    found: list[object] = []
    if isinstance(node, float):
        found.append(node)
    elif isinstance(node, dict):
        for value in node.values():
            found.extend(_floats(value))
    elif isinstance(node, list):
        for value in node:
            found.extend(_floats(value))
    return found


# --- the happy path --------------------------------------------------------


def test_the_endpoint_answers_200(client: TestClient) -> None:
    assert client.post(ENDPOINT, json=VALID_REQUEST).status_code == 200


def test_the_response_is_marked_advisory_and_not_statutory(client: TestClient) -> None:
    body = _post(client)
    assert body["advisory"] is True
    assert body["statutory"] is False
    notes = body["advisory_notes"]
    assert isinstance(notes, list) and len(notes) >= 4
    assert any("manager decides" in note for note in notes)


def test_the_worked_profile_scores_and_positions_as_computed(client: TestClient) -> None:
    body = _post(client)
    score = body["score"]
    proposed = body["proposed"]
    assert isinstance(score, dict) and isinstance(proposed, dict)
    assert score["score_100"] == 55
    assert proposed["gross_point_rial"] == 155_000_000
    assert proposed["range_low_rial"] == 150_000_000
    assert proposed["range_high_rial"] == 160_000_000


def test_the_proposal_carries_a_model_version_and_weights(client: TestClient) -> None:
    body = _post(client)
    assert body["model_version"] == "valuation-v1"
    assert str(body["proposal_version"]).startswith("valuation-v1+")
    score = body["score"]
    assert isinstance(score, dict)
    assert set(score["weights"]) == {
        "total_experience",
        "relevant_experience",
        "skill_level",
        "education",
    }
    assert all(isinstance(value, str) for value in score["weights"].values())
    assert all(isinstance(value, str) for value in score["weighted_contributions"].values())


def test_every_monetary_field_is_an_integer_and_no_float_is_emitted(
    client: TestClient,
) -> None:
    body = _post(client)
    assert _floats(body) == []


def test_the_provenance_envelope_is_present_and_complete(client: TestClient) -> None:
    body = _post(client)
    assert body["statutory_version"] == "1404.1"
    assert body["rule_set_status"] == "VERIFIED"
    assert body["rule_year_shamsi"] == 1404
    assert len(str(body["rule_set_fingerprint"])) == 64
    assert len(str(body["calculation_hash"])) == 64
    datetime.fromisoformat(str(body["generated_at"]))


def test_the_proposal_hash_is_deterministic_across_calls(client: TestClient) -> None:
    first = _post(client)
    second = _post(client)
    assert first["calculation_hash"] == second["calculation_hash"]
    # The hash is independent of the clock (invariant 11): only the envelope
    # timestamp moves. Two calls can share one timestamp on a host whose clock
    # resolution is coarser than the request, so ordering is what is asserted.
    first_generated = str(first["generated_at"])
    second_generated = str(second["generated_at"])
    assert first_generated.endswith("+00:00")
    assert datetime.fromisoformat(second_generated) >= datetime.fromisoformat(first_generated)


# --- the statutory costing is the engine's, not the module's ---------------


@pytest.mark.parametrize("bound", ["lower_bound", "point", "upper_bound"])
def test_the_net_identity_holds_for_every_bound(bound: str, client: TestClient) -> None:
    body = _post(client)
    costing = body["statutory_costing"]
    assert isinstance(costing, dict)
    block = costing[bound]
    assert isinstance(block, dict)
    assert block["net_rial"] == (
        block["gross_monthly_rial"] - block["employee_sso_7pct_rial"] - block["income_tax_rial"]
    )
    assert block["total_monthly_employer_cost_rial"] > block["gross_monthly_rial"]


def test_the_point_costing_is_reproducible_by_the_simulation_endpoint(
    client: TestClient,
) -> None:
    body = _post(client)
    costing = body["statutory_costing"]
    assert isinstance(costing, dict)
    block = costing["point"]
    assert isinstance(block, dict)
    request = block["request"]
    assert isinstance(request, dict)

    replay = client.post(
        SIMULATION,
        json={
            "gross_monthly_rial": request["gross_monthly_rial"],
            "rule_year": request["rule_year"],
            "days_in_month": request["days_in_month"],
            "tax_posture": request["tax_posture"],
            "allowances": {
                "housing": 0,
                "grocery": 0,
                "marriage": 0,
                "child": 0,
                "continuous_attraction": 0,
            },
        },
    )
    assert replay.status_code == 200
    replayed = replay.json()
    assert replayed["net_rial"] == block["net_rial"]
    assert replayed["employee_deductions"]["income_tax_rial"] == block["income_tax_rial"]
    assert (
        replayed["employer_cost"]["total_monthly_employer_cost_rial"]
        == block["total_monthly_employer_cost_rial"]
    )
    assert replayed["calculation_hash"] == block["calculation_hash"]


def test_the_statutory_floor_is_published_and_never_applied(client: TestClient) -> None:
    body = _post(client)
    context = body["statutory_context"]
    assert isinstance(context, dict)
    assert context["monthly_minimum_wage_rial"] == 103_909_680
    assert context["range_low_below_statutory_minimum"] is False
    assert context["applied_to_net"] is False
    assert "DEC-013" in str(context["applied_to_net_reason"])


def test_a_below_floor_band_is_flagged_rather_than_adjusted(client: TestClient) -> None:
    body = _post(client, band_min_gross_rial=50_000_000, band_max_gross_rial=60_000_000)
    context = body["statutory_context"]
    assert isinstance(context, dict)
    assert context["range_low_below_statutory_minimum"] is True
    proposed = body["proposed"]
    assert isinstance(proposed, dict)
    # 50,000,000 + 0.55 * 10,000,000 = 55,500,000, widened by 500,000.
    assert proposed["gross_point_rial"] == 55_500_000
    assert proposed["range_low_rial"] == 55_000_000
    # The proposal is flagged, never quietly lifted to the statutory minimum.
    assert proposed["range_low_rial"] < context["monthly_minimum_wage_rial"]


# --- refusals --------------------------------------------------------------


def _error_code(response: object) -> str:
    body = response.json()  # type: ignore[attr-defined]
    assert set(body) == {"error"}
    assert set(body["error"]) == {"code", "detail"}
    code = body["error"]["code"]
    assert isinstance(code, str) and code
    return code


def test_a_missing_band_is_refused(client: TestClient) -> None:
    response = client.post(
        ENDPOINT,
        json={
            "total_experience_months": 60,
            "relevant_experience_months": 42,
            "skill_level": 3,
            "education_level": "bachelor",
        },
    )
    assert response.status_code == 422
    assert _error_code(response) == "VALUATION_BAND_REQUIRED"


def test_an_inverted_band_is_refused(client: TestClient) -> None:
    response = client.post(
        ENDPOINT,
        json={
            **VALID_REQUEST,
            "band_min_gross_rial": 200_000_000,
            "band_max_gross_rial": 100_000_000,
        },
    )
    assert response.status_code == 422
    assert _error_code(response) == "VALUATION_BAND_INVALID"


def test_relevant_experience_above_total_is_refused(client: TestClient) -> None:
    response = client.post(ENDPOINT, json={**VALID_REQUEST, "relevant_experience_months": 96})
    assert response.status_code == 422
    assert _error_code(response) == "VALUATION_EXPERIENCE_INVALID"


def test_a_skill_level_outside_the_scale_is_refused(client: TestClient) -> None:
    response = client.post(ENDPOINT, json={**VALID_REQUEST, "skill_level": 9})
    assert response.status_code == 422
    assert _error_code(response) == "VALUATION_PROFILE_INVALID"


def test_an_inactive_rule_year_fails_closed(client: TestClient) -> None:
    response = client.post(ENDPOINT, json={**VALID_REQUEST, "rule_year": 1405})
    assert response.status_code == 422
    assert _error_code(response) == "STATUTORY_PARAMETER_UNAVAILABLE"


def test_an_unknown_field_is_refused(client: TestClient) -> None:
    response = client.post(ENDPOINT, json={**VALID_REQUEST, "market_rate_rial": 1})
    assert response.status_code == 422
    assert _error_code(response)


def test_a_refusal_never_echoes_a_personal_attribute(client: TestClient) -> None:
    response = client.post(ENDPOINT, json={**VALID_REQUEST, "total_experience_months": 2000})
    assert response.status_code == 422
    body = response.json()
    detail = body["error"]["detail"]
    assert "2000" not in detail


# --- the published contract ------------------------------------------------


def test_the_openapi_document_publishes_the_endpoint_and_its_refusal() -> None:
    application = create_app(Settings(_env_file=None, app_debug=True))
    with TestClient(application) as client:
        document = client.get("/openapi.json").json()
    path = document["paths"][ENDPOINT]["post"]
    assert path["responses"]["200"]
    assert "422" in path["responses"]
    schema_ref = path["responses"]["422"]["content"]["application/json"]["schema"]
    assert schema_ref["$ref"].endswith("/ErrorResponse")
