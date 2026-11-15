"""Exact Decimal money primitives and the Rial rounding policy.

Authority:
    ``docs/PISH_HESABDARI_HOLY_BIBLE.md`` §13.8 rule 7 (Decimal only, round once,
    surfaced residual) and HB-NFR-010 (``prec=34``, ``ROUND_HALF_UP``).
Spec:
    ``docs/EXECUTION_PLAN.md`` §7.2 rules 2-3 and §11.1 invariant (2);
    ``docs/specs/TESTING.md`` §3.1 (money-safety AST gate), §4.2 (reconciliation
    invariants) and §4.3 (rounding policy under test).
Related:
    WBS P1-T04 — Decimal money primitives and the rounding policy.

Contract notes
--------------
* Money enters this module as :class:`decimal.Decimal`, ``int`` Rial or an exact
  decimal ``str``.  ``float``/``bool`` are rejected: a binary float must never
  enter a monetary path.
* Arithmetic uses ``Decimal`` with ``prec=34`` and ``ROUND_HALF_UP`` only.  The
  built-in ``round()`` (banker's rounding) is never used.
* The shared process context is configured at import (``getcontext().prec =
  34``, ``ROUND_HALF_UP``), but every primitive quantizes and sums inside the
  module's own internal context.  A caller that mutates the ambient decimal
  context therefore cannot change a Rial figure: the result stays a pure
  function of the input value.
* A line item is rounded once, at the line-item boundary.  A total is rounded
  once from the *exact* sum, not from already-rounded lines.  The signed
  difference is surfaced as ``rounding_residual_rial``:

      ``residual_rial = Σ(rounded line items) - rounded total``

  which is the formula in EXECUTION_PLAN §11.1(2) and TESTING §4.2(2).  The
  amount that must be *posted* as an explicit residual line so that the posting
  lines add up to the total is the negation of that figure; it is exposed
  separately as :attr:`RoundingReport.closing_adjustment_rial` so that neither
  sign convention is chosen silently.
* Whole-Rial amounts are distributed with the largest-remainder method, so the
  parts sum exactly to the total and the allocation residual is always zero.
* This module is a pure calculation module: no clock, randomness, network,
  filesystem or environment reads take place at call time or on import.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from decimal import (
    ROUND_DOWN,
    ROUND_HALF_UP,
    Clamped,
    Context,
    Decimal,
    DivisionByZero,
    FloatOperation,
    Inexact,
    InvalidOperation,
    Overflow,
    Rounded,
    Subnormal,
    Underflow,
    getcontext,
    localcontext,
)

#: Shared decimal precision required by HB-NFR-010 and EXECUTION_PLAN §7.2.
MONEY_PRECISION: int = 34

#: The only quantum a monetary figure may be emitted in: one whole Rial.
RIAL_QUANTUM: Decimal = Decimal("1")

#: Maximum signed rounding residual attributable to one line item, in Rial.
MAX_RESIDUAL_RIAL_PER_LINE: int = 1

#: Internal context for guards that must not inherit an ambient mutation.
#:
#: The context is built explicitly rather than inherited from
#: ``DefaultContext`` so that neither the ambient thread context nor a mutated
#: ``decimal.DefaultContext`` can change a monetary result.  Every signal is
#: listed because ``Context`` rejects a partial trap mapping.
#:
#: ``InvalidOperation``, ``DivisionByZero`` and ``Overflow`` keep Python's
#: default trapping, so a value that cannot be represented at ``prec=34``
#: still fails closed.  ``Rounded`` and ``Inexact`` are deliberately **not**
#: trapped: rounding a non-whole Rial to a whole Rial is this module's own
#: policy and legitimately sets both flags, so rejecting every rounding flag
#: would reject the module's contract.  ``FloatOperation`` stays untrapped to
#: match Python's default; binary floats are rejected earlier, by type, in
#: :func:`to_decimal`.
_INTERNAL_CONTEXT: Context = Context(
    prec=MONEY_PRECISION,
    rounding=ROUND_HALF_UP,
    traps={
        Clamped: False,
        DivisionByZero: True,
        FloatOperation: False,
        Inexact: False,
        InvalidOperation: True,
        Overflow: True,
        Rounded: False,
        Subnormal: False,
        Underflow: False,
    },
)

# Configure the one shared process context at import.  Every consumer of
# ``decimal`` in the application is expected to inherit these settings
# (financial-data-integrity rule 2, HB-NFR-010).  Only precision and rounding
# mode are set; traps and flags are left untouched.
getcontext().prec = MONEY_PRECISION
getcontext().rounding = ROUND_HALF_UP


class MoneyError(ValueError):
    """Base class for money-contract violations."""


class MoneyTypeError(MoneyError, TypeError):
    """Raised when a value of a forbidden type (notably ``float``) is supplied."""


class MoneyValueError(MoneyError):
    """Raised when a value is of an accepted type but violates the contract."""


class RoundingResidualError(MoneyValueError):
    """Raised when a rounding residual exceeds the permitted per-line bound."""


def to_decimal(value: object, *, field: str = "value") -> Decimal:
    """Return *value* as an exact, finite :class:`~decimal.Decimal`.

    Accepted inputs are ``Decimal``, ``int`` and decimal ``str``.  ``float``,
    ``bool``, ``complex`` and every other type are rejected so that binary
    floating point cannot enter a calculation.  Construction from ``str`` keeps
    literals exact (``Decimal("0.07")``, never ``0.07``).

    Raises:
        MoneyTypeError: The value is not a ``Decimal``, ``int`` or ``str``.
        MoneyValueError: The value is not a finite decimal number.
    """
    if isinstance(value, (bool, float)):
        raise MoneyTypeError(
            f"{field} must be Decimal, int or str; float is banned on monetary values"
        )
    if isinstance(value, Decimal):
        result = value
    elif isinstance(value, int):
        result = Decimal(value)
    elif isinstance(value, str):
        try:
            result = Decimal(value)
        except (InvalidOperation, ValueError) as exc:
            raise MoneyValueError(f"{field} is not a valid decimal string") from exc
    else:
        raise MoneyTypeError(f"{field} must be Decimal, int or str, not {type(value).__name__}")
    if not result.is_finite():
        raise MoneyValueError(f"{field} must be a finite decimal number")
    return result


def quantize_rial(value: object, *, field: str = "value") -> Decimal:
    """Round *value* once to a whole Rial with ``ROUND_HALF_UP``.

    The result is a ``Decimal`` whose exponent is zero, so it can be emitted as
    an integer Rial without a second rounding.  Half-way values move away from
    zero (``2.5 -> 3``, ``-2.5 -> -3``); this is deliberately not Python's
    banker's rounding.  Negative zero is normalised to ``Decimal("0")``.

    The quantization runs inside the module's internal context (``prec=34``,
    ``ROUND_HALF_UP``), so the result is a pure function of *value* and cannot
    be changed by a caller that mutates the ambient decimal context — a
    lowered ambient precision can no longer reject a representable amount,
    and a raised ambient precision can no longer smuggle out a figure that
    exceeds ``prec=34``.  Ordinary quantization sets the ``Rounded`` and
    ``Inexact`` flags; they are expected here and are not treated as errors.

    Raises:
        MoneyTypeError: The value has a forbidden type.
        MoneyValueError: The value is not finite or does not fit ``prec=34``.
    """
    decimal_value = to_decimal(value, field=field)
    try:
        with localcontext(_INTERNAL_CONTEXT):
            quantized = decimal_value.quantize(RIAL_QUANTUM, rounding=ROUND_HALF_UP)
    except InvalidOperation as exc:
        raise MoneyValueError(
            f"{field} cannot be represented at precision {MONEY_PRECISION} Rial"
        ) from exc
    if quantized == 0:
        return Decimal(0)
    return quantized


def round_half_up(value: object, *, field: str = "value") -> int:
    """Return *value* rounded once to an ``int`` number of Rial (half-up)."""
    return int(quantize_rial(value, field=field))


#: Alias used by TESTING §5 property P-15 (``round_half_up`` monotonicity).
round_rial = round_half_up


def _require_int(value: object, *, field: str) -> int:
    """Return *value* if it is a genuine ``int`` (``bool`` rejected)."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise MoneyTypeError(f"{field} must be an int number of Rial")
    return value


