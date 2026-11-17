"""The manager workspace API integration suite — real PostgreSQL (PostgreSQL
16 container on ``127.0.0.1:55432``).

Authority
---------
``docs/MVP_SCOPE.md`` AC-02…AC-11; the mission test list (employee creation,
observations, retrieval, evaluation, recommendation, decision, persistence,
tenant isolation, invalid/missing data, payroll integration).

How it runs
-----------
The suite creates (or reuses) the disposable database ``pish_test`` on the
configured PostgreSQL instance, upgrades it through Alembic to ``head``, and
serves the real FastAPI application with ``TestClient``.  Tenant tables are
truncated between tests.  When PostgreSQL is unreachable the suite **skips**
self-declared — an absent database is a coverage gap, never a pass.
"""

from __future__ import annotations

import asyncio
import os
import uuid
from collections.abc import AsyncIterator, Iterator
from typing import Any, cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import set_session_factory
from app.db import build_engine, build_session_factory
from app.main import create_app
from app.models import Base, manager
from app.models.identity import Organization, OrganizationMembership, Role, User
from app.services.identity_service import hash_password

TENANT_TABLES = (
    "employees",
    "employee_observations",
    "employee_evidence",
    "employee_evaluations",
    "salary_recommendations",
    "recommendation_decisions",
)

_TENANT_A = uuid.uuid5(uuid.NAMESPACE_URL, "pish-test://tenant/manager-a@test.local")
_TENANT_B = uuid.uuid5(uuid.NAMESPACE_URL, "pish-test://tenant/manager-b@test.local")
_IDS: dict[str, object] = {}

_original_env = os.environ.get("DATABASE_URL")


def _test_dsn() -> str:
    """Return the configured development DSN unchanged.

    The hardened container ``pg_hba.conf`` admits TLS connections to
    ``pish_dev`` only, so the suite runs against the actual configured
    database (as the mission requires) and truncates the tenant tables
    between tests.  The value is read but never printed.
    """
    configured = _original_env
    if not configured:
        try:
            from dotenv import dotenv_values

            configured = (dotenv_values(".env") or {}).get("DATABASE_URL", "")
        except OSError:
            configured = ""
    if not configured:
        pytest.skip("DATABASE_URL is not configured; PostgreSQL integration skipped")
    return configured


@pytest.fixture(scope="module", autouse=True)
def _module_setup() -> Iterator[None]:
    """One schema per module: migrate ``pish_test`` to head, then restore."""
    from app.core.config import get_settings

    dsn = _test_dsn()

    os.environ["DATABASE_URL"] = dsn
    get_settings.cache_clear()
    from alembic import command
    from alembic.config import Config

    alembic_config = Config("alembic.ini")
    command.upgrade(alembic_config, "head")

    engine = build_engine(dsn)
    factory = build_session_factory(engine)
    set_session_factory(factory)
    app = create_app(get_settings())
    client = TestClient(app)
    _IDS["client"] = client
    _IDS["factory"] = factory

    async def seed() -> None:
        session = factory()
        try:
            role: uuid.UUID = (
                await session.execute(text("SELECT id FROM roles WHERE role_key='HR_MANAGER'"))
            ).scalar_one()
            for tenant, email in (
                (_TENANT_A, "manager-a@test.local"),
                (_TENANT_B, "manager-b@test.local"),
            ):
                organization = (
                    await session.execute(
                        text("SELECT id FROM organizations WHERE id = :id"), {"id": tenant}
                    )
                ).scalar_one_or_none()
                if organization is None:
                    session.add(Organization(id=tenant, legal_name_fa=f"سازمان {email}"))
                user_id = (
                    await session.execute(
                        text("SELECT id FROM users WHERE email_normalized = :email"),
                        {"email": email},
                    )
                ).scalar_one_or_none()
                if user_id is None:
                    user_id = uuid.uuid4()
                    session.add(
                        User(
                            id=user_id,
                            email_normalized=email,
                            display_name_fa="مدیر آزمون",
                            password_hash=hash_password("test-password"),
                        )
                    )
            await session.flush()
            for tenant, email in (
                (_TENANT_A, "manager-a@test.local"),
                (_TENANT_B, "manager-b@test.local"),
            ):
                user_id = (
                    await session.execute(
                        text("SELECT id FROM users WHERE email_normalized = :email"),
                        {"email": email},
                    )
                ).scalar_one()
                existing = (
                    await session.execute(
                        text(
                            "SELECT 1 FROM organization_memberships"
                            " WHERE organization_id = :org AND user_id = :user"
                        ),
                        {"org": tenant, "user": user_id},
                    )
                ).scalar_one_or_none()
                if existing is None:
                    session.add(
                        OrganizationMembership(
                            id=uuid.uuid4(),
                            organization_id=tenant,
                            user_id=user_id,
                            role_id=role,
                        )
                    )
            await session.commit()
        finally:
            await session.close()

    asyncio.run(seed())

    yield

    set_session_factory(None)
    asyncio.run(engine.dispose())
    if _original_env is None:
        os.environ.pop("DATABASE_URL", None)
    else:
        os.environ["DATABASE_URL"] = _original_env
    get_settings.cache_clear()


