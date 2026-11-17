"""The manager workspace service: evaluation, recommendation, decisions.

Authority
---------
``AGENTS.md`` §2 (all Financial and Security invariants — Decimal engines,
integer Rial at the boundary, fail-closed tenant context, provenance on every
figure); ``docs/adr/ADR-009`` (advisory only); ``docs/MVP_SCOPE.md`` AC-04…
AC-10; ``docs/MVP_WBS.md`` MVP-09…MVP-11, MVP-15.

Related
-------
``app/engines/perf_v1.py`` (the provisional ``perf-v1`` rule set),
``app/services/payroll_service.py`` (``compute_gross_to_net`` — the statutory
costing of every suggested amount), ``app/models/manager.py``.

Scope
-----
Every function here is orchestrating persistence plus one call into an
existing engine.  No scoring or statutory arithmetic is re-implemented:

* **Evaluation** — the latest non-rejected observation per criterion is scored
  by ``score_observations`` and persisted with its full explanation.
* **Recommendation** — the score positions the employee inside the
  manager-supplied band; the suggested gross and (when supplied) the current
  gross are costed by the existing 1404 statutory engine.  The response is
  always ``advisory`` and carries the engine's review status.
* **Decision** — one append-only decision per recommendation, enforced by the
  database trigger, plus the recommendation status flip.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.engines.errors import CodedDomainError, PayrollEngineError
from app.engines.perf_v1 import (
    CRITERIA,
    MISSING_POLICY_FA,
    RULE_SET_STATUS,
    RULE_SET_VERSION,
    WEIGHTS_SUM_BP,
    ScoreInput,
    score_observations,
    validate_observation_value,
)
from app.models.manager import (
    Employee,
    EmployeeEvaluation,
    EmployeeEvidence,
    EmployeeObservation,
    RecommendationDecision,
    SalaryRecommendation,
)
from app.services.payroll_service import (
    ENGINE_VERSION,
    PayrollInput,
    compute_gross_to_net,
)

MAX_MONEY_RIAL = 10_000_000_000_000  # sanity ceiling, not a policy
MAX_TEXT = 120


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    """The persisted evaluation."""

    evaluation: EmployeeEvaluation


# ------------------------------------------------------------------ helpers --


def _require_tenant_digits(value: int, code: str, detail: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0 or value > MAX_MONEY_RIAL:
        raise CodedDomainError(code, detail)
    return value


def _canonical_hash(payload: dict[str, Any]) -> str:
    """SHA-256 over canonical JSON — the traceability hash of the output."""
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _statutory_cost_block(gross_monthly_rial: int, *, rule_year: int = 1404) -> dict[str, Any]:
    """Cost one gross amount through the existing statutory engine.

    The engine is READY_FOR_REVIEW, not APPROVED: the block carries that
    status verbatim, and the caller labels the figures provisional.
    """
    payroll = compute_gross_to_net(
        PayrollInput(
            gross_monthly_rial=gross_monthly_rial,
            rule_year=rule_year,
            days_in_month=30,
        )
    )
    payload = payroll.payload
    return {
        "request": {
            "gross_monthly_rial": gross_monthly_rial,
            "rule_year": rule_year,
            "days_in_month": 30,
            "tax_posture": payload["primary_tax_posture"],
        },
        "calculation_hash": payroll.calculation_hash,
        "statutory_version": payload["statutory_version"],
        "rule_set_fingerprint": payload["rule_set_fingerprint"],
        "rule_set_status": payload.get("rule_set_status", "UNKNOWN"),
        "is_verified": payload.get("is_verified", False),
        "engine_version": payload.get("engine_version", ENGINE_VERSION),
        "gross_monthly_rial": payload["bases"]["total_gross_rial"],
        "employee_sso_7pct_rial": payload["employee_deductions"]["employee_sso_7pct_rial"],
        "sso_insurable_ceiling_applied": payload["sso"]["sso_insurable_ceiling_applied"],
        "income_tax_rial": payload["employee_deductions"]["income_tax_rial"],
        "net_rial": payload["net_rial"],
        "monthly_sanavat_accrual_rial": payload["severance_sanavat"]["monthly_accrual_rial"],
        "monthly_eydi_accrual_rial": payload["eydi"]["monthly_accrual_rial"],
        "total_monthly_employer_cost_rial": payload["employer_cost"][
            "total_monthly_employer_cost_rial"
        ],
        "annual_ctc_12month_rial": payload["employer_cost"]["annual_ctc_12month_rial"],
        "rounding_residual_rial": payload["rounding_residual_rial"],
    }


# --------------------------------------------------------------- evaluation --


async def _load_employees(db: AsyncSession, tenant_id: uuid.UUID) -> list[Employee]:
    result = await db.execute(
        select(Employee)
        .where(Employee.tenant_id == tenant_id)
        .order_by(Employee.created_at, Employee.id)
    )
    return list(result.scalars())


async def load_employees(db: AsyncSession, tenant_id: uuid.UUID) -> list[Employee]:
    """All employees of one tenant, oldest first."""
    return await _load_employees(db, tenant_id)


async def load_employee(db: AsyncSession, tenant_id: uuid.UUID, employee_id: uuid.UUID) -> Employee:
    """Return the employee or raise the stable 404 code."""
    employee = (
        await db.execute(
            select(Employee).where(Employee.tenant_id == tenant_id, Employee.id == employee_id)
        )
    ).scalar_one_or_none()
    if employee is None:
        raise CodedDomainError("EMPLOYEE_NOT_FOUND", "این کارمند در سازمان شما یافت نشد.")
    return employee


async def create_employee(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    created_by: uuid.UUID,
    *,
    name: str,
    role_label: str,
    start_date: str,
) -> Employee:
    """Create one employee after validating the fields the engine needs."""
    name = name.strip()
    if not name or len(name) > MAX_TEXT:
        raise CodedDomainError(
            "EMPLOYEE_NAME_INVALID", "نام کارمند الزامی است و حداکثر ۱۲۰ نویسه است."
        )
    role_label = role_label.strip()
    if not role_label or len(role_label) > 60:
        raise CodedDomainError(
            "EMPLOYEE_ROLE_INVALID", "عنوان شغلی الزامی است و حداکثر ۶۰ نویسه است."
        )
    if len(start_date) != 10 or not start_date[:4].isdigit() or start_date[4] != "-":
        raise CodedDomainError(
            "EMPLOYEE_START_DATE_INVALID", "تاریخ شروع باید به شکل میلادی 2024-03-20 باشد."
        )
    employee = Employee(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        name=name,
        role_label=role_label,
        start_date=start_date,
        created_by=created_by,
    )
    db.add(employee)
    await db.flush()
    return employee


async def update_employee(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    employee_id: uuid.UUID,
    *,
    name: str | None,
    role_label: str | None,
    start_date: str | None,
) -> Employee:
    """Edit the editable profile fields; every supplied value is revalidated."""
    employee = await load_employee(db, tenant_id, employee_id)
    if name is not None:
        name = name.strip()
        if not name or len(name) > MAX_TEXT:
            raise CodedDomainError(
                "EMPLOYEE_NAME_INVALID", "نام کارمند الزامی است و حداکثر ۱۲۰ نویسه است."
            )
        employee.name = name
    if role_label is not None:
        role_label = role_label.strip()
        if not role_label or len(role_label) > 60:
            raise CodedDomainError(
                "EMPLOYEE_ROLE_INVALID", "عنوان شغلی الزامی است و حداکثر ۶۰ نویسه است."
            )
        employee.role_label = role_label
    if start_date is not None:
        if len(start_date) != 10 or not start_date[:4].isdigit() or start_date[4] != "-":
            raise CodedDomainError(
                "EMPLOYEE_START_DATE_INVALID", "تاریخ شروع باید به شکل میلادی 2024-03-20 باشد."
            )
        employee.start_date = start_date
    await db.flush()
    return employee


# ------------------------------------------------------------- observations --


async def list_observations(
    db: AsyncSession, tenant_id: uuid.UUID, employee_id: uuid.UUID
) -> list[EmployeeObservation]:
    await load_employee(db, tenant_id, employee_id)
    result = await db.execute(
        select(EmployeeObservation)
        .where(
            EmployeeObservation.tenant_id == tenant_id,
            EmployeeObservation.employee_id == employee_id,
        )
        .order_by(EmployeeObservation.created_at, EmployeeObservation.id)
    )
    return list(result.scalars())


async def add_observation(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    employee_id: uuid.UUID,
    *,
    metric_code: str,
    period: str,
    raw_value: str,
    source: str = "manual",
) -> EmployeeObservation:
    """Record one observation; the raw value is validated against perf-v1."""
    await load_employee(db, tenant_id, employee_id)
    canonical = validate_observation_value(metric_code, raw_value)
    period = period.strip()
    if not period or len(period) > 40:
        raise CodedDomainError(
            "OBSERVATION_PERIOD_INVALID", "دورهٔ ارزیابی الزامی است و حداکثر ۴۰ نویسه است."
        )
    observation = EmployeeObservation(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        employee_id=employee_id,
        metric_code=metric_code,
        period=period,
        raw_value=canonical,
        state="valid",
        source=source,
    )
    db.add(observation)
    await db.flush()
    return observation


async def correct_observation(
    db: AsyncSession, tenant_id: uuid.UUID, observation_id: uuid.UUID, raw_value: str
) -> EmployeeObservation:
    """Correct one non-rejected observation; the correction is recorded as a state."""
    observation = (
        await db.execute(
            select(EmployeeObservation).where(
                EmployeeObservation.tenant_id == tenant_id,
                EmployeeObservation.id == observation_id,
            )
        )
    ).scalar_one_or_none()
    if observation is None:
        raise CodedDomainError("OBSERVATION_NOT_FOUND", "این مشاهده یافت نشد.")
    if observation.state == "rejected":
        raise CodedDomainError(
            "OBSERVATION_REJECTED", "مشاهدهٔ ردشده را نمی‌توان اصلاح کرد؛ یک مشاهدهٔ تازه ثبت کنید."
        )
    observation.raw_value = validate_observation_value(observation.metric_code, raw_value)
    observation.state = "corrected"
    await db.flush()
    return observation


async def reject_observation(
    db: AsyncSession, tenant_id: uuid.UUID, observation_id: uuid.UUID
) -> EmployeeObservation:
    """Reject one observation; rejected rows are excluded from scoring (AC-04)."""
    observation = (
        await db.execute(
            select(EmployeeObservation).where(
                EmployeeObservation.tenant_id == tenant_id,
                EmployeeObservation.id == observation_id,
            )
        )
    ).scalar_one_or_none()
    if observation is None:
        raise CodedDomainError("OBSERVATION_NOT_FOUND", "این مشاهده یافت نشد.")
    observation.state = "rejected"
    await db.flush()
    return observation


# ---------------------------------------------------------------- evidence --


async def add_evidence(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    employee_id: uuid.UUID,
    *,
    created_by: uuid.UUID,
    file_name: str,
    content_type: str,
    content: bytes,
    note: str | None,
) -> EmployeeEvidence:
    """Store one evidence file with its SHA-256 integrity digest."""
    await load_employee(db, tenant_id, employee_id)
    if not content:
        raise CodedDomainError("EVIDENCE_EMPTY", "فایل خالی است.")
    if len(content) > 5_000_000:
        raise CodedDomainError("EVIDENCE_TOO_LARGE", "حجم فایل باید کمتر از ۵ مگابایت باشد.")
    file_name = file_name.strip() or "evidence"
    if len(file_name) > 255:
        raise CodedDomainError("EVIDENCE_NAME_INVALID", "نام فایل بیش از حد مجاز است.")
    evidence = EmployeeEvidence(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        employee_id=employee_id,
        file_name=file_name,
        content_type=content_type or "application/octet-stream",
        byte_size=len(content),
        sha256=hashlib.sha256(content).hexdigest(),
        note=(note or None),
        content=content,
        created_by=created_by,
    )
    db.add(evidence)
    await db.flush()
    return evidence


async def list_evidence(
    db: AsyncSession, tenant_id: uuid.UUID, employee_id: uuid.UUID
) -> list[EmployeeEvidence]:
    """Return evidence metadata ordered oldest first (content excluded)."""
    await load_employee(db, tenant_id, employee_id)
    result = await db.execute(
        select(EmployeeEvidence)
        .where(
            EmployeeEvidence.tenant_id == tenant_id,
            EmployeeEvidence.employee_id == employee_id,
        )
        .order_by(EmployeeEvidence.created_at, EmployeeEvidence.id)
    )
    return list(result.scalars())


# -------------------------------------------------------------- evaluation --


async def evaluate_employee(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    employee_id: uuid.UUID,
    created_by: uuid.UUID,
) -> EmployeeEvaluation:
    """Score the employee's latest non-rejected observations (AC-04…AC-08)."""
    employee = await load_employee(db, tenant_id, employee_id)
    observations = await list_observations(db, tenant_id, employee_id)

    latest: dict[str, EmployeeObservation] = {}
    for observation in observations:
        if observation.state == "rejected":
            continue
        latest[observation.metric_code] = observation
    if not latest:
        raise CodedDomainError(
            "EVALUATION_NO_DATA",
            "برای این کارمند هیچ مشاهدهٔ معتبری ثبت نشده است؛ ابتدا دست‌کم یک معیار را وارد کنید.",
        )

    inputs = [
        ScoreInput(
            code=observation.metric_code,
            raw=observation.raw_value,
            observation_id=str(observation.id),
            period=observation.period,
        )
        for observation in latest.values()
    ]
    score = score_observations(inputs)

    evaluation = EmployeeEvaluation(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        employee_id=employee_id,
        rule_set_version=score.rule_set_version,
        rule_set_status=score.rule_set_status,
        score_100=score.score_100,
        total_bp=score.total_bp,
        contributions=[c.as_payload() for c in score.contributions],
        observations_used=list(score.observations_used),
        missing_criteria=list(score.missing_criteria),
        missing_policy_fa=score.missing_policy_fa,
        calculation_hash=score.calculation_hash,
        created_by=created_by,
    )
    db.add(evaluation)
    await db.flush()
    del employee
    return evaluation


