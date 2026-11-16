"""Service layer: the only place where calculation engines are composed.

``docs/EXECUTION_PLAN.md`` §7.1 — engines are composed only in services.
"""
from __future__ import annotations

from app.services.payroll_service import (
    ENGINE_VERSION,
    PayrollInput,
    PayrollResult,
    compute_gross_to_net,
)

__all__ = ("ENGINE_VERSION", "PayrollInput", "PayrollResult", "compute_gross_to_net")
