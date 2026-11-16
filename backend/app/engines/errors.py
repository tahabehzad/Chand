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
* **One taxonomy (remediation A-9 / B-11).** Every refusal raised on the
  calculation path is a subclass of :class:`PayrollEngineError` and carries a
  stable ``code`` property.  No engine raises a bare ``ValueError`` for a
  domain refusal, so the API can map every refusal to the documented
  ``{"error": {"code", "detail"}}`` envelope by reading ``exc.code`` instead
  of string-sniffing the message.  The message *also* starts with the code,
  which keeps the historical text contract (and every existing log line)
  intact while the code is read structurally.
* The codes are stable machine identifiers.  They are part of the published
  error contract and are never localised.
"""

from __future__ import annotations

__all__ = (
    "BaseDecompositionNegative",
    "MonthLengthInvalid",
    "PayrollEngineError",
    "PayrollInputError",
    "ProbationBeyondStatutoryMax",
    "RuleSetNotActive",
    "StatutoryInvariantViolation",
    "StatutoryParameterUnavailable",
    "TaxableBaseNegative",
)


class PayrollEngineError(ValueError):
    """Base class for statutory payroll engine failures.

    Subclasses override :attr:`code`; the base class carries a generic code so
    a future subclass can never emit an empty machine identifier.

    Inheriting from :class:`ValueError` preserves the historical contract:
    every pre-remediation refusal was a ``ValueError`` whose message began
    with the stable code, so existing callers that catch ``ValueError`` keep
    working while new callers can read ``exc.code`` structurally.
    """

    #: Stable categorical error code surfaced by the API.
    code: str = "PAYROLL_ENGINE_ERROR"


class StatutoryParameterUnavailable(PayrollEngineError):
    """A required statutory parameter is null, missing or unverified.

    Raised for the inactive 1405 placeholder, for any null parameter in a
    seed, and for any structural invariant violation detected at load time.
    """

    code = "STATUTORY_PARAMETER_UNAVAILABLE"


class StatutoryInvariantViolation(StatutoryParameterUnavailable):
    """A loaded rule set violates a documented structural invariant.

    It is a *kind* of :class:`StatutoryParameterUnavailable` (the rule set
    cannot be used), but the specific code lets an operator distinguish a
    malformed seed from an unverified one without parsing the message.
    """

    code = "STATUTORY_INVARIANT_VIOLATION"


class RuleSetNotActive(PayrollEngineError):
    """The requested rule set does not exist or is not loadable at all."""

    code = "RULE_SET_NOT_ACTIVE"


class TaxableBaseNegative(PayrollEngineError):
    """A taxable base was supplied negative; computation refused.

    A negative *post-exemption* base reaching the ladder is a programming
    defect: :func:`app.engines.tax.compute_tax_for_posture` clamps a negative
    taxable income to zero before the ladder, so the refusal here means an
    unclamped caller bypassed that boundary.  It is therefore a domain error,
    not an input error, and it is surfaced with its own code
    (remediation A-9).
    """

    code = "TAXABLE_BASE_NEGATIVE"


class PayrollInputError(PayrollEngineError):
    """An input violates the calculation contract; nothing is coerced."""

    code = "PAYROLL_INPUT_INVALID"


class MonthLengthInvalid(PayrollInputError):
    """``days_in_month`` is outside the statutory {29, 30, 31} set."""

    code = "PAYROLL_MONTH_LENGTH_INVALID"


class BaseDecompositionNegative(PayrollInputError):
    """The gross does not cover the declared welfare allowances.

    Never clamped: a negative *Mozd-e Saabet* is an input-contract violation.
    """

    code = "BASE_DECOMPOSITION_NEGATIVE"


class ProbationBeyondStatutoryMax(PayrollInputError):
    """The probation period exceeds the Art. 11 three-month maximum."""

    code = "PROBATION_BEYOND_STATUTORY_MAX"
