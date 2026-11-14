"""P0-T06/CR-01…03: synthetic-only field-encryption and failure-path evidence."""

from __future__ import annotations

import logging
import traceback
from dataclasses import FrozenInstanceError, replace
from uuid import UUID

import pytest
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import Settings
from app.core.logging import configure_logging, get_logger
from app.core.security.pii_transformer import (
    KEY_BYTES,
    NONCE_BYTES,
    TAG_BYTES,
    EncryptionContext,
    PiiDecryptionError,
    PiiEncryptionError,
    PiiFieldTransformer,
    PiiKeyUnavailableError,
)

TENANT = UUID(int=1)
RECORD = UUID(int=2)
SYNTHETIC_KEY = b"k" * KEY_BYTES
SYNTHETIC_TEXT = "synthetic-private-marker"


class StubRegistry:
    """Test-only registry, deliberately sharing bytes to test AAD isolation."""

    def __init__(self, key: bytes = SYNTHETIC_KEY) -> None:
        self._key = key
        self.calls: list[tuple[UUID, str]] = []

    def get_key(self, *, tenant_id: UUID, key_id: str) -> bytes:
        self.calls.append((tenant_id, key_id))
        return self._key


@pytest.fixture
def context() -> EncryptionContext:
    return EncryptionContext(TENANT, RECORD, "synthetic_field", "dek-v1")


@pytest.fixture
def transformer() -> PiiFieldTransformer:
    return PiiFieldTransformer(StubRegistry())


@pytest.mark.parametrize("plaintext", [b"", b"synthetic", bytes(range(256)), b"\x00\xff\x00"])
def test_binary_round_trip_and_adr003_layout(
    plaintext: bytes, transformer: PiiFieldTransformer, context: EncryptionContext
) -> None:
    encrypted = transformer.encrypt(plaintext, context=context)
    assert encrypted != plaintext
    assert len(encrypted) == len(plaintext) + NONCE_BYTES + TAG_BYTES
    assert transformer.decrypt(encrypted, context=context) == plaintext


@pytest.mark.parametrize("text", ["", "متن آزمایشی نیم‌فاصله ۱۲۳", "synthetic", "\x00"])
def test_text_preserves_exact_utf8(
    text: str, transformer: PiiFieldTransformer, context: EncryptionContext
) -> None:
    encrypted = transformer.encrypt_text(text, context=context)
    assert transformer.decrypt_text(encrypted, context=context) == text


def test_each_encryption_has_a_new_nonce(
    transformer: PiiFieldTransformer, context: EncryptionContext
) -> None:
    values = [transformer.encrypt(b"synthetic", context=context) for _ in range(128)]
    assert len(set(values)) == len(values)
    assert len({value[:NONCE_BYTES] for value in values}) == len(values)


@pytest.mark.parametrize("position", [0, NONCE_BYTES, -1])
def test_nonce_ciphertext_and_tag_tampering_fail_closed(
    position: int, transformer: PiiFieldTransformer, context: EncryptionContext
) -> None:
    value = bytearray(transformer.encrypt(b"synthetic", context=context))
    value[position] ^= 1
    with pytest.raises(PiiDecryptionError, match=r"^PII decryption failed\.$"):
        transformer.decrypt(bytes(value), context=context)


@pytest.mark.parametrize("length", [0, 1, 12, 27, 28, 30])
def test_truncated_values_never_return_plaintext(
    length: int, transformer: PiiFieldTransformer, context: EncryptionContext
) -> None:
    value = transformer.encrypt(b"synthetic", context=context)[:length]
    with pytest.raises(PiiDecryptionError):
        transformer.decrypt(value, context=context)


@pytest.mark.parametrize("axis", ["tenant", "record", "field", "key"])
def test_context_substitution_fails_even_with_identical_key_bytes(
    axis: str, transformer: PiiFieldTransformer, context: EncryptionContext
) -> None:
    changed = {
        "tenant": replace(context, tenant_id=UUID(int=3)),
        "record": replace(context, record_id=UUID(int=3)),
        "field": replace(context, field_name="other_field"),
        "key": replace(context, key_id="dek-v2"),
    }[axis]
    encrypted = transformer.encrypt(b"synthetic", context=context)
    with pytest.raises(PiiDecryptionError):
        transformer.decrypt(encrypted, context=changed)


@pytest.mark.parametrize("length", [0, 16, 24, 31, 33])
def test_only_aes256_keys_are_accepted(length: int, context: EncryptionContext) -> None:
    transformer = PiiFieldTransformer(StubRegistry(b"k" * length))
    with pytest.raises(PiiKeyUnavailableError, match=r"^Encryption key unavailable\.$"):
        transformer.encrypt(b"synthetic", context=context)
    encrypted = PiiFieldTransformer(StubRegistry()).encrypt(b"synthetic", context=context)
    with pytest.raises(PiiKeyUnavailableError):
        transformer.decrypt(encrypted, context=context)


