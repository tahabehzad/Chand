"""The manager workspace API: employees, observations, evidence, evaluations,
recommendations, decisions and the dashboard.

Authority
---------
``AGENTS.md`` §2 Security invariants 12-15 (tenant isolation fails closed,
structured errors, traceable actions); ``docs/adr/ADR-009``; ``docs/
MVP_SCOPE.md`` AC-02…AC-10.

Related
-------
``app/services/manager_service.py`` (the orchestration),
``app/api/deps.py`` (the authenticated manager context), ``app/schemas/
manager.py`` (the contracts).

Scope
-----
Every route requires an authenticated manager session and runs inside the
tenant context bound to that session.  Refusals keep the single
``{"error": {"code", "detail"}}`` shape and never carry an amount or a
personal attribute.
"""

from __future__ import annotations

import csv
import io
import uuid
from typing import Annotated, Literal

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DbSession, ManagerRequired
from app.engines.errors import CodedDomainError
from app.engines.perf_v1 import validate_observation_value
from app.models.manager import (
    Employee,
    EmployeeEvaluation,
    EmployeeEvidence,
    EmployeeObservation,
    RecommendationDecision,
    SalaryRecommendation,
)
from app.schemas.manager import (
    DashboardResponse,
    DecisionRequest,
    DecisionResponse,
    EmployeeCreateRequest,
    EmployeePatchRequest,
    EmployeeResponse,
    EvaluationRequest,
    EvaluationRulesResponse,
    EvidenceResponse,
    ImportRowError,
    ImportSummaryResponse,
    ObservationCreateRequest,
    ObservationPatchRequest,
    ObservationResponse,
    RecommendationResponse,
    RecommendationSummaryResponse,
)
from app.services import manager_service

router = APIRouter(prefix="/api/v1/manager", tags=["manager"])

NotFoundCodes = frozenset(
    {
        "EMPLOYEE_NOT_FOUND",
        "OBSERVATION_NOT_FOUND",
        "RECOMMENDATION_NOT_FOUND",
    }
)
ConflictCodes = frozenset({"OBSERVATION_REJECTED", "DECISION_ALREADY_RECORDED"})


def _error(status_code: int, code: str, detail: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code, content={"error": {"code": code, "detail": detail}}
    )


def _domain_error_response(exc: CodedDomainError) -> JSONResponse:
    if exc.code in NotFoundCodes:
        return _error(404, exc.code, str(exc))
    if exc.code in ConflictCodes:
        return _error(409, exc.code, str(exc))
    return _error(422, exc.code, str(exc))


# ------------------------------------------------------------- serialisers --


def _employee_response(employee: Employee) -> EmployeeResponse:
    return EmployeeResponse(
        id=str(employee.id),
        name=employee.name,
        role=employee.role_label,
        startDate=employee.start_date,
        createdAt=employee.created_at.isoformat(),
    )


def _observation_response(observation: EmployeeObservation) -> ObservationResponse:
    return ObservationResponse(
        id=str(observation.id),
        personId=str(observation.employee_id),
        code=observation.metric_code,
        period=observation.period,
        raw=observation.raw_value,
        state=observation.state,
        source=observation.source,
        createdAt=observation.created_at.isoformat(),
    )


def _evidence_response(evidence: EmployeeEvidence) -> EvidenceResponse:
    return EvidenceResponse(
        id=str(evidence.id),
        employeeId=str(evidence.employee_id),
        fileName=evidence.file_name,
        contentType=evidence.content_type,
        byteSize=evidence.byte_size,
        sha256=evidence.sha256,
        note=evidence.note,
        createdAt=evidence.created_at.isoformat(),
    )


