"""Observation validation and robust outlier detection.

Authority
---------
``docs/adr/ADR-014-market-salary-reference-data-and-estimation.md`` §2 (currency,
period and duplicate rules; the three validation outcomes; quarantine instead of
deletion); ``docs/LABOR_MARKET_DATA_SPEC.md`` R-01…R-05; ``AGENTS.md`` §2
Financial invariants 7-8 (Decimal only) and §2 Domain invariant 4 (a forensic
anomaly is not a verdict).

Related
-------
``statistics.py`` (IQR, MAD, percentiles), ``market_data.py`` (records),
``salary_estimator.py`` (uses only the ``VALID`` rows).

Scope
-----
Pure classification.  Nothing is deleted and nothing is silently dropped: every
row leaves with a status (``valid`` / ``suspicious`` / ``rejected``) and the
machine-readable reasons for it, so a quarantined row stays auditable.

Design rules enforced here
--------------------------
1. No global salary floor or ceiling decides *market* plausibility.  The only
   absolute constants are entry-error detectors (a monthly figure below 5,000
   Toman cannot be a salary) and they are named as such.
2. Every other test is **relative to the row's own cohort** — job family, then
   city, then seniority — so a low-paid occupation and a senior engineering role
   are never measured against the same band.
3. A row that merely differs from its peers is *quarantined*, not deleted, and
   never rejected by IQR alone.
4. A row whose licence state or provenance does not permit use is rejected
   regardless of how plausible its number looks.
"""

from __future__ import annotations

import datetime
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal

from app.engines.money import to_decimal

from .market_data import (
    DataQuality,
    MarketObservation,
    ObservationFinding,
    PeerCohort,
    ValidationOutcome,
    monthly_equivalent_rial,
)
from .statistics import interquartile_range, median, median_absolute_deviation, percentile

__all__ = (
    "ValidationPolicy",
    "classify_observations",
    "reason_text",
)

#: Below this monthly figure (5,000 Toman) the value cannot be a salary: it is an
#: entry error (a missing zero, or a raw hourly rate typed into a monthly field).
#: This is an *entry-error detector*, not a market floor for any occupation.
ENTRY_ERROR_FLOOR_RIAL = 50_000

#: Below this monthly figure (100,000 Toman) the value is more likely a unit or
#: period mistake than a salary.  Quarantined for a human, never auto-rejected.
IMPLAUSIBLY_LOW_RIAL = 1_000_000

#: Ratios treated as a Rial/Toman mix-up (x10 or ÷10) around the peer median.
UNIT_MISMATCH_BANDS: tuple[tuple[Decimal, Decimal], ...] = (
    (Decimal("0.08"), Decimal("0.12")),
    (Decimal("8"), Decimal("12")),
)

#: Peer-relative ratio at which a value becomes suspicious / impossible.
RATIO_SUSPICIOUS = Decimal("20")
RATIO_REJECTED = Decimal("1000")

#: Robust z-score above which a value is quarantined (3.5 is the usual robust
#: cut-off for the modified z-score).
MAD_SUSPICIOUS = Decimal("3.5")

#: IQR fence multiplier.  The fence quarantines; it never rejects.
IQR_FENCE = Decimal("3")

#: Percentile test needs a sample large enough for p1/p99 to mean anything.
MIN_SAMPLES_FOR_PERCENTILE_TEST = 20

#: Minimum peers before a robust test is allowed to run at all.
MIN_PEERS_IQR = 8
MIN_PEERS_MAD = 5
MIN_PEERS_RATIO = 3

_REASON_TEXT: Mapping[str, str] = {
    "synthetic_data_not_allowed": "دادهٔ نمونهٔ توسعه در مسیر تخمین واقعی مجاز نیست",
    "source_not_approved": "وضعیت مجوز منبع برای استفاده در تخمین تأیید نشده است",
    "amount_not_positive": "مبلغ گزارش‌شده مثبت نیست",
    "amount_below_entry_floor": "مبلغ کمتر از کف تشخیص خطای ورود اطلاعات است",
    "amount_implausibly_low": "مبلغ برای یک حقوق ماهانه غیرمحتمل پایین است",
    "unit_mismatch_suspected": "احتمال اشتباه واحد ریال/تومان وجود دارد",
    "duplicate_observation": "این رکورد تکراری یک رکورد دیگر همان منبع است",
    "stale_data": "تاریخ داده از حداکثر سن مجاز قدیمی‌تر است",
    "outlier_iqr_extreme": "مقدار خارج از حصار IQR گروه شغلی/شهری است",
    "outlier_mad": "انحراف مقاوم (MAD) از میانهٔ گروه بیش از حد مجاز است",
    "outside_p1_p99": "مقدار خارج از بازهٔ صدک ۱ تا ۹۹ گروه است",
    "ratio_implausible_high": "مقدار چند برابر میانهٔ گروه است و نیازمند بررسی است",
    "period_converted": "مبلغ ساعتی/روزانه به معادل ماهانه تبدیل شده است",
    "insufficient_peer_group": "حجم گروه همتا برای آزمون آماری کافی نیست",
}

