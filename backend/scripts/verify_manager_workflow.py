"""End-to-end verification of the manager workspace against a live API.

Usage
-----
Start the backend (``uvicorn app.main:app``) and seed the local manager
(``python scripts/seed_local_dev.py``), then run from ``backend/``:

    python scripts/verify_manager_workflow.py

Environment overrides: ``PISH_API_URL`` (default ``http://127.0.0.1:8000``),
``PISH_MANAGER_EMAIL`` and ``PISH_MANAGER_PASSWORD``.

The script creates three demo employees so it can exercise all three decision
actions (approve, edit, reject). It only uses synthetic data, never prints the
token or the password, and exits non-zero on the first failed assertion. It is
a local verification aid, not a CI job and not a production tool.
"""

from __future__ import annotations

import os
import sys

import httpx

BASE_URL = os.environ.get("PISH_API_URL", "http://127.0.0.1:8000").rstrip("/")
EMAIL = os.environ.get("PISH_MANAGER_EMAIL", "manager@local.dev")
PASSWORD = os.environ.get("PISH_MANAGER_PASSWORD", "local-dev-only")

CHECKS = [0]


def check(condition: bool, label: str) -> None:
    """Assert one observable fact and keep a running count."""
    CHECKS[0] += 1
    if not condition:
        raise AssertionError(f"FAILED: {label}")
    print(f"  ok  {label}")


