"""Unit tests for the Decimal money primitives and the Rial rounding policy.

Authority:
    ``docs/PISH_HESABDARI_HOLY_BIBLE.md`` §13.8 rule 7.
Spec:
    ``docs/EXECUTION_PLAN.md`` §7.2 rules 2-3, §11.1 invariant (2);
    ``docs/specs/TESTING.md`` §3.1, §4.2, §4.3 and property P-15.
Related:
    WBS P1-T04 — Decimal money primitives and the rounding policy.
"""

from __future__ import annotations

import ast
from decimal import (
    ROUND_HALF_EVEN,
    ROUND_HALF_UP,
    Decimal,
    Inexact,
    Rounded,
    getcontext,
    localcontext,
)
from pathlib import Path

import pytest
from hypothesis import given, settings, strategies as st

from app.engines import (
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
    money as money_module,
    quantize_rial,
    reconcile_lines,
    round_half_up,
    round_rial,
    round_total_rial,
    rounding_residual_rial,
    split_rial,
    to_decimal,
)

ENGINES_ROOT = Path(__file__).resolve().parents[2] / "app" / "engines"


# ---------------------------------------------------------------------------
# Shared context (TESTING §4.3: precision 34, ROUND_HALF_UP only)
# ---------------------------------------------------------------------------


def test_shared_context_is_precision_34_half_up() -> None:
    assert MONEY_PRECISION == 34
    assert getcontext().prec == 34
    assert getcontext().rounding == ROUND_HALF_UP
    assert int(RIAL_QUANTUM) == 1
    assert MAX_RESIDUAL_RIAL_PER_LINE == 1


def test_package_reexports_the_public_contract() -> None:
    assert money_module.round_half_up is round_half_up
    assert money_module.reconcile_lines is reconcile_lines
    assert money_module.allocate_rial is allocate_rial
    assert money_module.RoundingReport is RoundingReport
    assert money_module.MoneyError is MoneyError


# ---------------------------------------------------------------------------
# Exact construction — no float may enter
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (Decimal("0.1"), Decimal("0.1")),
        (7, Decimal(7)),
        ("0.07", Decimal("0.07")),
        ("001.50", Decimal("1.50")),
        ("1E+3", Decimal("1000")),
    ],
)
def test_to_decimal_accepts_exact_types(value: object, expected: Decimal) -> None:
    assert to_decimal(value) == expected


def test_to_decimal_keeps_decimal_literals_exact() -> None:
    assert to_decimal("0.1") + to_decimal("0.2") == Decimal("0.3")
    binary_tenth = 0.1
    assert to_decimal("0.1") != Decimal(binary_tenth)


@pytest.mark.parametrize("value", [0.1, 1.0, float("nan"), True, False, None, [], 1 + 2j])
def test_to_decimal_rejects_forbidden_types(value: object) -> None:
    with pytest.raises(MoneyTypeError):
        to_decimal(value)


@pytest.mark.parametrize("value", ["", "12,000", "NaN", "sNaN", "-Infinity", "abc"])
def test_to_decimal_rejects_non_finite_or_malformed_strings(value: str) -> None:
    with pytest.raises(MoneyValueError):
        to_decimal(value)


def test_to_decimal_rejects_non_finite_decimal() -> None:
    with pytest.raises(MoneyValueError):
        to_decimal(Decimal("Infinity"))


# ---------------------------------------------------------------------------
# Rounding: one half-up step to whole Rial
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("0", 0),
        ("0.4", 0),
        ("0.5", 1),
        ("0.5000001", 1),
        ("1.4999999", 1),
        ("1.5", 2),
        ("2.5", 3),
        ("-0.4", 0),
        ("-0.5", -1),
        ("-1.5", -2),
        ("-2.5", -3),
        ("123.49", 123),
        ("123.50", 124),
    ],
)
def test_round_half_up_rounds_away_from_zero_on_ties(value: str, expected: int) -> None:
    assert round_half_up(value) == expected
    assert round_rial(value) == expected


def test_quantize_rial_returns_whole_rial_decimal() -> None:
    quantized = quantize_rial("2.5")
    assert quantized == Decimal("3")
    assert quantized.as_tuple().exponent == 0
    assert quantize_rial("-0.4") == 0
    assert str(quantize_rial("-0.4")) == "0"


