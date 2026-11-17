"""Provision only local workspace keys and report migration state (ADR-012).

No key, DSN or personal data is printed. Existing keys are never replaced.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import os
import secrets
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, ".")

from sqlalchemy import text

from app.core.config import get_settings
from app.core.security.local_workspace import KEY_PATH
from app.db import build_engine


async def status() -> None:
    engine = build_engine()
    try:
        async with engine.connect() as connection:
            rows = (await connection.execute(text("SELECT version_num FROM alembic_version"))).scalars()
            print("local_revision:", ",".join(rows))
    finally:
        await engine.dispose()


async def encrypted_rows_exist() -> bool:
    """Missing master must never be silently replaced while ciphertext exists."""
    engine = build_engine()
    try:
        async with engine.connect() as connection:
            for table in ("employee_work_profiles", "employee_work_documents", "employee_work_calculations"):
                exists = (await connection.execute(text("SELECT to_regclass(:name)"), {"name": table})).scalar()
                query = {"employee_work_profiles": "SELECT EXISTS (SELECT 1 FROM employee_work_profiles)",
                         "employee_work_documents": "SELECT EXISTS (SELECT 1 FROM employee_work_documents)",
                         "employee_work_calculations": "SELECT EXISTS (SELECT 1 FROM employee_work_calculations)"}[table]
                if exists and (await connection.execute(text(query))).scalar():
                    return True
        return False
    finally:
        await engine.dispose()


def provision() -> None:
    if get_settings().app_env != "local":
        raise RuntimeError("Local key provisioning refused outside local environment.")
    KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
    created = False
    if KEY_PATH.exists():
        if KEY_PATH.is_symlink() or len(KEY_PATH.read_bytes()) != 32:
            raise RuntimeError("Existing workspace key is invalid; refusing to replace it.")
    else:
        if asyncio.run(encrypted_rows_exist()):
            raise RuntimeError("Encrypted records exist; restore the original workspace key.")
        descriptor = os.open(KEY_PATH, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        os.close(descriptor)
        created = True
    # A failed/retried ACL setup must never leave a usable readiness marker.
    ready = KEY_PATH.with_suffix(".ready")
    ready.write_text("pending", encoding="ascii")
    if os.name == "nt":
        user = os.environ.get("USERDOMAIN", "") + "\\" + os.environ["USERNAME"]
        executable = str(Path(os.environ["SYSTEMROOT"]) / "System32" / "icacls.exe")
        result = subprocess.run(  # noqa: S603 — trusted Windows ACL utility, no shell
            [executable, str(KEY_PATH), "/inheritance:r", "/grant:r", user + ":F"],
            capture_output=True, check=False,
        )
        if result.returncode != 0:
            raise RuntimeError("Workspace key ACL setup failed; stop local storage.")
    else:
        KEY_PATH.chmod(0o600)
    if created:
        # The empty file already has its private ACL before any key bytes exist.
        with KEY_PATH.open("r+b") as stream:
            stream.write(secrets.token_bytes(32))
    ready.write_text(hashlib.sha256(KEY_PATH.read_bytes()).hexdigest(), encoding="ascii")
    print("Workspace key provisioned; value never printed.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provision-key", action="store_true")
    args = parser.parse_args()
    if args.provision_key:
        provision()
    else:
        asyncio.run(status())


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("Local workspace setup failed; no credentials or keys rendered.", file=sys.stderr)
        raise SystemExit(1) from None