def _recommendation_response(
    recommendation: SalaryRecommendation,
    evaluation: EmployeeEvaluation,
    employee_name: str,
    decision: RecommendationDecision | None,
) -> RecommendationResponse:
    return RecommendationResponse(
        id=str(recommendation.id),
        personId=str(recommendation.employee_id),
        personName=employee_name,
        period=recommendation.period,
        ruleSetVersion=recommendation.rule_set_version,
        ruleSetStatus=evaluation.rule_set_status,
        score100=recommendation.score_100,
        totalBp=recommendation.band_position_bp,
        contributions=[
            {
                "code": c["code"],
                "labelFa": c["labelFa"],
                "weightBp": c["weightBp"],
                "missing": c["missing"],
                "raw": c["raw"],
                "normalisedBp": c["normalisedBp"],
                "contributionBp": c["contributionBp"],
            }
            for c in evaluation.contributions
        ],
        missingCriteria=list(evaluation.missing_criteria),
        observationsUsed=[
            {
                "id": o["id"],
                "code": o["code"],
                "period": o["period"],
                "raw": o["raw"],
            }
            for o in evaluation.observations_used
        ],
        band={
            "minRial": recommendation.band_min_rial,
            "maxRial": recommendation.band_max_rial,
            "currentRial": recommendation.band_current_rial,
            "positionBp": recommendation.band_position_bp,
        },
        suggestedGrossRial=recommendation.suggested_gross_rial,
        deltaRial=recommendation.delta_rial,
        statutory=recommendation.statutory_costing,
        currentStatutory=recommendation.current_costing,
        explanation={
            "reasons": recommendation.explanation.get("reasons", []),
            "warnings": recommendation.explanation.get("warnings", []),
            "dataQuality": recommendation.explanation.get("dataQuality", []),
            "advisory": True,
            "statutoryStatus": recommendation.explanation.get(
                "statutoryStatus", "provisional_engine_ready_for_review"
            ),
        },
        engineVersion=recommendation.engine_version,
        calculationHash=recommendation.calculation_hash,
        advisory=True,
        status=recommendation.status,
        decision=None if decision is None else _decision_response(decision),
        createdAt=recommendation.created_at.isoformat(),
    )


def _summary_response(
    recommendation: SalaryRecommendation,
    employee_name: str,
    decision: RecommendationDecision | None,
) -> RecommendationSummaryResponse:
    return RecommendationSummaryResponse(
        id=str(recommendation.id),
        personId=str(recommendation.employee_id),
        personName=employee_name,
        period=recommendation.period,
        score100=recommendation.score_100,
        suggestedGrossRial=recommendation.suggested_gross_rial,
        deltaRial=recommendation.delta_rial,
        status=recommendation.status,
        decisionAction=None if decision is None else decision.action,
        createdAt=recommendation.created_at.isoformat(),
    )


def _decision_response(decision: RecommendationDecision) -> DecisionResponse:
    return DecisionResponse(
        id=str(decision.id),
        recommendationId=str(decision.recommendation_id),
        action=decision.action,
        editedGrossRial=decision.edited_gross_rial,
        comment=decision.comment,
        decidedAt=decision.decided_at.isoformat(),
    )


async def _load_evaluation(db: AsyncSession, evaluation_id: uuid.UUID) -> EmployeeEvaluation:
    evaluation = await db.get(EmployeeEvaluation, evaluation_id)
    if evaluation is None:  # pragma: no cover - a recommendation always has one
        raise CodedDomainError("EVALUATION_NOT_FOUND", "ارزیابی این پیشنهاد یافت نشد.")
    return evaluation


# ------------------------------------------------------------------- rules --


@router.get(
    "/rules",
    response_model=EvaluationRulesResponse,
    summary="The published evaluation rule set",
)
async def get_rules(manager: ManagerRequired) -> EvaluationRulesResponse:
    """The ``perf-v1`` criteria, weights, bounds and missing-data policy.

    The client renders the observation form from this payload; it performs no
    scoring of its own.  The status is emitted verbatim so the provisional
    weights can never be presented as approved rules.
    """
    del manager  # authenticated + tenant-bound; the rule set is tenant-neutral
    return EvaluationRulesResponse(**manager_service.evaluation_rules_payload())


# --------------------------------------------------------------- dashboard --


@router.get("/dashboard", response_model=DashboardResponse, summary="Dashboard counters")
async def get_dashboard(
    manager: ManagerRequired, db: DbSession
) -> DashboardResponse | JSONResponse:
    """The manager dashboard counters and the recent decision history."""
    try:
        summary = await manager_service.dashboard_summary(db, manager.tenant_id)
    except CodedDomainError as exc:
        return _domain_error_response(exc)
    return DashboardResponse(**summary)


# ---------------------------------------------------------------- employees --


