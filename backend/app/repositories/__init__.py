"""Data-access layer.

Authority
---------
``docs/adr/ADR-014-market-salary-reference-data-and-estimation.md`` §8 (a
repository for market data, separate from the domain);
``docs/ARCHITECTURE.md`` §2 (dependency direction ``api → schemas → services →
domain → repositories → models``).

Related
-------
``app/repositories/market_data.py`` — the only module in this package today.

Scope
-----
Repositories own SQL.  Domain modules stay framework-free, so a driver change can
never change a calculation.
"""

from __future__ import annotations

from app.repositories import market_data, statutory_repository
from app.repositories.statutory_repository import (
    InMemoryStatutoryRepository,
    SqlStatutoryRepository,
    StatutoryRepository,
    StatutoryRuleSetRecord,
    get_default_statutory_repository,
    set_default_statutory_repository,
)

__all__ = (
    "InMemoryStatutoryRepository",
    "SqlStatutoryRepository",
    "StatutoryRepository",
    "StatutoryRuleSetRecord",
    "get_default_statutory_repository",
    "market_data",
    "set_default_statutory_repository",
    "statutory_repository",
)
