"""Robust descriptive statistics over whole-Rial market observations.

Authority
---------
``docs/adr/ADR-014-market-salary-reference-data-and-estimation.md`` §4
(statistical method: real median, real percentiles, IQR, MAD);
``AGENTS.md`` §2 Financial invariants 7-8 (Decimal only, ``ROUND_HALF_UP``,
surface the rounding outcome).

Related
-------
``validation.py`` (classifies observations), ``salary_estimator.py`` (publishes
the quantiles), ``app/engines/money.py`` (``to_decimal``, ``round_half_up``).

Scope
-----
Pure functions on sequences of monetary amounts.  Nothing here reads the clock,
the database or the environment.  Interpolation is decimal; rounding happens
only when a caller emits a figure (``salary_estimator``), never inside the
statistics.
"""

from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal

from app.engines.money import to_decimal

__all__ = (
    "histogram",
    "interquartile_range",
    "mean",
    "median",
    "median_absolute_deviation",
    "percentile",
    "quartiles",
    "robust_z_score",
)

#: Consistency constant that makes the MAD comparable to a standard deviation
#: for normally distributed data.  Decimal, never a float literal.
_MAD_SCALE = Decimal("1.4826")

#: Guard so a histogram of a tiny sample still has a readable axis.
_MAX_HISTOGRAM_BUCKETS = 8


def _ordered(values: Sequence[int | Decimal]) -> list[Decimal]:
    """Return the sample in ascending order as exact decimals."""
    if not values:
        raise ValueError("a statistic of an empty sample is undefined")
    return sorted(to_decimal(value) for value in values)


def _interpolate(ordered: list[Decimal], position: Decimal) -> Decimal:
    """Linear interpolation at *position* (0-based, fractional) in *ordered*."""
    lower = int(position)
    fraction = position - Decimal(lower)
    if fraction == 0 or lower + 1 >= len(ordered):
        return ordered[lower]
    return ordered[lower] + (ordered[lower + 1] - ordered[lower]) * fraction


def percentile(values: Sequence[int | Decimal], percent: int | Decimal | str) -> Decimal:
    """Return the *percent*-th percentile using linear interpolation (R-7).

    ``percent`` is 0-100.  The result is exact; the caller rounds once when it
    emits a figure.
    """
    share = to_decimal(percent)
    if share < 0 or share > 100:
        raise ValueError("percentile must be between 0 and 100")
    ordered = _ordered(values)
    position = Decimal(len(ordered) - 1) * share / Decimal(100)
    return _interpolate(ordered, position)


def median(values: Sequence[int | Decimal]) -> Decimal:
    """Return the arithmetic median.

    For an even sample this is the mean of the two central observations — not
    the upper middle value the previous implementation returned, which biased
    every even-sized sample upward.
    """
    return percentile(values, 50)


def quartiles(values: Sequence[int | Decimal]) -> tuple[Decimal, Decimal, Decimal]:
    """Return ``(p25, p50, p75)`` of the sample."""
    ordered = _ordered(values)
    return (
        _interpolate(ordered, Decimal(len(ordered) - 1) * Decimal(25) / Decimal(100)),
        _interpolate(ordered, Decimal(len(ordered) - 1) * Decimal(50) / Decimal(100)),
        _interpolate(ordered, Decimal(len(ordered) - 1) * Decimal(75) / Decimal(100)),
    )


def interquartile_range(values: Sequence[int | Decimal]) -> Decimal:
    """Return ``p75 - p25``; zero when the sample is single-valued."""
    low, _mid, high = quartiles(values)
    return high - low


def median_absolute_deviation(values: Sequence[int | Decimal]) -> Decimal:
    """Return the median of ``|x - median(x)|``."""
    central = median(values)
    deviations = [abs(to_decimal(value) - central) for value in values]
    return median(deviations)


def robust_z_score(value: int | Decimal, values: Sequence[int | Decimal]) -> Decimal | None:
    """Return ``(x - median) / (1.4826 * MAD)``.

    ``None`` when the MAD is zero: a degenerate sample makes the score
    undefined, and returning an arbitrary large number would classify every
    value as an outlier.
    """
    spread = median_absolute_deviation(values) * _MAD_SCALE
    if spread == 0:
        return None
    return (to_decimal(value) - median(values)) / spread


def mean(values: Sequence[int | Decimal]) -> Decimal:
    """Return the arithmetic mean, exactly."""
    ordered = _ordered(values)
    return sum(ordered, Decimal(0)) / Decimal(len(ordered))


def histogram(
    values: Sequence[int | Decimal], buckets: int = 5
) -> tuple[tuple[int, int, int], ...]:
    """Return ``(bucket_min_rial, bucket_max_rial, count)`` tuples.

    Buckets are equal-width and integral.  A degenerate sample (every value
    equal) yields a single bucket rather than a division by zero.
    """
    ordered = _ordered(values)
    count_buckets = max(1, min(buckets, _MAX_HISTOGRAM_BUCKETS, len(ordered)))
    lowest = ordered[0]
    highest = ordered[-1]
    if highest == lowest:
        return ((int(lowest), int(highest), len(ordered)),)

    width = (highest - lowest) / Decimal(count_buckets)
    edges = [lowest + width * Decimal(index) for index in range(count_buckets + 1)]
    counts = [0] * count_buckets
    for value in ordered:
        if value >= highest:
            index = count_buckets - 1
        else:
            index = int((value - lowest) / width)
            index = min(max(index, 0), count_buckets - 1)
        counts[index] += 1

    return tuple(
        (int(edges[index]), int(edges[index + 1]), counts[index])
        for index in range(count_buckets)
    )
