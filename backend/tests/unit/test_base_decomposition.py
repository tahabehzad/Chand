"""Unit tests for the base decomposition engine (P1-T07).

Authority:
    ``docs/PISH_HESABDARI_HOLY_BIBLE.md`` §2.3 D (the base definition that is
    most often got wrong) and §2.5; Labour Law Art. 36 Note 3; Diwan-e Edalat
    Judgment 3328 (``FIND-LEG-05``).
Related:
    WBS P1-T07 - Mozd-e Saabet / Mozd-e Mabna decomposition.
"""

from __future__ import annotations

import pytest

from app.engines.bases import Allowances, decompose_bases
from app.engines.errors import PayrollInputError

# The Appendix A worked package (Holy Bible §A.1).
APPENDIX_A_GROSS = 341_850_120
APPENDIX_A_ALLOWANCES = Allowances(
    housing_rial=9_000_000,
    grocery_rial=22_000_000,
    marriage_rial=5_000_000,
    child_rial=10_390_968,
    continuous_attraction_rial=40_000_000,
)
APPENDIX_A_WELFARE_TOTAL = 46_390_968
APPENDIX_A_SAABET = 295_459_152


def test_the_welfare_allowances_are_excluded_from_the_base() -> None:
    """Art. 36 Note 3: housing, grocery, marriage and child are excluded."""
    result = decompose_bases(APPENDIX_A_GROSS, APPENDIX_A_ALLOWANCES)
    assert result.welfare_total_rial == APPENDIX_A_WELFARE_TOTAL
    assert result.mozd_e_saabet_rial == APPENDIX_A_SAABET
    assert result.gross_monthly_rial == APPENDIX_A_GROSS


def test_the_continuous_attraction_stays_inside_the_base() -> None:
    """FIND-LEG-05 / Judgment 3328: the attraction is *not* a welfare item."""
    allowances = Allowances(continuous_attraction_rial=20_000_000)
    result = decompose_bases(100_000_000, allowances)
    assert result.welfare_total_rial == 0
    assert result.mozd_e_saabet_rial == 100_000_000


def test_the_attraction_is_never_counted_twice() -> None:
    allowances = Allowances(
        housing_rial=9_000_000,
        continuous_attraction_rial=20_000_000,
    )
    result = decompose_bases(100_000_000, allowances)
    assert result.welfare_total_rial == 9_000_000
    assert result.mozd_e_saabet_rial == 91_000_000


def test_a_gross_that_does_not_cover_the_allowances_fails_closed() -> None:
    allowances = Allowances(housing_rial=9_000_000, grocery_rial=22_000_000)
    with pytest.raises(PayrollInputError) as caught:
        decompose_bases(10_000_000, allowances)
    assert "BASE_DECOMPOSITION_NEGATIVE" in str(caught.value)


def test_a_gross_that_exactly_covers_the_allowances_is_accepted() -> None:
    allowances = Allowances(housing_rial=9_000_000, grocery_rial=1_000_000)
    result = decompose_bases(10_000_000, allowances)
    assert result.mozd_e_saabet_rial == 0
    assert result.welfare_total_rial == 10_000_000


@pytest.mark.parametrize(
    "gross",
    [-1, -100_000, True, False, 1.5, "1000", None],
)
def test_a_non_whole_rial_gross_is_refused(gross: object) -> None:
    with pytest.raises(PayrollInputError) as caught:
        decompose_bases(gross, Allowances())  # type: ignore[arg-type]
    assert "PAYROLL_INPUT_INVALID" in str(caught.value)


@pytest.mark.parametrize(
    "allowances",
    [
        Allowances(housing_rial=-1),
        Allowances(grocery_rial=-5),
        Allowances(marriage_rial=True),
        Allowances(child_rial=-2),
        Allowances(continuous_attraction_rial=-3),
    ],
)
def test_a_negative_allowance_is_refused(allowances: Allowances) -> None:
    with pytest.raises(PayrollInputError):
        decompose_bases(100_000_000, allowances)


def test_the_welfare_total_property_is_the_sum_of_the_four_items() -> None:
    allowances = Allowances(
        housing_rial=1,
        grocery_rial=2,
        marriage_rial=3,
        child_rial=4,
        continuous_attraction_rial=100,
    )
    assert allowances.welfare_total_rial == 10


def test_the_decomposition_is_deterministic() -> None:
    first = decompose_bases(APPENDIX_A_GROSS, APPENDIX_A_ALLOWANCES)
    second = decompose_bases(APPENDIX_A_GROSS, APPENDIX_A_ALLOWANCES)
    assert first == second