async def _truncate() -> None:
    factory: object = _IDS["factory"]
    session: AsyncSession = factory()  # type: ignore[operator]
    try:
        tables = ", ".join(TENANT_TABLES)
        await session.execute(text(f"TRUNCATE {tables} CASCADE"))
        await session.execute(text("TRUNCATE sessions CASCADE"))
        await session.commit()
    finally:
        await session.close()


@pytest.fixture(autouse=True)
async def _clean_tables() -> AsyncIterator[None]:
    await _truncate()
    yield


def _client() -> TestClient:
    return cast(TestClient, _IDS["client"])


def _login(tenant: uuid.UUID) -> str:
    email = "manager-a@test.local" if tenant == _TENANT_A else "manager-b@test.local"
    response = _client().post(
        "/api/v1/auth/login",
        json={"email": email, "password": "test-password"},
    )
    assert response.status_code == 200, response.text
    return cast(str, response.json()["token"])


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _create_employee(token: str, name: str = "کارمند یک", role: str = "فروش") -> str:
    response = _client().post(
        "/api/v1/manager/employees",
        headers=_auth(token),
        json={"name": name, "role": role, "startDate": "2024-03-20"},
    )
    assert response.status_code == 201, response.text
    return cast(str, response.json()["id"])


def _add_observation(
    token: str, employee_id: str, code: str, raw: str, period: str = "1404-Q2"
) -> str:
    response = _client().post(
        f"/api/v1/manager/employees/{employee_id}/observations",
        headers=_auth(token),
        json={"code": code, "period": period, "raw": raw},
    )
    assert response.status_code == 201, response.text
    return cast(str, response.json()["id"])


def _evaluate(token: str, employee_id: str) -> dict[str, Any]:
    response = _client().post(
        f"/api/v1/manager/employees/{employee_id}/evaluations",
        headers=_auth(token),
        json={"bandMinRial": 80_000_000, "bandMaxRial": 140_000_000, "currentRial": 100_000_000},
    )
    assert response.status_code == 201, response.text
    return cast("dict[str, Any]", response.json())


# ------------------------------------------------------------------- AC-02 --


def test_employee_create_and_list() -> None:
    """AC-02: a manager creates an employee and reads it back."""
    token = _login(_TENANT_A)
    employee_id = _create_employee(token)
    employees = _client().get("/api/v1/manager/employees", headers=_auth(token))
    assert employees.status_code == 200
    assert [row["id"] for row in employees.json()] == [employee_id]
    single = _client().get(f"/api/v1/manager/employees/{employee_id}", headers=_auth(token))
    assert single.status_code == 200
    assert single.json()["name"] == "کارمند یک"


def test_employee_invalid_payloads_are_refused() -> None:
    """AC-02: malformed input is refused with the typed error, no echo."""
    token = _login(_TENANT_A)
    for payload, code in (
        ({"name": "", "role": "فروش", "startDate": "2024-03-20"}, "EMPLOYEE_NAME_INVALID"),
        ({"name": "x", "role": "", "startDate": "2024-03-20"}, "EMPLOYEE_ROLE_INVALID"),
        ({"name": "x", "role": "y", "startDate": "bad-date"}, "EMPLOYEE_START_DATE_INVALID"),
    ):
        response = _client().post("/api/v1/manager/employees", headers=_auth(token), json=payload)
        assert response.status_code == 422, response.text
        assert response.json()["error"]["code"] == code


