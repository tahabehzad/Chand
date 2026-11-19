"""P0-T16 backup and restore dry run against disposable PostgreSQL 16.

Authority: ``docs/specs/DEPLOYMENT.md`` §5 and WBS §14.3 ``P0-T16`` — "a backup
completes and restores to a schema-identical isolated instance".

The scripts under ``infra/postgres/backup/`` are executed unmodified; the test
only starts and removes the two containers it created. No pull is attempted and
no production or development database is touched.
"""

from __future__ import annotations

import os
import secrets
import shutil
import socket
import subprocess
import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[3]
BACKUP = ROOT / "infra" / "postgres" / "backup" / "backup.sh"
RESTORE = ROOT / "infra" / "postgres" / "backup" / "restore.sh"

IMAGE = "postgres:16.16-bookworm"
DB_NAME = "pish_p0t16"

#: A representative slice of the project's catalogue surface: a table with a
#: CHECK, a forced-RLS policy, an index, a function and a trigger. A restore
#: that loses any of them changes the fingerprint.
SEED_SQL = """
CREATE TABLE organizations (
    id uuid PRIMARY KEY,
    legal_name_fa varchar(200) NOT NULL,
    national_company_id varchar(11),
    CONSTRAINT ck_organizations_national_company_id
        CHECK (national_company_id IS NULL OR national_company_id ~ '^[0-9]{11}$')
);
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE organizations FORCE ROW LEVEL SECURITY;
CREATE POLICY organizations_tenant ON organizations FOR SELECT USING (true);
CREATE INDEX ix_organizations_legal_name ON organizations (legal_name_fa);
CREATE FUNCTION organizations_touch() RETURNS trigger
LANGUAGE plpgsql AS $$ BEGIN RETURN NEW; END $$;
CREATE TRIGGER trg_organizations_touch BEFORE UPDATE ON organizations
    FOR EACH ROW EXECUTE FUNCTION organizations_touch();
INSERT INTO organizations VALUES
    ('11111111-1111-4111-8111-111111111111', 'نمونه سازمان', '12345678901');
"""


def docker(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", *args], capture_output=True, text=True, timeout=120, check=False
    )


def script_env() -> dict[str, str]:
    """Environment for the shell scripts.

    ``MSYS_NO_PATHCONV`` stops Git Bash from rewriting an in-container path
    (``/tmp/...``) into a Windows path before it reaches ``docker``.
    """
    env = dict(os.environ)
    env["MSYS_NO_PATHCONV"] = "1"
    return env


def resolve_shell() -> str:
    """Return a POSIX shell that can run the scripts, or skip the module.

    On Windows ``bash`` on ``PATH`` can resolve to the WSL relay, which fails
    for a host script; the Git-for-Windows shell is therefore preferred and
    validated by execution rather than by name.
    """
    candidates: list[str | None] = [os.environ.get("GIT_BASH")]
    git = shutil.which("git")
    if git is not None:
        root = Path(git).resolve().parent.parent
        candidates += [str(root / "bin" / "bash.exe"), str(root / "usr" / "bin" / "bash.exe")]
    candidates += [
        r"C:\Program Files\Git\bin\bash.exe",
        r"C:\Program Files (x86)\Git\bin\bash.exe",
        shutil.which("bash"),
    ]
    for candidate in candidates:
        if not candidate or not Path(candidate).exists():
            continue
        try:
            probe = subprocess.run(
                [candidate, "-c", "command -v sha256sum"],
                capture_output=True, text=True, timeout=30, check=False,
            )
        except OSError:
            continue
        if probe.returncode == 0 and probe.stdout.strip():
            return candidate
    pytest.skip("NOT RUN: no POSIX shell with sha256sum for the backup scripts")


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def psql(container: str, sql: str, *, database: str = "postgres") -> str:
    result = subprocess.run(
        ["docker", "exec", "-i", container, "psql", "-U", "postgres",
         "-d", database, "-At", "-F", "|", "-v", "ON_ERROR_STOP=1", "-f", "-"],
        input=sql,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
        check=False,
        env=script_env(),
    )
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def start(image_ok: bool, name: str, port: int) -> str:
    assert image_ok
    started = docker(
        "run", "-d", "--rm", "--name", name,
        "-p", f"127.0.0.1:{port}:5432",
        "-e", "POSTGRES_HOST_AUTH_METHOD=trust",
        "-e", f"POSTGRES_DB={DB_NAME}",
        IMAGE,
    )
    assert started.returncode == 0, started.stderr
    deadline = time.monotonic() + 60
    while True:
        ready = docker("exec", name, "psql", "-U", "postgres", "-d", "postgres", "-c", "SELECT 1")
        if ready.returncode == 0:
            return name
        if time.monotonic() > deadline:
            pytest.fail("Disposable PostgreSQL did not become ready")
        time.sleep(0.4)


