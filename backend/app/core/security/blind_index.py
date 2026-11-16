"""P0-T07: HMAC-SHA256 blind index under ADR-003 and SPEC-AUTH-001 §8.

Authority
---------
``docs/adr/ADR-003-sensitive-data-encryption-alee-blind-indexing.md``
(directives 2-3: exact-match lookup on National ID / mobile / Sheba through a
deterministic HMAC-SHA256 digest, never ``pgcrypto``);
``docs/specs/AUTH.md`` §5.6 and §8.1-§8.2 (isolated pepper, one digest per
tenant and field); ``docs/PISH_HESABDARI_HOLY_BIBLE.md`` §5.6 (the corpus does
not fix the normalisation rule, so ``P0-T07`` owns it — QB-10, HB-MR-011) and
``AGENTS.md`` §2 invariant 13.
Related: WBS P0-T07 · CR-04…CR-07 · ``docs/specs/AUTH.md`` §8.6.

Why a normalisation rule is part of this module
----------------------------------------------
A blind index is only useful if two spellings of the same identifier produce
the same digest.  The corpus does not fix that rule (HB §5.6), so leaving it
to each caller would silently break duplicate detection — two engineers, two
rules, two digests for one National ID.  The rule is therefore implemented
here, once, and published in SPEC-AUTH-001 §8.6:

* digits are folded from Persian (U+06F0…U+06F9) and Arabic-Indic
  (U+0660…U+0669) to ASCII before hashing;
* layout and presentation characters (LRM/RLM, embedding/isolate controls,
  BOM, NBSP, ZWNJ between digits, hyphen/en-dash, dot) are removed for the
  three structured identifiers, because they are typographic artefacts of a
  Persian form, not part of the identifier;
* leading zeros are **kept**: ``0012345678`` and ``12345678`` are different
  National IDs, so no trimming or padding is applied;
* the canonical form is then strictly validated (10 digits for a National ID,
  ``09`` + 9 digits for a mobile, ``IR`` + 24 digits for a Sheba);
* anything that does not validate is refused, never hashed: a blind index over
  a malformed identifier would create an undetectable false match.

Key discipline
--------------
ADR-003 mandates an isolated enterprise pepper that is not derivable from any
stored data.  SPEC-AUTH-001 §8.1 draws a per-tenant blind-index key while §8.2
describes one platform-wide pepper; both readings are satisfied without
choosing a key-custody backend: the pepper is a single injected secret, and the
tenant identity is bound into the authenticated message, which gives the same
separation a per-tenant salt would (a digest is therefore valid for exactly one
tenant and one field).  Custody, storage and rotation of the pepper belong to
P0-T08 and are deliberately not implemented here — no registry, no fallback, no
cache, no default pepper.

Everything else
---------------
No logging, no I/O, no clock, no randomness: ``index()`` is a pure function of
``(pepper, tenant_id, field, value)``.  Failures raise a fixed message that
contains neither the supplied identifier nor key material.
"""

from __future__ import annotations

import hashlib
import hmac
import re
import unicodedata
from enum import StrEnum
from typing import Final, Protocol
from uuid import UUID

PEPPER_MIN_BYTES: Final[int] = 32
DIGEST_HEX_CHARS: Final[int] = 64

_DOMAIN: Final[bytes] = b"pish:bindex:v1"

# Persian (Extended Arabic-Indic) and Arabic-Indic digits, folded to ASCII.
_DIGIT_FOLD: Final[dict[int, str]] = {
    **{0x06F0 + offset: str(offset) for offset in range(10)},
    **{0x0660 + offset: str(offset) for offset in range(10)},
}

# Presentation characters that carry no identity.  ZWNJ (U+200C) is absent on
# purpose: it is removed only *between digits*, and preserved everywhere else
# because SPEC-FE-001 §3.4 requires it to survive hashing of text.
_LAYOUT_CHARS: Final[str] = (
    "\u200e\u200f"  # LRM, RLM
    "\u202a\u202b\u202c\u202d\u202e"  # LRE…RLO
    "\u2066\u2067\u2068\u2069"  # LRI…PDI
    "\ufeff"  # BOM / ZWNBSP
)

_SEPARATORS: Final[str] = " +\u200c-\u2010\u2011\u2012\u2013\u2014._\u00a0\t"

_NATIONAL_ID_PATTERN: Final[re.Pattern[str]] = re.compile(r"[0-9]{10}")
_MOBILE_PATTERN: Final[re.Pattern[str]] = re.compile(r"09[0-9]{9}")
_SHEBA_PATTERN: Final[re.Pattern[str]] = re.compile(r"IR[0-9]{24}")


class BlindIndexError(RuntimeError):
    """A blind index could not be produced; the message carries no value."""


class BlindIndexPepperUnavailableError(BlindIndexError):
    """The pepper is missing, malformed or unusable."""


class BlindIndexValueInvalidError(BlindIndexError):
    """The identifier cannot be canonicalised into the documented form."""


