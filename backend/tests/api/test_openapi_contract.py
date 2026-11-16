"""OpenAPI contract conformance for the simulation endpoint (SPEC-QA-001 L5).

Authority:
    ``docs/specs/TESTING.md`` §5 (the contract layer) and the release rule
    that the published contract and the served response must agree;
    ``docs/EXECUTION_PLAN.md`` §7.3 (the API design rules).
Related:
    WBS P1-T19 - Simulation API. The generated cases are the machine
    counterpart of ``tests/api/test_payroll_simulation.py``: the hand-written
    suite asserts the *intended* behaviour, this one asserts that whatever a
    client can send, the response still matches the published contract.

Contract notes
--------------
* The application is created with the documentation surface enabled, because
  the contract is only published in that mode.
* Every refusal the endpoint can produce must be described by the contract.
  A refusal that the contract does not describe is a contract defect, not a
  passing test.
"""

from __future__ import annotations

import json

import pytest
import schemathesis
from pydantic import ValidationError
from schemathesis import DataGenerationMethod

from app.core.config import Settings
from app.main import create_app
from app.schemas.payroll import GrossToNetRequest

ENDPOINT = "/api/v1/simulations/gross-to-net"

schema = schemathesis.from_asgi(
    "/openapi.json",
    create_app(Settings(_env_file=None, app_debug=True)),
    # ``endpoint`` is a regex over the path, not "METHOD path"; the method is
    # selected separately.  The previous "POST <path>" value matched nothing.
    endpoint=f"^{ENDPOINT}$",
    method="POST",
    # schemathesis 3.39 expects the short version selector "30"; the full
    # "3.0.3" string is ignored and detection then rejects FastAPI's 3.1.0
    # document before generation starts.
    force_schema_version="30",
)

negative_schema = schemathesis.from_asgi(
    "/openapi.json",
    create_app(Settings(_env_file=None, app_debug=True)),
    endpoint=f"^{ENDPOINT}$",
    method="POST",
    force_schema_version="30",
    data_generation_methods=(
        DataGenerationMethod.positive,
        DataGenerationMethod.negative,
    ),
)


@schema.parametrize()
def test_the_response_matches_the_published_contract(case: schemathesis.Case) -> None:
    """Every generated request must produce a conforming response."""
    response = case.call()
    case.validate_response(response)


@negative_schema.parametrize()
def test_the_endpoint_refuses_an_invalid_request(case: schemathesis.Case) -> None:
    """A malformed request must be refused, never silently accepted.

    Schemathesis' negative generation may still emit a body that satisfies a
    deliberately minimal schema (for example ``{"gross_monthly_rial": 1}``,
    where the only required field is a positive integer).  Such a body is a
    **valid** request, so refusing it would be the defect; the assertion
    applies to bodies that genuinely violate the published request contract.
    """
    try:
        GrossToNetRequest.model_validate(case.body)
    except ValidationError:
        pass
    else:
        pytest.skip("schemathesis generated a contract-valid request")

    response = case.call()
    assert response.status_code in {400, 422}, (
        f"a malformed request was answered with {response.status_code}"
    )
    body = json.loads(response.content)
    assert set(body) == {"error"}
    assert set(body["error"]) == {"code", "detail"}
    assert body["error"]["code"]
    assert body["error"]["detail"]
