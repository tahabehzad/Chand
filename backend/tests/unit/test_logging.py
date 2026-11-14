"""Logging and secret-redaction tests.

Authority: ``docs/specs/DEPLOYMENT.md`` §7.2 and §5.2;
            ``docs/specs/TESTING.md`` §9 — CR-13.
Related:   WBS P0-T02 — FastAPI skeleton and configuration.

These tests assert against the **real** emission path — logger, filter,
formatter, stdout — rather than against an in-memory copy of the record.
A test that inspected the record before the filter ran would prove nothing.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator

import pytest

from app.core.config import Settings
from app.core.logging import (
    REDACTED,
    SecretRedactingFilter,
    configure_logging,
    get_logger,
    is_secret_key,
    redact_text,
)

FAKE_SECRET = "hunter2"
FAKE_URL = f"postgresql://pish:{FAKE_SECRET}@db:5432/pish"
FAKE_BEARER = "eyJhbGciOiJIUzI1NiJ9.cGF5bG9hZA.c2lnbmF0dXJl"
FAKE_NATIONAL_CODE = "0012345678"
FAKE_MOBILE = "09121234567"
FAKE_SHEBA = "IR820540102680020817909002"


@pytest.fixture(autouse=True)
def _reset_logging() -> Iterator[None]:
    """Leave the root logger as the suite found it."""
    yield
    root = logging.getLogger()
    root.handlers.clear()


def test_a_bare_value_is_protected_only_by_its_context() -> None:
    """A random string carries no pattern, so only context can protect it.

    The filter redacts by **name** and by **pattern**.  A value is removed
    when it is the value of a secret-named key, when it sits inside a URL
    credential, or when it matches a known credential shape.  An unlabelled
    random string is undetectable by *any* pattern-matching filter, which
    is why CR-13 is paired with the rule that a secret is never
    interpolated into a log message in the first place.
    """
    assert FAKE_SECRET in redact_text(f"the value is {FAKE_SECRET}")
    assert FAKE_SECRET not in redact_text(f"MASTER_KEK={FAKE_SECRET}")
    assert FAKE_SECRET not in redact_text(FAKE_URL)


def test_a_json_web_token_is_removed_without_the_word_bearer() -> None:
    """A JWT is a credential even when no keyword introduces it."""
    assert FAKE_BEARER not in redact_text(f"token rejected: {FAKE_BEARER}")


def test_url_credentials_are_removed_but_the_url_stays_readable() -> None:
    redacted = redact_text(f"connecting to {FAKE_URL}")
    assert FAKE_SECRET not in redacted
    assert "pish" in redacted
    assert "db:5432" in redacted


def test_bearer_tokens_are_removed() -> None:
    assert FAKE_BEARER not in redact_text(f"Authorization: Bearer {FAKE_BEARER}")


def test_a_national_code_is_removed() -> None:
    assert FAKE_NATIONAL_CODE not in redact_text(f"candidate {FAKE_NATIONAL_CODE}")


def test_a_mobile_number_is_removed() -> None:
    assert FAKE_MOBILE not in redact_text(f"candidate {FAKE_MOBILE}")
    assert "09121234567" not in redact_text("candidate +989121234567")


def test_a_sheba_number_is_removed() -> None:
    assert FAKE_SHEBA not in redact_text(f"account {FAKE_SHEBA}")


def test_a_secret_named_key_is_removed() -> None:
    assert "s3cr3t" not in redact_text("BLIND_INDEX_PEPPER=s3cr3t")


def test_secret_key_names_are_recognised() -> None:
    assert is_secret_key("database_url")
    assert is_secret_key("VAULT_TOKEN")
    assert is_secret_key("blind_index_pepper")
    assert not is_secret_key("status_code")
    assert not is_secret_key("correlation_id")


def test_no_secret_reaches_a_log_line(capsys: pytest.CaptureFixture[str]) -> None:
    configure_logging(Settings(_env_file=None))
    logger = get_logger("app.tests.logging")

    logger.info("connecting to %s", FAKE_URL)
    logger.info("authorization is Bearer %s", FAKE_BEARER)
    logger.info("candidate national code %s", FAKE_NATIONAL_CODE)
    logger.info("candidate mobile %s", FAKE_MOBILE)
    logger.info("settlement account %s", FAKE_SHEBA)
    logger.info("BLIND_INDEX_PEPPER=s3cr3t")
    logger.warning("field value", extra={"database_url": FAKE_URL})
    logger.info("an ordinary message")

    out = capsys.readouterr().out
    for secret in (
        FAKE_SECRET,
        FAKE_BEARER,
        FAKE_NATIONAL_CODE,
        FAKE_MOBILE,
        FAKE_SHEBA,
        "s3cr3t",
    ):
        assert secret not in out, f"{secret} leaked into the log"
    assert "an ordinary message" in out
    assert REDACTED in out


def test_a_traceback_is_redacted(capsys: pytest.CaptureFixture[str]) -> None:
    configure_logging(Settings(_env_file=None))
    logger = get_logger("app.tests.logging")

    try:
        raise RuntimeError(f"cannot reach {FAKE_URL}")
    except RuntimeError:
        logger.exception("operation_failed")

    out = capsys.readouterr().out
    assert FAKE_SECRET not in out
    assert "operation_failed" in out


def test_the_filter_is_installed_on_the_handler_and_on_the_logger() -> None:
    configure_logging(Settings(_env_file=None))
    logger = get_logger("app.tests.filter")
    assert any(isinstance(item, SecretRedactingFilter) for item in logger.filters)
    handlers = logger.handlers + logging.getLogger().handlers
    assert any(
        isinstance(item, SecretRedactingFilter) for handler in handlers for item in handler.filters
    )


def test_redaction_is_idempotent() -> None:
    once = redact_text(f"value {FAKE_SECRET}")
    assert redact_text(once) == once
