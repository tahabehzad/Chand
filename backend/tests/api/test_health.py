"""API tests for the application skeleton.

Authority: ``docs/specs/DEPLOYMENT.md`` §7.1 (health endpoints) and §7.2
            (correlation identifier).
Related:   WBS P0-T02 — FastAPI skeleton and configuration.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app

FAKE_SECRET = "hunter2"
FAKE_URL = f"postgresql://pish:{FAKE_SECRET}@db:5432/pish"


@pytest.fixture
def client() -> Iterator[TestClient]:
    """Return a client over a local-configured application."""
    application = create_app(Settings(_env_file=None))
    with TestClient(application) as test_client:
        yield test_client


def test_health_live_returns_200(client: TestClient) -> None:
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_health_live_checks_no_dependency(client: TestClient) -> None:
    """A failing dependency must not turn into a restart loop (§7.1).

    The probe answers without touching PostgreSQL, the object store or the
    rule set, so it is the only endpoint that can be exercised before those
    exist.
    """
    response = client.get("/health/live")
    assert response.status_code == 200
    assert "dependencies" not in response.json()


def test_the_request_id_is_echoed_and_carried_into_the_log(
    client: TestClient, capsys: pytest.CaptureFixture[str]
) -> None:
    response = client.get("/health/live", headers={"X-Request-Id": "req-1234"})
    assert response.status_code == 200
    assert response.headers["X-Request-Id"] == "req-1234"
    out = capsys.readouterr().out
    assert "req-1234" in out


def test_a_request_id_is_generated_when_the_client_supplies_none(
    client: TestClient,
) -> None:
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.headers["X-Request-Id"]


def test_no_secret_reaches_a_log_line_during_startup(
    capsys: pytest.CaptureFixture[str],
) -> None:
    settings = Settings(_env_file=None, database_url=FAKE_URL, master_kek=FAKE_SECRET)
    application = create_app(settings)
    with TestClient(application) as client:
        response = client.get("/health/live")
    assert response.status_code == 200
    out = capsys.readouterr().out
    assert FAKE_SECRET not in out
    assert "application_starting" in out


def test_debug_controls_the_documentation_surface() -> None:
    """``APP_DEBUG`` drives behaviour; no code change is required."""
    debug_application = create_app(Settings(_env_file=None, app_debug=True))
    assert debug_application.docs_url == "/docs"

    production_application = create_app(Settings(_env_file=None, app_env="staging"))
    assert production_application.docs_url is None
    assert production_application.openapi_url is None