# ----------------------------------------------------------- recommendation --


def _build_explanation(
    *,
    score_100: int,
    current: int | None,
    missing_criteria: list[str],
    observations_used_count: int,
) -> dict[str, Any]:
    """Assemble reasons, warnings and data-quality limitations."""
    reasons = [
        f"امتیاز ارزیابی {score_100} از ۱۰۰ بر مبنای {observations_used_count} مشاهدهٔ معتبر محاسبه شد.",
        "مبلغ پیشنهادی در نقطهٔ متناظرِ امتیاز داخل بازهٔ تعیین‌شده توسط مدیر قرار می‌گیرد.",
    ]
    warnings = [
        "وزن‌های مدل ارزیابی perf-v1 پیش‌نویس و تأییدنشده‌اند (۴۰/۳۰/۲۰/۱۰ نمونه است، نه قاعدهٔ مصوب).",
        "مبالغ قانونی (مالیات، بیمه، هزینهٔ کارفرما) با موتور نسخهٔ "
        f"{ENGINE_VERSION} در وضعیت READY_FOR_REVIEW محاسبه شده‌اند؛ نتایج قطعی و مصوب نیستند.",
    ]
    data_quality: list[str] = []
    if missing_criteria:
        data_quality.append(
            "معیارهای زیر ثبت نشده‌اند و صفر امتیاز گرفته‌اند: " + "، ".join(missing_criteria)
        )
    if current is None:
        data_quality.append("حقوق فعلی کارمند ارائه نشده است؛ اختلاف محاسبه نشد.")
    return {
        "reasons": reasons,
        "warnings": warnings,
        "dataQuality": data_quality,
        "advisory": True,
        "statutoryStatus": "provisional_engine_ready_for_review",
    }


