"""Structured JSON logging with mandatory secret redaction.

Authority
---------
``docs/specs/DEPLOYMENT.md`` §7.2 (logging rules) and §5.2 (secret
handling); ``docs/specs/TESTING.md`` §9 — CR-13: *"No secret appears in a
log line, an error message or a traceback."*

Related
-------
WBS P0-T02 — FastAPI skeleton and configuration.

Design note — where the filter has to sit
-----------------------------------------
``Logger.handle`` applies the filters of the logger that emitted the
record, and then walks the hierarchy calling ``handler.handle`` on each
ancestor **without** re-entering the ancestor's ``handle``.  A filter on
the root logger therefore never sees a record emitted by ``app.main``.
The redaction filter is therefore installed on the handler (which every
emitted record reaches) *and* on every logger this module hands out.
The redaction itself is idempotent, so the double application is harmless.
"""

from __future__ import annotations

import json
import logging
import re
import sys
from collections.abc import Mapping
from contextlib import suppress
from contextvars import ContextVar, Token
from datetime import UTC, datetime
from typing import Final, TextIO

from app.core.config import Settings

#: The placeholder that replaces any redacted value.
REDACTED: Final[str] = "[REDACTED]"

#: Names that identify secret material regardless of their value.
SECRET_KEY_NAMES: Final[frozenset[str]] = frozenset(
    {
        "access_key",
        "api_key",
        "blind_index_pepper",
        "credential",
        "credentials",
        "database_url",
        "kek",
        "master_kek",
        "passwd",
        "password",
        "pepper",
        "private_key",
        "s3_access_key_id",
        "s3_secret_access_key",
        "secret",
        "secret_key",
        "token",
        "vault_addr",
        "vault_role_id",
        "vault_token",
    }
)

#: A key whose *name* marks its value as secret.
_SECRET_KEY_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(?i)(secret|token|password|passwd|pepper|kek|api[_-]?key|access[_-]?key"
    r"|private[_-]?key|credential|database[_-]?url|vault)"
)

#: ``scheme://user:password@host`` — the password is removed, the rest stays.
_URL_CREDENTIALS: Final[re.Pattern[str]] = re.compile(
    r"(?i)([a-z][a-z0-9+.\-]*://[^:/\s@]+:)([^/\s@]+)(@)"
)

#: A bearer token presented as a credential.
_BEARER: Final[re.Pattern[str]] = re.compile(r"(?i)\bbearer\s+[A-Za-z0-9\-._~+/]+=*")

#: A JSON Web Token.  The header of a JWT base64url-encodes a JSON object
#: and therefore always begins with ``eyJ``; requiring that prefix keeps
#: the pattern from firing on ordinary dotted identifiers.
_JWT: Final[re.Pattern[str]] = re.compile(
    r"(?<![A-Za-z0-9_\-])eyJ[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}"
    r"(?![A-Za-z0-9_\-])"
)

#: A keyword in the *format string* that marks the arguments it fills as
#: credential material.  The keyword and the value are often only
#: recognisable together — "Bearer %s" and an opaque token are a pair.
_CREDENTIAL_HINT: Final[re.Pattern[str]] = re.compile(
    r"(?i)\b(bearer|authorization|auth[_-]?token|access[_-]?token|refresh[_-]?token"
    r"|token|password|passwd|secret|api[_-]?key|access[_-]?key|credential)s?\b"
)

#: An IR/IBAN Sheba number.
_SHEBA: Final[re.Pattern[str]] = re.compile(r"(?<![A-Za-z0-9])IR[0-9]{24}(?![A-Za-z0-9])")

#: An Iranian mobile number in its local form, ``09xxxxxxxxx``.
_IRANIAN_MOBILE_LOCAL: Final[re.Pattern[str]] = re.compile(r"(?<![0-9])09[0-9]{9}(?![0-9])")

#: An Iranian mobile number in its international form.
_IRANIAN_MOBILE: Final[re.Pattern[str]] = re.compile(
    r"(?<![0-9])(?:\+98|0098|98)?9[0-9]{9}(?![0-9])"
)

#: A ten-digit National Code.
_NATIONAL_CODE: Final[re.Pattern[str]] = re.compile(r"(?<![0-9])[0-9]{10}(?![0-9])")

