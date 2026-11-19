"""Declarative base for Pish Hesabdari database models.

Hosts the statutory provenance models (WBS ``P0-T04``; ``app.models.statutory``),
the tenant identity schema (``P0-T05``; ``app.models.identity``), the manager
workspace (``P0-T09``/ADR-009; ``app.models.manager``) and the append-only,
hash-chained audit ledger (``P0-T10``; ``app.models.audit``).  Importing a
model module registers its tables on :class:`Base` so Alembic autogenerate and
catalogue introspection see the full schema.

Constraints use explicit, stable names in every model and migration so the
catalogue is introspectable (docs/specs/STATUTORY_DATABASE_CONTRACT.md §4,
AC-07 / AC-12).
"""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base for all Pish Hesabdari tables."""


from app.models import audit, estimation, identity, manager, statutory, work_profile  # noqa: E402

__all__ = ("Base", "audit", "estimation", "identity", "manager", "statutory", "work_profile")