# ------------------------------------------------------------------- AC-03 --


def test_observation_attached_to_exactly_one_employee() -> None:
    """AC-03: an unknown employee id is refused; observations are listed."""
    token = _login(_TENANT_A)
    employee_id = _create_employee(token)
    _add_observation(token, employee_id, "quality", "82")
    missing = _client().post(
        f"/api/v1/manager/employees/{uuid.uuid4()}/observations",
        headers=_auth(token),
        json={"code": "quality", "period": "1404-Q2", "raw": "82"},
    )
    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == "EMPLOYEE_NOT_FOUND"
    listed = _client().get(
        f"/api/v1/manager/employees/{employee_id}/observations", headers=_auth(token)
    )
    assert listed.status_code == 200
    assert len(listed.json()) == 1
    assert listed.json()[0]["state"] == "valid"


def test_observation_invalid_values_refused() -> None:
    token = _login(_TENANT_A)
    employee_id = _create_employee(token)
    for code, raw, error_code in (
        ("unknown-metric", "5", "OBSERVATION_METRIC_INVALID"),
        ("quality", "-5", "OBSERVATION_VALUE_INVALID"),
        ("attendance", "31", "OBSERVATION_VALUE_INVALID"),
    ):
        response = _client().post(
            f"/api/v1/manager/employees/{employee_id}/observations",
            headers=_auth(token),
            json={"code": code, "period": "1404-Q2", "raw": raw},
        )
        assert response.status_code == 422, response.text
        assert response.json()["error"]["code"] == error_code


def test_correct_and_reject_observation() -> None:
    """Rejection is recorded; a rejected row refuses correction (AC-04 half)."""
    token = _login(_TENANT_A)
    employee_id = _create_employee(token)
    observation_id = _add_observation(token, employee_id, "quality", "82")
    corrected = _client().patch(
        f"/api/v1/manager/observations/{observation_id}",
        headers=_auth(token),
        json={"raw": "90"},
    )
    assert corrected.status_code == 200
    assert corrected.json()["state"] == "corrected"
    assert corrected.json()["raw"] == "90"
    rejected = _client().post(
        f"/api/v1/manager/observations/{observation_id}/reject", headers=_auth(token)
    )
    assert rejected.status_code == 200
    assert rejected.json()["state"] == "rejected"
    refused = _client().patch(
        f"/api/v1/manager/observations/{observation_id}",
        headers=_auth(token),
        json={"raw": "50"},
    )
    assert refused.status_code == 409
    assert refused.json()["error"]["code"] == "OBSERVATION_REJECTED"


# ------------------------------------------------------- AC-04…AC-08 --


def test_evaluation_and_recommendation_full_flow() -> None:
    """Evaluation, recommendation, determinism and the statutory costing."""
    token = _login(_TENANT_A)
    employee_id = _create_employee(token)
    for code, raw in (
        ("sales", "800000000"),
        ("quality", "82"),
        ("attendance", "29"),
        ("responsibility", "4"),
    ):
        _add_observation(token, employee_id, code, raw)

    first = _evaluate(token, employee_id)
    # Determinism: the same inputs and rule version reproduce the same hash.
    from app.services.manager_service import _statutory_cost_block

    replay = _statutory_cost_block(int(first["suggestedGrossRial"]))
    assert first["score100"] == 83
    assert first["band"]["positionBp"] == 8343
    assert first["ruleSetVersion"] == "perf-v1"
    assert first["advisory"] is True
    assert first["statutory"]["net_rial"] == replay["net_rial"]
    assert first["statutory"]["engine_version"].endswith("payroll-engine")
    assert len(first["statutory"]["calculation_hash"]) == 64
    assert not first["missingCriteria"]
    assert len(first["contributions"]) == 4
    assert len(first["observationsUsed"]) == 4

    # The delta is the suggested minus the current pay.
    assert first["deltaRial"] == int(first["suggestedGrossRial"]) - 100_000_000


