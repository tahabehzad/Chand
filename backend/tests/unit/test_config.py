"""Configuration tests.

Authority: ``docs/specs/DEPLOYMENT.md`` §5.1 and §5.2.
Related:   WBS P0-T02 — FastAPI skeleton and configuration.
"""

from __future__ import annotations

import pytest
from pydantic import SecretStr

from app.core.config import (
    ACTIVE_STATUTORY_YEARS,
    SECRET_VARIABLE_NAMES,
    ConfigurationError,
    Settings,
    get_settings,
)

#: Every variable of the §5.1 matrix, in both classes.  A name that is
#: added to the model without being added here fails the suite, and so does
#: the reverse.  The matrix is the contract; the model may not drift from it.
EXPECTED_VARIABLES: frozenset[str] = frozenset(
    {
        "allowed_origins",
        "app_debug",
        "app_env",
        "blind_index_pepper",
        "database_url",
        "db_ssl_mode",
        "job_lease_seconds",
        "log_level",
        "master_kek",
        "ocr_worker_concurrency",
        "s3_access_key_id",
        "s3_bucket",
        "s3_endpoint_url",
        "s3_object_lock_mode",
        "s3_retention_days",
        "s3_secret_access_key",
        "session_cookie_secure",
        "statutory_active_year",
        "statutory_bootstrap_seed_dir",
        "vault_addr",
        "vault_role_id",
        "vault_token",
    }
)


def test_model_exposes_exactly_the_matrix_variables() -> None:
    assert frozenset(Settings.model_fields) == EXPECTED_VARIABLES


def test_every_secret_variable_is_a_secret_str() -> None:
    for name in SECRET_VARIABLE_NAMES:
        annotation = Settings.model_fields[name].annotation
        assert annotation is SecretStr, f"{name} must be typed SecretStr"


def test_no_public_variable_is_mistaken_for_a_secret() -> None:
    public = EXPECTED_VARIABLES - SECRET_VARIABLE_NAMES
    for name in public:
        annotation = Settings.model_fields[name].annotation
        assert annotation is not SecretStr, f"{name} is public-class"


def test_secret_values_are_never_in_the_public_projection() -> None:
    settings = Settings(
        _env_file=None,
        database_url="postgresql://pish:hunter2@db:5432/pish",
        master_kek="a-real-looking-kek",
    )
    projection = settings.public_dump()
    rendered = repr(projection)
    assert "hunter2" not in rendered
    assert "a-real-looking-kek" not in rendered
    assert "database_url" not in projection
    assert "master_kek" not in projection


def test_environment_is_read_by_the_matrix_name(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "staging")
    monkeypatch.setenv("LOG_LEVEL", "info")
    monkeypatch.setenv("STATUTORY_BOOTSTRAP_SEED_DIR", "some/other/dir")
    settings = Settings(_env_file=None)
    assert settings.app_env == "staging"
    assert settings.log_level == "INFO"
    assert settings.statutory_bootstrap_seed_dir == "some/other/dir"


def test_production_refuses_debug() -> None:
    with pytest.raises(ConfigurationError):
        Settings(_env_file=None, app_env="production", app_debug=True)


def test_production_refuses_insecure_cookies() -> None:
    with pytest.raises(ConfigurationError):
        Settings(_env_file=None, app_env="production", session_cookie_secure=False)


def test_production_refuses_a_non_verifying_database_tls() -> None:
    with pytest.raises(ConfigurationError):
        Settings(_env_file=None, app_env="production", db_ssl_mode="require")


def test_production_requires_every_secret_to_hold_a_value() -> None:
    with pytest.raises(ConfigurationError):
        Settings(_env_file=None, app_env="production")


def test_staging_refuses_debug() -> None:
    with pytest.raises(ConfigurationError):
        Settings(_env_file=None, app_env="staging", app_debug=True)


def test_1405_may_not_be_activated() -> None:
    with pytest.raises(ConfigurationError):
        Settings(_env_file=None, statutory_active_year=1405)


def test_only_1404_is_an_activated_baseline() -> None:
    assert frozenset({1404}) == ACTIVE_STATUTORY_YEARS
    assert Settings(_env_file=None, statutory_active_year=1404).statutory_active_year == 1404


def test_object_lock_mode_is_governance_only() -> None:
    with pytest.raises(ConfigurationError):
        Settings(_env_file=None, s3_object_lock_mode="COMPLIANCE")
    assert Settings(_env_file=None).s3_object_lock_mode == "GOVERNANCE"


def test_allowed_origins_are_parsed_into_a_list() -> None:
    settings = Settings(_env_file=None, allowed_origins="http://a:5173, http://b:5173")
    assert settings.allowed_origin_list == ["http://a:5173", "http://b:5173"]


def test_get_settings_is_cached_and_clearable(monkeypatch: pytest.MonkeyPatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("APP_ENV", "staging")
    first = get_settings()
    assert get_settings() is first
    get_settings.cache_clear()
    monkeypatch.setenv("APP_ENV", "local")
    assert get_settings().app_env == "local"
    get_settings.cache_clear()