@router.post(
    "/employees",
    response_model=EmployeeResponse,
    status_code=201,
    summary="Create one employee",
)
async def create_employee(
    payload: EmployeeCreateRequest, manager: ManagerRequired, db: DbSession
) -> EmployeeResponse | JSONResponse:
    try:
        employee = await manager_service.create_employee(
            db,
            manager.tenant_id,
            manager.user_id,
            name=payload.name,
            role_label=payload.role,
            start_date=payload.startDate,
        )
        await db.commit()
    except CodedDomainError as exc:
        await db.rollback()
        return _domain_error_response(exc)
    except ValueError as exc:
        await db.rollback()
        return _error(422, "EMPLOYEE_INVALID", str(exc))
    return _employee_response(employee)


@router.get("/employees", response_model=list[EmployeeResponse], summary="List employees")
async def list_employees(manager: ManagerRequired, db: DbSession) -> list[EmployeeResponse] | JSONResponse:
    try:
        employees = await manager_service.load_employees(db, manager.tenant_id)
        return [_employee_response(employee) for employee in employees]
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"error": {"code": "DATASTORE_UNAVAILABLE", "detail": "پایگاه داده در دسترس نیست."}},
        )


@router.get("/employees/{employee_id}", response_model=EmployeeResponse, summary="One employee")
async def get_employee(
    employee_id: uuid.UUID, manager: ManagerRequired, db: DbSession
) -> EmployeeResponse | JSONResponse:
    try:
        employee = await manager_service.load_employee(db, manager.tenant_id, employee_id)
    except CodedDomainError as exc:
        return _domain_error_response(exc)
    return _employee_response(employee)


@router.patch(
    "/employees/{employee_id}", response_model=EmployeeResponse, summary="Edit one employee"
)
async def patch_employee(
    employee_id: uuid.UUID,
    payload: EmployeePatchRequest,
    manager: ManagerRequired,
    db: DbSession,
) -> EmployeeResponse | JSONResponse:
    try:
        employee = await manager_service.update_employee(
            db,
            manager.tenant_id,
            employee_id,
            name=payload.name,
            role_label=payload.role,
            start_date=payload.startDate,
        )
        await db.commit()
    except CodedDomainError as exc:
        await db.rollback()
        return _domain_error_response(exc)
    return _employee_response(employee)


# -------------------------------------------------------------- observations --


@router.get(
    "/employees/{employee_id}/observations",
    response_model=list[ObservationResponse],
    summary="List one employee's observations",
)
async def get_observations(
    employee_id: uuid.UUID, manager: ManagerRequired, db: DbSession
) -> list[ObservationResponse] | JSONResponse:
    try:
        observations = await manager_service.list_observations(db, manager.tenant_id, employee_id)
    except CodedDomainError as exc:
        return _domain_error_response(exc)
    return [_observation_response(observation) for observation in observations]


@router.post(
    "/employees/{employee_id}/observations",
    response_model=ObservationResponse,
    status_code=201,
    summary="Record one observation",
)
async def post_observation(
    employee_id: uuid.UUID,
    payload: ObservationCreateRequest,
    manager: ManagerRequired,
    db: DbSession,
) -> ObservationResponse | JSONResponse:
    try:
        observation = await manager_service.add_observation(
            db,
            manager.tenant_id,
            employee_id,
            metric_code=payload.code,
            period=payload.period,
            raw_value=payload.raw,
        )
        await db.commit()
    except CodedDomainError as exc:
        await db.rollback()
        return _domain_error_response(exc)
    return _observation_response(observation)


@router.patch(
    "/observations/{observation_id}",
    response_model=ObservationResponse,
    summary="Correct one observation",
)
async def patch_observation(
    observation_id: uuid.UUID,
    payload: ObservationPatchRequest,
    manager: ManagerRequired,
    db: DbSession,
) -> ObservationResponse | JSONResponse:
    try:
        observation = await manager_service.correct_observation(
            db, manager.tenant_id, observation_id, payload.raw
        )
        await db.commit()
    except CodedDomainError as exc:
        await db.rollback()
        return _domain_error_response(exc)
    return _observation_response(observation)