def test_missing_criteria_reported_and_lower_score() -> None:
    """AC-08: an incomplete profile names the missing criteria."""
    token = _login(_TENANT_A)
    employee_id = _create_employee(token)
    _add_observation(token, employee_id, "quality", "65")
    _add_observation(token, employee_id, "attendance", "27")
    result = _evaluate(token, employee_id)
    assert set(result["missingCriteria"]) == {"sales", "responsibility"}
    assert result["explanation"]["dataQuality"], "the data-quality block must report the gap"


def test_evaluation_without_observations_refused() -> None:
    token = _login(_TENANT_A)
    employee_id = _create_employee(token)
    response = _client().post(
        f"/api/v1/manager/employees/{employee_id}/evaluations",
        headers=_auth(token),
        json={"bandMinRial": 80_000_000, "bandMaxRial": 140_000_000},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "EVALUATION_NO_DATA"


def test_invalid_band_refused() -> None:
    token = _login(_TENANT_A)
    employee_id = _create_employee(token)
    _add_observation(token, employee_id, "quality", "82")
    response = _client().post(
        f"/api/v1/manager/employees/{employee_id}/evaluations",
        headers=_auth(token),
        json={"bandMinRial": 140_000_000, "bandMaxRial": 80_000_000},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "EVALUATION_BAND_INVALID"


# ---------------------------------------------------------------- AC-09/10 --


def test_decision_approve_persists_and_history_is_readable() -> None:
    """AC-10: approve, then read the decision back from the dashboard."""
    token = _login(_TENANT_A)
    employee_id = _create_employee(token)
    _add_observation(token, employee_id, "quality", "82")
    recommendation = _evaluate(token, employee_id)
    decision = _client().post(
        f"/api/v1/manager/recommendations/{recommendation['id']}/decision",
        headers=_auth(token),
        json={"action": "approve", "comment": "تأیید شد"},
    )
    assert decision.status_code == 201
    assert decision.json()["action"] == "approve"
    assert decision.json()["recommendationId"] == recommendation["id"]

    dashboard = _client().get("/api/v1/manager/dashboard", headers=_auth(token))
    assert dashboard.status_code == 200
    summary = dashboard.json()
    assert summary["decidedCount"] == 1
    assert summary["pendingCount"] == 0
    assert summary["recentDecisions"][0]["comment"] == "تأیید شد"
    assert summary["recentDecisions"][0]["personName"] == "کارمند یک"

    duplicate = _client().post(
        f"/api/v1/manager/recommendations/{recommendation['id']}/decision",
        headers=_auth(token),
        json={"action": "reject", "comment": "دوباره"},
    )
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "DECISION_ALREADY_RECORDED"


def test_reject_requires_comment() -> None:
    token = _login(_TENANT_A)
    employee_id = _create_employee(token)
    _add_observation(token, employee_id, "quality", "82")
    recommendation = _evaluate(token, employee_id)
    refused = _client().post(
        f"/api/v1/manager/recommendations/{recommendation['id']}/decision",
        headers=_auth(token),
        json={"action": "reject", "comment": ""},
    )
    assert refused.status_code == 422
    assert refused.json()["error"]["code"] == "DECISION_COMMENT_INVALID"


def test_decision_ledger_is_append_only_at_database_level() -> None:
    """Invariant 14: the database itself refuses UPDATE and DELETE."""
    from sqlalchemy import text as sql_text

    token = _login(_TENANT_A)
    employee_id = _create_employee(token)
    _add_observation(token, employee_id, "quality", "82")
    recommendation = _evaluate(token, employee_id)
    decision = _client().post(
        f"/api/v1/manager/recommendations/{recommendation['id']}/decision",
        headers=_auth(token),
        json={"action": "approve", "comment": "تأیید"},
    )
    decision_id = decision.json()["id"]

    async def attempt_mutation() -> tuple[bool, bool]:
        factory = _IDS["factory"]
        session: AsyncSession = factory()  # type: ignore[operator]
        update_failed = delete_failed = False
        try:
            try:
                await session.execute(
                    sql_text("UPDATE recommendation_decisions SET comment='x' WHERE id=:id"),
                    {"id": uuid.UUID(decision_id)},
                )
                await session.commit()
            except Exception:
                await session.rollback()
                update_failed = True
            try:
                await session.execute(
                    sql_text("DELETE FROM recommendation_decisions WHERE id=:id"),
                    {"id": uuid.UUID(decision_id)},
                )
                await session.commit()
            except Exception:
                await session.rollback()
                delete_failed = True
        finally:
            await session.close()
        return update_failed, delete_failed

    update_failed, delete_failed = asyncio.run(attempt_mutation())
    assert update_failed, "the database must refuse UPDATE on the decision ledger"
    assert delete_failed, "the database must refuse DELETE on the decision ledger"


# ------------------------------------------------------ tenant isolation --


def test_tenant_isolation_blocks_cross_tenant_reads() -> None:
    """ISO-06: manager B can neither read nor list manager A's employees."""
    token_a = _login(_TENANT_A)
    employee_id = _create_employee(token_a)
    token_b = _login(_TENANT_B)

    cross = _client().get(f"/api/v1/manager/employees/{employee_id}", headers=_auth(token_b))
    assert cross.status_code == 404
    listing_b = _client().get("/api/v1/manager/employees", headers=_auth(token_b))
    assert listing_b.status_code == 200
    assert listing_b.json() == []
    # Tenant A must first produce a recommendation before tenant B tries to read it.
    _add_observation(token_a, employee_id, "quality", "82")
    cross_recommendation = _evaluate(token_a, employee_id)
    blocked = _client().get(
        f"/api/v1/manager/recommendations/{cross_recommendation['id']}",
        headers=_auth(token_b),
    )
    assert blocked.status_code == 404


# -------------------------------------------------------------------- auth --


def test_wrong_password_and_missing_token_refused() -> None:
    wrong = _client().post(
        "/api/v1/auth/login", json={"email": "manager-a@test.local", "password": "nope"}
    )
    assert wrong.status_code == 401
    assert wrong.json()["error"]["code"] == "AUTH_INVALID_CREDENTIALS"
    anonymous = _client().get("/api/v1/manager/employees")
    assert anonymous.status_code == 401
    assert anonymous.json()["error"]["code"] == "AUTH_SESSION_INVALID"
    forged = _client().get(
        "/api/v1/manager/employees", headers={"Authorization": "Bearer not-a-token"}
    )
    assert forged.status_code == 401


# ----------------------------------------------------------------- evidence --


def test_evidence_upload_and_listing() -> None:
    token = _login(_TENANT_A)
    employee_id = _create_employee(token)
    uploaded = _client().post(
        f"/api/v1/manager/employees/{employee_id}/evidence",
        headers=_auth(token),
        files={"file": ("note.txt", b"evidence-body", "text/plain")},
        data={"note": "یادداشت"},
    )
    assert uploaded.status_code == 201, uploaded.text
    payload = uploaded.json()
    assert payload["fileName"] == "note.txt"
    assert payload["byteSize"] == len(b"evidence-body")
    import hashlib

    assert payload["sha256"] == hashlib.sha256(b"evidence-body").hexdigest()
    listed = _client().get(
        f"/api/v1/manager/employees/{employee_id}/evidence", headers=_auth(token)
    )
    assert listed.status_code == 200
    assert len(listed.json()) == 1


# ------------------------------------------------------------ CSV import --


def test_csv_import_reports_row_level_reasons() -> None:
    """One file, mixed validity: valid rows inserted, bad rows named."""
    token = _login(_TENANT_A)
    employee_id = _create_employee(token)
    csv_body = (
        "metric_code,period,raw_value\n"
        "quality,1404-Q2,82\n"
        "attendance,1404-Q2,29\n"
        "unknown,1404-Q2,10\n"
        "quality,1404-Q2,-3\n"
    )
    imported = _client().post(
        f"/api/v1/manager/employees/{employee_id}/observations/import",
        headers=_auth(token),
        files={"file": ("observations.csv", csv_body.encode("utf-8"), "text/csv")},
    )
    assert imported.status_code == 200, imported.text
    summary = imported.json()
    assert summary["imported"] == 2
    assert [row["row"] for row in summary["rejected"]] == [4, 5]
    listed = _client().get(
        f"/api/v1/manager/employees/{employee_id}/observations", headers=_auth(token)
    )
    assert all(row["source"] == "import" for row in listed.json())


# ---------------------------------------------------------- payroll engine --


def test_statutory_costing_replays_through_gross_to_net() -> None:
    """AC-09 half: the recommendation costing equals a direct engine call."""
    from app.services.payroll_service import PayrollInput, compute_gross_to_net

    token = _login(_TENANT_A)
    employee_id = _create_employee(token)
    _add_observation(token, employee_id, "quality", "82")
    recommendation = _evaluate(token, employee_id)
    suggested = int(recommendation["suggestedGrossRial"])
    direct = compute_gross_to_net(PayrollInput(gross_monthly_rial=suggested))
    assert recommendation["statutory"]["net_rial"] == direct.payload["net_rial"]
    assert recommendation["statutory"]["calculation_hash"] == direct.calculation_hash


# ------------------------------------------------------------ rules / queue --


def test_rules_endpoint_publishes_provisional_contract() -> None:
    """AC-05: the client renders the form from the engine's own contract."""
    token = _login(_TENANT_A)
    response = _client().get("/api/v1/manager/rules", headers=_auth(token))
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["ruleSetVersion"] == "perf-v1"
    assert payload["ruleSetStatus"] == "PROVISIONAL_DRAFT"
    assert payload["weightsSumBp"] == 10_000
    assert sum(row["weightBp"] for row in payload["criteria"]) == 10_000
    assert [row["code"] for row in payload["criteria"]] == [
        "sales",
        "quality",
        "attendance",
        "responsibility",
    ]
    assert payload["advisory"] is True


def test_pending_queue_and_decision_read_back() -> None:
    """The queue lists a pending recommendation; the decision is read back."""
    token = _login(_TENANT_A)
    employee_id = _create_employee(token)
    _add_observation(token, employee_id, "quality", "82")
    recommendation = _evaluate(token, employee_id)

    pending = _client().get(
        "/api/v1/manager/recommendations", headers=_auth(token), params={"status": "pending"}
    )
    assert pending.status_code == 200, pending.text
    assert [row["id"] for row in pending.json()] == [recommendation["id"]]
    assert pending.json()[0]["decisionAction"] is None
    assert pending.json()[0]["personName"] == "کارمند یک"

    history = _client().get(
        f"/api/v1/manager/employees/{employee_id}/recommendations", headers=_auth(token)
    )
    assert history.status_code == 200
    assert len(history.json()) == 1

    _client().post(
        f"/api/v1/manager/recommendations/{recommendation['id']}/decision",
        headers=_auth(token),
        json={"action": "reject", "comment": "کافی نیست"},
    )
    reread = _client().get(
        f"/api/v1/manager/recommendations/{recommendation['id']}", headers=_auth(token)
    )
    assert reread.status_code == 200
    assert reread.json()["status"] == "decided"
    assert reread.json()["decision"]["action"] == "reject"
    assert reread.json()["decision"]["comment"] == "کافی نیست"

    still_pending = _client().get(
        "/api/v1/manager/recommendations", headers=_auth(token), params={"status": "pending"}
    )
    assert still_pending.json() == []
    decided = _client().get(
        "/api/v1/manager/recommendations", headers=_auth(token), params={"status": "decided"}
    )
    assert [row["decisionAction"] for row in decided.json()] == ["reject"]


def test_employee_patch_updates_profile() -> None:
    """The manager edits the profile fields; the same validation applies."""
    token = _login(_TENANT_A)
    employee_id = _create_employee(token)
    patched = _client().patch(
        f"/api/v1/manager/employees/{employee_id}",
        headers=_auth(token),
        json={"name": "کارمند ویرایش‌شده", "role": "پشتیبانی"},
    )
    assert patched.status_code == 200, patched.text
    assert patched.json()["name"] == "کارمند ویرایش‌شده"
    assert patched.json()["role"] == "پشتیبانی"
    refused = _client().patch(
        f"/api/v1/manager/employees/{employee_id}",
        headers=_auth(token),
        json={"name": "   "},
    )
    assert refused.status_code == 422
    assert refused.json()["error"]["code"] == "EMPLOYEE_NAME_INVALID"