async def create_recommendation(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    employee_id: uuid.UUID,
    *,
    created_by: uuid.UUID,
    band_min_rial: int,
    band_max_rial: int,
    band_current_rial: int | None,
) -> SalaryRecommendation:
    """Score, position in the band, cost by the statutory engine and persist."""
    employee = await load_employee(db, tenant_id, employee_id)

    _require_tenant_digits(band_min_rial, "EVALUATION_BAND_REQUIRED", "حداقل بازهٔ حقوق الزامی است.")
    _require_tenant_digits(
        band_max_rial, "EVALUATION_BAND_REQUIRED", "حداکثر بازهٔ حقوق الزامی است."
    )
    if band_max_rial <= band_min_rial:
        raise CodedDomainError(
            "EVALUATION_BAND_INVALID", "حداکثر بازه باید بزرگ‌تر از حداقل بازه باشد."
        )
    current: int | None = None
    if band_current_rial is not None:
        current = _require_tenant_digits(
            band_current_rial, "EVALUATION_CURRENT_INVALID", "حقوق فعلی نامعتبر است."
        )

    evaluation = await evaluate_employee(db, tenant_id, employee_id, created_by)
    score_bp = evaluation.total_bp
    width = band_max_rial - band_min_rial
    suggested = band_min_rial + (width * score_bp) // 10_000
    delta = None if current is None else suggested - current

    period = ""
    if evaluation.observations_used:
        period = str(evaluation.observations_used[-1].get("period", ""))

    try:
        costing = _statutory_cost_block(suggested)
    except PayrollEngineError as exc:
        raise CodedDomainError("STATUTORY_COSTING_UNAVAILABLE", str(exc)) from exc
    current_costing = None
    if current is not None:
        try:
            current_costing = _statutory_cost_block(current)
        except PayrollEngineError as exc:
            raise CodedDomainError("STATUTORY_COSTING_UNAVAILABLE", str(exc)) from exc

    explanation = _build_explanation(
        score_100=evaluation.score_100,
        current=current,
        missing_criteria=list(evaluation.missing_criteria),
        observations_used_count=len(evaluation.observations_used),
    )

    canonical_payload = {
        "employee_id": str(employee_id),
        "evaluation_id": str(evaluation.id),
        "rule_set_version": evaluation.rule_set_version,
        "score_100": evaluation.score_100,
        "band": [band_min_rial, band_max_rial],
        "current": current,
        "suggested": suggested,
        "costing_hash": costing["calculation_hash"],
    }
    recommendation = SalaryRecommendation(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        employee_id=employee_id,
        evaluation_id=evaluation.id,
        period=period,
        rule_set_version=evaluation.rule_set_version,
        engine_version=ENGINE_VERSION,
        score_100=evaluation.score_100,
        band_min_rial=band_min_rial,
        band_max_rial=band_max_rial,
        band_current_rial=current,
        band_position_bp=score_bp,
        suggested_gross_rial=suggested,
        delta_rial=delta,
        explanation=explanation,
        statutory_costing=costing,
        current_costing=current_costing,
        calculation_hash=_canonical_hash(canonical_payload),
        status="pending",
        created_by=created_by,
    )
    db.add(recommendation)
    await db.flush()
    del employee
    return recommendation