def test_half_up_is_not_bankers_rounding_even_if_context_changes() -> None:
    with localcontext() as context:
        context.rounding = ROUND_HALF_EVEN
        assert round_half_up("2.5") == 3
        assert round_half_up("-2.5") == -3


def test_precision_34_prevents_default_28_digit_loss() -> None:
    value = Decimal("1234567890123456789012345678.5")
    assert round_half_up(value) == 1234567890123456789012345679


# ---------------------------------------------------------------------------
# Ambient decimal context must not change a Rial figure
# ---------------------------------------------------------------------------

#: 31 digits before the point, one after: 32 significant digits, below the
#: 34-digit money precision, so the amount is representable and must round to
#: the same whole Rial under any ambient context.
HIGH_PRECISION_HALF_RIAL = Decimal("1000000000000000000000000000000.5")
HIGH_PRECISION_EXPECTED_RIAL = 1000000000000000000000000000001


def test_quantize_rial_is_independent_of_the_ambient_precision() -> None:
    for precision in (34, 28, 12, 60):
        with localcontext() as context:
            context.prec = precision
            assert quantize_rial(HIGH_PRECISION_HALF_RIAL) == Decimal(HIGH_PRECISION_EXPECTED_RIAL)
            assert round_half_up(HIGH_PRECISION_HALF_RIAL) == HIGH_PRECISION_EXPECTED_RIAL


def test_quantize_rial_still_rejects_values_beyond_precision_34() -> None:
    # A wide ambient context must not smuggle out a figure that exceeds prec=34.
    with localcontext() as context:
        context.prec = 60
        with pytest.raises(MoneyValueError):
            quantize_rial("1E+40")
    with localcontext() as context:
        context.prec = 60
        with pytest.raises(MoneyValueError):
            round_half_up(Decimal("1" + "0" * 40))


def test_round_total_rial_is_independent_of_the_ambient_precision() -> None:
    values = ["1234567890123456789012345678.5", "0.5"]
    with localcontext() as context:
        context.prec = 12
        total = round_total_rial(values)
    assert total == 1234567890123456789012345679


def test_reconcile_lines_is_independent_of_the_ambient_precision() -> None:
    with localcontext() as context:
        context.prec = 12
        report = reconcile_lines(["0.4", "0.4", "0.4"])
    assert report.lines_rial == (0, 0, 0)
    assert report.total_rial == 1
    assert report.residual_rial == -1


def test_quantize_rial_is_independent_of_the_ambient_exponent_range() -> None:
    with localcontext() as context:
        context.Emax = 9
        context.Emin = -9
        assert quantize_rial("1E+20") == Decimal("100000000000000000000")
        assert quantize_rial("1E-20") == Decimal("0")


def test_ambient_rounding_traps_do_not_break_ordinary_quantization() -> None:
    # Rounded/Inexact are the expected outcome of rounding to a whole Rial;
    # an ambient trap on them must not turn a valid figure into an error.
    with localcontext() as context:
        context.traps[Inexact] = True
        context.traps[Rounded] = True
        assert quantize_rial("2.5") == Decimal("3")
        assert round_half_up("2.5") == 3


def test_money_primitives_do_not_write_to_the_ambient_context() -> None:
    with localcontext() as context:
        context.prec = 34
        context.clear_flags()
        assert quantize_rial("2.5") == Decimal("3")
        assert round_half_up("2.5") == 3
        assert not context.flags[Inexact]
        assert not context.flags[Rounded]
        assert context.prec == 34


def test_the_shared_process_context_is_still_configured_at_34_half_up() -> None:
    # The fix isolates the primitives; it must not weaken the global policy.
    assert getcontext().prec == 34
    assert getcontext().rounding == ROUND_HALF_UP


