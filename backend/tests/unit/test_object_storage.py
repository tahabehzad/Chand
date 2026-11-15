"""P0-T11 synthetic unit tests for the tenant-scoped WORM S3 adapter.

No live S3/RGW endpoint is contacted. The real-bucket acceptance criterion
(upload succeeds, the standard credential cannot delete, and the runtime
credential lacks ``s3:BypassGovernanceRetention``) remains ``NOT RUN`` until a
local RGW integration environment exists.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import MagicMock, call
from uuid import UUID

import pytest
from botocore.exceptions import ClientError

from app.storage.s3_adapter import (
    GOVERNANCE_MODE,
    GOVERNANCE_RETENTION_DAYS,
    InvalidStorageKeyError,
    ObjectAlreadyExistsError,
    S3ObjectStorage,
    StorageConfigurationError,
    StorageInputError,
    StorageIntegrityError,
    StorageOperationError,
)

TENANT = UUID("11111111-1111-1111-1111-111111111111")
OTHER_TENANT = UUID("22222222-2222-2222-2222-222222222222")
BUCKET = "pish-synthetic"
NOW = datetime(2026, 11, 15, 9, 30, tzinfo=UTC)
EXPECTED_UNTIL = NOW + timedelta(days=GOVERNANCE_RETENTION_DAYS)
VERSION_ID = "synthetic-version-1"
ETAG = '"synthetic-etag-1"'


def _versioning(status: str = "Enabled") -> dict[str, Any]:
    return {"Status": status} if status else {}


def _lock(
    mode: str = "GOVERNANCE",
    *,
    days: int | None = 3650,
    enabled: str = "Enabled",
) -> dict[str, Any]:
    configuration: dict[str, Any] = {"ObjectLockEnabled": enabled}
    retention: dict[str, Any] = {"Mode": mode}
    if days is not None:
        retention["Days"] = days
    configuration["Rule"] = {"DefaultRetention": retention}
    return {"ObjectLockConfiguration": configuration}


def _client_error(code: str, status: int, message: str = "synthetic") -> ClientError:
    return ClientError(
        {
            "Error": {"Code": code, "Message": message},
            "ResponseMetadata": {"HTTPStatusCode": status},
        },
        "SyntheticS3Operation",
    )


def _not_found() -> ClientError:
    return _client_error("NoSuchKey", 404)


def _put_receipt(
    version_id: str = VERSION_ID,
    etag: str = ETAG,
) -> dict[str, Any]:
    return {"VersionId": version_id, "ETag": etag}


def _head_receipt(
    *,
    version_id: str = VERSION_ID,
    mode: str = GOVERNANCE_MODE,
    retain_until: datetime = EXPECTED_UNTIL,
    etag: str = ETAG,
) -> dict[str, Any]:
    return {
        "VersionId": version_id,
        "ETag": etag,
        "ObjectLockMode": mode,
        "ObjectLockRetainUntilDate": retain_until,
    }


def _new_client() -> MagicMock:
    client = MagicMock()
    client.get_bucket_versioning.return_value = _versioning()
    client.get_object_lock_configuration.return_value = _lock()
    client.put_object.return_value = _put_receipt()
    return client


def _adapter(client: MagicMock, *, clock: Any = None) -> S3ObjectStorage:
    return S3ObjectStorage(
        client,
        bucket=BUCKET,
        clock=clock if clock is not None else (lambda: NOW),
    )


def test_put_writes_tenant_prefixed_governance_object_and_returns_receipt() -> None:
    client = _new_client()
    client.head_object.side_effect = [_not_found(), _head_receipt()]
    adapter = _adapter(client)

    result = adapter.put_object(
        tenant_id=TENANT,
        relative_key="documents/scan.pdf",
        body=b"synthetic-bytes",
        content_type="application/pdf",
    )

    expected_key = f"tenants/{TENANT}/documents/scan.pdf"
    client.get_bucket_versioning.assert_called_once_with(Bucket=BUCKET)
    client.get_object_lock_configuration.assert_called_once_with(Bucket=BUCKET)
    assert client.head_object.call_args_list == [
        call(Bucket=BUCKET, Key=expected_key),
        call(Bucket=BUCKET, Key=expected_key, VersionId=VERSION_ID),
    ]
    client.put_object.assert_called_once_with(
        Bucket=BUCKET,
        Key=expected_key,
        Body=b"synthetic-bytes",
        IfNoneMatch="*",
        ObjectLockMode=GOVERNANCE_MODE,
        ObjectLockRetainUntilDate=EXPECTED_UNTIL,
        ContentType="application/pdf",
    )
    assert result.bucket == BUCKET
    assert result.tenant_id == TENANT
    assert result.key == expected_key
    assert result.version_id == VERSION_ID
    assert result.etag == ETAG
    assert result.retention_mode == GOVERNANCE_MODE
    assert result.retain_until == EXPECTED_UNTIL


def test_governance_retention_is_3650_days_from_the_injected_clock() -> None:
    client = _new_client()
    client.head_object.side_effect = [_not_found(), _head_receipt()]
    adapter = _adapter(client)

    result = adapter.put_object(
        tenant_id=TENANT,
        relative_key="documents/scan.pdf",
        body=b"synthetic",
    )

    written = client.put_object.call_args.kwargs
    assert written["ObjectLockRetainUntilDate"] == NOW + timedelta(days=3650)
    assert written["ObjectLockMode"] == "GOVERNANCE"
    assert written["IfNoneMatch"] == "*"
    assert result.retain_until == EXPECTED_UNTIL


def test_different_tenants_cannot_share_a_key() -> None:
    client = _new_client()
    client.head_object.side_effect = [_not_found(), _head_receipt()]
    adapter = _adapter(client)

    first = adapter.put_object(
        tenant_id=TENANT, relative_key="documents/shared.pdf", body=b"synthetic"
    )
    client.head_object.side_effect = [_not_found(), _head_receipt()]
    second = adapter.put_object(
        tenant_id=OTHER_TENANT, relative_key="documents/shared.pdf", body=b"synthetic"
    )

    assert first.key == f"tenants/{TENANT}/documents/shared.pdf"
    assert second.key == f"tenants/{OTHER_TENANT}/documents/shared.pdf"
    assert first.key != second.key


def test_persian_filename_is_preserved_exactly() -> None:
    client = _new_client()
    client.head_object.side_effect = [_not_found(), _head_receipt()]
    adapter = _adapter(client)

    result = adapter.put_object(
        tenant_id=TENANT,
        relative_key="documents/پرونده‌ بیمه.pdf",
        body=b"synthetic",
    )

    assert result.key == f"tenants/{TENANT}/documents/پرونده‌ بیمه.pdf"


@pytest.mark.parametrize(
    "relative_key",
    [
        "",
        "/absolute.pdf",
        "documents/scan.pdf/",
        "documents//scan.pdf",
        "./scan.pdf",
        "documents/../scan.pdf",
        "documents/./scan.pdf",
        "documents\\scan.pdf",
        " documents/scan.pdf",
        "documents/scan.pdf ",
        "documents/\x00scan.pdf",
        "documents/\x1fscan.pdf",
        "documents/\x7fscan.pdf",
        "documents/\ud800scan.pdf",
        "documents/\udfffscan.pdf",
        "tenants/scan.pdf",
        "x" * 1024,
    ],
)
def test_unsafe_relative_keys_are_rejected_before_any_network_call(
    relative_key: str,
) -> None:
    client = _new_client()
    adapter = _adapter(client)

    with pytest.raises(InvalidStorageKeyError):
        adapter.put_object(
            tenant_id=TENANT,
            relative_key=relative_key,
            body=b"synthetic",
        )

    client.get_bucket_versioning.assert_not_called()
    client.put_object.assert_not_called()


def test_invalid_unicode_key_error_does_not_disclose_the_key() -> None:
    client = _new_client()
    adapter = _adapter(client)
    private_marker = "synthetic-private-marker"
    with pytest.raises(InvalidStorageKeyError) as raised:
        adapter.put_object(
            tenant_id=TENANT,
            relative_key=f"documents/{private_marker}\ud800.pdf",
            body=b"synthetic",
        )
    assert private_marker not in str(raised.value)
    assert raised.value.__suppress_context__ is True
    assert client.mock_calls == []


def test_tenant_must_be_a_uuid_not_a_string() -> None:
    client = _new_client()
    adapter = _adapter(client)

    with pytest.raises(InvalidStorageKeyError):
        adapter.put_object(
            tenant_id=str(TENANT),  # type: ignore[arg-type]
            relative_key="documents/scan.pdf",
            body=b"synthetic",
        )

    client.put_object.assert_not_called()


def test_body_and_content_type_are_typed_without_coercion() -> None:
    client = _new_client()
    adapter = _adapter(client)

    with pytest.raises(StorageInputError):
        adapter.put_object(
            tenant_id=TENANT,
            relative_key="documents/scan.pdf",
            body="not-bytes",  # type: ignore[arg-type]
        )
    with pytest.raises(StorageInputError):
        adapter.put_object(
            tenant_id=TENANT,
            relative_key="documents/scan.pdf",
            body=b"synthetic",
            content_type="application/pdf\ninjected: value",
        )

    client.get_bucket_versioning.assert_not_called()
    client.put_object.assert_not_called()


@pytest.mark.parametrize(
    "versioning",
    [
        {},
        {"Status": "Suspended"},
        {"Status": "Disabled"},
    ],
)
def test_bucket_versioning_must_be_enabled(versioning: dict[str, Any]) -> None:
    client = _new_client()
    client.get_bucket_versioning.return_value = versioning
    adapter = _adapter(client)

    with pytest.raises(StorageConfigurationError):
        adapter.put_object(
            tenant_id=TENANT,
            relative_key="documents/scan.pdf",
            body=b"synthetic",
        )

    client.head_object.assert_not_called()
    client.put_object.assert_not_called()


@pytest.mark.parametrize(
    "lock",
    [
        {},
        {"ObjectLockConfiguration": {}},
        {"ObjectLockConfiguration": {"ObjectLockEnabled": "Disabled"}},
        _lock(mode="COMPLIANCE"),
        _lock(mode="GOVERNANCE", days=None),
        {"ObjectLockConfiguration": {"ObjectLockEnabled": "Enabled", "Rule": "bad"}},
        {
            "ObjectLockConfiguration": {
                "ObjectLockEnabled": "Enabled",
                "Rule": {},
            }
        },
    ],
)
def test_bucket_object_lock_must_be_governance_and_well_formed(
    lock: dict[str, Any],
) -> None:
    client = _new_client()
    client.get_object_lock_configuration.return_value = lock
    adapter = _adapter(client)

    with pytest.raises(StorageConfigurationError):
        adapter.put_object(
            tenant_id=TENANT,
            relative_key="documents/scan.pdf",
            body=b"synthetic",
        )

    client.head_object.assert_not_called()
    client.put_object.assert_not_called()


def test_shorter_environment_default_is_overridden_by_explicit_3650_day_lock() -> None:
    client = _new_client()
    client.get_object_lock_configuration.return_value = _lock(days=1)
    client.head_object.side_effect = [_not_found(), _head_receipt()]
    adapter = _adapter(client)

    result = adapter.put_object(
        tenant_id=TENANT,
        relative_key="documents/scan.pdf",
        body=b"synthetic",
    )

    assert client.put_object.call_args.kwargs["ObjectLockRetainUntilDate"] == EXPECTED_UNTIL
    assert result.retain_until == EXPECTED_UNTIL


def test_bucket_without_default_retention_uses_explicit_object_lock() -> None:
    client = _new_client()
    client.get_object_lock_configuration.return_value = {
        "ObjectLockConfiguration": {"ObjectLockEnabled": "Enabled"}
    }
    client.head_object.side_effect = [_not_found(), _head_receipt()]
    adapter = _adapter(client)

    result = adapter.put_object(
        tenant_id=TENANT,
        relative_key="documents/scan.pdf",
        body=b"synthetic",
    )

    assert result.retention_mode == GOVERNANCE_MODE
    assert client.put_object.call_args.kwargs["ObjectLockRetainUntilDate"] == EXPECTED_UNTIL


def test_configuration_read_errors_are_sanitised() -> None:
    client = _new_client()
    client.get_bucket_versioning.side_effect = _client_error(
        "AccessDenied", 403, "SYNTHETIC_SECRET_ENDPOINT_VALUE"
    )
    adapter = _adapter(client)

    with pytest.raises(StorageOperationError) as caught:
        adapter.put_object(
            tenant_id=TENANT,
            relative_key="documents/scan.pdf",
            body=b"synthetic",
        )

    assert "SYNTHETIC_SECRET_ENDPOINT_VALUE" not in str(caught.value)
    assert caught.value.__suppress_context__ is True
    client.put_object.assert_not_called()


def test_existing_key_is_refused_without_put() -> None:
    client = _new_client()
    client.head_object.side_effect = [_head_receipt()]
    adapter = _adapter(client)

    with pytest.raises(ObjectAlreadyExistsError):
        adapter.put_object(
            tenant_id=TENANT,
            relative_key="documents/scan.pdf",
            body=b"synthetic",
        )

    client.put_object.assert_not_called()


def test_conditional_write_race_is_reported_as_existing_object() -> None:
    client = _new_client()
    client.head_object.side_effect = [_not_found()]
    client.put_object.side_effect = _client_error("PreconditionFailed", 412)
    adapter = _adapter(client)

    with pytest.raises(ObjectAlreadyExistsError):
        adapter.put_object(
            tenant_id=TENANT,
            relative_key="documents/scan.pdf",
            body=b"synthetic",
        )

    assert client.head_object.call_count == 1


def test_put_failure_does_not_leak_endpoint_or_secret() -> None:
    client = _new_client()
    client.head_object.side_effect = [_not_found()]
    client.put_object.side_effect = _client_error(
        "AccessDenied", 403, "SYNTHETIC_SECRET_ENDPOINT_VALUE"
    )
    adapter = _adapter(client)

    with pytest.raises(StorageOperationError) as caught:
        adapter.put_object(
            tenant_id=TENANT,
            relative_key="documents/scan.pdf",
            body=b"synthetic",
        )

    assert "SYNTHETIC_SECRET_ENDPOINT_VALUE" not in str(caught.value)
    assert caught.value.__suppress_context__ is True


def test_existence_check_failure_is_sanitised_and_prevents_put() -> None:
    client = _new_client()
    client.head_object.side_effect = _client_error(
        "AccessDenied", 403, "SYNTHETIC_SECRET_ENDPOINT_VALUE"
    )
    adapter = _adapter(client)

    with pytest.raises(StorageOperationError) as caught:
        adapter.put_object(
            tenant_id=TENANT,
            relative_key="documents/scan.pdf",
            body=b"synthetic",
        )

    assert "SYNTHETIC_SECRET_ENDPOINT_VALUE" not in str(caught.value)
    client.put_object.assert_not_called()


@pytest.mark.parametrize(
    "receipt",
    [
        {},
        {"ETag": ETAG},
        {"VersionId": "", "ETag": ETAG},
        {"VersionId": VERSION_ID},
        {"VersionId": VERSION_ID, "ETag": ""},
    ],
)
def test_put_receipt_must_include_version_and_etag(receipt: dict[str, Any]) -> None:
    client = _new_client()
    client.head_object.side_effect = [_not_found()]
    client.put_object.return_value = receipt
    adapter = _adapter(client)

    with pytest.raises(StorageIntegrityError):
        adapter.put_object(
            tenant_id=TENANT,
            relative_key="documents/scan.pdf",
            body=b"synthetic",
        )

    assert client.head_object.call_count == 1


@pytest.mark.parametrize(
    "head",
    [
        _head_receipt(version_id="different-version"),
        _head_receipt(mode="COMPLIANCE"),
        _head_receipt(retain_until=EXPECTED_UNTIL - timedelta(days=1)),
        _head_receipt(retain_until=EXPECTED_UNTIL.replace(tzinfo=None)),
        _head_receipt(etag='"different-etag"'),
        {"VersionId": VERSION_ID, "ETag": ETAG},
        {"VersionId": VERSION_ID, "ObjectLockMode": GOVERNANCE_MODE, "ETag": ETAG},
        {"VersionId": VERSION_ID, "ObjectLockRetainUntilDate": EXPECTED_UNTIL, "ETag": ETAG},
        "not-a-mapping",
    ],
)
def test_retention_and_version_receipt_is_verified(head: Any) -> None:
    client = _new_client()
    client.head_object.side_effect = [_not_found(), head]
    adapter = _adapter(client)

    with pytest.raises(StorageIntegrityError):
        adapter.put_object(
            tenant_id=TENANT,
            relative_key="documents/scan.pdf",
            body=b"synthetic",
        )


def test_missing_written_version_is_an_integrity_failure_not_success() -> None:
    client = _new_client()
    client.head_object.side_effect = [_not_found(), _client_error("NoSuchVersion", 404)]
    adapter = _adapter(client)

    with pytest.raises(StorageIntegrityError):
        adapter.put_object(
            tenant_id=TENANT,
            relative_key="documents/scan.pdf",
            body=b"synthetic",
        )

    assert client.head_object.call_count == 2


def test_naive_storage_clock_is_rejected() -> None:
    client = _new_client()
    client.head_object.side_effect = [_not_found()]
    adapter = _adapter(client, clock=lambda: datetime(2026, 11, 15, 9, 30))  # noqa: DTZ001

    with pytest.raises(StorageConfigurationError):
        adapter.put_object(
            tenant_id=TENANT,
            relative_key="documents/scan.pdf",
            body=b"synthetic",
        )

    client.put_object.assert_not_called()


@pytest.mark.parametrize(
    "bucket",
    ["", " pish-synthetic", "pish-synthetic ", "pish/synthetic", "pish\\synthetic", "x" * 256],
)
def test_invalid_bucket_names_fail_closed(bucket: str) -> None:
    with pytest.raises(StorageConfigurationError):
        S3ObjectStorage(_new_client(), bucket=bucket, clock=lambda: NOW)


def test_public_api_has_no_delete_or_bypass_surface() -> None:
    public_names = {name for name in dir(S3ObjectStorage) if not name.startswith("_")}
    forbidden = ("delete", "remove", "purge", "bypass", "governance_override")

    assert public_names == {"bucket", "put_object", "verify_configuration"}
    assert not any(token in name.lower() for name in public_names for token in forbidden)
    assert GOVERNANCE_MODE == "GOVERNANCE"
    assert GOVERNANCE_RETENTION_DAYS == 3650


def test_bucket_configuration_validation_is_read_only() -> None:
    client = _new_client()
    adapter = _adapter(client)

    adapter.verify_configuration()
    adapter.verify_configuration()

    assert client.get_bucket_versioning.call_count == 2
    assert client.get_object_lock_configuration.call_count == 2
    client.head_object.assert_not_called()
    client.put_object.assert_not_called()


def test_put_receipt_object_is_immutable() -> None:
    client = _new_client()
    client.head_object.side_effect = [_not_found(), _head_receipt()]
    adapter = _adapter(client)
    result = adapter.put_object(
        tenant_id=TENANT, relative_key="documents/scan.pdf", body=b"synthetic"
    )

    with pytest.raises(FrozenInstanceError):
        result.version_id = "mutated"  # type: ignore[misc]