async def load_recommendation(
    db: AsyncSession, tenant_id: uuid.UUID, recommendation_id: uuid.UUID
) -> SalaryRecommendation:
    recommendation = (
        await db.execute(
            select(SalaryRecommendation).where(
                SalaryRecommendation.tenant_id == tenant_id,
                SalaryRecommendation.id == recommendation_id,
            )
        )
    ).scalar_one_or_none()
    if recommendation is None:
        raise CodedDomainError("RECOMMENDATION_NOT_FOUND", "این پیشنهاد یافت نشد.")
    return recommendation


def evaluation_rules_payload() -> dict[str, Any]:
    """The published ``perf-v1`` contract, exactly as the engine defines it.

    The frontend renders its entry form from this payload, so the weights,
    bounds and labels cannot drift from the engine that scores the values.
    ``ruleSetStatus`` states that the weights are a provisional draft.
    """
    return {
        "ruleSetVersion": RULE_SET_VERSION,
        "ruleSetStatus": RULE_SET_STATUS,
        "statusLabelFa": "پیش‌نویس تأییدنشده — وزن‌ها قاعدهٔ مصوب نیستند",
        "weightsSumBp": WEIGHTS_SUM_BP,
        "missingPolicyFa": MISSING_POLICY_FA,
        "criteria": [
            {
                "code": definition.code,
                "labelFa": definition.label_fa,
                "unitFa": definition.unit_fa,
                "weightBp": definition.weight_bp,
                "minRaw": definition.min_raw,
                "maxRaw": definition.max_raw,
                "guidanceFa": definition.guidance_fa,
            }
            for definition in CRITERIA
        ],
        "advisory": True,
    }