class BlindIndexField(StrEnum):
    """The identifier kinds the schema indexes (SPEC-AUTH-001 §5.6, §7.3)."""

    NATIONAL_ID = "national_id"
    MOBILE = "mobile"
    SHEBA = "sheba"


class BlindIndexPepperRegistry(Protocol):
    """Retrieve the single isolated pepper; never infer, derive or fall back.

    Implementations own custody (Vault or the encrypted local master config,
    P0-T08).  They must not keep the pepper in the database, in application
    logs, or in an exception message.
    """

    def get_pepper(self) -> bytes:
        """Return at least 32 pepper bytes, or raise when unavailable."""
        ...


def _strip_layout(value: str) -> str:
    return "".join(char for char in value if char not in _LAYOUT_CHARS)


def _fold_digits(value: str) -> str:
    return _strip_layout(unicodedata.normalize("NFKC", value)).translate(_DIGIT_FOLD)


def _canonical_digits(value: str) -> str:
    return "".join(char for char in _fold_digits(value) if char not in _SEPARATORS)


def normalise(value: str, *, field: BlindIndexField) -> str:
    """Return the one canonical spelling of an identifier.

    Public because the canonical form is also what a human-facing comparison
    shows and what the tests pin; hashing is a separate step.
    """
    if not isinstance(value, str):
        raise BlindIndexValueInvalidError("Blind-index value must be text.")
    if not isinstance(field, BlindIndexField):
        raise BlindIndexValueInvalidError("Blind-index field is not supported.")

    digits = _canonical_digits(value)

    if field is BlindIndexField.NATIONAL_ID:
        # Length and leading zeros are identity: never trim, pad or truncate.
        if _NATIONAL_ID_PATTERN.fullmatch(digits) is None:
            raise BlindIndexValueInvalidError("National ID is not ten digits.")
        return digits

    if field is BlindIndexField.MOBILE:
        # Accept the international forms a Persian form will produce, then
        # keep exactly one canonical national form: 09xxxxxxxxx.
        national = digits
        if national.startswith("0098"):
            national = national[4:]
        elif national.startswith("98") and len(national) == 12:
            national = national[2:]
        if national and not national.startswith("0"):
            national = f"0{national}"
        if _MOBILE_PATTERN.fullmatch(national) is None:
            raise BlindIndexValueInvalidError("Mobile number is not a national mobile.")
        return national

    # SHEBA: the country prefix is Latin in every printed form, so the value is
    # upper-cased before validation; digits were already folded.
    sheba = digits.upper()
    if _SHEBA_PATTERN.fullmatch(sheba) is None:
        raise BlindIndexValueInvalidError("Sheba number is not IR plus twenty-four digits.")
    return sheba


def _message(*, tenant_id: UUID, field: BlindIndexField, canonical: str) -> bytes:
    """Bind tenant, field and value into one unambiguous authenticated message.

    Every component is ASCII and NUL-separated, so no split of the value can be
    read as a different tenant or field (no length-prefix ambiguity for these
    fixed alphabets).
    """
    return b"\x00".join(
        (
            _DOMAIN,  # no trailing NUL: the join supplies every separator
            tenant_id.hex.encode("ascii"),
            field.value.encode("ascii"),
            canonical.encode("ascii"),
        )
    )


class BlindIndexService:
    """Produce the ``CHAR(64)`` hex blind index stored next to a ciphertext."""

    def __init__(self, pepper_registry: BlindIndexPepperRegistry) -> None:
        self._pepper_registry = pepper_registry

    def _pepper(self) -> bytes:
        try:
            pepper = self._pepper_registry.get_pepper()
        except Exception:
            # Registry exceptions may describe custody or credentials; the
            # value, message and chain are suppressed (AUTH §8.5 discipline).
            raise BlindIndexPepperUnavailableError("Blind-index pepper unavailable.") from None
        if not isinstance(pepper, bytes) or len(pepper) < PEPPER_MIN_BYTES:
            raise BlindIndexPepperUnavailableError("Blind-index pepper unavailable.")
        return pepper

    def index(self, value: str, *, tenant_id: UUID, field: BlindIndexField) -> str:
        """Return the lowercase hex HMAC-SHA256 digest for one tenant and field.

        Deterministic for the same ``(tenant_id, field, value)``; a different
        tenant or field yields a different digest even for identical values.
        """
        if not isinstance(tenant_id, UUID):
            raise BlindIndexValueInvalidError("Blind-index tenant must be a UUID.")
        canonical = normalise(value, field=field)
        digest = hmac.new(
            self._pepper(),
            _message(tenant_id=tenant_id, field=field, canonical=canonical),
            hashlib.sha256,
        ).hexdigest()
        if len(digest) != DIGEST_HEX_CHARS:  # pragma: no cover - structural guard
            raise BlindIndexError("Blind-index digest has an unexpected length.")
        return digest


__all__ = [
    "DIGEST_HEX_CHARS",
    "PEPPER_MIN_BYTES",
    "BlindIndexError",
    "BlindIndexField",
    "BlindIndexPepperRegistry",
    "BlindIndexPepperUnavailableError",
    "BlindIndexService",
    "BlindIndexValueInvalidError",
    "normalise",
]
