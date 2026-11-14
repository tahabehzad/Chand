"""Deterministic statutory calculation engines.

The package currently exposes the exact Decimal money primitives and the Rial
rounding policy (WBS P1-T04).  Engines are pure: they never read the clock,
randomness, the network or the environment.  Importing this package also sets
the shared decimal context (``prec=34``, ``ROUND_HALF_UP``) once, as required by
HB-NFR-010 and ``docs/EXECUTION_PLAN.md`` §7.2.

Authority: ``docs/PISH_HESABDARI_HOLY_BIBLE.md`` §13.8 rule 7.
"""

from __future__ import annotations

from app.engines.money import (
    MAX_RESIDUAL_RIAL_PER_LINE,
    MONEY_PRECISION,
    RIAL_QUANTUM,
    MoneyError,
    MoneyTypeError,
    MoneyValueError,
    RialAllocation,
    RoundingReport,
    RoundingResidualError,
    allocate_rial,
    quantize_rial,
    reconcile_lines,
    round_half_up,
    round_rial,
    round_total_rial,
    rounding_residual_rial,
    split_rial,
    to_decimal,
)

__all__ = (
    "MAX_RESIDUAL_RIAL_PER_LINE",
    "MONEY_PRECISION",
    "RIAL_QUANTUM",
    "MoneyError",
    "MoneyTypeError",
    "MoneyValueError",
    "RialAllocation",
    "RoundingReport",
    "RoundingResidualError",
    "allocate_rial",
    "quantize_rial",
    "reconcile_lines",
    "round_half_up",
    "round_rial",
    "round_total_rial",
    "rounding_residual_rial",
    "split_rial",
    "to_decimal",
)