@router.post(
    "/observations/{observation_id}/reject",
    response_model=ObservationResponse,
    summary="Reject one observation",
)
async def reject_observation(
    observation_id: uuid.UUID, manager: ManagerRequired, db: DbSession
) -> ObservationResponse | JSONResponse:
    try:
        observation = await manager_service.reject_observation(
            db, manager.tenant_id, observation_id
        )
        await db.commit()
    except CodedDomainError as exc:
        await db.rollback()
        return _domain_error_response(exc)
    return _observation_response(observation)


@router.post(
    "/employees/{employee_id}/observations/import",
    response_model=ImportSummaryResponse,
    summary="Import observations from a UTF-8 CSV file",
)
async def import_observations(
    employee_id: uuid.UUID,
    manager: ManagerRequired,
    db: DbSession,
    file: Annotated[UploadFile, File()],
) -> ImportSummaryResponse | JSONResponse:
    """Import rows of ``metric_code,period,raw_value``.

    Every row is validated independently; rejected rows are reported with a
    row number and never inserted, valid rows are inserted with the ``import``
    source tag.  The whole file is one transaction: a database failure rolls
    back every row.
    """
    raw_bytes = await file.read()
    try:
        text = raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        return _error(422, "IMPORT_ENCODING_INVALID", "فایل باید با کدگذاری UTF-8 باشد.")
    reader = csv.reader(io.StringIO(text))
    imported = 0
    rejected: list[ImportRowError] = []
    staged: list[tuple[str, str, str]] = []
    for row_number, row in enumerate(reader, start=1):
        if not row or all(cell.strip() == "" for cell in row):
            continue
        if row_number == 1 and row[0].strip().lower() in {"metric_code", "code"}:
            continue  # header row
        if len(row) < 3:
            rejected.append(ImportRowError(row=row_number, reason="ستون‌های کافی وجود ندارد."))
            continue
        try:
            canonical = validate_observation_value(row[0].strip(), row[2].strip())
            period = row[1].strip()
            if not period or len(period) > 40:
                raise CodedDomainError("OBSERVATION_PERIOD_INVALID", "دورهٔ ارزیابی نامعتبر است.")
            staged.append((row[0].strip(), period, canonical))
        except CodedDomainError as exc:
            rejected.append(ImportRowError(row=row_number, reason=str(exc)))
    if imported == 0 and not rejected and not staged:
        return _error(422, "IMPORT_EMPTY", "فایل خالی است یا سطر قابل خواندنی ندارد.")
    try:
        for metric_code, period, value in staged:
            await manager_service.add_observation(
                db,
                manager.tenant_id,
                employee_id,
                metric_code=metric_code,
                period=period,
                raw_value=value,
                source="import",
            )
            imported += 1
        await db.commit()
    except CodedDomainError as exc:
        await db.rollback()
        return _domain_error_response(exc)
    return ImportSummaryResponse(imported=imported, rejected=rejected)


# ----------------------------------------------------------------- evidence --


@router.post(
    "/employees/{employee_id}/evidence",
    response_model=EvidenceResponse,
    status_code=201,
    summary="Upload one supporting evidence file",
)
async def upload_evidence(
    employee_id: uuid.UUID,
    manager: ManagerRequired,
    db: DbSession,
    file: Annotated[UploadFile, File()],
    note: Annotated[str | None, Form()] = None,
) -> EvidenceResponse | JSONResponse:
    content = await file.read()
    try:
        evidence = await manager_service.add_evidence(
            db,
            manager.tenant_id,
            employee_id,
            created_by=manager.user_id,
            file_name=file.filename or "evidence",
            content_type=file.content_type or "application/octet-stream",
            content=content,
            note=note,
        )
        await db.commit()
    except CodedDomainError as exc:
        await db.rollback()
        return _domain_error_response(exc)
    return _evidence_response(evidence)


@router.get(
    "/employees/{employee_id}/evidence",
    response_model=list[EvidenceResponse],
    summary="List one employee's evidence metadata",
)
async def get_evidence(
    employee_id: uuid.UUID, manager: ManagerRequired, db: DbSession
) -> list[EvidenceResponse] | JSONResponse:
    try:
        evidence_rows = await manager_service.list_evidence(db, manager.tenant_id, employee_id)
    except CodedDomainError as exc:
        return _domain_error_response(exc)
    return [_evidence_response(evidence) for evidence in evidence_rows]


