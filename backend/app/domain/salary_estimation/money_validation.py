"""Post-conditions for a published estimate.

Authority
---------
``AGENTS.md`` §2 Financial invariants 7-8 (round once at the boundary, surface the
residual) and ADR-013's currency convention (store Rial, display Toman) as
reconciled in ``docs/adr/ADR-014-market-salary-reference-data-and-estimation.md``
§4.6.

Related
-------
``salary_estimator.py`` (produces the figures), ``app/services/estimation/service.py``
(calls this guard before responding).

Scope
-----
A guard, not a calculation.  The previous version of this module was named
``validate_range_consistency`` but only summed the values, so it passed for
``min > max``; the check below is the one its name always promised.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ("EstimationInvariantError", "MoneyPathReport", "validate_estimate_money_path")

#: Published figures are whole-Toman multiples so the UI never rounds.
TOMAN_QUANTUM_RIAL = 10


class EstimationInvariantError(RuntimeError):
    """A published figure violated a money-path invariant.

    This is an engine defect, never a user error: the router turns it into a 500
    and the estimate is withheld.
    """


@dataclass(frozen=True)
class MoneyPathReport:
    """The outcome of the post-condition checks."""

    ordering_ok: bool
    toman_exact: bool
    issues: tuple[str, ...]

    @property
    def passed(self) -> bool:
        """Whether every invariant held."""
        return not self.issues


def validate_estimate_money_path(
    min_salary_rial: int,
    median_salary_rial: int,
    primary_estimate_rial: int,
    max_salary_rial: int,
) -> MoneyPathReport:
    """Check ordering, non-negativity and exact Toman divisibility.

    ``median == primary`` is required because the published recommendation *is*
    the market median of the validated cohort: any other value would mean an
    undocumented adjustment had been applied.
    """
    issues: list[str] = []
    values = {
        "min_salary_rial": min_salary_rial,
        "median_salary_rial": median_salary_rial,
        "primary_estimate_rial": primary_estimate_rial,
        "max_salary_rial": max_salary_rial,
    }
    for name, value in values.items():
        if value < 0:
            issues.append(f"{name} is negative")
        if value % TOMAN_QUANTUM_RIAL != 0:
            issues.append(f"{name} is not a whole-Toman multiple")
    if not (min_salary_rial <= median_salary_rial <= max_salary_rial):
        issues.append("range is not ordered min <= median <= max")
    if primary_estimate_rial != median_salary_rial:
        issues.append("primary estimate differs from the market median without a documented adjustment")

    return MoneyPathReport(
        ordering_ok=min_salary_rial <= median_salary_rial <= max_salary_rial,
        toman_exact=all(value % TOMAN_QUANTUM_RIAL == 0 for value in values.values()),
        issues=tuple(issues),
    )