_REJECTING_REASONS = frozenset(
    {
        "synthetic_data_not_allowed",
        "source_not_approved",
        "amount_not_positive",
        "amount_below_entry_floor",
        "duplicate_observation",
    }
)


def reason_text(reason: str) -> str:
    """Return the Persian explanation of a machine-readable reason code."""
    return _REASON_TEXT.get(reason, reason)


@dataclass(frozen=True)
class ValidationPolicy:
    """Thresholds of the validation pass.

    Every field is configurable so the owner can retune the policy without a
    code change; the defaults are the ones documented in ADR-014 §2.3.
    """

    max_age_days: int = 730
    allow_synthetic: bool = False
    min_peers_iqr: int = MIN_PEERS_IQR
    min_peers_mad: int = MIN_PEERS_MAD
    min_peers_ratio: int = MIN_PEERS_RATIO


def _cohorts(
    observations: Sequence[MarketObservation],
) -> dict[str, tuple[str, tuple[str, ...]]]:
    """Return the peer values of the widest usable cohort for each observation.

    The fallback order is city+seniority → city → national.  The scope that was
    actually used is reported on the finding, because a national fallback is a
    weaker comparison and must be visible in the output.
    """
    by_city_seniority: dict[tuple[str, str, str], list[str]] = {}
    by_city: dict[tuple[str, str], list[str]] = {}
    by_family: dict[str, list[str]] = {}
    for row in observations:
        seniority = row.seniority_level or ""
        by_city_seniority.setdefault((row.family_key, row.city, seniority), []).append(row.id)
        by_city.setdefault((row.family_key, row.city), []).append(row.id)
        by_family.setdefault(row.family_key, []).append(row.id)

    result: dict[str, tuple[str, tuple[str, ...]]] = {}
    for row in observations:
        seniority = row.seniority_level or ""
        scopes = (
            ("city_seniority", by_city_seniority[(row.family_key, row.city, seniority)]),
            ("city", by_city[(row.family_key, row.city)]),
            ("national", by_family[row.family_key]),
        )
        chosen_scope, ids = scopes[-1]
        for scope, candidate_ids in scopes:
            if len([other for other in candidate_ids if other != row.id]) >= MIN_PEERS_RATIO:
                chosen_scope, ids = scope, candidate_ids
                break
        result[row.id] = (chosen_scope, tuple(id_ for id_ in ids if id_ != row.id))
    return result


def _duplicate_ids(observations: Sequence[MarketObservation]) -> set[str]:
    """Return the ids of rows that repeat an earlier row of the same source.

    A repeat means: same source, same family, same city, same seniority and the
    same reported amount *and period*.  The first row in ``(collected_at, id)``
    order is kept so the verdict does not depend on input order.
    """
    seen: set[tuple[str, str, str, str, int, str]] = set()
    duplicates: set[str] = set()
    for row in sorted(observations, key=lambda item: (item.collected_at, item.id)):
        key = (
            row.source_id,
            row.family_key,
            row.city,
            row.seniority_level or "",
            row.amount_rial,
            row.period,
        )
        if key in seen:
            duplicates.add(row.id)
        else:
            seen.add(key)
    return duplicates