def test_half_up_tie_is_the_specified_policy_not_a_defect() -> None:
    # REVIEW NOTE: "1.5 -> 2" is the specified ROUND_HALF_UP policy, not a bug.
    # The genuine ambient-context defect is the precision case above.
    assert round_half_up("1.5") == 2
    assert round_half_up("2.5") == 3
    assert round_half_up("-2.5") == -3
    with localcontext() as context:
        context.rounding = ROUND_HALF_EVEN
        assert round_half_up("1.5") == 2
        assert round_half_up("2.5") == 3
        assert round_half_up("-2.5") == -3


def test_quantize_rial_rejects_values_beyond_precision() -> None:
    with pytest.raises(MoneyValueError):
        quantize_rial("1E+40")


def test_round_half_up_is_monotonic_on_samples() -> None:
    samples = [Decimal(index) / Decimal(10) for index in range(-500, 501)]
    rounded = [round_half_up(value) for value in samples]
    assert rounded == sorted(rounded)


# ---------------------------------------------------------------------------
# Round-once totals and the surfaced residual
# ---------------------------------------------------------------------------


def test_round_total_rounds_the_exact_sum_once() -> None:
    assert round_total_rial(["0.4", "0.4", "0.4"]) == 1
    assert round_total_rial([]) == 0
    assert round_total_rial(["10", "20", "30"]) == 60


def test_residual_uses_the_binding_sign_convention() -> None:
    assert rounding_residual_rial([34, 33, 33], 100) == 0
    assert rounding_residual_rial([0, 0, 0], 1) == -1
    assert rounding_residual_rial([1, 1, 1], 2) == 1


def test_reconcile_lines_understated_lines_surface_negative_residual() -> None:
    report = reconcile_lines(["0.4", "0.4", "0.4"])
    assert report.lines_rial == (0, 0, 0)
    assert report.total_rial == 1
    assert report.residual_rial == -1
    assert report.closing_adjustment_rial == 1


def test_reconcile_lines_overstated_lines_surface_positive_residual() -> None:
    report = reconcile_lines(["0.6", "0.6", "0.6"])
    assert report.lines_rial == (1, 1, 1)
    assert report.total_rial == 2
    assert report.residual_rial == 1
    assert report.closing_adjustment_rial == -1


def test_reconcile_lines_exact_integer_case_has_zero_residual() -> None:
    report = reconcile_lines([10, 20, 30])
    assert report.lines_rial == (10, 20, 30)
    assert report.total_rial == 60
    assert report.residual_rial == 0
    assert report.closing_adjustment_rial == 0


def test_reconcile_lines_empty_input() -> None:
    report = reconcile_lines([])
    assert report.lines_rial == ()
    assert report.total_rial == 0
    assert report.residual_rial == 0


def test_reconcile_lines_does_not_reuse_a_rounded_intermediate() -> None:
    # If each line were quarter-rounded to 0.5 first, the total would be 3.
    # The contract rounds each line once and the exact total once.
    report = reconcile_lines(["0.4", "0.4", "0.4"])
    assert report.total_rial == 1


def test_report_validates_identity_and_bound() -> None:
    with pytest.raises(MoneyValueError):
        RoundingReport(lines_rial=(1,), total_rial=5, residual_rial=0)
    with pytest.raises(RoundingResidualError):
        RoundingReport(lines_rial=(0, 0), total_rial=5, residual_rial=-5)


def test_report_accepts_bound_of_one_per_line() -> None:
    report = RoundingReport(lines_rial=(2, 2), total_rial=3, residual_rial=1)
    assert report.sum_lines_rial == 4
    assert report.closing_adjustment_rial == -1


@pytest.mark.parametrize(
    ("lines", "expected"),
    [(["0.4", "0.4", "0.4"], -1), (["0.6", "0.6", "0.6"], 1), ([10, 20], 0)],
)
def test_public_residual_name_preserves_the_binding_sign(
    lines: list[object], expected: int
) -> None:
    report = reconcile_lines(lines)
    assert report.rounding_residual_rial == expected
    assert report.rounding_residual_rial == sum(report.lines_rial) - report.total_rial
    assert report.sum_lines_rial + report.closing_adjustment_rial == report.total_rial
    assert report.closing_adjustment_rial == -report.rounding_residual_rial


