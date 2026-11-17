"""Local key fail-closed contract and upload-body limits (ADR-012).

Authority: WORK_PROFILE_PAYROLL and independent security findings.
Related: PiiFieldTransformer; local-only key adapter and setup script.
Scope: synthetic keys, temporary files, no live database or real documents.
"""

from __future__ import annotations

import asyncio
import hashlib
import uuid
from pathlib import Path
from types import SimpleNamespace

import pytest
from scripts import work_profile_setup

from app.core.security import local_workspace
from app.core.security.pii_transformer import PiiKeyUnavailableError
from app.core.security.upload_limit import MAX_UPLOAD_REQUEST, WorkUploadLimit


def test_registry_requires_ready_marker_and_isolates_tenants(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "master.key"
    monkeypatch.setattr(local_workspace, "KEY_PATH", path)
    monkeypatch.setattr(local_workspace, "get_settings", lambda: SimpleNamespace(app_env="local"))
    registry = local_workspace.LocalWorkspaceKeyRegistry()
    tenant = uuid.uuid4()
    with pytest.raises(PiiKeyUnavailableError):
        registry.get_key(tenant_id=tenant, key_id=local_workspace.KEY_ID)
    path.write_bytes(b"k" * 32)
    with pytest.raises(PiiKeyUnavailableError):
        registry.get_key(tenant_id=tenant, key_id=local_workspace.KEY_ID)
    path.with_suffix(".ready").write_text(hashlib.sha256(path.read_bytes()).hexdigest(), encoding="ascii")
    first = registry.get_key(tenant_id=tenant, key_id=local_workspace.KEY_ID)
    assert len(first) == 32
    assert first != registry.get_key(tenant_id=uuid.uuid4(), key_id=local_workspace.KEY_ID)
    with pytest.raises(PiiKeyUnavailableError):
        registry.get_key(tenant_id=tenant, key_id="unknown")
    monkeypatch.setattr(local_workspace, "get_settings", lambda: SimpleNamespace(app_env="production"))
    with pytest.raises(PiiKeyUnavailableError):
        registry.get_key(tenant_id=tenant, key_id=local_workspace.KEY_ID)


def test_missing_master_with_existing_ciphertext_is_not_regenerated(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "master.key"
    monkeypatch.setattr(work_profile_setup, "KEY_PATH", path)
    monkeypatch.setattr(work_profile_setup, "get_settings", lambda: SimpleNamespace(app_env="local"))
    async def existing() -> bool:
        return True
    monkeypatch.setattr(work_profile_setup, "encrypted_rows_exist", existing)
    with pytest.raises(RuntimeError, match="restore"):
        work_profile_setup.provision()
    assert not path.exists()


def test_chunked_upload_is_rejected_before_application_parsing() -> None:
    called: list[bool] = []
    sent: list[dict[str, object]] = []
    async def application(scope: object, receive: object, send: object) -> None:
        called.append(True)
    chunks = iter([b"x" * 65536] * (MAX_UPLOAD_REQUEST // 65536 + 2))
    async def receive() -> dict[str, object]:
        return {"type": "http.request", "body": next(chunks), "more_body": True}
    async def send(message: dict[str, object]) -> None:
        sent.append(message)
    asyncio.run(WorkUploadLimit(application)(  # type: ignore[arg-type]
        {"type": "http", "method": "POST", "path": "/api/v1/manager/employees/demo/work-documents"},
        receive, send,  # type: ignore[arg-type]
    ))
    assert not called
    assert sent[0]["status"] == 413