def _classify_one(  # noqa: PLR0912, PLR0915 - one documented check per branch
    row: Mapping[str, object],
    *,
    monthly: Decimal,
    peers: PeerCohort,
    duplicates: set[str],
    policy: ValidationPolicy,
    as_of: datetime.datetime,
) -> tuple[str, tuple[str, ...]]:
    """Return the status and the reasons for a single observation."""
    observation = row["observation"]
    assert isinstance(observation, MarketObservation)

    hard: list[str] = []
    soft: list[str] = []
    notes: list[str] = []

    if observation.is_synthetic:
        # A sample row is evidence of nothing.  It may be served only when the
        # deployment explicitly allows sample data, which production refuses.
        if not policy.allow_synthetic:
            hard.append("synthetic_data_not_allowed")
    elif not observation.is_approved_source:
        hard.append("source_not_approved")
    if observation.amount_rial <= 0:
        hard.append("amount_not_positive")
    elif monthly < ENTRY_ERROR_FLOOR_RIAL:
        hard.append("amount_below_entry_floor")
    elif monthly < IMPLAUSIBLY_LOW_RIAL:
        soft.append("amount_implausibly_low")
    if observation.id in duplicates:
        hard.append("duplicate_observation")

    collected = observation.collected_at
    if collected.tzinfo is None:
        collected = collected.replace(tzinfo=datetime.UTC)
    age_days = (as_of - collected).days
    if age_days > policy.max_age_days:
        soft.append("stale_data")

    converted = bool(row["converted"])
    if converted:
        notes.append("period_converted")

    if peers.size >= policy.min_peers_ratio and monthly > 0:
        peer_median = median(peers.values_rial)
        if peer_median > 0:
            ratio = monthly / peer_median
            for band_low, band_high in UNIT_MISMATCH_BANDS:
                if band_low <= ratio <= band_high:
                    soft.append("unit_mismatch_suspected")
                    break
            if ratio > RATIO_REJECTED:
                # Three orders of magnitude away from its own cohort: extra
                # zeros, not a negotiation.  Rejected but still recorded.
                hard.append("ratio_implausible_high")
            elif ratio > RATIO_SUSPICIOUS:
                soft.append("ratio_implausible_high")
            if Decimal(1) / ratio > RATIO_REJECTED or Decimal(1) / ratio > RATIO_SUSPICIOUS:
                soft.append("amount_implausibly_low")

    if peers.size >= policy.min_peers_iqr:
        spread = interquartile_range(peers.values_rial)
        if spread > 0:
            low_fence = percentile(peers.values_rial, 25) - IQR_FENCE * spread
            high_fence = percentile(peers.values_rial, 75) + IQR_FENCE * spread
            if monthly < low_fence or monthly > high_fence:
                soft.append("outlier_iqr_extreme")

    if peers.size >= policy.min_peers_mad:
        spread = median_absolute_deviation(peers.values_rial)
        if spread > 0:
            robust = (monthly - median(peers.values_rial)) / (spread * Decimal("1.4826"))
            if abs(robust) > MAD_SUSPICIOUS:
                soft.append("outlier_mad")

    if peers.size >= MIN_SAMPLES_FOR_PERCENTILE_TEST and (
        monthly < percentile(peers.values_rial, 1)
        or monthly > percentile(peers.values_rial, 99)
    ):
        soft.append("outside_p1_p99")

    if len(peers.values_rial) < MIN_PEERS_MAD:
        notes.append("insufficient_peer_group")

    reasons = tuple(dict.fromkeys([*hard, *soft, *notes]))
    if hard:
        return DataQuality.REJECTED, reasons
    if soft:
        return DataQuality.SUSPICIOUS, reasons
    return DataQuality.VALID, reasons


def classify_observations(
    observations: Sequence[MarketObservation],
    *,
    as_of: datetime.datetime,
    policy: ValidationPolicy | None = None,
) -> ValidationOutcome:
    """Classify *observations* against their own cohorts.

    ``as_of`` is supplied by the caller (the API boundary) so this function stays
    a pure function of its arguments.
    """
    resolved = policy or ValidationPolicy()
    if not observations:
        return ValidationOutcome()

    monthly_by_id: dict[str, int] = {}
    converted_by_id: dict[str, bool] = {}
    for row in observations:
        exact, converted = monthly_equivalent_rial(row)
        monthly_by_id[row.id] = int(exact)
        converted_by_id[row.id] = converted

    cohorts = _cohorts(observations)
    duplicates = _duplicate_ids(observations)

    valid: list[MarketObservation] = []
    suspicious: list[ObservationFinding] = []
    rejected: list[ObservationFinding] = []
    findings: list[ObservationFinding] = []

    for row in observations:
        scope, peer_ids = cohorts[row.id]
        peer_values = tuple(to_decimal(monthly_by_id[peer_id]) for peer_id in peer_ids)
        monthly = to_decimal(monthly_by_id[row.id])
        status, reasons = _classify_one(
            {"observation": row, "converted": converted_by_id[row.id]},
            monthly=monthly,
            peers=PeerCohort(scope=scope, values_rial=peer_values),
            duplicates=duplicates,
            policy=resolved,
            as_of=as_of,
        )
        finding = ObservationFinding(
            observation_id=row.id,
            status=status,
            reasons=reasons,
            monthly_rial=monthly_by_id[row.id],
            peer_scope=scope,
            conversion_applied=converted_by_id[row.id],
        )
        findings.append(finding)
        if status == DataQuality.VALID:
            valid.append(row)
        elif status == DataQuality.SUSPICIOUS:
            suspicious.append(finding)
        else:
            rejected.append(finding)

    return ValidationOutcome(
        valid=tuple(valid),
        suspicious=tuple(suspicious),
        rejected=tuple(rejected),
        findings=tuple(findings),
        monthly_by_id=monthly_by_id,
    )


def iter_reasons(findings: Iterable[ObservationFinding]) -> dict[str, int]:
    """Return a reason → count map for a sequence of findings."""
    counts: dict[str, int] = {}
    for finding in findings:
        for reason in finding.reasons:
            counts[reason] = counts.get(reason, 0) + 1
    return counts