def test_report_preserves_identity_after_caller_mutates_input() -> None:
    lines = [1, 1]
    report = RoundingReport(lines_rial=lines, total_rial=2, residual_rial=0)  # type: ignore[arg-type]
    lines.append(100)
    assert report.lines_rial == (1, 1)
    assert report.rounding_residual_rial == report.sum_lines_rial - report.total_rial == 0


def test_allocation_preserves_identity_after_caller_mutates_input() -> None:
    parts = [1, 1]
    allocation = RialAllocation(total_rial=2, parts_rial=parts)  # type: ignore[arg-type]
    parts.append(100)
    assert allocation.parts_rial == (1, 1)
    assert sum(allocation.parts_rial) == allocation.total_rial
    assert allocation.rounding_residual_rial == allocation.residual_rial == 0


def test_invalid_report_errors_do_not_disclose_amounts() -> None:
    # Synthetic values only. These messages may reach a traceback/log sink.
    for total, residual in [(234567891, 0), (234567891, -234567890)]:
        with pytest.raises(MoneyValueError) as raised:
            RoundingReport(lines_rial=(1,), total_rial=total, residual_rial=residual)
        assert str(total) not in str(raised.value)
        assert str(abs(residual)) not in str(raised.value)


def test_invalid_allocation_error_does_not_disclose_amounts() -> None:
    with pytest.raises(MoneyValueError) as raised:
        RialAllocation(total_rial=234567891, parts_rial=(123456789,))
    assert "234567891" not in str(raised.value)
    assert "123456789" not in str(raised.value)


@settings(max_examples=200, database=None)
@given(st.integers(min_value=-(10**15), max_value=10**15), st.integers(1, 100))
def test_split_conserves_signed_total_and_equal_parts_differ_by_at_most_one(
    total: int, count: int
) -> None:
    allocation = split_rial(total, count)
    assert sum(allocation.parts_rial) == total
    assert len(allocation.parts_rial) == count
    assert max(allocation.parts_rial) - min(allocation.parts_rial) <= 1
    assert allocation.rounding_residual_rial == 0
    assert (
        all(part >= 0 for part in allocation.parts_rial)
        if total >= 0
        else all(part <= 0 for part in allocation.parts_rial)
    )


@settings(max_examples=200, database=None)
@given(st.lists(st.integers(min_value=-(10**12), max_value=10**12), max_size=100))
def test_reconciliation_surfaces_signed_residual_and_closes_exactly(
    thousandths: list[int],
) -> None:
    # Construct exact synthetic fractions without the ambient Decimal context.
    lines = [
        f"{'-' if amount < 0 else ''}{abs(amount) // 1000}.{abs(amount) % 1000:03d}"
        for amount in thousandths
    ]
    report = reconcile_lines(lines)
    assert sum(report.lines_rial) - report.total_rial == report.rounding_residual_rial
    assert abs(report.rounding_residual_rial) <= len(lines)
    assert sum(report.lines_rial) + report.closing_adjustment_rial == report.total_rial


def test_reconcile_lines_rejects_exact_sum_beyond_precision() -> None:
    with pytest.raises(MoneyValueError):
        reconcile_lines([Decimal("1" + "0" * 33), Decimal("0.5")])


# ---------------------------------------------------------------------------
# Largest-remainder allocation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("total", "parts", "expected"),
    [
        (100, 3, (34, 33, 33)),
        (10, 4, (3, 3, 2, 2)),
        (1, 3, (1, 0, 0)),
        (0, 3, (0, 0, 0)),
        (-10, 4, (-3, -3, -2, -2)),
        (60, 2, (30, 30)),
    ],
)
def test_split_rial_equal_shares_sum_exactly(
    total: int, parts: int, expected: tuple[int, ...]
) -> None:
    allocation = split_rial(total, parts)
    assert allocation.parts_rial == expected
    assert sum(allocation.parts_rial) == total
    assert allocation.residual_rial == 0