def _require_whole_rial(value: object, *, field: str) -> int:
    """Return *value* as an ``int`` Rial, rejecting any fractional part.

    A fractional total means a rounding step is missing upstream; allocating it
    would round a second time and hide the error.
    """
    decimal_value = to_decimal(value, field=field)
    if decimal_value != decimal_value.to_integral_value(rounding=ROUND_DOWN):
        raise MoneyValueError(
            f"{field} must already be a whole number of Rial; "
            "round the total once before allocating it"
        )
    return int(decimal_value)


def _sum_decimals(values: Iterable[Decimal], *, field: str) -> Decimal:
    """Return the exact sum of *values*, refusing a lossy (``prec=34``) sum."""
    with localcontext(_INTERNAL_CONTEXT) as context:
        context.clear_flags()
        total = sum(values, Decimal(0))
        if context.flags[Rounded] or context.flags[Inexact]:
            raise MoneyValueError(
                f"{field} exceeds {MONEY_PRECISION} significant digits; "
                "the exact sum cannot be represented"
            )
    return total


def _exact_sum(values: Iterable[object], *, field: str) -> Decimal:
    """Convert and exactly sum *values*, naming the offending field on error."""
    decimals = tuple(
        to_decimal(value, field=f"{field}[{index}]") for index, value in enumerate(values)
    )
    return _sum_decimals(decimals, field=field)


