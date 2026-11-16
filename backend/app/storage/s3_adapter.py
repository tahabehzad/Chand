"""P0-T11 — tenant-scoped, WORM-governed S3 object storage.

Authority
---------
- ``docs/adr/ADR-002-object-storage-worm-ceph-s3-governance.md`` (Accepted),
  directives 1-3: ``boto3``/S3 SigV4; Object Lock enabled with default
  ``GOVERNANCE`` retention of 3650 days; standard service accounts are denied
  ``s3:BypassGovernanceRetention``, which is isolated in an offline vault.
- ``docs/EXECUTION_PLAN.md`` §14.3 row ``P0-T11`` and
  ``docs/specs/DEPLOYMENT.md`` §§2.5, 5.1-5.2, 10: bucket versioning and Object
  Lock validation, 3650-day evidence retention, and no emergency bypass in the
  runtime credential.
- ``docs/PISH_HESABDARI_HOLY_BIBLE.md`` §§4.7, 8.1, 9.1: tenant-prefixed keys,
  Object Lock ``GOVERNANCE`` for 3650 days, and the object version ID recorded
  as custody metadata.
- ``docs/specs/DOCUMENT_FORENSICS.md`` §3.1: the example document path is
  ``tenants/{tenant_id}/documents/{document_id}/``. Holy Bible §4.7 marks that
  layout ``PROPOSED``; this adapter therefore enforces only the accepted tenant
  prefix and leaves the relative path to the caller.

Exact contract
--------------
1. **Key ownership.** Every object key is
   ``tenants/{canonical tenant UUID}/{relative_key}``. The tenant identifier
   must be a ``UUID`` instance and the relative key must be a non-empty,
   relative, UTF-8 path without control characters, ``.``/``..`` segments,
   backslashes, empty segments or a leading/trailing slash. Callers cannot
   supply the ``tenants/`` root themselves, and the full key must fit the S3
   1024-byte limit. No normalisation or silent rewriting is performed.
2. **Configuration validation.** Every upload re-reads bucket versioning and
   Object Lock configuration. Versioning must be ``Enabled`` and Object Lock
   must be ``Enabled``. If a default retention rule is present, its mode must
   be ``GOVERNANCE``; ``COMPLIANCE`` and malformed rules are rejected. A
   shorter local/staging default, or no default rule, is permitted by
   ``DEPLOYMENT`` §2.5/§5.1 because the adapter applies the production
   retention explicitly per object.
3. **Retention.** Each object is written with ``ObjectLockMode='GOVERNANCE'``
   and ``ObjectLockRetainUntilDate = clock() + 3650 days``. The clock must
   return a timezone-aware datetime; it is injectable for deterministic tests.
4. **No silent overwrite.** A preflight ``HEAD`` rejects an existing key, and
   the conditional write uses ``IfNoneMatch='*'`` to close the race. An
   endpoint that does not honour the precondition fails closed rather than
   replacing evidence. With versioning enabled, a prior version would still be
   retained, but this adapter never treats overwrite as acceptable.
5. **Receipt validation.** ``PutObject`` must return a non-empty ``VersionId``
   and ``ETag``. A subsequent ``HEAD`` of that exact version must confirm the
   same version and ETag, ``ObjectLockMode='GOVERNANCE'`` and a retained-until
   timestamp at least as late as the requested 3650-day horizon. Missing or
   mismatched evidence is an integrity failure, never a success.
6. **Safe errors.** All adapter failures are subclasses of ``StorageError``.
   Botocore messages, request URLs, credentials, object bodies and caller keys
   are not rendered into the exception text or chained as the displayed cause.
7. **No destructive API.** This module exposes no delete, purge, retention
   bypass or governance bypass method and never passes
   ``BypassGovernanceRetention``. Emergency access remains an offline,
   two-person procedure (ADR-002 directive 3; AUTH §9.2).
8. **Scope.** Bucket creation, IAM policy, lifecycle/replication, the
   quarantine bucket, statutory/global (non-tenant) artefacts and the live
   RGW integration belong to other contracts. No live endpoint is exercised by
   the P0-T11 unit tests; the integration criterion remains ``NOT RUN``.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, Final, Protocol
from uuid import UUID

from botocore.exceptions import BotoCoreError, ClientError

GOVERNANCE_MODE: Final[str] = "GOVERNANCE"
GOVERNANCE_RETENTION_DAYS: Final[int] = 3650
TENANT_ROOT: Final[str] = "tenants"
MAX_OBJECT_KEY_BYTES: Final[int] = 1024
MAX_BUCKET_NAME_LENGTH: Final[int] = 255
_RETENTION_TOLERANCE: Final[timedelta] = timedelta(seconds=1)
_NOT_FOUND_CODES: Final[frozenset[str]] = frozenset(
    {"404", "NoSuchKey", "NoSuchVersion", "NotFound"}
)
_PRECONDITION_CODES: Final[frozenset[str]] = frozenset({"412", "PreconditionFailed"})


class StorageError(RuntimeError):
    """Base class for sanitised object-storage failures."""


class StorageConfigurationError(StorageError):
    """The bucket or adapter configuration cannot provide WORM custody."""


class StorageInputError(StorageError):
    """The caller supplied a body or content type the adapter cannot store."""


class InvalidStorageKeyError(StorageInputError):
    """The tenant identifier or relative object key is unsafe or malformed."""


class ObjectAlreadyExistsError(StorageError):
    """An object already occupies the requested key; no overwrite is attempted."""


class StorageIntegrityError(StorageError):
    """The object store did not return a complete, consistent retention receipt."""


class StorageOperationError(StorageError):
    """The storage operation failed without exposing endpoint or credential data."""


class S3Client(Protocol):
    """The boto3 S3 subset used here; the live client is injected by the caller."""

    def get_bucket_versioning(self, **kwargs: Any) -> Mapping[str, Any]:
        """Return the bucket versioning configuration."""
        ...

    def get_object_lock_configuration(self, **kwargs: Any) -> Mapping[str, Any]:
        """Return the bucket Object Lock configuration."""
        ...

    def head_object(self, **kwargs: Any) -> Mapping[str, Any]:
        """Return object or object-version metadata."""
        ...

    def put_object(self, **kwargs: Any) -> Mapping[str, Any]:
        """Write one object and return its receipt metadata."""
        ...


@dataclass(frozen=True, slots=True)
class StoredObject:
    """The verified custody receipt for one newly written object version."""

    bucket: str
    tenant_id: UUID
    key: str
    version_id: str
    etag: str
    retention_mode: str
    retain_until: datetime


def _utc_now() -> datetime:
    """Return a timezone-aware UTC clock value."""
    return datetime.now(UTC)


class S3ObjectStorage:
    """Tenant-prefixed, ``GOVERNANCE``-locked object writes under ADR-002.

    The caller owns the boto3 client and its credential. The adapter does not
    create buckets, manage IAM, read credentials or expose a deletion path.
    """

    def __init__(
        self,
        client: S3Client,
        *,
        bucket: str,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._client = client
        self._bucket = _validate_bucket(bucket)
        self._clock = clock if clock is not None else _utc_now

    @property
    def bucket(self) -> str:
        """Return the validated bucket name (public configuration)."""
        return self._bucket

    def verify_configuration(self) -> None:
        """Fail closed unless versioning and Object Lock can support WORM.

        The check is intentionally repeated for every upload because a bucket
        policy can drift after process start. No result is cached.
        """
        self._verify_versioning()
        self._verify_object_lock()

    def _verify_versioning(self) -> None:
        """Require versioning, without which overwrite could destroy a version."""
        try:
            versioning = self._client.get_bucket_versioning(Bucket=self._bucket)
        except (BotoCoreError, ClientError):
            raise StorageOperationError(
                "Object-store versioning configuration could not be read."
            ) from None
        if not isinstance(versioning, Mapping) or versioning.get("Status") != "Enabled":
            raise StorageConfigurationError("Object-store versioning must be enabled.")

    def _verify_object_lock(self) -> None:
        """Require Object Lock and a non-COMPLIANCE default retention rule."""
        try:
            lock_configuration = self._client.get_object_lock_configuration(Bucket=self._bucket)
        except (BotoCoreError, ClientError):
            raise StorageOperationError(
                "Object-store Object Lock configuration could not be read."
            ) from None
        if not isinstance(lock_configuration, Mapping):
            raise StorageConfigurationError("Object Lock configuration is malformed.")
        configuration = lock_configuration.get("ObjectLockConfiguration")
        if not isinstance(configuration, Mapping):
            raise StorageConfigurationError("Object Lock is not configured on the bucket.")
        if configuration.get("ObjectLockEnabled") != "Enabled":
            raise StorageConfigurationError("Object Lock must be enabled on the bucket.")

        rule = configuration.get("Rule")
        if rule is None:
            return
        if not isinstance(rule, Mapping):
            raise StorageConfigurationError("Object Lock retention rule is malformed.")
        default_retention = rule.get("DefaultRetention")
        if default_retention is None:
            raise StorageConfigurationError("Object Lock default retention is missing.")
        if not isinstance(default_retention, Mapping):
            raise StorageConfigurationError("Object Lock default retention is malformed.")
        if default_retention.get("Mode") != GOVERNANCE_MODE:
            raise StorageConfigurationError(
                "Object Lock default retention mode must be GOVERNANCE."
            )
        days = default_retention.get("Days")
        years = default_retention.get("Years")
        if days is None and years is None:
            raise StorageConfigurationError("Object Lock default retention has no duration.")
        if days is not None and years is not None:
            raise StorageConfigurationError("Object Lock default retention is ambiguous.")
        duration = days if days is not None else years
        if not isinstance(duration, int) or isinstance(duration, bool) or duration <= 0:
            raise StorageConfigurationError("Object Lock default retention duration is invalid.")

    def put_object(
        self,
        *,
        tenant_id: UUID,
        relative_key: str,
        body: bytes,
        content_type: str | None = None,
    ) -> StoredObject:
        """Write one immutable object and return a verified retention receipt.

        Raises:
            StorageInputError: the body or content type is malformed.
            InvalidStorageKeyError: the tenant or relative key is unsafe.
            StorageConfigurationError: the bucket cannot provide WORM custody.
            ObjectAlreadyExistsError: the key already exists.
            StorageIntegrityError: the store omitted or contradicted the receipt.
            StorageOperationError: the store call failed for another reason.
        """
        tenant = _validate_tenant(tenant_id)
        key = _build_object_key(tenant, relative_key)
        if not isinstance(body, bytes):
            raise StorageInputError("Object body must be bytes.")
        if content_type is not None:
            content_type = _validate_content_type(content_type)

        self.verify_configuration()
        self._ensure_absent(key)

        retain_until = _clock_value(self._clock) + timedelta(days=GOVERNANCE_RETENTION_DAYS)
        request: dict[str, Any] = {
            "Bucket": self._bucket,
            "Key": key,
            "Body": body,
            "IfNoneMatch": "*",
            "ObjectLockMode": GOVERNANCE_MODE,
            "ObjectLockRetainUntilDate": retain_until,
        }
        if content_type is not None:
            request["ContentType"] = content_type

        try:
            response = self._client.put_object(**request)
        except ClientError as error:
            if _is_precondition_failure(error):
                raise ObjectAlreadyExistsError(
                    "An object already exists at the requested key."
                ) from None
            raise StorageOperationError("Object write failed.") from None
        except BotoCoreError:
            raise StorageOperationError("Object write failed.") from None

        version_id, etag = _parse_put_receipt(response)
        observed_mode, observed_until, observed_etag = self._head_receipt(key, version_id)
        if _normalise_etag(observed_etag) != _normalise_etag(etag):
            raise StorageIntegrityError("Object receipt ETag does not match the write.")
        if observed_mode != GOVERNANCE_MODE:
            raise StorageIntegrityError("Object retention mode is not GOVERNANCE.")
        if observed_until < retain_until - _RETENTION_TOLERANCE:
            raise StorageIntegrityError("Object retention horizon is shorter than 3650 days.")

        return StoredObject(
            bucket=self._bucket,
            tenant_id=tenant,
            key=key,
            version_id=version_id,
            etag=etag,
            retention_mode=observed_mode,
            retain_until=observed_until,
        )

    def _ensure_absent(self, key: str) -> None:
        """Refuse to write over an existing key before attempting the PUT."""
        try:
            self._client.head_object(Bucket=self._bucket, Key=key)
        except ClientError as error:
            if _is_not_found(error):
                return
            raise StorageOperationError("Object existence could not be established.") from None
        except BotoCoreError:
            raise StorageOperationError("Object existence could not be established.") from None
        raise ObjectAlreadyExistsError("An object already exists at the requested key.")

    def _head_receipt(self, key: str, version_id: str) -> tuple[str, datetime, str]:
        """Read back the exact written version and validate the lock metadata."""
        try:
            head = self._client.head_object(
                Bucket=self._bucket,
                Key=key,
                VersionId=version_id,
            )
        except (BotoCoreError, ClientError):
            raise StorageIntegrityError(
                "The written object version could not be verified."
            ) from None

        if not isinstance(head, Mapping):
            raise StorageIntegrityError("The written object receipt is malformed.")
        if head.get("VersionId") != version_id:
            raise StorageIntegrityError("The written object version does not match the receipt.")

        mode = head.get("ObjectLockMode")
        retain_until = head.get("ObjectLockRetainUntilDate")
        etag = head.get("ETag")
        if not isinstance(mode, str) or not isinstance(etag, str) or not etag:
            raise StorageIntegrityError("The retention receipt is incomplete.")
        if not isinstance(retain_until, datetime):
            raise StorageIntegrityError("The retention-until value is missing.")
        if retain_until.tzinfo is None or retain_until.utcoffset() is None:
            raise StorageIntegrityError("The retention-until value is not timezone-aware.")
        return mode, retain_until.astimezone(UTC), etag


def _validate_tenant(tenant_id: object) -> UUID:
    if not isinstance(tenant_id, UUID):
        raise InvalidStorageKeyError("Tenant identifier must be a UUID.")
    return tenant_id


def _validate_bucket(bucket: object) -> str:
    if (
        not isinstance(bucket, str)
        or not bucket
        or bucket != bucket.strip()
        or len(bucket) > MAX_BUCKET_NAME_LENGTH
        or not bucket.isprintable()
        or "/" in bucket
        or "\\" in bucket
    ):
        raise StorageConfigurationError("Object-store bucket name is invalid.")
    return bucket


def _validate_content_type(content_type: object) -> str:
    if (
        not isinstance(content_type, str)
        or not content_type
        or content_type != content_type.strip()
        or len(content_type) > 255
        or not content_type.isprintable()
    ):
        raise StorageInputError("Content type is invalid.")
    return content_type


def _build_object_key(tenant_id: UUID, relative_key: object) -> str:
    if not isinstance(relative_key, str) or not relative_key:
        raise InvalidStorageKeyError("Relative object key must be a non-empty string.")
    if relative_key != relative_key.strip():
        raise InvalidStorageKeyError("Relative object key must not have edge whitespace.")
    if relative_key.startswith(f"{TENANT_ROOT}/"):
        raise InvalidStorageKeyError("Relative object key must not include the tenant root.")
    if "\\" in relative_key:
        raise InvalidStorageKeyError("Relative object key must not contain backslashes.")
    if any(ord(character) < 32 or 127 <= ord(character) <= 159 for character in relative_key):
        raise InvalidStorageKeyError("Relative object key must not contain control characters.")
    segments = relative_key.split("/")
    if any(segment in {"", ".", ".."} for segment in segments):
        raise InvalidStorageKeyError("Relative object key contains an unsafe path segment.")

    key = f"{TENANT_ROOT}/{tenant_id}/{relative_key}"
    try:
        key_bytes = key.encode("utf-8")
    except UnicodeEncodeError:
        raise InvalidStorageKeyError("Object key must be valid UTF-8 text.") from None
    if len(key_bytes) > MAX_OBJECT_KEY_BYTES:
        raise InvalidStorageKeyError("Object key exceeds the S3 1024-byte limit.")
    return key


def _clock_value(clock: Callable[[], datetime]) -> datetime:
    value = clock()
    if not isinstance(value, datetime):
        raise StorageConfigurationError("Storage clock did not return a datetime.")
    if value.tzinfo is None or value.utcoffset() is None:
        raise StorageConfigurationError("Storage clock must return a timezone-aware datetime.")
    return value.astimezone(UTC)


def _parse_put_receipt(response: object) -> tuple[str, str]:
    if not isinstance(response, Mapping):
        raise StorageIntegrityError("The object-store write receipt is malformed.")
    version_id = response.get("VersionId")
    etag = response.get("ETag")
    if not isinstance(version_id, str) or not version_id:
        raise StorageIntegrityError("The object-store write did not return a version ID.")
    if not isinstance(etag, str) or not etag:
        raise StorageIntegrityError("The object-store write did not return an ETag.")
    return version_id, etag


def _normalise_etag(etag: str) -> str:
    return etag.strip('"')


def _client_error_code(error: ClientError) -> str | None:
    response = getattr(error, "response", None)
    if not isinstance(response, Mapping):
        return None
    detail = response.get("Error")
    if not isinstance(detail, Mapping):
        return None
    code = detail.get("Code")
    return code if isinstance(code, str) else None


def _client_error_status(error: ClientError) -> int | None:
    response = getattr(error, "response", None)
    if not isinstance(response, Mapping):
        return None
    metadata = response.get("ResponseMetadata")
    if not isinstance(metadata, Mapping):
        return None
    status = metadata.get("HTTPStatusCode")
    return status if isinstance(status, int) and not isinstance(status, bool) else None


def _is_not_found(error: ClientError) -> bool:
    return _client_error_code(error) in _NOT_FOUND_CODES or _client_error_status(error) == 404


def _is_precondition_failure(error: ClientError) -> bool:
    return _client_error_code(error) in _PRECONDITION_CODES or _client_error_status(error) == 412
