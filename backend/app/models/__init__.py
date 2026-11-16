"""Declarative base for Pish Hesabdari database models.

Currently hosts only the statutory provenance models (WBS ``P0-T04``;
``app.models.statutory``). Other schema tasks add their own modules here:
identity/tenancy (``P0-T05``), the audit ledger (``P0-T10``) and the
forensic document model (``P2-T01``).

Constraints use explicit, stable names in every model and migration so the
catalogue is introspectable (docs/specs/STATUTORY_DATABASE_CONTRACT.md §4,
AC-07 / AC-12).
"""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base for all Pish Hesabdari tables."""
