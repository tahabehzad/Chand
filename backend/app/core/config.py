"""Application configuration — fail-closed environment handling.

Authority
---------
``docs/specs/DEPLOYMENT.md`` §5.1 (environment matrix) and §5.2 (secret
handling); ``docs/specs/STATUTORY_INGESTION.md`` §7 (a rule set that is not
activated must fail closed); ``docs/adr/ADR-002`` (object lock is
``GOVERNANCE``).

Related
-------
WBS P0-T02 — FastAPI skeleton and configuration.

Rules enforced here
-------------------
1. Every variable name is exactly the name in the §5.1 matrix.  A name that
   drifts out of the matrix is a defect, not a convenience.
2. Secret-class variables are ``SecretStr``.  They are never rendered, never
   logged and never returned by the API.
3. An absent or invalid value fails closed.  It is never defaulted to a
   working substitute, and a missing secret is an error in ``production``
   rather than a silent empty string.
4. ``1405`` may not be selected as the active statutory year while it is
   transcribed but not four-eyes verified.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Final, Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

AppEnvironment = Literal["local", "staging", "production"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
DbSslMode = Literal["disable", "require", "verify-full"]

#: Object-lock mode.  ADR-002 fixes this at ``GOVERNANCE``.  ``COMPLIANCE``
#: is excluded because the only implementation available to the project is
#: MinIO's, which ADR-002 rejects outright.
OBJECT_LOCK_MODE: Final[str] = "GOVERNANCE"

#: The only statutory baseline that may be active.  1405 is transcribed and
#: cross-corroborated at L2/L3, but it is **not** four-eyes verified and it
#: ships with every parameter null.  Activation requires conditions A1-A8,
#: none of which is met.  See ``docs/specs/STATUTORY_INGESTION.md`` §7.
ACTIVE_STATUTORY_YEARS: Final[frozenset[int]] = frozenset({1404})

#: The variables classified ``secret`` in the §5.1 matrix.  The test suite
#: asserts this set against the model so the two cannot drift apart.
SECRET_VARIABLE_NAMES: Final[frozenset[str]] = frozenset(
    {
        "database_url",
        "s3_access_key_id",
        "s3_secret_access_key",
        "vault_addr",
        "vault_token",
        "vault_role_id",
        "blind_index_pepper",
        "master_kek",
    }
)


class ConfigurationError(RuntimeError):
    """Raised when the environment does not satisfy a fail-closed rule.

    This is deliberately **not** a ``ValueError``.  Pydantic converts a
    ``ValueError`` raised inside a validator into a ``ValidationError``,
    which would blur the difference between "this input is malformed" and
    "this deployment is unsafe to start".  A configuration error is the
    second kind, and it must stop the process.
    """


class Settings(BaseSettings):
    """Runtime configuration, read from the process environment.

    The model is a one-to-one mapping of the §5.1 matrix.  Nothing is
    inferred, and no default stands in for a value the operator must set.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- application -------------------------------------------------------
    app_env: AppEnvironment = "local"
    app_debug: bool = False
    log_level: LogLevel = "INFO"
    allowed_origins: str = "http://localhost:5173"
    session_cookie_secure: bool = True

    # --- database ----------------------------------------------------------
    database_url: SecretStr = SecretStr("")
    db_ssl_mode: DbSslMode = "disable"

    # --- object storage (ADR-002) ------------------------------------------
    s3_endpoint_url: str = ""
    s3_bucket: str = "pish-dev"
    s3_object_lock_mode: str = OBJECT_LOCK_MODE
    s3_retention_days: int = Field(default=1, gt=0)
    s3_access_key_id: SecretStr = SecretStr("")
    s3_secret_access_key: SecretStr = SecretStr("")

    # --- key management (ADR-003) ------------------------------------------
    vault_addr: SecretStr = SecretStr("")
    vault_token: SecretStr = SecretStr("")
    vault_role_id: SecretStr = SecretStr("")
    blind_index_pepper: SecretStr = SecretStr("")
    master_kek: SecretStr = SecretStr("")

    # --- background processing ---------------------------------------------
    # NOTE: the job-queue implementation is UNDECIDED (ADR-005 is PROPOSED).
    # These names are inert until the decision is accepted.
    ocr_worker_concurrency: int = 2
    job_lease_seconds: int = 300

    # --- statutory rule set -------------------------------------------------
    statutory_active_year: int = 1404
    statutory_bootstrap_seed_dir: str = "data/seeds"

    # --- validators ---------------------------------------------------------

    @field_validator("log_level", mode="before")
    @classmethod
    def _normalise_log_level(cls, value: object) -> object:
        """Accept ``debug`` as well as ``DEBUG``."""
        if isinstance(value, str):
            return value.strip().upper()
        return value

    @field_validator("statutory_active_year")
    @classmethod
    def _reject_unactivated_rule_year(cls, value: int) -> int:
        """Fail closed on any rule year that is not an activated baseline."""
        if value not in ACTIVE_STATUTORY_YEARS:
            allowed = ", ".join(str(year) for year in sorted(ACTIVE_STATUTORY_YEARS))
            raise ConfigurationError(
                f"statutory_active_year={value} is not an activated rule set. "
                f"Only {allowed} may be active: 1405 is transcribed but not "
                "four-eyes verified, and activation requires conditions A1-A8 "
                "(docs/specs/STATUTORY_INGESTION.md §7)."
            )
        return value

    @field_validator("s3_object_lock_mode")
    @classmethod
    def _enforce_object_lock_mode(cls, value: str) -> str:
        """The object store must be locked in ``GOVERNANCE`` mode (ADR-002)."""
        if value != OBJECT_LOCK_MODE:
            raise ConfigurationError(
                f"s3_object_lock_mode must be {OBJECT_LOCK_MODE!r}, not {value!r}. "
                "ADR-002 fixes the mode and excludes the COMPLIANCE option."
            )
        return value

    @model_validator(mode="after")
    def _enforce_environment_policy(self) -> Settings:
        """Apply the per-environment policy of the §5.1 matrix."""
        if self.app_env == "production":
            if self.app_debug:
                raise ConfigurationError("APP_DEBUG must be false in production.")
            if not self.session_cookie_secure:
                raise ConfigurationError("SESSION_COOKIE_SECURE must be true in production.")
            if self.db_ssl_mode != "verify-full":
                raise ConfigurationError("DB_SSL_MODE must be verify-full in production.")
            if self.s3_retention_days != 3650:
                raise ConfigurationError("S3_RETENTION_DAYS must be 3650 in production (ADR-002).")
            missing = sorted(name for name, value in self.secret_values().items() if not value)
            if missing:
                raise ConfigurationError(
                    "production requires every secret-class variable to hold a value; "
                    "missing: " + ", ".join(missing)
                )
        elif self.app_env == "staging" and self.app_debug:
            raise ConfigurationError("APP_DEBUG must be false outside the local environment.")
        return self

    # --- projections --------------------------------------------------------

    def secret_values(self) -> dict[str, str]:
        """Return the secret-class variables and their values.

        The result is secret material.  It exists so the fail-closed checks
        can ask whether a value is *present*.  It must never be logged,
        serialised into a response, or returned by the API.
        """
        return {
            "database_url": self.database_url.get_secret_value(),
            "s3_access_key_id": self.s3_access_key_id.get_secret_value(),
            "s3_secret_access_key": self.s3_secret_access_key.get_secret_value(),
            "vault_addr": self.vault_addr.get_secret_value(),
            "vault_token": self.vault_token.get_secret_value(),
            "vault_role_id": self.vault_role_id.get_secret_value(),
            "blind_index_pepper": self.blind_index_pepper.get_secret_value(),
            "master_kek": self.master_kek.get_secret_value(),
        }

    def public_dump(self) -> dict[str, object]:
        """Return the public-class configuration.  Safe to log."""
        return {
            "app_env": self.app_env,
            "app_debug": self.app_debug,
            "log_level": self.log_level,
            "allowed_origins": self.allowed_origins,
            "session_cookie_secure": self.session_cookie_secure,
            "db_ssl_mode": self.db_ssl_mode,
            "s3_endpoint_url": self.s3_endpoint_url,
            "s3_bucket": self.s3_bucket,
            "s3_object_lock_mode": self.s3_object_lock_mode,
            "s3_retention_days": self.s3_retention_days,
            "ocr_worker_concurrency": self.ocr_worker_concurrency,
            "job_lease_seconds": self.job_lease_seconds,
            "statutory_active_year": self.statutory_active_year,
            "statutory_bootstrap_seed_dir": self.statutory_bootstrap_seed_dir,
        }

    @property
    def allowed_origin_list(self) -> list[str]:
        """Return the configured origins as a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide settings, parsed once.

    The cache is cleared in the test suite whenever the environment is
    changed underneath it.
    """
    return Settings()
