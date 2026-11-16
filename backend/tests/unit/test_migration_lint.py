"""Storage declarations are checked before PostgreSQL normalizes them."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from app.core.migration_lint import lint_migration


@pytest.mark.parametrize(
    "declaration",
    [
        "sa.CHAR()",
        "sa.VARCHAR()",
        "sa.String(length=None)",
        "CHAR(0)",
        "sa.Float()",
        "postgresql.DOUBLE_PRECISION()",
        "sa.REAL()",
        "sa.DateTime()",
        "sa.TIMESTAMP(timezone=False)",
    ],
)
def test_rejects_unsafe_storage(declaration: str) -> None:
    assert len(lint_migration(f"column_type = {declaration}")) == 1


def test_accepts_explicit_storage_and_dates() -> None:
    assert (
        lint_migration(
            "types = [sa.CHAR(64), sa.String(length=2), sa.Text(), "
            "sa.DateTime(timezone=True), sa.Date(), sa.Numeric(24, 4)]"
        )
        == []
    )


def test_actual_baseline_declarations() -> None:
    migration = Path(__file__).resolve().parents[2] / "alembic/versions/0001_statutory_baseline.py"
    assert lint_migration(migration.read_text(encoding="utf-8")) == []


@pytest.mark.parametrize("url", ["", "postgresql+asyncpg://synthetic-private-marker@[invalid"])
def test_alembic_failure_does_not_disclose_url(url: str) -> None:
    backend = Path(__file__).resolve().parents[2]
    environment = os.environ.copy()
    environment["DATABASE_URL"] = url
    environment["APP_ENV"] = "local"
    result = subprocess.run(
        [sys.executable, "-B", "-m", "alembic", "upgrade", "head"],
        cwd=backend,
        env=environment,
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert result.returncode != 0
    assert "synthetic-private-marker" not in result.stdout + result.stderr
    assert "Migration failed" in result.stderr
