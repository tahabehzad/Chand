"""P0-T07 / CR-04…CR-07: synthetic-only blind-index evidence.

Every identifier used here is synthetic.  The suite pins the published
normalisation rule (SPEC-AUTH-001 §8.6), the tenant/field separation and the
fail-closed key path.  Database-level properties of CR-05 (the pepper is absent
from the database) and the < 1 ms B-Tree lookup need PostgreSQL and are
therefore NOT RUN here.
"""

from __future__ import annotations

import hashlib
import hmac
import traceback
from uuid import UUID

import pytest

from app.core.security.blind_index import (
    DIGEST_HEX_CHARS,
    PEPPER_MIN_BYTES,
    BlindIndexField,
    BlindIndexPepperUnavailableError,
    BlindIndexService,
    BlindIndexValueInvalidError,
    normalise,
)

TENANT = UUID(int=1)
OTHER_TENANT = UUID(int=2)
SYNTHETIC_PEPPER = b"p" * PEPPER_MIN_BYTES
SYNTHETIC_NATIONAL_ID = "0012345678"
SYNTHETIC_MOBILE = "09123456789"
SYNTHETIC_SHEBA = "IR" + "0" * 24
# A private marker that must never reach a message, a log line or a traceback.
SYNTHETIC_MARKER = "synthetic-private-marker"


class StubPepperRegistry:
    """Test-only registry; records calls so a retry/fallback would be visible."""

    def __init__(self, pepper: bytes = SYNTHETIC_PEPPER) -> None:
        self._pepper = pepper
        self.calls = 0

    def get_pepper(self) -> bytes:
        self.calls += 1
        return self._pepper


@pytest.fixture
def service() -> BlindIndexService:
    return BlindIndexService(StubPepperRegistry())


def test_digest_has_the_published_shape(service: BlindIndexService) -> None:
    digest = service.index(
        SYNTHETIC_NATIONAL_ID, tenant_id=TENANT, field=BlindIndexField.NATIONAL_ID
    )
    assert len(digest) == DIGEST_HEX_CHARS
    assert digest == digest.lower()
    assert all(character in "0123456789abcdef" for character in digest)


def test_digest_is_deterministic(service: BlindIndexService) -> None:
    digests = {
        service.index(SYNTHETIC_NATIONAL_ID, tenant_id=TENANT, field=BlindIndexField.NATIONAL_ID)
        for _ in range(64)
    }
    assert len(digests) == 1


@pytest.mark.parametrize(
    "spelling",
    [
        "0012345678",
        " 0012345678 ",
        "00-1234-5678",
        "0012 345 678",
        "\u200f0012345678\u200e",
        "\u20660012345678\u2069",
        "۰۰۱۲۳۴۵۶۷۸",  # Persian digits
        "٠٠١٢٣٤٥٦٧٨",  # Arabic-Indic digits
        "۰۰۱۲\u200c۳۴۵۶۷۸",  # ZWNJ inside a Persian form
        "００１２３４５６７８",  # fullwidth digits (NFKC)
    ],
)
def test_every_documented_national_id_spelling_hashes_identically(
    spelling: str, service: BlindIndexService
) -> None:
    expected = service.index(
        SYNTHETIC_NATIONAL_ID, tenant_id=TENANT, field=BlindIndexField.NATIONAL_ID
    )
    assert service.index(spelling, tenant_id=TENANT, field=BlindIndexField.NATIONAL_ID) == expected


def test_leading_zeros_are_identity() -> None:
    assert normalise("0012345678", field=BlindIndexField.NATIONAL_ID) == "0012345678"
    assert normalise("0112345678", field=BlindIndexField.NATIONAL_ID) == "0112345678"


def test_a_padded_or_truncated_national_id_is_refused(service: BlindIndexService) -> None:
    for value in ("12345678", "00123456789", "999999999"):
        with pytest.raises(BlindIndexValueInvalidError):
            service.index(value, tenant_id=TENANT, field=BlindIndexField.NATIONAL_ID)


@pytest.mark.parametrize(
    "spelling",
    [
        "09123456789",
        "+989123456789",
        "00989123456789",
        "989123456789",
        "0912 345 6789",
        "۰۹۱۲۳۴۵۶۷۸۹",
    ],
)
def test_mobile_international_forms_share_one_canonical_digest(
    spelling: str, service: BlindIndexService
) -> None:
    expected = service.index(SYNTHETIC_MOBILE, tenant_id=TENANT, field=BlindIndexField.MOBILE)
    assert service.index(spelling, tenant_id=TENANT, field=BlindIndexField.MOBILE) == expected
    assert normalise(spelling, field=BlindIndexField.MOBILE) == SYNTHETIC_MOBILE


@pytest.mark.parametrize("value", ["0212345678", "0912345678", "091234567890", "not-a-mobile"])
def test_a_non_mobile_number_is_refused(value: str, service: BlindIndexService) -> None:
    with pytest.raises(BlindIndexValueInvalidError):
        service.index(value, tenant_id=TENANT, field=BlindIndexField.MOBILE)


@pytest.mark.parametrize(
    "spelling",
    [
        SYNTHETIC_SHEBA,
        SYNTHETIC_SHEBA.lower(),
        "ir" + " 0000 0000 0000 0000 0000 0000",
        "IR-0000-0000-0000-0000-0000-0000",
    ],
)
def test_sheba_grouping_and_case_are_presentation_only(
    spelling: str, service: BlindIndexService
) -> None:
    expected = service.index(SYNTHETIC_SHEBA, tenant_id=TENANT, field=BlindIndexField.SHEBA)
    assert service.index(spelling, tenant_id=TENANT, field=BlindIndexField.SHEBA) == expected
    assert normalise(spelling, field=BlindIndexField.SHEBA) == SYNTHETIC_SHEBA