def round_total_rial(values: Iterable[object], *, field: str = "total") -> int:
    """Round the exact sum of *values* once to an ``int`` Rial total."""
    return round_half_up(_exact_sum(values, field=field), field=field)


def rounding_residual_rial(
    rounded_lines_rial: Iterable[object],
    total_rial: object,
) -> int:
    """Return ``Σ(rounded line items) - total``, signed, exactly as specified.

    This is the binding sign convention of EXECUTION_PLAN §11.1(2) and
    TESTING §4.2(2).  If an explicit residual line must be posted so that the
    lines sum to the total, post the negation (see
    :attr:`RoundingReport.closing_adjustment_rial`).
    """
    lines = tuple(
        _require_int(value, field=f"rounded_lines_rial[{index}]")
        for index, value in enumerate(rounded_lines_rial)
    )
    total = _require_int(total_rial, field="total_rial")
    return sum(lines) - total


@dataclass(frozen=True, slots=True)
class RoundingReport:
    """The rounded lines, the rounded total and the surfaced residual.

    Attributes:
        lines_rial: Each exact line rounded once to whole Rial.
        total_rial: The exact total rounded once to whole Rial.
        residual_rial: ``sum(lines_rial) - total_rial``.  A positive value
            means independently rounded lines overstate the total; a negative
            value means they understate it.

    The constructor validates both the reconciliation identity and the
    per-line residual bound, so an inconsistent report cannot exist.
    """

    lines_rial: tuple[int, ...]
    total_rial: int
    residual_rial: int

    def __post_init__(self) -> None:
        lines = tuple(
            _require_int(value, field=f"lines_rial[{index}]")
            for index, value in enumerate(self.lines_rial)
        )
        total = _require_int(self.total_rial, field="total_rial")
        residual = _require_int(self.residual_rial, field="residual_rial")
        expected = sum(lines) - total
        if residual != expected:
            raise MoneyValueError("residual_rial does not equal sum(lines_rial) - total_rial")
        bound = MAX_RESIDUAL_RIAL_PER_LINE * len(lines)
        if abs(residual) > bound:
            raise RoundingResidualError(
                "residual_rial exceeds the permitted bound of one Rial per line"
            )
        # Copy validated inputs so a caller-owned mutable iterable cannot
        # invalidate this frozen report after construction.
        object.__setattr__(self, "lines_rial", lines)

    @property
    def rounding_residual_rial(self) -> int:
        """Return the public residual: sum of rounded lines minus rounded total.

        ``residual_rial`` remains available for existing callers. This public
        name follows TESTING §4.2(2); a closing posting uses the opposite sign.
        """
        return self.residual_rial

    @property
    def sum_lines_rial(self) -> int:
        """Return the sum of the individually rounded line items, in Rial."""
        return sum(self.lines_rial)

    @property
    def closing_adjustment_rial(self) -> int:
        """Return the signed residual line to post so lines add up to the total.

        This is ``total_rial - sum(lines_rial)``, the negation of
        :attr:`rounding_residual_rial`. Use the separate name
        ``closing_adjustment_rial`` for this posting; publishing it under the
        public residual name would reverse the binding sign convention.
        """
        return self.total_rial - self.sum_lines_rial


