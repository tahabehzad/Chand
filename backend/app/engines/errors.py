"""Domain error catalogue for the statutory payroll engine.

Authority
---------
``docs/PISH_HESABDARI_HOLY_BIBLE.md`` §3.2 Module 1 (error catalogue) and
§10.6 (fail-closed loader behaviour); ``docs/EXECUTION_PLAN.md`` §7.2 rule 6.

Contract notes
--------------
* Every failure is **fail-closed and categorical**: the message carries a
  stable code, never a monetary amount, a secret or a raw exception trace.
* ``StatutoryParameterUnavailable`` is the single refusal raised when a
  statutory parameter is null, missing, unverified or otherwise unusable —
  a null is never coerced to zero and there is never a silent fallback to
  another rule year.
"""

from __future__ import annotations

__all__ = (
    "PayrollEngineError",
    "PayrollInputError",
    "RuleSetNotActive",
    "StatutoryParameterUnavailable",
    "TaxableBaseNegative",
)


class PayrollEngineError(RuntimeError):
    """Base class for statutory payroll engine failures."""


class StatutoryParameterUnavailable(PayrollEngineError):
    """A required statutory parameter is null, missing or unverified.

    Raised for the inactive 1405 placeholder, for any null parameter in a
    seed, and for any structural invariant violation detected at load time.
    """

    @property
    def code(self) -> str:
        """Return the stable categorical error code."""
        return "STATUTORY_PARAMETER_UNAVAILABLE"


class RuleSetNotActive(PayrollEngineError):
    """The requested rule set does not exist or is not loadable at all."""

    @property
    def code(self) -> str:
        """Return the stable categorical error code."""
        return "RULE_SET_NOT_ACTIVE"


class TaxableBaseNegative(PayrollEngineError):
    """A taxable base was supplied negative; computation refused."""

    @property
    def code(self) -> str:
        """Return the stable categorical error code."""
        return "TAXABLE_BASE_NEGATIVE"


class PayrollInputError(PayrollEngineError):
    """An input violates the calculation contract; nothing is coerced."""

    @property
    def code(self) -> str:
        """Return the stable categorical error code."""
        return "PAYROLL_INPUT_INVALID"
