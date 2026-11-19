"""Persist encrypted work profiles, documents and reproducible payroll snapshots.

Authority: ADR-012; WORK_PROFILE_PAYROLL; AGENTS §2 financial/security invariants.
Related: manager employee ownership, work_schedule and existing payroll service.
Scope: orchestration; new personal text/bytes never persist as plaintext.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import re
import uuid
from dataclasses import asdict
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.local_workspace import KEY_ID, context, transformer
from app.engines.bases import Allowances
from app.engines.errors import CodedDomainError
from app.engines.rules import load_rule_set
from app.engines.work_schedule import WorkSchedule, prepare_work_pay
from app.models.manager import Employee
from app.models.work_profile import WorkCalculation, WorkDocument, WorkProfile
from app.schemas.payroll import GrossToNetRequest
from app.schemas.work_profile import WorkProfileRequest
from app.services.manager_service import load_employee
from app.services.payroll_service import PayrollInput, compute_gross_to_net

MAX_DOCUMENT_BYTES = 5_000_000


def _json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _seal(value: object, tenant: uuid.UUID, record: uuid.UUID, field: str) -> bytes:
    return transformer().encrypt_text(_json(value), context=context(tenant, record, field))


def _open(blob: bytes, tenant: uuid.UUID, record: uuid.UUID, field: str, key_id: str) -> Any:
    return json.loads(transformer().decrypt_text(blob, context=context(tenant, record, field, key_id)))


async def _profile(db: AsyncSession, tenant: uuid.UUID, employee: uuid.UUID) -> WorkProfile | None:
    await load_employee(db, tenant, employee)
    return (await db.execute(select(WorkProfile).where(
        WorkProfile.tenant_id == tenant, WorkProfile.employee_id == employee,
    ))).scalar_one_or_none()


async def get_profile(
    db: AsyncSession, tenant: uuid.UUID, employee: uuid.UUID,
) -> dict[str, Any] | None:
    row = await _profile(db, tenant, employee)
    if row is None:
        return None
    return {"profile": _open(row.ciphertext, tenant, row.id, "work-profile", row.key_id), "revision": row.revision}


async def save_profile(
    db: AsyncSession, tenant: uuid.UUID, employee: uuid.UUID, profile: WorkProfileRequest,
    *, actor: uuid.UUID, expected_revision: int,
) -> dict[str, Any]:
    await db.execute(select(Employee.id).where(Employee.id == employee, Employee.tenant_id == tenant)
                     .with_for_update())
    row = await _profile(db, tenant, employee)
    if expected_revision != (0 if row is None else row.revision):
        raise CodedDomainError("WORK_PROFILE_ALREADY_CHANGED", "پرونده در زبانه دیگری تغییر کرده؛ دوباره دریافت کنید.")
    if row is not None:
        _open(row.ciphertext, tenant, row.id, "work-profile", row.key_id)
    if row is None:
        row = WorkProfile(id=uuid.uuid4(), tenant_id=tenant, employee_id=employee, revision=0)
        db.add(row)
    row.ciphertext = _seal(profile.model_dump(), tenant, row.id, "work-profile")
    row.key_id = KEY_ID
    row.actor_id = actor
    row.updated_at = datetime.datetime.now(datetime.UTC)
    row.revision += 1
    await db.flush()
    return {"profile": profile.model_dump(), "revision": row.revision}


def detect_document_type(content: bytes) -> str:
    if content.startswith(b"%PDF-"):
        return "application/pdf"
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if content.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    raise CodedDomainError("WORK_DOCUMENT_TYPE_INVALID", "فقط فایل PDF، JPG یا PNG پذیرفته می‌شود.")


async def add_document(
    db: AsyncSession, tenant: uuid.UUID, employee: uuid.UUID, *,
    filename: str, declared_type: str, content: bytes,
    actor: uuid.UUID,
) -> dict[str, Any]:
    await load_employee(db, tenant, employee)
    if not content or len(content) > MAX_DOCUMENT_BYTES:
        raise CodedDomainError("WORK_DOCUMENT_SIZE_INVALID", "فایل باید غیرخالی و حداکثر پنج مگابایت باشد.")
    detected = detect_document_type(content)
    if declared_type not in {detected, "application/octet-stream"}:
        raise CodedDomainError("WORK_DOCUMENT_TYPE_MISMATCH", "نوع فایل با محتوای آن مطابقت ندارد.")
    filename = re.split(r"[/\\]", filename)[-1].strip()
    if not filename or len(filename) > 200 or any(ord(char) < 32 for char in filename):
        raise CodedDomainError("WORK_DOCUMENT_NAME_INVALID", "نام فایل نامعتبر است.")
    record = uuid.uuid4()
    metadata = {"id": str(record), "fileName": filename, "contentType": detected,
                "byteSize": len(content), "sha256": hashlib.sha256(content).hexdigest()}
    row = WorkDocument(
        id=record, tenant_id=tenant, employee_id=employee, key_id=KEY_ID,
        actor_id=actor,
        ciphertext=transformer().encrypt(content, context=context(tenant, record, "work-document")),
        metadata_ciphertext=_seal(metadata, tenant, record, "work-document-metadata"),
    )
    db.add(row)
    await db.flush()
    return metadata


async def list_documents(
    db: AsyncSession, tenant: uuid.UUID, employee: uuid.UUID,
) -> list[dict[str, Any]]:
    await load_employee(db, tenant, employee)
    rows = (await db.execute(select(WorkDocument).where(
        WorkDocument.tenant_id == tenant, WorkDocument.employee_id == employee,
    ).order_by(WorkDocument.created_at, WorkDocument.id))).scalars()
    return [_open(row.metadata_ciphertext, tenant, row.id, "work-document-metadata", row.key_id) for row in rows]


async def download_document(
    db: AsyncSession, tenant: uuid.UUID, employee: uuid.UUID, record: uuid.UUID,
) -> tuple[bytes, dict[str, Any]]:
    await load_employee(db, tenant, employee)
    row = (await db.execute(select(WorkDocument).where(
        WorkDocument.id == record, WorkDocument.tenant_id == tenant,
        WorkDocument.employee_id == employee,
    ))).scalar_one_or_none()
    if row is None:
        raise CodedDomainError("WORK_DOCUMENT_NOT_FOUND", "مدرک یافت نشد.")
    raw = transformer().decrypt(row.ciphertext, context=context(tenant, row.id, "work-document", row.key_id))
    metadata = _open(row.metadata_ciphertext, tenant, row.id, "work-document-metadata", row.key_id)
    if hashlib.sha256(raw).hexdigest() != metadata["sha256"]:
        raise CodedDomainError("WORK_DOCUMENT_INTEGRITY_INVALID", "صحت مدرک تأیید نشد.")
    return raw, metadata


async def calculate_profile(
    db: AsyncSession, tenant: uuid.UUID, employee: uuid.UUID, data: GrossToNetRequest,
    actor: uuid.UUID,
) -> dict[str, Any]:
    saved = await get_profile(db, tenant, employee)
    if saved is None:
        raise CodedDomainError("WORK_PROFILE_NOT_FOUND", "ابتدا شرایط همکاری را ذخیره کنید.")
    profile = WorkProfileRequest.model_validate(saved["profile"])
    if data.probation_months is not None or data.probation_days_worked is not None:
        raise CodedDomainError("WORK_PROBATION_UNSUPPORTED", "این مسیر فقط پایان همکاری عادی را محاسبه می‌کند.")
    if profile.daily_hours is None:
        raise CodedDomainError("WORK_HOURS_REQUIRED", "ساعات کار را تکمیل کنید.")
    rules = load_rule_set(data.rule_year)
    allowances = Allowances(
        housing_rial=data.allowances.housing, grocery_rial=data.allowances.grocery,
        marriage_rial=data.allowances.marriage, child_rial=data.allowances.child,
        continuous_attraction_rial=data.allowances.continuous_attraction,
    )
    prepared = prepare_work_pay(data.gross_monthly_rial, allowances, WorkSchedule(
        daily_hours=profile.daily_hours, period=profile.schedule_period,
        weekly_days=profile.weekly_days, monthly_paid_days=profile.monthly_paid_days,
        recognised_seniority_months=profile.recognised_seniority_months,
        employer_tenure_months=profile.employer_tenure_months, workshop_type=profile.workshop_type,
        documented_daily_seniority_rial=profile.documented_daily_seniority_rial,
    ), rules, data.days_in_month)
    payroll = compute_gross_to_net(PayrollInput(
        gross_monthly_rial=prepared.gross_rial, rule_year=data.rule_year,
        days_in_month=data.days_in_month, tax_posture=data.tax_posture,
        allowances=prepared.allowances, overtime_hours=data.overtime_hours,
        night_hours=data.night_hours, continuous_attraction_taxable=data.continuous_attraction_taxable,
        tenure_months=profile.employer_tenure_months,
        termination_scenario=("ordinary_termination" if profile.employer_tenure_months is not None else None),
        accumulated_unused_leave_days=data.accumulated_unused_leave_days,
        employment_ratio=Decimal(prepared.ratio), premium_base_rial=prepared.premium_base_rial,
    ))
    payroll.payload["generated_at"] = datetime.datetime.now(datetime.UTC).isoformat()
    payroll.payload["calculation_hash"] = payroll.calculation_hash
    work_context = asdict(prepared)
    work_context["allowances"] = asdict(prepared.allowances)
    work_context["provenance"] = {
        field: {"rule_id": rule, "rule_version": rules.statutory_version,
                "formula_ref": formula, "rule_set_status": rules.rule_set_status}
        for field, rule, formula in [
            ("gross_rial", "LABOUR_LAW_ART_39", "sum(rounded prepared fixed, welfare, seniority lines)"),
            ("fixed_wage_rial", "LABOUR_LAW_ART_39", "full-time fixed wage x employment ratio"),
            ("seniority_rial", "WAGE_CIRCULAR_S1", "daily seniority x calendar days x employment ratio"),
            ("seniority_daily_rial", prepared.seniority_source, "active annual increment or documented rate"),
            ("premium_base_rial", "LABOUR_LAW_ART_51_58_59", "full-time fixed wage + full-time monthly seniority"),
            ("rounding_residual_rial", "EXECUTION_PLAN_11_1_2", "sum(rounded lines) - round(sum(exact lines))"),
            *[("allowances." + name, "LABOUR_LAW_ART_39", "full-time allowance x employment ratio")
              for name in asdict(prepared.allowances)],
        ]
    }
    envelope: dict[str, Any] = {
        "payroll": payroll.payload, "work_context": work_context,
        "profile_revision": saved["revision"], "profile": saved["profile"],
        "full_time_inputs": data.model_dump(), "preparation_version": "work-profile-v1",
    }
    # The distinct work hash binds original contract/profile as well as engine output.
    envelope["work_calculation_hash"] = hashlib.sha256(_json({
        "profile": saved, "inputs": data.model_dump(), "prepared": work_context,
        "payroll_hash": payroll.calculation_hash, "version": "work-profile-v1",
    }).encode()).hexdigest()
    record = uuid.uuid4()
    db.add(WorkCalculation(
        id=record, tenant_id=tenant, employee_id=employee, key_id=KEY_ID,
        actor_id=actor,
        ciphertext=_seal(envelope, tenant, record, "work-calculation"),
        calculation_hash=envelope["work_calculation_hash"],
    ))
    await db.flush()
    return envelope


async def latest_calculation(
    db: AsyncSession, tenant: uuid.UUID, employee: uuid.UUID,
) -> dict[str, Any] | None:
    await load_employee(db, tenant, employee)
    row = (await db.execute(select(WorkCalculation).where(
        WorkCalculation.tenant_id == tenant, WorkCalculation.employee_id == employee,
    ).order_by(WorkCalculation.created_at.desc(), WorkCalculation.id.desc()).limit(1))).scalar_one_or_none()
    return None if row is None else _open(row.ciphertext, tenant, row.id, "work-calculation", row.key_id)