def test_registry_failure_does_not_leak_into_tracebacks_or_logs(
    context: EncryptionContext, capsys: pytest.CaptureFixture[str]
) -> None:
    class UnavailableRegistry:
        def get_key(self, *, tenant_id: UUID, key_id: str) -> bytes:
            raise RuntimeError(SYNTHETIC_TEXT)

    original_handlers = logging.getLogger().handlers[:]
    try:
        configure_logging(Settings(_env_file=None))
        transformer = PiiFieldTransformer(UnavailableRegistry())
        with pytest.raises(PiiKeyUnavailableError) as caught:
            transformer.encrypt(SYNTHETIC_TEXT.encode(), context=context)
        rendered = "".join(traceback.format_exception(caught.value))
        assert SYNTHETIC_TEXT not in rendered
        assert SYNTHETIC_KEY.decode() not in rendered
        try:
            transformer.decrypt(b"x" * 40, context=context)
        except PiiKeyUnavailableError:
            get_logger("app.tests.crypto").exception("encryption_unavailable")
        out = capsys.readouterr().out
        assert SYNTHETIC_TEXT not in out
        assert SYNTHETIC_KEY.decode() not in out
        assert "encryption_unavailable" in out
    finally:
        logging.getLogger().handlers[:] = original_handlers


def test_wrong_key_is_not_retried_with_another_key(context: EncryptionContext) -> None:
    encrypted = PiiFieldTransformer(StubRegistry()).encrypt(b"synthetic", context=context)
    wrong = StubRegistry(b"w" * KEY_BYTES)
    with pytest.raises(PiiDecryptionError):
        PiiFieldTransformer(wrong).decrypt(encrypted, context=context)
    assert wrong.calls == [(TENANT, "dek-v1")]


def test_context_is_immutable_and_not_rendered(context: EncryptionContext) -> None:
    with pytest.raises(FrozenInstanceError):
        context.key_id = "other"  # type: ignore[misc]
    assert context.field_name not in repr(context)
    assert context.key_id not in repr(context)


@pytest.mark.parametrize("name", ["", " ", "x" * 129, "field\nname"])
def test_context_rejects_invalid_metadata(name: str) -> None:
    with pytest.raises(ValueError):
        EncryptionContext(TENANT, RECORD, name, "dek-v1")
    with pytest.raises(ValueError):
        EncryptionContext(TENANT, RECORD, "field", name)


def test_binary_plaintext_cannot_be_mistaken_for_utf8(
    transformer: PiiFieldTransformer, context: EncryptionContext
) -> None:
    encrypted = transformer.encrypt(b"\xff", context=context)
    with pytest.raises(PiiDecryptionError):
        transformer.decrypt_text(encrypted, context=context)


def test_ciphertext_interoperates_with_documented_aad_format(context: EncryptionContext) -> None:
    # Independently spelled contract: this must not import the production AAD helper.
    aad = (
        b'pish:pii:v1\x00{"field":"synthetic_field","key_id":"dek-v1",'
        b'"record":"00000000000000000000000000000002",'
        b'"tenant":"00000000000000000000000000000001"}'
    )
    encrypted = PiiFieldTransformer(StubRegistry()).encrypt(b"synthetic", context=context)
    assert AESGCM(SYNTHETIC_KEY).decrypt(encrypted[:12], encrypted[12:], aad) == b"synthetic"


def test_text_encoding_failure_has_a_fixed_error(
    transformer: PiiFieldTransformer, context: EncryptionContext
) -> None:
    with pytest.raises(PiiEncryptionError, match=r"^PII encryption failed\.$"):
        transformer.encrypt_text("\ud800", context=context)


@pytest.mark.parametrize(
    "field", ["national_id", "mobile", "sheba", "candidate_name", "salary_rial"]
)
def test_supported_sensitive_field_representations_do_not_emit_plaintext_or_keys(
    field: str,
    transformer: PiiFieldTransformer,
    context: EncryptionContext,
    capsys: pytest.CaptureFixture[str],
) -> None:
    field_context = replace(context, field_name=field)
    encrypted = transformer.encrypt_text(SYNTHETIC_TEXT, context=field_context)
    assert transformer.decrypt_text(encrypted, context=field_context) == SYNTHETIC_TEXT
    captured = capsys.readouterr()
    assert not captured.out and not captured.err


def test_nonce_source_failure_does_not_expose_its_exception(
    transformer: PiiFieldTransformer,
    context: EncryptionContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def unavailable(nbytes: int) -> bytes:
        raise OSError(SYNTHETIC_TEXT)

    monkeypatch.setattr("app.core.security.pii_transformer.secrets.token_bytes", unavailable)
    with pytest.raises(PiiEncryptionError) as caught:
        transformer.encrypt(b"synthetic", context=context)
    assert SYNTHETIC_TEXT not in "".join(traceback.format_exception(caught.value))