@pytest.mark.parametrize("value", ["IR" + "0" * 23, "IR" + "0" * 25, "DE" + "0" * 24, ""])
def test_an_invalid_sheba_is_refused(value: str, service: BlindIndexService) -> None:
    with pytest.raises(BlindIndexValueInvalidError):
        service.index(value, tenant_id=TENANT, field=BlindIndexField.SHEBA)


def test_two_tenants_never_share_a_digest(service: BlindIndexService) -> None:
    first = service.index(
        SYNTHETIC_NATIONAL_ID, tenant_id=TENANT, field=BlindIndexField.NATIONAL_ID
    )
    second = service.index(
        SYNTHETIC_NATIONAL_ID, tenant_id=OTHER_TENANT, field=BlindIndexField.NATIONAL_ID
    )
    assert first != second


def test_field_is_bound_into_the_digest(service: BlindIndexService) -> None:
    # Independently spelled variant of the published message: the tenant and
    # field must both be in the authenticated message, not only the value.
    def digest_for(field: str) -> str:
        message = b"pish:bindex:v1\x00" + TENANT.hex.encode("ascii") + b"\x00"
        return hmac.new(
            SYNTHETIC_PEPPER,
            message + field.encode("ascii") + b"\x00" + SYNTHETIC_NATIONAL_ID.encode("ascii"),
            hashlib.sha256,
        ).hexdigest()

    assert service.index(
        SYNTHETIC_NATIONAL_ID, tenant_id=TENANT, field=BlindIndexField.NATIONAL_ID
    ) == digest_for("national_id")
    assert digest_for("national_id") != digest_for("mobile")


def test_invalid_input_never_reaches_the_error_message(
    service: BlindIndexService,
) -> None:
    with pytest.raises(BlindIndexValueInvalidError) as caught:
        service.index(SYNTHETIC_MARKER, tenant_id=TENANT, field=BlindIndexField.NATIONAL_ID)
    rendered = "".join(traceback.format_exception(caught.value))
    assert SYNTHETIC_MARKER not in rendered
    assert str(caught.value) == "National ID is not ten digits."


@pytest.mark.parametrize("pepper", [b"", b"p" * (PEPPER_MIN_BYTES - 1), "p" * 64])
def test_an_unusable_pepper_fails_closed(pepper: bytes) -> None:
    # A guarded registry would already reject a str pepper; the service must
    # refuse it even when the registry hands one back anyway.
    registry = StubPepperRegistry(pepper)
    service = BlindIndexService(registry)
    with pytest.raises(
        BlindIndexPepperUnavailableError, match=r"^Blind-index pepper unavailable\.$"
    ):
        service.index(SYNTHETIC_NATIONAL_ID, tenant_id=TENANT, field=BlindIndexField.NATIONAL_ID)
    assert registry.calls == 1


def test_a_registry_failure_is_not_retried_and_does_not_leak() -> None:
    class UnavailableRegistry:
        def __init__(self) -> None:
            self.calls = 0

        def get_pepper(self) -> bytes:
            self.calls += 1
            raise RuntimeError(SYNTHETIC_MARKER)

    registry = UnavailableRegistry()
    service = BlindIndexService(registry)
    with pytest.raises(BlindIndexPepperUnavailableError) as caught:
        service.index(SYNTHETIC_NATIONAL_ID, tenant_id=TENANT, field=BlindIndexField.NATIONAL_ID)
    assert registry.calls == 1
    assert SYNTHETIC_MARKER not in "".join(traceback.format_exception(caught.value))


def test_the_pepper_is_read_per_call_and_never_cached() -> None:
    rotating = BlindIndexService(StubPepperRegistry(b"a" * 32))
    other = BlindIndexService(StubPepperRegistry(b"b" * 32))
    assert rotating.index(SYNTHETIC_MOBILE, tenant_id=TENANT, field=BlindIndexField.MOBILE) != (
        other.index(SYNTHETIC_MOBILE, tenant_id=TENANT, field=BlindIndexField.MOBILE)
    )


def test_indexing_emits_no_output(
    service: BlindIndexService, capsys: pytest.CaptureFixture[str]
) -> None:
    service.index(SYNTHETIC_NATIONAL_ID, tenant_id=TENANT, field=BlindIndexField.NATIONAL_ID)
    captured = capsys.readouterr()
    assert not captured.out and not captured.err


def test_the_tenant_must_be_a_uuid(service: BlindIndexService) -> None:
    with pytest.raises(BlindIndexValueInvalidError):
        service.index(
            SYNTHETIC_NATIONAL_ID,
            tenant_id="00000000-0000-0000-0000-000000000001",  # type: ignore[arg-type]
            field=BlindIndexField.NATIONAL_ID,
        )


@pytest.mark.parametrize("value", [None, 1234567890, b"0012345678"])
def test_a_non_text_identifier_is_refused(value: object, service: BlindIndexService) -> None:
    with pytest.raises(BlindIndexValueInvalidError):
        service.index(value, tenant_id=TENANT, field=BlindIndexField.NATIONAL_ID)  # type: ignore[arg-type]
