"""Create first manager user — run once, then delete this file."""

import asyncio
import uuid
from datetime import datetime, timezone

from argon2 import PasswordHasher
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import Settings
from app.models.identity import Organization, User, OrganizationMembership, Role

_hasher = PasswordHasher()


async def main():
    settings = Settings()
    db_url = settings.database_url.get_secret_value()
    # Convert postgresql:// to postgresql+asyncpg:// for async
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    engine = create_async_engine(db_url, echo=False)

    async with engine.begin() as conn:
        from app.models.identity import Base

        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Find or create an OWNER role
        result = await session.execute(
            select(Role).where(Role.role_key == "OWNER")
        )
        role = result.scalar_one_or_none()
        if role is None:
            role = Role(
                id=uuid.uuid4(),
                role_key="OWNER",
                display_name_fa="مالک سیستم",
                description_fa="دسترسی کامل به سیستم",
                is_system_role=True,
                created_at=datetime.now(timezone.utc),
            )
            session.add(role)
            await session.flush()
            print(f"✅ نقش OWNER ساخته شد: {role.id}")

        # Create organization
        org = Organization(
            id=uuid.uuid4(),
            legal_name_fa="شرکت پیش‌حسابداری",
            national_company_id=None,
            is_active=True,
            key_store_id=None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(org)
        await session.flush()

        # Create user with Argon2id hashed password
        password = "PishHesabdari2026!"  # ← تغییر دهید در اولین ورود
        password_hash = _hasher.hash(password).encode("utf-8")

        user = User(
            id=uuid.uuid4(),
            email_normalized="manager@example.com",  # ← تغییر دهید در اولین ورود
            display_name_fa="مدیر سیستم",
            password_hash=password_hash,
            password_params=None,
            totp_secret_enc=None,
            totp_enabled=False,
            is_platform_admin=True,
            is_active=True,
            failed_attempts=0,
            locked_until=None,
            last_login_at=None,
            must_change_password=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(user)
        await session.flush()

        # Create membership with the real role_id
        membership = OrganizationMembership(
            id=uuid.uuid4(),
            organization_id=org.id,
            user_id=user.id,
            role_id=role.id,
            is_active=True,
            invited_by=None,
            accepted_at=datetime.now(timezone.utc),
        )
        session.add(membership)

        await session.commit()
        print(f"✅ کاربر ساخته شد: {user.email_normalized}")
        print(f"🔑 رمز عبور: {password}")
        print(f"🏢 سازمان: {org.legal_name_fa}")
        print(f"⚠️  رمز عبور و ایمیل را در اولین ورود تغییر دهید.")
        print(f"🗑️  بعد از لاگین موفق، فایل create_first_user.py را حذف کنید.")


if __name__ == "__main__":
    asyncio.run(main())