def reconcile_lines(
    exact_lines: Iterable[object],
    *,
    field: str = "line",
) -> RoundingReport:
    """Round each line once and the exact total once, surfacing the residual.

    Each element of *exact_lines* is an unrounded monetary amount; it is rounded
    exactly once to whole Rial.  The total is rounded exactly once from the sum
    of the *unrounded* lines.  No rounded intermediate is reused.

    Raises:
        MoneyTypeError: An element has a forbidden type.
        MoneyValueError: An element is not finite or the exact sum is not
            representable at ``prec=34``.
        RoundingResidualExceeded: The residual exceeds 1 Rial per line.
    """
    decimals = tuple(
        to_decimal(value, field=f"{field}[{index}]") for index, value in enumerate(exact_lines)
    )
    lines_rial = tuple(
        round_half_up(value, field=f"{field}[{index}]") for index, value in enumerate(decimals)
    )
    total_rial = round_half_up(
        _sum_decimals(decimals, field=field),
        field=field,
    )
    residual_rial = sum(lines_rial) - total_rial
    return RoundingReport(
        lines_rial=lines_rial,
        total_rial=total_rial,
        residual_rial=residual_rial,
    )


def _integer_weights(
    weights: tuple[Decimal, ...],
    *,
    field: str,
) -> tuple[int, ...]:
    """Scale finite, non-negative decimal *weights* to exact integers."""
    normalised = tuple(Decimal(0) if weight == 0 else weight for weight in weights)
    scale = 0
    for weight in normalised:
        exponent = weight.as_tuple().exponent
        if not isinstance(exponent, int):  # pragma: no cover - finite guaranteed
            raise MoneyValueError(f"{field} has no finite decimal exponent")
        if exponent < 0:
            scale = max(scale, -exponent)
        if weight != 0 and weight.adjusted() >= MONEY_PRECISION:
            raise MoneyValueError(f"{field} magnitude exceeds {MONEY_PRECISION} significant digits")
    if scale > MONEY_PRECISION:
        raise MoneyValueError(f"{field} has more than {MONEY_PRECISION} decimal places")
    integers: list[int] = []
    for weight in normalised:
        exponent = weight.as_tuple().exponent
        if not isinstance(exponent, int):  # pragma: no cover - finite guaranteed
            raise MoneyValueError(f"{field} has no finite decimal exponent")
        mantissa = 0
        for digit in weight.as_tuple().digits:
            mantissa = mantissa * 10 + digit
        integers.append(mantissa * 10 ** (exponent + scale))
    return tuple(integers)