async def list_recommendations(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    *,
    employee_id: uuid.UUID | None = None,
    status: str | None = None,
    limit: int = 50,
) -> list[tuple[SalaryRecommendation, Employee, RecommendationDecision | None]]:
    """Recommendations of one tenant, newest first, with their decision.

    ``status`` is ``pending`` or ``decided``; ``None`` returns both.  The
    employee join carries the tenant predicate as well, so a cross-tenant row
    can never be returned even if a recommendation id were guessed.
    """
    query = (
        select(SalaryRecommendation, Employee, RecommendationDecision)
        .join(Employee, Employee.id == SalaryRecommendation.employee_id)
        .outerjoin(
            RecommendationDecision,
            RecommendationDecision.recommendation_id == SalaryRecommendation.id,
        )
        .where(
            SalaryRecommendation.tenant_id == tenant_id,
            Employee.tenant_id == tenant_id,
        )
        .order_by(SalaryRecommendation.created_at.desc(), SalaryRecommendation.id.desc())
        .limit(limit)
    )
    if employee_id is not None:
        query = query.where(SalaryRecommendation.employee_id == employee_id)
    if status is not None:
        query = query.where(SalaryRecommendation.status == status)
    result = await db.execute(query)
    return [(row[0], row[1], row[2]) for row in result.all()]