#: ``NAME=value`` or ``name: value`` where the name marks a secret.
_SECRET_ASSIGNMENT: Final[re.Pattern[str]] = re.compile(
    r"(?i)\b([A-Za-z0-9_.\-]*"
    r"(?:secret|token|password|passwd|pepper|kek|api[_-]?key|access[_-]?key"
    r"|private[_-]?key|credential|database[_-]?url|vault)"
    r"[A-Za-z0-9_.\-]*)(\s*[:=]\s*)(\"[^\"]*\"|'[^']*'|[^\s,;)\]}]+)"
)

#: The attributes ``logging.LogRecord`` defines for itself.  Anything else
#: in ``record.__dict__`` was supplied by the caller through ``extra``.
_STANDARD_RECORD_ATTRIBUTES: Final[frozenset[str]] = frozenset(
    logging.LogRecord("probe", 0, "probe.py", 0, "probe", None, None).__dict__
) | {"asctime", "exc_text", "message"}

#: The correlation identifier carried by every log line (§7.2).
correlation_id_var: Final[ContextVar[str]] = ContextVar("correlation_id", default="-")

#: Framework extras that carry no information a JSON log consumer needs.
#: ``color_message`` holds an ANSI-escaped template, not a message.
_DROPPED_EXTRA_KEYS: Final[frozenset[str]] = frozenset({"color_message"})


def set_correlation_id(value: str) -> Token[str]:
    """Bind the correlation identifier for the current context."""
    return correlation_id_var.set(value)


def reset_correlation_id(token: Token[str]) -> None:
    """Restore the previous correlation identifier."""
    correlation_id_var.reset(token)


def get_correlation_id() -> str:
    """Return the correlation identifier for the current context."""
    return correlation_id_var.get()


def is_secret_key(name: str) -> bool:
    """Return whether a field or key name identifies secret material."""
    lowered = name.lower()
    if lowered in SECRET_KEY_NAMES:
        return True
    return bool(_SECRET_KEY_PATTERN.search(lowered))


def redact_text(text: str) -> str:
    """Return ``text`` with every recognised secret pattern removed.

    The function is idempotent: redacting an already-redacted string
    returns it unchanged.
    """
    redacted = _URL_CREDENTIALS.sub(rf"\1{REDACTED}\3", text)
    redacted = _BEARER.sub(f"bearer {REDACTED}", redacted)
    redacted = _JWT.sub(REDACTED, redacted)
    redacted = _SHEBA.sub(REDACTED, redacted)
    redacted = _IRANIAN_MOBILE_LOCAL.sub(REDACTED, redacted)
    redacted = _IRANIAN_MOBILE.sub(REDACTED, redacted)
    redacted = _NATIONAL_CODE.sub(REDACTED, redacted)
    redacted = _SECRET_ASSIGNMENT.sub(rf"\1\2{REDACTED}", redacted)
    return redacted


def _redact_value(value: object) -> object:
    """Return ``value`` with any secret content removed."""
    if isinstance(value, str):
        return redact_text(value)
    return value


def _redact_arg(value: object, *, redact_all: bool) -> object:
    """Return one log argument with any secret content removed.

    ``redact_all`` is set when the *format string* names a credential.  In
    that case the argument is replaced wholesale: ``"Bearer %s"`` carries
    no token and an opaque token carries no word "Bearer", so neither half
    is detectable on its own.
    """
    if isinstance(value, str):
        return REDACTED if redact_all else redact_text(value)
    return value


def _redact_args(
    args: tuple[object, ...] | Mapping[str, object] | None,
    *,
    redact_all: bool = False,
) -> tuple[object, ...] | Mapping[str, object] | None:
    """Return the log arguments with any secret content removed.

    The **shape** of the arguments is preserved exactly.  A log record is
    shared with every other handler in the chain, and each formatter has
    its own contract for ``record.args`` — uvicorn's access formatter, for
    instance, unpacks it into five positional values.  A filter that
    reshapes the arguments breaks those contracts.
    """
    if args is None:
        return None
    if isinstance(args, Mapping):
        redacted: dict[str, object] = {}
        for key, value in args.items():
            if is_secret_key(key):
                redacted[key] = REDACTED
            else:
                redacted[key] = _redact_arg(value, redact_all=redact_all)
        return redacted
    return tuple(_redact_arg(item, redact_all=redact_all) for item in args)


