"""P0-T03 local TLS/material evidence, independent of Docker availability."""

from __future__ import annotations

import hashlib
import importlib.util
import os
import ssl
import subprocess
from datetime import datetime, timedelta, tzinfo
from pathlib import Path
from types import ModuleType

import pytest


@pytest.fixture(scope="module")
def material_module() -> ModuleType:
    source = Path(__file__).resolve().parents[3] / "infra" / "postgres" / "local_material.py"
    specification = importlib.util.spec_from_file_location("pish_postgres_material", source)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def verifier_module() -> ModuleType:
    source = Path(__file__).resolve().parents[3] / "infra" / "postgres" / "verify_local.py"
    specification = importlib.util.spec_from_file_location("pish_postgres_verifier", source)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def _fingerprints(directory: Path) -> dict[str, bytes]:
    # Assertions never render private file contents, even on failure.
    return {path.name: hashlib.sha256(path.read_bytes()).digest() for path in directory.iterdir()}


def _handshake(directory: Path, hostname: str = "localhost") -> str | None:
    server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    server_context.minimum_version = ssl.TLSVersion.TLSv1_3
    server_context.load_cert_chain(directory / "server.crt", directory / "server.key")
    client_context = ssl.create_default_context(cafile=str(directory / "ca.crt"))
    client_context.minimum_version = ssl.TLSVersion.TLSv1_3
    client_context.verify_flags |= ssl.VERIFY_X509_STRICT
    client_in, client_out = ssl.MemoryBIO(), ssl.MemoryBIO()
    server_in, server_out = ssl.MemoryBIO(), ssl.MemoryBIO()
    client = client_context.wrap_bio(client_in, client_out, server_hostname=hostname)
    server = server_context.wrap_bio(server_in, server_out, server_side=True)
    client_ready = server_ready = False
    for _ in range(20):
        try:
            client.do_handshake()
            client_ready = True
        except ssl.SSLWantReadError:
            pass
        if client_out.pending:
            server_in.write(client_out.read())
        try:
            server.do_handshake()
            server_ready = True
        except ssl.SSLWantReadError:
            pass
        if server_out.pending:
            client_in.write(server_out.read())
        if client_ready and server_ready:
            return client.version()
    raise AssertionError("TLS handshake did not complete")


def test_complete_material_is_private_and_repeat_does_not_rotate(
    material_module: ModuleType, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    directory = tmp_path / "postgres"
    assert material_module.prepare_material(directory) == "created"
    assert {path.name for path in directory.iterdir()} == material_module.EXPECTED_FILES
    before = _fingerprints(directory)
    assert material_module.prepare_material(directory) == "validated"
    assert before == _fingerprints(directory)
    captured = capsys.readouterr()
    assert not captured.out and not captured.err


def test_tls13_with_strict_ca_and_hostname_verification(
    material_module: ModuleType, tmp_path: Path
) -> None:
    directory = tmp_path / "postgres"
    material_module.prepare_material(directory)
    assert _handshake(directory) == "TLSv1.3"
    with pytest.raises(ssl.SSLCertVerificationError):
        _handshake(directory, "untrusted.test")


def test_partial_material_is_rejected_without_overwrite(
    material_module: ModuleType, tmp_path: Path
) -> None:
    directory = tmp_path / "postgres"
    directory.mkdir()
    (directory / "password").write_text("synthetic-incomplete", encoding="ascii")
    before = _fingerprints(directory)
    with pytest.raises(material_module.LocalMaterialError):
        material_module.prepare_material(directory)
    assert before == _fingerprints(directory)


def test_expired_material_is_rejected_without_rotation(
    material_module: ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    directory = tmp_path / "postgres"
    material_module.prepare_material(directory)
    before = _fingerprints(directory)

    class FutureClock:
        @staticmethod
        def now(tz: tzinfo | None = None) -> datetime:
            return datetime.now(tz) + timedelta(days=40)

    monkeypatch.setattr(material_module, "datetime", FutureClock)
    with pytest.raises(material_module.LocalMaterialError):
        material_module.prepare_material(directory)
    assert before == _fingerprints(directory)


def test_mismatched_server_key_is_rejected(material_module: ModuleType, tmp_path: Path) -> None:
    first, second = tmp_path / "first", tmp_path / "second"
    material_module.prepare_material(first)
    material_module.prepare_material(second)
    (first / "server.key").write_bytes((second / "server.key").read_bytes())
    with pytest.raises(material_module.LocalMaterialError):
        material_module.prepare_material(first)


def test_secret_directory_has_only_private_access(
    material_module: ModuleType, tmp_path: Path
) -> None:
    directory = tmp_path / "postgres"
    material_module.prepare_material(directory)
    if os.name != "nt":
        assert directory.stat().st_mode & 0o077 == 0
        assert all(path.stat().st_mode & 0o077 == 0 for path in directory.iterdir())
        return
    # Inspect the actual ACL independently of the setup routine. Output is
    # a status code only, never an identity name, password or key content.
    script = r"""
$ErrorActionPreference='Stop'
$allowed=@([System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value,'S-1-5-18')
$dir=[System.IO.DirectoryInfo]::new($env:PISH_LOCAL_SECRET_DIR)
$objects=@($dir)+@($dir.EnumerateFiles())
foreach($item in $objects) {
 $acl=$item.GetAccessControl()
 if(-not $acl.AreAccessRulesProtected) {exit 1}
 foreach($rule in $acl.GetAccessRules($true,$true,[System.Security.Principal.SecurityIdentifier])) {
  if($rule.AccessControlType -ne 'Allow' -or $rule.IdentityReference.Value -notin $allowed) {exit 2}
 }
}
"""
    environment = os.environ.copy()
    environment["PISH_LOCAL_SECRET_DIR"] = str(directory)
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
        check=False,
        env=environment,
        capture_output=True,
        timeout=20,
    )
    assert result.returncode == 0


def test_audit_verifier_rejects_history_and_requires_current_commands(
    verifier_module: ModuleType,
) -> None:
    current = "pish_probe_current"
    events = [
        f"AUDIT: SESSION,1,1,DDL,CREATE TABLE,TABLE,pg_temp_3.{current},,<not logged>",
        f"AUDIT: SESSION,2,1,WRITE,INSERT,TABLE,pg_temp_3.{current},,<not logged>",
        f"AUDIT: SESSION,3,1,READ,SELECT,TABLE,pg_temp_3.{current},,<not logged>",
    ]
    arguments = {
        "table": current,
        "marker": "synthetic-private-payload",
        "password": "synthetic-password",
    }
    assert verifier_module.audit_probe_passed("\n".join(events), **arguments)
    assert not verifier_module.audit_probe_passed("\n".join(events[:2]), **arguments)
    assert not verifier_module.audit_probe_passed(
        "\n".join(events).replace(current, "old_probe"), **arguments
    )
    assert not verifier_module.audit_probe_passed(
        "\n".join(events) + "synthetic-private-payload", **arguments
    )
    assert not verifier_module.audit_probe_passed(
        "\n".join(events) + "synthetic-password", **arguments
    )
