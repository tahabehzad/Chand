"""P0-T06: authenticated field encryption under ADR-003 and AUTH §8.5.

No key persistence, active-key selection, logging or financial conversion
occurs here. Production key custody/rotation is delegated to P0-T08.
"""

from __future__ import annotations

import json
import secrets
from dataclasses import dataclass
from typing import Final, Protocol
from uuid import UUID

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

NONCE_BYTES: Final[int] = 12
TAG_BYTES: Final[int] = 16
KEY_BYTES: Final[int] = 32
_DOMAIN: Final[bytes] = b"pish:pii:v1\x00"


class PiiEncryptionError(RuntimeError):
    """Encryption could not complete; the message carries no input data."""


class PiiDecryptionError(RuntimeError):
    """No authenticated plaintext is available."""


class PiiKeyUnavailableError(RuntimeError):
    """The requested tenant/version key is unavailable or invalid."""


@dataclass(frozen=True, slots=True, repr=False)
class EncryptionContext:
    """Explicit non-secret binding of tenant, record, schema field and DEK reference."""

    tenant_id: UUID
    record_id: UUID
    field_name: str
    key_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.tenant_id, UUID) or not isinstance(self.record_id, UUID):
            raise ValueError("Encryption context identifiers must be UUIDs.")
        for name in (self.field_name, self.key_id):
            if (
                not isinstance(name, str)
                or not name.strip()
                or len(name) > 128
                or not name.isprintable()
            ):
                raise ValueError(
                    "Encryption context names must be printable, nonempty and bounded."
                )


class TenantKeyRegistry(Protocol):
    """Retrieve one explicit unwrapped tenant DEK; never silently fall back.

    Implementations own authorization and key custody. They must not store
    or log plaintext key material in a database or diagnostic stream.
    """

    def get_key(self, *, tenant_id: UUID, key_id: str) -> bytes:
        """Return exactly 32 key bytes, or raise when unavailable."""
        ...


def _associated_data(context: EncryptionContext) -> bytes:
    payload = {
        "field": context.field_name,
        "key_id": context.key_id,
        "record": context.record_id.hex,
        "tenant": context.tenant_id.hex,
    }
    return _DOMAIN + json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


class PiiFieldTransformer:
    """AES-256-GCM with a fresh 96-bit nonce and context authentication.

    The stored value is nonce || ciphertext || full 128-bit tag. The caller
    retains the explicit key reference and original context separately.
    """

    def __init__(self, key_registry: TenantKeyRegistry) -> None:
        self._key_registry = key_registry

    def _get_key(self, context: EncryptionContext) -> bytes:
        try:
            key = self._key_registry.get_key(tenant_id=context.tenant_id, key_id=context.key_id)
        except Exception:
            # Adapter exceptions may contain credentials. Do not render
            # their values, messages or exception chain in application logs.
            raise PiiKeyUnavailableError("Encryption key unavailable.") from None
        if not isinstance(key, bytes) or len(key) != KEY_BYTES:
            raise PiiKeyUnavailableError("Encryption key unavailable.")
        return key

    def encrypt(self, value: bytes, *, context: EncryptionContext) -> bytes:
        """Encrypt bytes without coercion, normalization, logging or key fallback."""
        if not isinstance(value, bytes) or not isinstance(context, EncryptionContext):
            raise PiiEncryptionError("Invalid encryption input.")
        key = self._get_key(context)
        try:
            nonce = secrets.token_bytes(NONCE_BYTES)
            return nonce + AESGCM(key).encrypt(nonce, value, _associated_data(context))
        except (OSError, OverflowError, TypeError, ValueError):
            raise PiiEncryptionError("PII encryption failed.") from None

    def decrypt(self, value: bytes, *, context: EncryptionContext) -> bytes:
        """Return plaintext only after successful authentication of bytes and context."""
        if (
            not isinstance(value, bytes)
            or len(value) < NONCE_BYTES + TAG_BYTES
            or not isinstance(context, EncryptionContext)
        ):
            raise PiiDecryptionError("PII decryption failed.")
        key = self._get_key(context)
        try:
            return AESGCM(key).decrypt(
                value[:NONCE_BYTES], value[NONCE_BYTES:], _associated_data(context)
            )
        except (InvalidTag, OverflowError, TypeError, ValueError):
            raise PiiDecryptionError("PII decryption failed.") from None

    def encrypt_text(self, value: str, *, context: EncryptionContext) -> bytes:
        """Encode text as UTF-8 without changing Persian text, digits or ZWNJ."""
        if not isinstance(value, str):
            raise PiiEncryptionError("Invalid encryption input.")
        try:
            encoded = value.encode("utf-8")
        except UnicodeError:
            raise PiiEncryptionError("PII encryption failed.") from None
        return self.encrypt(encoded, context=context)

    def decrypt_text(self, value: bytes, *, context: EncryptionContext) -> str:
        """Decode authenticated UTF-8; reject authenticated non-text as text."""
        plaintext = self.decrypt(value, context=context)
        try:
            return plaintext.decode("utf-8")
        except UnicodeError:
            raise PiiDecryptionError("PII decryption failed.") from None
