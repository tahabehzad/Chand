"""Object-storage adapters.

P0-T11 exposes only the tenant-scoped, ``GOVERNANCE``-locked S3 adapter.
Bucket provisioning, IAM, lifecycle and emergency retention bypass are not
application APIs and are intentionally absent.
"""

from __future__ import annotations

from app.storage.s3_adapter import (
    GOVERNANCE_MODE,
    GOVERNANCE_RETENTION_DAYS,
    InvalidStorageKeyError,
    ObjectAlreadyExistsError,
    S3ObjectStorage,
    StorageConfigurationError,
    StorageError,
    StorageInputError,
    StorageIntegrityError,
    StorageOperationError,
    StoredObject,
)

__all__ = [
    "GOVERNANCE_MODE",
    "GOVERNANCE_RETENTION_DAYS",
    "InvalidStorageKeyError",
    "ObjectAlreadyExistsError",
    "S3ObjectStorage",
    "StorageConfigurationError",
    "StorageError",
    "StorageInputError",
    "StorageIntegrityError",
    "StorageOperationError",
    "StoredObject",
]
