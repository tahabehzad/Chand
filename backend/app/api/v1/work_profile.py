"""Authenticated work-profile persistence and real local document uploads.

Authority: ADR-012; WORK_PROFILE_PAYROLL.
Related: ManagerRequired/DbSession; encrypted work-profile service.
Scope: local prototype; no client-selected tenant/key or public file URLs.
"""

from __future__ import annotations

import uuid
from collections.abc import Awaitable
from typing import Annotated
from urllib.parse import quote

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DbSession, ManagerRequired
from app.core.security.pii_transformer import (
    PiiDecryptionError,
    PiiEncryptionError,
    PiiKeyUnavailableError,
)
from app.engines.errors import CodedDomainError, PayrollEngineError
from app.schemas.work_profile import WorkCalculationRequest, WorkProfileSaveRequest
from app.services import work_profile as service

router = APIRouter(prefix="/api/v1/manager/employees/{employee_id}", tags=["work-profile"])


async def _run[T](task: Awaitable[T], db: AsyncSession, *, commit: bool = False) -> T | JSONResponse:
    try:
        value = await task
        if commit:
            await db.commit()
        return value
    except (PiiKeyUnavailableError, PiiEncryptionError, PiiDecryptionError):
        await db.rollback()
        return JSONResponse(status_code=503, content={"error": {
            "code": "WORK_STORAGE_UNAVAILABLE", "detail": "کلید یا اطلاعات رمز‌شده در دسترس نیست.",
        }})
    except PayrollEngineError as exc:
        await db.rollback()
        message = str(exc)
        details = {
            "WORK_BASE_BELOW_MINIMUM": "مزد ثابت تمام‌وقت کمتر از حداقل مبنای فعال است.",
            "DOCUMENTED_SENIORITY_RATE_REQUIRED": "مبلغ روزانه پایه سنوات طبق حکم را وارد کنید.",
            "WORK_ORDINARY_HOURS_EXCEED_FULL_TIME": "کار عادی از سقف تمام‌وقت بیشتر است؛ اضافه‌کاری را جدا وارد کنید.",
            "SENIORITY_BELOW_CURRENT_INCREMENT": "پایه سنوات واردشده کمتر از پایه سال جاری است.",
        }
        if isinstance(exc, CodedDomainError):
            detail = message
        else:
            detail = details.get(message, "اطلاعات کارکرد یا سابقه کامل و معتبر نیست.")
        status = 404 if "NOT_FOUND" in exc.code else (409 if "ALREADY" in exc.code else 422)
        return JSONResponse(status_code=status,
                            content={"error": {"code": exc.code, "detail": detail}})


@router.get("/work-profile", response_model=None)
async def get_profile(employee_id: uuid.UUID, manager: ManagerRequired, db: DbSession) -> object:
    return await _run(service.get_profile(db, manager.tenant_id, employee_id), db)


@router.put("/work-profile", response_model=None)
async def put_profile(
    employee_id: uuid.UUID, payload: WorkProfileSaveRequest, manager: ManagerRequired, db: DbSession,
) -> object:
    return await _run(service.save_profile(db, manager.tenant_id, employee_id, payload.profile,
        actor=manager.user_id, expected_revision=payload.expected_revision), db, commit=True)


@router.post("/work-profile/calculate", response_model=None)
async def calculate(
    employee_id: uuid.UUID, payload: WorkCalculationRequest, manager: ManagerRequired, db: DbSession,
) -> object:
    return await _run(service.calculate_profile(db, manager.tenant_id, employee_id, payload.payroll,
                                               manager.user_id),
                      db, commit=True)


@router.get("/work-profile/calculations/latest", response_model=None)
async def latest(employee_id: uuid.UUID, manager: ManagerRequired, db: DbSession) -> object:
    return await _run(service.latest_calculation(db, manager.tenant_id, employee_id), db)


@router.get("/work-documents", response_model=None)
async def documents(employee_id: uuid.UUID, manager: ManagerRequired, db: DbSession) -> object:
    return await _run(service.list_documents(db, manager.tenant_id, employee_id), db)


@router.post("/work-documents", status_code=201, response_model=None)
async def upload(
    employee_id: uuid.UUID, manager: ManagerRequired, db: DbSession,
    file: Annotated[UploadFile, File()],
) -> object:
    content = bytearray()
    try:
        while chunk := await file.read(65536):
            if len(content) + len(chunk) > service.MAX_DOCUMENT_BYTES:
                raise CodedDomainError("WORK_DOCUMENT_TOO_LARGE", "حداکثر حجم فایل پنج مگابایت است.")
            content.extend(chunk)
        return await _run(service.add_document(
            db, manager.tenant_id, employee_id, filename=file.filename or "document",
            declared_type=file.content_type or "application/octet-stream", content=bytes(content),
            actor=manager.user_id,
        ), db, commit=True)
    finally:
        await file.close()


@router.get("/work-documents/{document_id}/content", response_model=None)
async def download(
    employee_id: uuid.UUID, document_id: uuid.UUID, manager: ManagerRequired, db: DbSession,
) -> Response:
    result = await _run(service.download_document(db, manager.tenant_id, employee_id, document_id), db)
    if isinstance(result, JSONResponse):
        return result
    raw, metadata = result
    return Response(content=raw, media_type=metadata["contentType"], headers={
        "Content-Disposition": "attachment; filename*=UTF-8''" + quote(metadata["fileName"], safe=""),
        "X-Content-Type-Options": "nosniff", "Cache-Control": "no-store",
        "Content-Security-Policy": "sandbox",
    })