# --------------------------------------------------------------- decisions --


async def load_decision(
    db: AsyncSession, tenant_id: uuid.UUID, recommendation_id: uuid.UUID
) -> RecommendationDecision | None:
    """The recorded decision of one recommendation, or ``None`` while pending."""
    decision: RecommendationDecision | None = (
        await db.execute(
            select(RecommendationDecision).where(
                RecommendationDecision.tenant_id == tenant_id,
                RecommendationDecision.recommendation_id == recommendation_id,
            )
        )
    ).scalar_one_or_none()
    return decision


async def decide_recommendation(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    manager_user_id: uuid.UUID,
    recommendation_id: uuid.UUID,
    *,
    action: str,
    comment: str,
    edited_gross_rial: int | None,
) -> RecommendationDecision:
    """Record the one append-only decision for a pending recommendation."""
    recommendation = await load_recommendation(db, tenant_id, recommendation_id)
    existing = (
        await db.execute(
            select(RecommendationDecision).where(
                RecommendationDecision.recommendation_id == recommendation_id
            )
        )
    ).scalar_one_or_none()
    if existing is not None:
        raise CodedDomainError(
            "DECISION_ALREADY_RECORDED", "برای این پیشنهاد پیش‌تر تصمیم ثبت شده است."
        )

    comment = comment.strip()
    if len(comment) > 500:
        raise CodedDomainError("DECISION_COMMENT_INVALID", "توضیح تصمیم بیش از ۵۰۰ نویسه است.")
    if action == "reject" and not comment:
        raise CodedDomainError("DECISION_COMMENT_INVALID", "برای رد پیشنهاد، دلیل را بنویسید.")
    edited: int | None = None
    if action == "edit":
        if edited_gross_rial is None:
            raise CodedDomainError(
                "DECISION_EDIT_REQUIRED", "برای ویرایش، مبلغ ویرایش‌شده را وارد کنید."
            )
        edited = _require_tenant_digits(
            edited_gross_rial, "DECISION_EDIT_REQUIRED", "مبلغ ویرایش‌شده نامعتبر است."
        )
        if not comment:
            raise CodedDomainError(
                "DECISION_COMMENT_INVALID", "برای ویرایش مبلغ، دلیل ویرایش را بنویسید."
            )
    elif edited_gross_rial is not None and action != "edit":
        raise CodedDomainError(
            "DECISION_EDIT_NOT_ALLOWED", "مبلغ ویرایش‌شده فقط برای تصمیم ویرایش است."
        )
    if action not in ("approve", "edit", "reject"):
        raise CodedDomainError("DECISION_INVALID", "نوع تصمیم نامعتبر است.")

    decision = RecommendationDecision(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        recommendation_id=recommendation_id,
        action=action,
        edited_gross_rial=edited,
        comment=comment,
        decided_by=manager_user_id,
    )
    db.add(decision)
    recommendation.status = "decided"
    await db.flush()
    return decision


