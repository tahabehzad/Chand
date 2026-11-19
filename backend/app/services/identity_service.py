"""Identity service: password verification and server-side sessions.

Authority
---------
``docs/specs/AUTH.md`` §5 (Argon2id), §6 (multi-tenant isolation, ISO-06:
a session is bound to one organisation and the tenant context can never be
chosen by the client); ``AGENTS.md`` §2 Security invariants 13-15 (secrets
never logged or echoed).

Related
-------
``app/models/identity.py`` (``User``, ``UserSession``, ``OrganizationMembership``),
``app/core/security/tenant_context.py``.

Scope
-----
* Passwords are verified with Argon2id via ``argon2-cffi``; the hash never
  leaves this module and a failure is indistinguishable from an unknown user
  in the API response.
* A session stores only the SHA-256 digest of its opaque token; the plaintext
  token exists in the login response and in the client, nowhere else.
* A brute-force guard: five consecutive failures lock the account for the
  remainder of a fifteen-minute window.
"""

from __future__ import annotations

import datetime
import hashlib
import secrets
import uuid
from typing import Any

import sqlalchemy as sa
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.identity import Organization, OrganizationMembership, User, UserSession

#: Argon2id parameters follow SPEC-AUTH-001 §4.1 defaults.
_HASHER = PasswordHasher()

_TOKEN_BYTES = 32
_ABSOLUTE_TTL = datetime.timedelta(hours=12)
_IDLE_TTL = datetime.timedelta(hours=2)
_FAILURE_LOCK = 5
_LOCK_WINDOW = datetime.timedelta(minutes=15)

#: The roles that may act as the manager in this MVP.  The full permission
#: matrix is unapproved (P0-T05), so the check is role-key based.
_MANAGER_ROLE_KEYS = frozenset({"OWNER", "ADMIN", "HR_MANAGER"})


def hash_password(password: str) -> bytes:
    """Return the Argon2id digest for a new password."""
    return _HASHER.hash(password).encode("utf-8")


def verify_password(password_hash: bytes | None, password: str) -> bool:
    """Verify a password against a stored Argon2id digest.

    A stored ``None`` (no password set) is a refusal, never a match.
    """
    if not password_hash:
        return False
    try:
        return _HASHER.verify(password_hash.decode("utf-8"), password)
    except (VerifyMismatchError, ValueError):
        return False


def _token_digest(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


async def _register_failure(session: AsyncSession, user: User) -> None:
    failures = user.failed_attempts + 1
    values: dict[str, Any] = {"failed_attempts": failures}
    if failures >= _FAILURE_LOCK:
        values["locked_until"] = datetime.datetime.now(datetime.UTC) + _LOCK_WINDOW
        values["failed_attempts"] = 0
    await session.execute(update(User).where(User.id == user.id).values(**values))


async def authenticate(  # noqa: PLR0911 - each return is a distinct documented refusal
    session: AsyncSession, email: str, password: str
) -> tuple[User, OrganizationMembership, Organization, str] | None:
    """Verify credentials and return the bound manager context and token.

    Returns ``None`` for unknown users, wrong passwords, locked or inactive
    accounts and memberships without a manager role.  No caller can tell
    which refusal happened from the API response.

    Each ``return None`` below is a distinct, documented refusal path; the
    guard-return shape is kept deliberately so no refusal can be confused
    with another, hence ``noqa: PLR0911``.
    """
    email_normalized = email.strip().lower()
    user = (
        await session.execute(select(User).where(User.email_normalized == email_normalized))
    ).scalar_one_or_none()
    if user is None or not user.is_active:
        return None
    now = datetime.datetime.now(datetime.UTC)
    if user.locked_until is not None and user.locked_until > now:
        return None
    if not verify_password(user.password_hash, password):
        await _register_failure(session, user)
        await session.commit()
        return None

    membership = (
        (
            await session.execute(
                select(OrganizationMembership)
                .where(
                    OrganizationMembership.user_id == user.id,
                    OrganizationMembership.is_active.is_(True),
                )
                .limit(2)
            )
        )
        .scalars()
        .all()
    )
    if not membership:
        return None
    # The MVP binds exactly one organisation per manager; several are refused
    # rather than guessed.
    if len(membership) > 1:
        return None
    binding = membership[0]

    role_key: str | None = (
        await session.execute(
            sa.text("SELECT r.role_key FROM roles r WHERE r.id = :role_id"),
            {"role_id": binding.role_id},
        )
    ).scalar_one_or_none()
    if role_key is None or role_key not in _MANAGER_ROLE_KEYS:
        return None

    organization = (
        await session.execute(
            select(Organization).where(Organization.id == binding.organization_id)
        )
    ).scalar_one_or_none()
    if organization is None or not organization.is_active:
        return None

    token = secrets.token_hex(_TOKEN_BYTES)
    issued = datetime.datetime.now(datetime.UTC)
    user_session = UserSession(
        id=uuid.uuid4(),
        user_id=user.id,
        organization_id=organization.id,
        token_hash=_token_digest(token),
        issued_at=issued,
        last_seen_at=issued,
        absolute_expires_at=issued + _ABSOLUTE_TTL,
        idle_expires_at=issued + _IDLE_TTL,
    )
    session.add(user_session)
    await session.execute(
        update(User).where(User.id == user.id).values(failed_attempts=0, last_login_at=issued)
    )
    await session.commit()
    return user, binding, organization, token


__all__ = [
    "authenticate",
    "hash_password",
    "verify_password",
]