@dataclass(frozen=True, slots=True)
class RialAllocation:
    """A whole-Rial total split into parts that sum exactly to that total.

    ``parts_rial`` preserves the caller's weight order.  The allocation residual
    is structurally zero; :attr:`residual_rial` re-derives it for audit.
    """

    total_rial: int
    parts_rial: tuple[int, ...]

    def __post_init__(self) -> None:
        total = _require_int(self.total_rial, field="total_rial")
        parts = tuple(
            _require_int(value, field=f"parts_rial[{index}]")
            for index, value in enumerate(self.parts_rial)
        )
        if not parts:
            raise MoneyValueError("parts_rial must not be empty")
        if sum(parts) != total:
            raise MoneyValueError("parts_rial do not sum to total_rial")
        object.__setattr__(self, "parts_rial", parts)

    @property
    def rounding_residual_rial(self) -> int:
        """Return the public allocation residual, always zero by construction."""
        return self.residual_rial

    @property
    def residual_rial(self) -> int:
        """Return ``sum(parts_rial) - total_rial``; always zero by contract."""
        return sum(self.parts_rial) - self.total_rial


def allocate_rial(
    total_rial: object,
    weights: Iterable[object],
    *,
    field: str = "weight",
) -> RialAllocation:
    """Distribute a whole-Rial total by *weights* with largest remainders.

    The method is deterministic: each part receives the floor of its exact
    share, and the remaining Rial are assigned one each to the largest
    fractional remainders, ties broken by ascending weight index.  Weights must
    be finite, non-negative decimals; a zero weight always receives zero.  The
    parts sum exactly to the total, so the allocation residual is zero.

    A negative total is allocated by magnitude and negated, preserving the
    exact-sum guarantee.

    Raises:
        MoneyTypeError: A weight has a forbidden type.
        MoneyValueError: *total_rial* is not a whole Rial, the weight list is
            empty, a weight is negative, or all weights are zero.
    """
    total = _require_whole_rial(total_rial, field="total_rial")
    weight_values = tuple(
        to_decimal(weight, field=f"{field}[{index}]") for index, weight in enumerate(weights)
    )
    if not weight_values:
        raise MoneyValueError(f"{field} list must not be empty")
    for index, weight in enumerate(weight_values):
        if weight < 0:
            raise MoneyValueError(f"{field}[{index}] must not be negative")
    integer_weights = _integer_weights(weight_values, field=field)
    weight_sum = sum(integer_weights)
    if weight_sum == 0:
        raise MoneyValueError(f"{field} list must not sum to zero")

    total_magnitude = abs(total)
    parts = [0] * len(integer_weights)
    remainders = [0] * len(integer_weights)
    for index, integer_weight in enumerate(integer_weights):
        parts[index], remainders[index] = divmod(total_magnitude * integer_weight, weight_sum)

    leftover = total_magnitude - sum(parts)
    if leftover:
        order = sorted(
            range(len(parts)),
            key=lambda index: (-remainders[index], index),
        )
        eligible = [index for index in order if integer_weights[index] > 0]
        if leftover > len(eligible):  # pragma: no cover - mathematically impossible
            raise MoneyValueError("internal largest-remainder allocation error")
        for index in eligible[:leftover]:
            parts[index] += 1

    if total < 0:
        parts = [-part for part in parts]
    return RialAllocation(total_rial=total, parts_rial=tuple(parts))


def split_rial(total_rial: object, parts: int) -> RialAllocation:
    """Split a whole-Rial total into *parts* equal shares by largest remainder.

    Extra Rial are assigned to the lowest indices, which makes the result
    deterministic; the shares sum exactly to the total.
    """
    if isinstance(parts, bool) or not isinstance(parts, int) or parts < 1:
        raise MoneyValueError("parts must be a positive int")
    return allocate_rial(total_rial, (1 for _ in range(parts)), field="share")


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