async def list_decisions(
    db: AsyncSession, tenant_id: uuid.UUID, limit: int = 50
) -> list[tuple[RecommendationDecision, SalaryRecommendation, Employee]]:
    """The decision history, newest first, joined to its recommendation."""
    result = await db.execute(
        select(RecommendationDecision, SalaryRecommendation, Employee)
        .join(
            SalaryRecommendation,
            SalaryRecommendation.id == RecommendationDecision.recommendation_id,
        )
        .join(Employee, Employee.id == SalaryRecommendation.employee_id)
        .where(RecommendationDecision.tenant_id == tenant_id)
        .order_by(RecommendationDecision.decided_at.desc())
        .limit(limit)
    )
    return [(row[0], row[1], row[2]) for row in result.all()]


# ---------------------------------------------------------------- dashboard --


async def dashboard_summary(db: AsyncSession, tenant_id: uuid.UUID) -> dict[str, Any]:
    """The manager dashboard counters and the recent decision history."""
    people_count = (
        await db.execute(
            select(func.count()).select_from(Employee).where(Employee.tenant_id == tenant_id)
        )
    ).scalar_one()

    valid_observations = (
        await db.execute(
            select(func.count())
            .select_from(EmployeeObservation)
            .where(
                EmployeeObservation.tenant_id == tenant_id,
                EmployeeObservation.state != "rejected",
            )
        )
    ).scalar_one()

    pending = (
        await db.execute(
            select(func.count())
            .select_from(SalaryRecommendation)
            .where(
                SalaryRecommendation.tenant_id == tenant_id,
                SalaryRecommendation.status == "pending",
            )
        )
    ).scalar_one()

    decided = (
        await db.execute(
            select(func.count())
            .select_from(RecommendationDecision)
            .where(RecommendationDecision.tenant_id == tenant_id)
        )
    ).scalar_one()

    recent_rows = await list_decisions(db, tenant_id, limit=5)
    recent = [
        {
            "id": str(decision.id),
            "recommendationId": str(decision.recommendation_id),
            "action": decision.action,
            "editedGrossRial": decision.edited_gross_rial,
            "comment": decision.comment,
            "decidedAt": decision.decided_at.isoformat(),
            "personName": employee.name,
            "score100": recommendation.score_100,
        }
        for decision, recommendation, employee in recent_rows
    ]
    return {
        "peopleCount": people_count,
        "validObservationCount": valid_observations,
        "pendingCount": pending,
        "decidedCount": decided,
        "recentDecisions": recent,
    }


__all__ = [
    "MAX_MONEY_RIAL",
    "EvaluationResult",
    "add_evidence",
    "add_observation",
    "correct_observation",
    "create_employee",
    "create_recommendation",
    "dashboard_summary",
    "decide_recommendation",
    "evaluate_employee",
    "evaluation_rules_payload",
    "list_decisions",
    "list_evidence",
    "list_observations",
    "list_recommendations",
    "load_decision",
    "load_employee",
    "load_recommendation",
    "reject_observation",
    "update_employee",
]
