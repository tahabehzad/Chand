"""Seed one local development tenant and one manager account.

Usage
-----
``python scripts/seed_local_dev.py`` from ``backend/`` (reads ``DATABASE_URL``
and creates ``organizations`` / ``users`` / ``organization_memberships``).

This script exists for the local MVP only.  The password is read from
``LOCAL_DEV_PASSWORD`` (default ``local-dev-only``) and the credentials are
printed to stdout; it must never run against a production database and never
be wired into CI or deployment.
"""

from __future__ import annotations

import asyncio
import os
import sys
import uuid

sys.path.insert(0, ".")

from sqlalchemy import select

from app.db import build_engine, build_session_factory
from app.models.identity import (
    Organization,
    OrganizationMembership,
    Role,
    User,
)
from app.services.identity_service import hash_password

MANAGER_EMAIL = "manager@local.dev"
MANAGER_DISPLAY_NAME = "مدیر سازمان نمونه"
ORGANIZATION_NAME = "سازمان نمونهٔ محلی"


async def main() -> None:
    factory = build_session_factory(build_engine())
    session = factory()
    try:
        email = MANAGER_EMAIL
        user = (
            await session.execute(select(User).where(User.email_normalized == email))
        ).scalar_one_or_none()
        role = (
            await session.execute(select(Role).where(Role.role_key == "HR_MANAGER"))
        ).scalar_one()
        if user is None:
            user = User(
                id=uuid.uuid4(),
                email_normalized=email,
                display_name_fa=MANAGER_DISPLAY_NAME,
                password_hash=hash_password(os.environ.get("LOCAL_DEV_PASSWORD", "local-dev-only")),
            )
            session.add(user)
            await session.flush()
            print(f"created user {email}")
        else:
            print(f"user {email} already exists")

        organization = (
            await session.execute(
                select(Organization).where(Organization.legal_name_fa == ORGANIZATION_NAME)
            )
        ).scalar_one_or_none()
        if organization is None:
            organization = Organization(id=uuid.uuid4(), legal_name_fa=ORGANIZATION_NAME)
            session.add(organization)
            await session.flush()
            print(f"created organization {organization.id}")
        else:
            print(f"organization already exists: {organization.id}")

        membership = (
            await session.execute(
                select(OrganizationMembership).where(
                    OrganizationMembership.user_id == user.id,
                    OrganizationMembership.organization_id == organization.id,
                )
            )
        ).scalar_one_or_none()
        if membership is None:
            session.add(
                OrganizationMembership(
                    id=uuid.uuid4(),
                    organization_id=organization.id,
                    user_id=user.id,
                    role_id=role.id,
                )
            )
            await session.commit()
            print("created membership")
        else:
            print("membership already exists")

        print(f"login email: {email}")
        print("login password: value of LOCAL_DEV_PASSWORD (default local-dev-only)")
        print(f"tenant id: {organization.id}")
    finally:
        await session.close()


if __name__ == "__main__":
    asyncio.run(main())