class SecretRedactingFilter(logging.Filter):
    """Remove secret material from a record before any handler emits it.

    The filter mutates the record in place, so every handler downstream —
    including a handler installed by a test framework — sees the redacted
    values only.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.msg if isinstance(record.msg, str) else ""
        if isinstance(record.msg, str):
            record.msg = redact_text(record.msg)
        if record.args:
            record.args = _redact_args(
                record.args,
                redact_all=bool(_CREDENTIAL_HINT.search(message)),
            )
        for key in list(record.__dict__):
            if key in _STANDARD_RECORD_ATTRIBUTES or key.startswith("_"):
                continue
            value = record.__dict__[key]
            if is_secret_key(key):
                record.__dict__[key] = REDACTED
            elif isinstance(value, str):
                record.__dict__[key] = redact_text(value)
        if record.exc_info and not record.exc_text:
            record.exc_text = redact_text(logging.Formatter().formatException(record.exc_info))
        return True


#: The single filter instance installed everywhere.
SECRET_REDACTING_FILTER: Final[SecretRedactingFilter] = SecretRedactingFilter()


class JsonFormatter(logging.Formatter):
    """Render a record as exactly one structured JSON object per line."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": get_correlation_id(),
        }
        for key, value in record.__dict__.items():
            if key in _STANDARD_RECORD_ATTRIBUTES or key.startswith("_"):
                continue
            if key in _DROPPED_EXTRA_KEYS:
                continue
            if isinstance(value, (str, int, float, bool, type(None))):
                payload[key] = value
            else:
                payload[key] = repr(value)
        if record.exc_text:
            payload["exception"] = record.exc_text
        if record.stack_info:
            payload["stack"] = record.stack_info
        return json.dumps(payload, ensure_ascii=False, default=str)


class ApplicationHandler(logging.StreamHandler[TextIO]):
    """The stdout handler used by the application.

    The dedicated type exists so that :func:`configure_logging` can replace
    its own handler instead of accumulating duplicates.  The stream is
    resolved on every emit rather than at construction, so the handler
    follows the process's current stdout.
    """

    def emit(self, record: logging.LogRecord) -> None:
        """Write the record to the process's current stdout."""
        self.stream = sys.stdout
        super().emit(record)


def _utf8_stdout() -> TextIO:
    """Return stdout, forced to UTF-8 so Persian text is never lost.

    The runtime image is Linux with a UTF-8 locale; on a Windows
    development host the console code page would otherwise raise
    ``UnicodeEncodeError`` the first time a Persian string is logged.
    """
    stream = sys.stdout
    reconfigure = getattr(stream, "reconfigure", None)
    if callable(reconfigure):
        with suppress(OSError, ValueError):  # pragma: no cover - platform dependent
            reconfigure(encoding="utf-8", errors="backslashreplace")
    return stream


def _build_handler(settings: Settings) -> ApplicationHandler:
    """Build the JSON handler with the redaction filter attached."""
    handler = ApplicationHandler(stream=_utf8_stdout())
    handler.setFormatter(JsonFormatter())
    handler.addFilter(SECRET_REDACTING_FILTER)
    handler.setLevel(settings.log_level)
    return handler


def _install_handler(
    logger: logging.Logger, handler: ApplicationHandler, *, replace_all: bool = False
) -> None:
    """Attach ``handler`` to ``logger``, replacing a previous one.

    ``replace_all`` also removes the handlers the framework installed by
    itself.  It is used for the uvicorn loggers, whose default handler
    writes a second, plain-text copy of every record to stderr — the
    specification requires one structured JSON stream on stdout, and a
    duplicate plain-text copy would also bypass the redaction filter.
    """
    for existing in list(logger.handlers):
        if replace_all or isinstance(existing, ApplicationHandler):
            logger.removeHandler(existing)
    logger.addHandler(handler)


def configure_logging(settings: Settings) -> None:
    """Install the JSON handler and the redaction filter on the process.

    The call is idempotent: a second call replaces the handler rather than
    duplicating every log line.
    """
    handler = _build_handler(settings)
    root = logging.getLogger()
    root.setLevel(settings.log_level)
    root.addFilter(SECRET_REDACTING_FILTER)
    _install_handler(root, handler)
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "uvicorn.asgi", "fastapi"):
        logger = logging.getLogger(name)
        logger.setLevel(settings.log_level)
        logger.addFilter(SECRET_REDACTING_FILTER)
        logger.propagate = False
        _install_handler(logger, handler, replace_all=True)


def get_logger(name: str) -> logging.Logger:
    """Return a logger that carries the redaction filter."""
    logger = logging.getLogger(name)
    if not any(isinstance(existing, SecretRedactingFilter) for existing in logger.filters):
        logger.addFilter(SECRET_REDACTING_FILTER)
    return logger