def main() -> int:  # noqa: PLR0915 - one linear script is easier to audit here
    client = httpx.Client(base_url=BASE_URL, timeout=20.0)

    print("[1] login and rules")
    login = client.post("/api/v1/auth/login", json={"email": EMAIL, "password": PASSWORD})
    check(login.status_code == 200, "POST /auth/login returns 200")
    payload = login.json()
    token = payload["token"]
    check(isinstance(token, str) and len(token) >= 32, "login returns an opaque token")
    check(payload["manager"]["email"] == EMAIL, "login echoes the manager identity")
    headers = {"Authorization": f"Bearer {token}"}

    me = client.get("/api/v1/auth/me", headers=headers)
    check(me.status_code == 200, "GET /auth/me accepts the token")

    rules = client.get("/api/v1/manager/rules", headers=headers)
    check(rules.status_code == 200, "GET /manager/rules returns 200")
    rules_payload = rules.json()
    check(rules_payload["ruleSetVersion"] == "perf-v1", "rules publish perf-v1")
    check(rules_payload["ruleSetStatus"] == "PROVISIONAL_DRAFT", "rules are marked provisional")
    check(sum(item["weightBp"] for item in rules_payload["criteria"]) == 10_000, "weights sum to 1")

    baseline = client.get("/api/v1/manager/dashboard", headers=headers).json()

    print("[2] employee validation and creation")
    invalid = client.post(
        "/api/v1/manager/employees",
        headers=headers,
        json={"name": "", "role": "x", "startDate": "2024-03-20"},
    )
    check(invalid.status_code == 422, "empty name is refused")
    check(invalid.json()["error"]["code"] == "EMPLOYEE_NAME_INVALID", "refusal carries a stable code")

    def create(name: str, post: str) -> dict[str, str]:
        response = client.post(
            "/api/v1/manager/employees",
            headers=headers,
            json={"name": name, "role": post, "startDate": "2024-03-20"},
        )
        check(response.status_code == 201, f"create employee {name}")
        created: dict[str, str] = response.json()
        return created

    approved = create("کارمند آزمون تأیید", "کارشناس فروش")
    edited = create("کارمند آزمون ویرایش", "کارشناس پشتیبانی")
    rejected = create("کارمند آزمون رد", "کارشناس عملیات")

    patched = client.patch(
        f"/api/v1/manager/employees/{approved['id']}",
        headers=headers,
        json={"role": "سرپرست فروش"},
    )
    check(patched.status_code == 200, "PATCH employee profile")
    check(patched.json()["role"] == "سرپرست فروش", "profile edit is persisted")
    fetched = client.get(f"/api/v1/manager/employees/{approved['id']}", headers=headers)
    check(fetched.json()["role"] == "سرپرست فروش", "GET returns the edited profile")

    print("[3] observations, CSV import and evidence")
    observations = (
        ("sales", "800000000"),
        ("quality", "82"),
        ("attendance", "29"),
        ("responsibility", "4"),
    )
    for code, raw in observations:
        added = client.post(
            f"/api/v1/manager/employees/{approved['id']}/observations",
            headers=headers,
            json={"code": code, "period": "1404-Q2", "raw": raw},
        )
        check(added.status_code == 201, f"add observation {code}")

    csv_body = (
        "metric_code,period,raw_value\n"
        "quality,1404-Q3,88\n"
        "attendance,1404-Q3,30\n"
        "unknown,1404-Q3,7\n"
        "quality,1404-Q3,-1\n"
    )
    imported = client.post(
        f"/api/v1/manager/employees/{edited['id']}/observations/import",
        headers=headers,
        files={"file": ("observations.csv", csv_body.encode("utf-8"), "text/csv")},
    )
    check(imported.status_code == 200, "CSV import returns 200")
    summary = imported.json()
    check(summary["imported"] == 2, "two valid rows imported")
    check(len(summary["rejected"]) == 2, "two invalid rows rejected with reasons")

    evidence = client.post(
        f"/api/v1/manager/employees/{approved['id']}/evidence",
        headers=headers,
        files={"file": ("sample.txt", b"local verification evidence", "text/plain")},
        data={"note": "شاهد نمونه برای سنجش جریان"},
    )
    check(evidence.status_code == 201, "evidence upload returns 201")
    evidence_payload = evidence.json()
    check(
        evidence_payload["byteSize"] == len(b"local verification evidence"),
        "evidence byte size is recorded",
    )
    checked_evidence = client.get(
        f"/api/v1/manager/employees/{approved['id']}/evidence", headers=headers
    )
    check(len(checked_evidence.json()) == 1, "evidence is listed from the database")

    print("[4] evaluation and recommendation")
    evaluation = client.post(
        f"/api/v1/manager/employees/{approved['id']}/evaluations",
        headers=headers,
        json={"bandMinRial": 80_000_000, "bandMaxRial": 140_000_000, "currentRial": 100_000_000},
    )
    check(evaluation.status_code == 201, "evaluation returns 201")
    evaluated = evaluation.json()
    recommendation_id = evaluated["id"]
    check(evaluated["score100"] == 83, "score is deterministic (83)")
    check(evaluated["ruleSetVersion"] == "perf-v1", "evaluation records perf-v1")
    check(evaluated["advisory"] is True, "result is advisory")
    check(evaluated["missingCriteria"] == [], "no missing criterion on the full profile")
    check(len(evaluated["contributions"]) == 4, "four explainable contributions")
    check(evaluated["statutory"]["net_rial"] > 0, "statutory net is positive")
    check(evaluated["statutory"]["engine_version"].endswith("payroll-engine"), "payroll engine reused")
    check(len(evaluated["statutory"]["calculation_hash"]) == 64, "statutory hash is present")

    detail = client.get(f"/api/v1/manager/recommendations/{recommendation_id}", headers=headers)
    check(detail.status_code == 200, "recommendation detail is readable")
    check(detail.json()["decision"] is None, "new recommendation is pending")
    pending = client.get("/api/v1/manager/recommendations?status=pending", headers=headers).json()
    check(any(row["id"] == recommendation_id for row in pending), "pending queue contains it")

    print("[5] partial profile reports missing criteria")
    for code, raw in (("quality", "65"), ("attendance", "27")):
        client.post(
            f"/api/v1/manager/employees/{edited['id']}/observations",
            headers=headers,
            json={"code": code, "period": "1404-Q3", "raw": raw},
        )
    partial = client.post(
        f"/api/v1/manager/employees/{edited['id']}/evaluations",
        headers=headers,
        json={"bandMinRial": 80_000_000, "bandMaxRial": 140_000_000},
    )
    check(partial.status_code == 201, "partial profile still evaluates")
    partial_payload = partial.json()
    check(
        set(partial_payload["missingCriteria"]) == {"sales", "responsibility"},
        "missing criteria are named",
    )
    check(len(partial_payload["explanation"]["dataQuality"]) > 0, "data-quality limit is reported")
    check(partial_payload["deltaRial"] is None, "missing current pay is not coerced to zero")

    client.post(
        f"/api/v1/manager/employees/{rejected['id']}/observations",
        headers=headers,
        json={"code": "quality", "period": "1404-Q3", "raw": "40"},
    )
    reject_target = client.post(
        f"/api/v1/manager/employees/{rejected['id']}/evaluations",
        headers=headers,
        json={"bandMinRial": 70_000_000, "bandMaxRial": 120_000_000},
    ).json()

    print("[6] decisions are persisted and immutable")
    approve = client.post(
        f"/api/v1/manager/recommendations/{recommendation_id}/decision",
        headers=headers,
        json={"action": "approve", "comment": "تأیید نمونهٔ محلی"},
    )
    check(approve.status_code == 201, "approve decision returns 201")
    check(approve.json()["action"] == "approve", "decision action is approve")

    duplicate = client.post(
        f"/api/v1/manager/recommendations/{recommendation_id}/decision",
        headers=headers,
        json={"action": "reject", "comment": "تلاش دوم"},
    )
    check(duplicate.status_code == 409, "a second decision is refused")
    check(duplicate.json()["error"]["code"] == "DECISION_ALREADY_RECORDED", "duplicate carries a code")

    read_back = client.get(f"/api/v1/manager/recommendations/{recommendation_id}", headers=headers)
    check(read_back.json()["decision"]["action"] == "approve", "decision reads back after reload")

    edit_decision = client.post(
        f"/api/v1/manager/recommendations/{partial_payload['id']}/decision",
        headers=headers,
        json={
            "action": "edit",
            "comment": "مبلغ اصلاح‌شده",
            "editedGrossRial": 105_000_000,
        },
    )
    check(edit_decision.status_code == 201, "edit decision returns 201")
    check(edit_decision.json()["editedGrossRial"] == 105_000_000, "edited amount is stored")

    reject_decision = client.post(
        f"/api/v1/manager/recommendations/{reject_target['id']}/decision",
        headers=headers,
        json={"action": "reject", "comment": "دادهٔ کافی نیست"},
    )
    check(reject_decision.status_code == 201, "reject decision returns 201")

    print("[7] dashboard and history reflect the workflow")
    dashboard = client.get("/api/v1/manager/dashboard", headers=headers).json()
    check(dashboard["peopleCount"] == baseline["peopleCount"] + 3, "people count grew by three")
    check(dashboard["pendingCount"] == baseline["pendingCount"], "no pending recommendation remains")
    check(dashboard["decidedCount"] == baseline["decidedCount"] + 3, "three decisions recorded")
    actions = {row["action"] for row in dashboard["recentDecisions"]}
    check({"approve", "edit", "reject"} <= actions, "history names all three actions")
    decided = client.get("/api/v1/manager/recommendations?status=decided", headers=headers).json()
    check(len(decided) == dashboard["decidedCount"], "decided queue matches the counter")

    print("[8] unauthenticated access fails closed")
    anonymous = httpx.get(f"{BASE_URL}/api/v1/manager/dashboard", timeout=10.0)
    check(anonymous.status_code == 401, "missing bearer token is refused")
    forged = httpx.get(
        f"{BASE_URL}/api/v1/manager/dashboard",
        headers={"Authorization": "Bearer not-a-real-token"},
        timeout=10.0,
    )
    check(forged.status_code == 401, "unknown token is refused")

    print(f"\nPASS: {CHECKS[0]} checks against {BASE_URL}")
    print(f"demo employees: {approved['id']}, {edited['id']}, {rejected['id']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"\n{exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    except httpx.HTTPError as exc:
        print(f"\nHTTP error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
