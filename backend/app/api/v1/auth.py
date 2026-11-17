"""Authentication endpoints: sign-in, session read-back and sign-out.

Authority
---------
``docs/specs/AUTH.md`` §5 (Argon2id), §6 (session bound to one organisation);
``AGENTS.md`` §2 Security invariants 13-15.

Related
-------
``app/services/identity_service.py`` (credential verification and session
issue), ``app/api/deps.py`` (session resolution).

Scope
-----
The MVP exposes exactly one manager identity flow: an email/password sign-in
against the identity foundation, one organisation bound at sign-in, and one
opaque bearer token.  No MFA, no password reset and no registration here:
those belong to P0-T18 and stay unimplemented rather than stubbed.
"""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from app.api.deps import DbSession, ManagerRequired, renew_tenant
from app.models.identity import UserSession
from app.services.identity_service import authenticate

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class LoginRequest(BaseModel):
    """One sign-in attempt.  Only the identifier and the secret are accepted."""

    model_config = ConfigDict(extra="forbid")

    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=200)


class ManagerView(BaseModel):
    """The signed-in manager, as bound at sign-in."""

    id: str
    displayName: str
    email: str


class OrganizationView(BaseModel):
    """The tenant bound to the session."""

    id: str
    nameFa: str


class LoginResponse(BaseModel):
    """The opaque bearer token and the bound manager and organisation."""

    token: str
    tokenType: str = "Bearer"
    manager: ManagerView
    organization: OrganizationView


def _error(status_code: int, code: str, detail: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code, content={"error": {"code": code, "detail": detail}}
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Manager sign-in",
    responses={401: {"description": "The credentials were refused."}},
)
async def login(payload: LoginRequest, db: DbSession) -> LoginResponse | JSONResponse:
    """Verify the credentials and issue one organisation-bound session."""
    result = await authenticate(db, payload.email, payload.password)
    if result is None:
        return _error(401, "AUTH_INVALID_CREDENTIALS", "شناسه یا گذرواژه نادرست است.")
    user, _membership, organization, token = result
    return LoginResponse(
        token=token,
        manager=ManagerView(
            id=str(user.id), displayName=user.display_name_fa, email=user.email_normalized
        ),
        organization=OrganizationView(id=str(organization.id), nameFa=organization.legal_name_fa),
    )


class MeResponse(BaseModel):
    """The bound manager context of the presented session."""

    manager: ManagerView
    organization: OrganizationView


@router.get("/me", response_model=MeResponse, summary="The bound manager context")
async def me(manager: ManagerRequired) -> MeResponse:
    """Return the manager and organisation bound to this session."""
    return MeResponse(
        manager=ManagerView(
            id=str(manager.user_id),
            displayName=manager.display_name,
            email=manager.email,
        ),
        organization=OrganizationView(
            id=str(manager.tenant_id),
            nameFa="",  # resolved by the login response; not re-read here
        ),
    )


@router.post("/logout", summary="Revoke the presented session")
async def logout(manager: ManagerRequired, db: DbSession) -> dict[str, str]:
    """Revoke the session that made this request."""
    result = await db.get(UserSession, manager.session_id)
    if result is not None:
        result.revoked_at = datetime.now(UTC)
        result.revoked_reason = "manager_logout"
        await renew_tenant(db, manager)
        await db.commit()
    return {"status": "revoked"}


__all__ = ["LoginRequest", "LoginResponse", "router"]