@pytest.fixture(scope="module")
def containers() -> Iterator[dict[str, Any]]:
    if shutil.which("docker") is None or docker("image", "inspect", IMAGE).returncode:
        pytest.skip("NOT RUN: official PostgreSQL image/Docker unavailable; no pull attempted")
    shell = resolve_shell()
    token = secrets.token_hex(4)
    source = start(True, f"pish-p0t16-src-{token}", free_port())
    target = start(True, f"pish-p0t16-dst-{token}", free_port())
    try:
        psql(source, SEED_SQL, database=DB_NAME)
        yield {"source": source, "target": target, "shell": shell}
    finally:
        for name in (target, source):
            docker("rm", "-f", name)


def run_script(shell: str, script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [shell, str(script), *args],
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
        env=script_env(),
    )


def test_backup_restores_a_schema_identical_instance(
    containers: dict[str, Any], tmp_path: Path
) -> None:
    source = containers["source"]
    target = containers["target"]
    output = tmp_path / "backups"

    backed_up = run_script(
        containers["shell"], BACKUP, source, str(output), "7", "postgres", DB_NAME
    )
    assert backed_up.returncode == 0, backed_up.stderr
    sets = [p for p in output.iterdir() if p.is_dir()]
    assert len(sets) == 1
    manifest = (sets[0] / "manifest.txt").read_text(encoding="utf-8")
    source_fingerprint = next(
        line.split("=", 1)[1] for line in manifest.splitlines()
        if line.startswith("schema_fingerprint=")
    )
    dump_sha = next(
        line.split("=", 1)[1] for line in manifest.splitlines()
        if line.startswith("dump_sha256=")
    )
    assert len(dump_sha) == 64
    assert (sets[0] / "db.dump").stat().st_size > 0

    restored = run_script(
        containers["shell"], RESTORE, str(sets[0]), target, "postgres", DB_NAME
    )
    assert restored.returncode == 0, restored.stderr
    restored_fields = restored.stdout.strip().split("|")
    assert len(restored_fields) == 2, repr(restored.stdout)
    restored_fingerprint, restored_count = restored_fields
    source_fingerprint, source_count = source_fingerprint.split()

    # Schema-identical: same catalogue digest over the same object count.
    assert restored_fingerprint == source_fingerprint
    assert restored_count == source_count
    assert int(restored_count) > 0

    # The data came with it, and the forced policy survived the restore.
    rows = psql(
        target,
        "SELECT legal_name_fa FROM organizations "
        "WHERE id = '11111111-1111-4111-8111-111111111111'",
        database=DB_NAME,
    )
    assert rows == "نمونه سازمان"
    assert psql(
        target,
        "SELECT relrowsecurity AND relforcerowsecurity FROM pg_class "
        "WHERE relname = 'organizations'",
        database=DB_NAME,
    ) == "t"


def test_retention_keeps_only_the_newest_sets(
    containers: dict[str, Any], tmp_path: Path
) -> None:
    output = tmp_path / "retained"
    for _ in range(3):
        result = run_script(
            containers["shell"], BACKUP, containers["source"], str(output), "2",
            "postgres", DB_NAME,
        )
        assert result.returncode == 0, result.stderr
    sets = sorted(p for p in output.iterdir() if p.is_dir())
    assert len(sets) == 2, "retention must prune all but the newest N sets"


def test_restore_refuses_its_own_source(containers: dict[str, Any], tmp_path: Path) -> None:
    output = tmp_path / "guard"
    backed_up = run_script(
        containers["shell"], BACKUP, containers["source"], str(output),
        "7", "postgres", DB_NAME,
    )
    assert backed_up.returncode == 0, backed_up.stderr
    backup_set = next(p for p in output.iterdir() if p.is_dir())
    refused = run_script(
        containers["shell"], RESTORE, str(backup_set), containers["source"],
        "postgres", DB_NAME,
    )
    assert refused.returncode == 3
    assert "refusing to restore" in refused.stderr
