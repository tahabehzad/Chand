"""P0-T03 real-server assertions. Never display passwords, raw logs or DSNs."""

from __future__ import annotations

import asyncio
import secrets
import ssl
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import asyncpg

ROOT = Path(__file__).resolve().parents[2]
MATERIAL = ROOT / ".secrets" / "postgres"
COMPOSE = ROOT / "infra" / "compose" / "compose.dev.yml"


class VerificationError(RuntimeError):
    """One real-server assertion failed; raw errors are intentionally suppressed."""


def audit_probe_passed(logs: str, *, table: str, marker: str, password: str) -> bool:
    """Require this probe's safe relation metadata and no private payload."""
    if marker in logs or password in logs:
        return False
    lines = logs.splitlines()
    return all(
        any(
            "AUDIT:" in line and f",{category},{command},TABLE," in line and f".{table}," in line
            for line in lines
        )
        for category, command in (("DDL", "CREATE TABLE"), ("WRITE", "INSERT"), ("READ", "SELECT"))
    )


async def verify() -> None:
    started = datetime.now(UTC).isoformat(timespec="seconds")
    password = (MATERIAL / "password").read_text(encoding="ascii")
    trusted = ssl.create_default_context(cafile=str(MATERIAL / "ca.crt"))
    trusted.minimum_version = ssl.TLSVersion.TLSv1_3
    connection = await asyncpg.connect(
        host="127.0.0.1",
        port=55432,
        user="postgres",
        password=password,
        database="pish_dev",
        ssl=trusted,
        timeout=10,
    )
    marker = "pish-private-probe-" + secrets.token_hex(16)
    # Non-secret unique relation metadata, distinct from the private payload.
    table = "pish_probe_" + secrets.token_hex(8)
    try:
        await connection.execute(
            (Path(__file__).with_name("verify-hardening.sql")).read_text(encoding="utf-8")
        )
        await connection.execute(f"CREATE TEMP TABLE {table} (payload text)")
        # Identifier is exclusively a fixed prefix + generated hex, never
        # caller input. SQL values remain bound; identifiers cannot be $1.
        await connection.execute(f"INSERT INTO {table} VALUES ($1)", marker)  # noqa: S608
        if (
            await connection.fetchval(f"SELECT payload FROM {table} WHERE payload=$1", marker)  # noqa: S608
            != marker
        ):
            raise VerificationError("Synthetic probe failed.")
        await connection.execute("SELECT pg_sleep(0.55), $1::text", marker)
        try:
            await connection.execute("SELECT 1/0 WHERE $1::text IS NOT NULL", marker)
        except asyncpg.DivisionByZeroError:
            pass
        else:
            raise VerificationError("Error probe did not execute.")
    finally:
        await connection.close()

    # Positive TLS success above prevents a dead server being mistaken for
    # successful rejection. Require the specific expected failure classes.
    for mode in ("plaintext", "password", "untrusted-ca"):
        rejected = False
        expected = {
            "plaintext": asyncpg.InvalidAuthorizationSpecificationError,
            "password": asyncpg.InvalidPasswordError,
            "untrusted-ca": ssl.SSLCertVerificationError,
        }[mode]
        try:
            probe = await asyncpg.connect(
                host="127.0.0.1",
                port=55432,
                user="postgres",
                password="synthetic-wrong-password" if mode == "password" else password,
                database="pish_dev",
                timeout=10,
                ssl=False
                if mode == "plaintext"
                else (ssl.create_default_context() if mode == "untrusted-ca" else trusted),
            )
        except expected:
            rejected = True
        else:
            await probe.close()
        if not rejected:
            raise VerificationError("Connection rejection assertion failed.")

    # Logs stay in memory and are never printed, including on a failure.
    await asyncio.sleep(0.3)
    result = await asyncio.to_thread(
        subprocess.run,
        ["docker", "compose", "-f", str(COMPOSE), "logs", "--no-color", "--since", started, "db"],
        check=True,
        capture_output=True,
        text=True,
        timeout=15,
    )
    logs = result.stdout + result.stderr
    if not audit_probe_passed(logs, table=table, marker=marker, password=password):
        raise VerificationError("Logging confidentiality/audit assertion failed.")


def main() -> int:
    try:
        asyncio.run(verify())
    except Exception:
        print("FAIL: PostgreSQL runtime verification did not pass; raw details suppressed.")  # noqa: T201
        return 1
    print("PASS: PostgreSQL 16 TLS/SCRAM/settings/audit/privacy assertions.")  # noqa: T201
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
