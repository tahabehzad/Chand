"""Unit tests for the severance (Sanavat) engine (P1-T08).

Authority:
    ``docs/PISH_HESABDARI_HOLY_BIBLE.md`` آ§2.3 E; Labour Law Art. 24;
    ``FIND-LEG-05`` (the base includes the continuous fixed attraction
    allowance, Diwan Precedent 3328).
Spec:
    ``docs/specs/TESTING.md`` property P-05.
Related:
    WBS P1-T08 - Sanavat engine.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

import pytest

from app.engines.severance import compute_monthly_severance_accrual


def _rial(value: Decimal) -> int:
    """Round a Decimal to whole Rial, half up."""
    return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def test_the_accrual_is_one_twelfth_of_the_base() -> None:
    result = compute_monthly_severance_accrual(295_459_152)
    assert result.monthly_accrual_rial == 24_621_596
    assert result.monthly_accrual_exact == Decimal(295_459_152) / Decimal(12)


def test_the_appendix_a5_vector_is_reproduced() -> None:
    """A.5: Mozd-e Saabet 402,691,891 -> monthly accrual 33,557,658."""
    result = compute_monthly_severance_accrual(402_691_891)
    assert result.monthly_accrual_rial == 33_557_658


def test_the_accrual_is_rounded_once_at_the_line_boundary() -> None:
    """A base that does not divide evenly rounds half up, exactly once."""
    result = compute_monthly_severance_accrual(100_000_001)
    assert result.monthly_accrual_exact == Decimal(100_000_001) / Decimal(12)
    assert result.monthly_accrual_rial == _rial(result.monthly_accrual_exact)
    assert result.monthly_accrual_rial == 8_333_333


def test_a_half_rial_is_rounded_up_not_to_even() -> None:
    """12 * x + 0.5 must round up; Python's round() would round to even."""
    result = compute_monthly_severance_accrual(6)
    assert result.monthly_accrual_exact == Decimal("0.5")
    assert result.monthly_accrual_rial == 1


def test_a_zero_base_yields_a_zero_accrual() -> None:
    result = compute_monthly_severance_accrual(0)
    assert result.monthly_accrual_rial == 0
    assert result.monthly_accrual_exact == Decimal(0)


def test_the_seed_literal_is_never_used() -> None:
    """HB-GAP-017: 0.0833333333 is not the monthly accrual rate."""
    result = compute_monthly_severance_accrual(12_000_000)
    assert result.monthly_accrual_rial == 1_000_000
    assert result.monthly_accrual_rial != int(12_000_000 * 0.0833333333)


def test_a_non_integer_base_is_refused() -> None:
    with pytest.raises(TypeError):
        compute_monthly_severance_accrual(1.5)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        compute_monthly_severance_accrual(True)


def test_a_negative_base_is_refused() -> None:
    with pytest.raises(ValueError, match="PAYROLL_INPUT_INVALID"):
        compute_monthly_severance_accrual(-1)
