"""Statistics: real median, real percentiles, IQR and MAD.

Authority: ``docs/adr/ADR-014-market-salary-reference-data-and-estimation.md`` §4
and ``AGENTS.md`` §2 Financial invariant 7 (Decimal only).
"""

from __future__ import annotations

import itertools
from decimal import Decimal

import pytest

from app.domain.salary_estimation.statistics import (
    histogram,
    interquartile_range,
    mean,
    median,
    median_absolute_deviation,
    percentile,
    quartiles,
    robust_z_score,
)


class TestMedian:
    """The median must be the arithmetic median, not the upper middle value."""

    def test_odd_sample_is_the_middle_value(self) -> None:
        assert median([300, 100, 200]) == Decimal(200)

    def test_even_sample_is_the_mean_of_the_two_central_values(self) -> None:
        # The previous engine returned values[len // 2] == 600 here, which biased
        # every even-sized cohort upward.
        assert median([400, 500, 600, 700]) == Decimal(550)

    def test_is_exact_decimal_not_float(self) -> None:
        assert median([1, 2]) == Decimal("1.5")

    def test_empty_sample_is_undefined(self) -> None:
        with pytest.raises(ValueError):
            median([])


class TestPercentile:
    """Percentiles use linear interpolation (R-7) and agree with the median."""

    def test_known_vector(self) -> None:
        values = [400, 500, 600, 700]
        assert percentile(values, 25) == Decimal(475)
        assert percentile(values, 50) == Decimal(550)
        assert percentile(values, 75) == Decimal(625)

    def test_edges_are_the_minimum_and_maximum(self) -> None:
        values = [10, 20, 30]
        assert percentile(values, 0) == Decimal(10)
        assert percentile(values, 100) == Decimal(30)

    def test_single_value(self) -> None:
        assert percentile([42], 90) == Decimal(42)

    def test_rejects_out_of_range(self) -> None:
        with pytest.raises(ValueError):
            percentile([1, 2, 3], 101)

    def test_quartiles_and_median_agree(self) -> None:
        values = [100, 200, 300, 400, 500]
        low, mid, high = quartiles(values)
        assert mid == median(values)
        assert low < mid < high


class TestDispersion:
    """IQR and MAD describe spread without a mean or a standard deviation."""

    def test_interquartile_range(self) -> None:
        assert interquartile_range([400, 500, 600, 700]) == Decimal(150)

    def test_interquartile_range_of_a_constant_sample_is_zero(self) -> None:
        assert interquartile_range([500, 500, 500]) == 0

    def test_median_absolute_deviation(self) -> None:
        # median = 300; deviations = [200, 0, 400] -> median 200
        assert median_absolute_deviation([100, 300, 700]) == Decimal(200)

    def test_robust_z_score_flags_an_extreme_value(self) -> None:
        sample = [100, 102, 104, 106, 108, 110]
        score = robust_z_score(10_000, sample)
        assert score is not None
        assert score > 5

    def test_robust_z_score_is_undefined_for_a_degenerate_sample(self) -> None:
        # Every value identical: a zero MAD would turn any tiny difference into an
        # "outlier", so the score refuses instead.
        assert robust_z_score(500, [500, 500, 500]) is None

    def test_mean_is_exact(self) -> None:
        assert mean([1, 2]) == Decimal("1.5")


class TestHistogram:
    """The distribution shown to the user is derived, never invented."""

    def test_counts_add_up_to_the_sample(self) -> None:
        buckets = histogram([100, 200, 300, 400, 500], buckets=4)
        assert sum(count for _low, _high, count in buckets) == 5

    def test_buckets_are_ordered_and_contiguous(self) -> None:
        buckets = histogram([100, 200, 300, 400], buckets=3)
        for previous, current in itertools.pairwise(buckets):
            assert previous[1] == current[0]

    def test_degenerate_sample_is_one_bucket(self) -> None:
        assert histogram([500, 500, 500]) == ((500, 500, 3),)

    def test_bucket_bounds_are_whole_rial(self) -> None:
        for low, high, _count in histogram([1, 2, 3, 4, 5, 6, 7]):
            assert isinstance(low, int)
            assert isinstance(high, int)