# ------------------------------------------------- evaluation/recommendation --


@router.post(
    "/employees/{employee_id}/evaluations",
    response_model=RecommendationResponse,
    status_code=201,
    summary="Evaluate the employee and produce the salary recommendation",
)
async def post_evaluation(
    employee_id: uuid.UUID,
    payload: EvaluationRequest,
    manager: ManagerRequired,
    db: DbSession,
) -> RecommendationResponse | JSONResponse:
    try:
        recommendation = await manager_service.create_recommendation(
            db,
            manager.tenant_id,
            employee_id,
            created_by=manager.user_id,
            band_min_rial=payload.bandMinRial,
            band_max_rial=payload.bandMaxRial,
            band_current_rial=payload.currentRial,
        )
        employee = await manager_service.load_employee(db, manager.tenant_id, employee_id)
        evaluation = await _load_evaluation(db, recommendation.evaluation_id)
        await db.commit()
    except CodedDomainError as exc:
        await db.rollback()
        return _domain_error_response(exc)
    except ValueError as exc:
        await db.rollback()
        return _error(422, "EVALUATION_INVALID", str(exc))
    return _recommendation_response(recommendation, evaluation, employee.name, None)


@router.get(
    "/employees/{employee_id}/recommendations",
    response_model=list[RecommendationSummaryResponse],
    summary="One employee's recommendation history",
)
async def get_employee_recommendations(
    employee_id: uuid.UUID, manager: ManagerRequired, db: DbSession
) -> list[RecommendationSummaryResponse] | JSONResponse:
    """Every recommendation for one employee, newest first."""
    try:
        await manager_service.load_employee(db, manager.tenant_id, employee_id)
        rows = await manager_service.list_recommendations(
            db, manager.tenant_id, employee_id=employee_id
        )
    except CodedDomainError as exc:
        return _domain_error_response(exc)
    return [
        _summary_response(recommendation, employee.name, decision)
        for recommendation, employee, decision in rows
    ]


@router.get(
    "/recommendations",
    response_model=list[RecommendationSummaryResponse],
    summary="Recommendations, optionally filtered by status",
)
async def get_recommendations(
    manager: ManagerRequired,
    db: DbSession,
    status: Literal["pending", "decided"] | None = None,
) -> list[RecommendationSummaryResponse]:
    """The manager's queue (``status=pending``) or the decided history."""
    rows = await manager_service.list_recommendations(db, manager.tenant_id, status=status)
    return [
        _summary_response(recommendation, employee.name, decision)
        for recommendation, employee, decision in rows
    ]


@router.get(
    "/recommendations/{recommendation_id}",
    response_model=RecommendationResponse,
    summary="One recommendation with its full explanation",
)
async def get_recommendation(
    recommendation_id: uuid.UUID, manager: ManagerRequired, db: DbSession
) -> RecommendationResponse | JSONResponse:
    try:
        recommendation = await manager_service.load_recommendation(
            db, manager.tenant_id, recommendation_id
        )
        employee = await manager_service.load_employee(
            db, manager.tenant_id, recommendation.employee_id
        )
        evaluation = await _load_evaluation(db, recommendation.evaluation_id)
        decision = await manager_service.load_decision(db, manager.tenant_id, recommendation_id)
    except CodedDomainError as exc:
        return _domain_error_response(exc)
    return _recommendation_response(recommendation, evaluation, employee.name, decision)


# ----------------------------------------------------------------- decisions --


@router.post(
    "/recommendations/{recommendation_id}/decision",
    response_model=DecisionResponse,
    status_code=201,
    summary="Approve, edit or reject a pending recommendation",
)
async def post_decision(
    recommendation_id: uuid.UUID,
    payload: DecisionRequest,
    manager: ManagerRequired,
    db: DbSession,
) -> DecisionResponse | JSONResponse:
    try:
        decision = await manager_service.decide_recommendation(
            db,
            manager.tenant_id,
            manager.user_id,
            recommendation_id,
            action=payload.action,
            comment=payload.comment,
            edited_gross_rial=payload.editedGrossRial,
        )
        await db.commit()
    except CodedDomainError as exc:
        await db.rollback()
        return _domain_error_response(exc)
    return _decision_response(decision)


__all__ = ["router"]