@pytest.mark.parametrize(
    ("total", "weights", "expected"),
    [
        (100, [1, 2, 3], (17, 33, 50)),
        (101, ["0.5", "0.5"], (51, 50)),
        (1, ["0.1", "0.2", "0.7"], (0, 0, 1)),
        (3, [1, 0, 1], (2, 0, 1)),
        (100, [1, 1, 1], (34, 33, 33)),
        (-5, [1, 1], (-3, -2)),
        (0, [3, 1], (0, 0)),
        (7, [Decimal("0.25"), Decimal("0.75")], (2, 5)),
    ],
)
def test_allocate_rial_uses_largest_remainders(
    total: int, weights: list[object], expected: tuple[int, ...]
) -> None:
    allocation = allocate_rial(total, weights)
    assert allocation.parts_rial == expected
    assert sum(allocation.parts_rial) == total
    assert allocation.residual_rial == 0


def test_allocate_rial_is_deterministic_and_ties_favour_lowest_index() -> None:
    first = allocate_rial(101, [1, 1])
    second = allocate_rial(101, [1, 1])
    assert first == second
    assert first.parts_rial == (51, 50)


def test_allocate_rial_zero_weight_never_receives_a_rial() -> None:
    allocation = allocate_rial(2, [1, 0, 1])
    assert allocation.parts_rial[1] == 0
    assert sum(allocation.parts_rial) == 2


def test_allocate_rial_large_total_stays_exact() -> None:
    total = 10**15 + 1
    allocation = split_rial(total, 3)
    assert sum(allocation.parts_rial) == total
    assert allocation.parts_rial == (333333333333334, 333333333333334, 333333333333333)


@pytest.mark.parametrize(
    ("total", "weights", "error"),
    [
        ("100.5", [1, 1], MoneyValueError),
        (100.0, [1, 1], MoneyTypeError),
        (100, [], MoneyValueError),
        (100, [1, -1], MoneyValueError),
        (100, [0, 0], MoneyValueError),
        (100, [True, 1], MoneyTypeError),
        (100, [0.5, 0.5], MoneyTypeError),
        (100, [Decimal("NaN")], MoneyValueError),
        (100, [Decimal("1E+34")], MoneyValueError),
        (100, [Decimal("1E-35")], MoneyValueError),
        (100, ["abc"], MoneyValueError),
    ],
)
def test_allocate_rial_rejects_invalid_inputs(
    total: object, weights: list[object], error: type[MoneyError]
) -> None:
    with pytest.raises(error):
        allocate_rial(total, weights)


@pytest.mark.parametrize("parts", [0, -1, 1.5, True])
def test_split_rial_rejects_invalid_part_counts(parts: object) -> None:
    with pytest.raises(MoneyValueError):
        split_rial(10, parts)  # type: ignore[arg-type]


def test_allocation_dataclass_rejects_a_broken_sum() -> None:
    with pytest.raises(MoneyValueError):
        RialAllocation(total_rial=10, parts_rial=(5, 4))


# ---------------------------------------------------------------------------
# Money-safety AST gate (TESTING §3.1) and engine purity
# ---------------------------------------------------------------------------


def _engine_sources() -> list[Path]:
    sources = sorted(ENGINES_ROOT.rglob("*.py"))
    assert sources, "no engine sources found; the AST gate would be vacuous"
    return sources


def test_engine_sources_contain_no_float_literal() -> None:
    violations: list[str] = []
    for path in _engine_sources():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        violations.extend(
            f"{path.name}:{node.lineno}={node.value!r}"
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, float)
        )
    assert not violations, f"float literals in a money path: {violations}"


def test_engine_sources_never_call_builtin_round() -> None:
    violations: list[str] = []
    for path in _engine_sources():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        violations.extend(
            f"{path.name}:{node.lineno}"
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "round"
        )
    assert not violations, f"round() calls in a money path: {violations}"


def test_engine_sources_have_no_clock_random_or_environment_imports() -> None:
    forbidden = {"random", "time", "os", "socket"}
    violations: list[str] = []
    for path in _engine_sources():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                imported = [node.module or ""]
            else:
                continue
            violations.extend(
                f"{path.name}:{name}" for name in imported if name.split(".")[0] in forbidden
            )
    assert not violations, f"impure engine imports: {violations}"


def test_money_module_does_not_import_float_or_round_helpers() -> None:
    source = (ENGINES_ROOT / "money.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }
    assert "round" not in imported
    assert "math" not in imported
    assert "fsum" not in imported
