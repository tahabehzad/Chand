"""The provisional evaluation rule set ``perf-v1`` and its scoring engine.

Authority
---------
``docs/MVP_SCOPE.md`` §3 and AC-05…AC-08; ``docs/MVP_WBS.md`` MVP-09/MVP-10;
``docs/DECISIONS.md`` PB-D03; ``frontend/src/prototype/rules.ts`` and
``scoring.ts`` (the semantics this module mirrors exactly, so the backend and
the historical prototype agree to the Rial).

Status
------
**The criteria and weights below are the owner brief's illustrative example
(40/30/20/10).  They are NOT approved business rules.**  The rule set is
published under the version string ``perf-v1`` so a later confirmed model
arrives as ``perf-v2`` and never rewrites a historical evaluation.

Arithmetic
----------
Weights are integer basis points of one (sum exactly 10 000).  Only
``Decimal``/integer arithmetic is used — no float literal, no ``round()``.
Everything is a pure function of the inputs: no clock, no randomness, no
network, no environment read (invariant 11).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal
from typing import Final, Literal

from app.engines.errors import CodedDomainError

RULE_SET_VERSION: Final[str] = "perf-v1"
#: The rule set is a provisional draft, never an approved rule.
RULE_SET_STATUS: Final[str] = "PROVISIONAL_DRAFT"

WEIGHTS_SUM_BP: Final[int] = 10_000

MetricCode = Literal["sales", "quality", "attendance", "responsibility"]

METRIC_CODES: Final[tuple[str, ...]] = ("sales", "quality", "attendance", "responsibility")


@dataclass(frozen=True)
class CriterionDef:
    """One published criterion: weight and normalisation bounds."""

    code: str
    label_fa: str
    unit_fa: str
    #: Integer basis points of one: 4 000 = 40 %.
    weight_bp: int
    #: Inclusive normalisation bounds as integer digit strings.
    min_raw: str
    max_raw: str
    guidance_fa: str


CRITERIA: Final[tuple[CriterionDef, ...]] = (
    CriterionDef(
        code="sales",
        label_fa="فروش / خروجی قابل اندازه‌گیری",
        unit_fa="ریال فروش در دوره",
        weight_bp=4_000,
        min_raw="0",
        max_raw="1000000000",
        guidance_fa="سقف امتیاز کامل: ۱٬۰۰۰٬۰۰۰٬۰۰۰ ریال فروش در دوره",
    ),
    CriterionDef(
        code="quality",
        label_fa="کیفیت کار",
        unit_fa="امتیاز ۰ تا ۱۰۰",
        weight_bp=3_000,
        min_raw="0",
        max_raw="100",
        guidance_fa="ارزیابی کیفیت توسط مدیر در همان دوره",
    ),
    CriterionDef(
        code="attendance",
        label_fa="حضور و نظم",
        unit_fa="روز حضور مؤثر (۰ تا ۳۰)",
        weight_bp=2_000,
        min_raw="0",
        max_raw="30",
        guidance_fa="۳۰ روز حضور در دوره = امتیاز کامل",
    ),
    CriterionDef(
        code="responsibility",
        label_fa="مسئولیت‌پذیری و اتکاپذیری",
        unit_fa="امتیاز ۱ تا ۵",
        weight_bp=1_000,
        min_raw="1",
        max_raw="5",
        guidance_fa="۱ = ضعیف، ۳ = مطابق انتظار، ۵ = نمونه",
    ),
)

#: The published missing-data policy: an absent criterion scores zero and is
#: named in the response; weights are never renormalised, so two people are
#: always compared on the same weighting.
MISSING_POLICY_FA: Final[str] = (
    "معیار ثبت‌نشده صفر امتیاز می‌گیرد و در خروجی نام برده می‌شود؛ وزن‌ها برای "
    "جبران دادهٔ غایب بازمحاسبه نمی‌شوند تا مقایسهٔ افراد بر یک مبنا بماند."
)

_BP_SCALE: Final[Decimal] = Decimal(10_000)
_HALF_OF_SCORE_STEP: Final[Decimal] = Decimal(50)


def criterion_by_code(code: str) -> CriterionDef | None:
    """Return the published definition for a metric code."""
    for definition in CRITERIA:
        if definition.code == code:
            return definition
    return None


def _assert_rule_set_integrity() -> None:
    """Refuse to load with a rule set whose weights do not sum to one."""
    total = sum(definition.weight_bp for definition in CRITERIA)
    if total != WEIGHTS_SUM_BP:
        raise RuntimeError(
            f"RULE_SET_INVALID: {RULE_SET_VERSION} weights sum to {total} basis points,"
            f" expected {WEIGHTS_SUM_BP}"
        )
    if not CRITERIA:
        raise RuntimeError("RULE_SET_INVALID: the rule set has no criteria")
    for definition in CRITERIA:
        if definition.weight_bp <= 0:
            raise RuntimeError(f"RULE_SET_INVALID: {definition.code} has a non-positive weight")


_assert_rule_set_integrity()


def normalise_to_bp(definition: CriterionDef, raw: str) -> int:
    """Normalise one raw value into basis points of its criterion range.

    Out-of-range values are clamped; the entry layer rejects most of them,
    but the scorer must stay total so a stored value can never crash a read.
    """
    value = Decimal(raw)
    minimum = Decimal(definition.min_raw)
    maximum = Decimal(definition.max_raw)
    if maximum <= minimum:
        raise RuntimeError(f"RULE_SET_INVALID: {definition.code} has an empty range")
    if value <= minimum:
        return 0
    if value >= maximum:
        return WEIGHTS_SUM_BP
    return int(((value - minimum) * _BP_SCALE) / (maximum - minimum))


@dataclass(frozen=True)
class ScoreInput:
    """One observation value entering the score."""

    code: str
    raw: str
    #: Traceability of the observation row that supplied the value.
    observation_id: str
    period: str


@dataclass(frozen=True)
class CriterionScore:
    """One criterion as it contributed to the score."""

    code: str
    label_fa: str
    weight_bp: int
    missing: bool
    raw: str | None
    normalised_bp: int
    contribution_bp: int

    def as_payload(self) -> dict[str, object]:
        """The JSON view of this contribution."""
        return {
            "code": self.code,
            "labelFa": self.label_fa,
            "weightBp": self.weight_bp,
            "missing": self.missing,
            "raw": self.raw,
            "normalisedBp": self.normalised_bp,
            "contributionBp": self.contribution_bp,
        }


@dataclass(frozen=True)
class ScoreResult:
    """The complete, explainable score."""

    rule_set_version: str
    rule_set_status: str
    score_100: int
    total_bp: int
    contributions: tuple[CriterionScore, ...]
    missing_criteria: tuple[str, ...]
    observations_used: tuple[dict[str, str], ...]
    missing_policy_fa: str
    calculation_hash: str


def score_observations(inputs: list[ScoreInput]) -> ScoreResult:
    """Score a set of observations deterministically.

    One value per criterion is expected (the caller passes the latest
    non-rejected value per code); a duplicate code is overwritten by the later
    entry so the function is total rather than ambiguous.
    """
    latest: dict[str, ScoreInput] = {}
    for entry in inputs:
        latest[entry.code] = entry

    contributions: list[CriterionScore] = []
    missing: list[str] = []
    observations_used: list[dict[str, str]] = []
    total_bp = 0

    for definition in CRITERIA:
        item = latest.get(definition.code)
        if item is None:
            missing.append(definition.code)
            contributions.append(
                CriterionScore(
                    code=definition.code,
                    label_fa=definition.label_fa,
                    weight_bp=definition.weight_bp,
                    missing=True,
                    raw=None,
                    normalised_bp=0,
                    contribution_bp=0,
                )
            )
            continue

        normalised_bp = normalise_to_bp(definition, item.raw)
        contribution_bp = int((Decimal(normalised_bp) * Decimal(definition.weight_bp)) / _BP_SCALE)
        total_bp += contribution_bp
        observations_used.append(
            {
                "id": item.observation_id,
                "code": item.code,
                "period": item.period,
                "raw": item.raw,
            }
        )
        contributions.append(
            CriterionScore(
                code=definition.code,
                label_fa=definition.label_fa,
                weight_bp=definition.weight_bp,
                missing=False,
                raw=item.raw,
                normalised_bp=normalised_bp,
                contribution_bp=contribution_bp,
            )
        )

    score_100 = int((Decimal(total_bp) + _HALF_OF_SCORE_STEP) / Decimal(100))

    canonical = json.dumps(
        {
            "rule_set_version": RULE_SET_VERSION,
            "values": [[c.code, c.raw] for c in contributions],
            "total_bp": total_bp,
            "score_100": score_100,
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    calculation_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    return ScoreResult(
        rule_set_version=RULE_SET_VERSION,
        rule_set_status=RULE_SET_STATUS,
        score_100=score_100,
        total_bp=total_bp,
        contributions=tuple(contributions),
        missing_criteria=tuple(missing),
        observations_used=tuple(observations_used),
        missing_policy_fa=MISSING_POLICY_FA,
        calculation_hash=calculation_hash,
    )


def validate_observation_value(code: str, raw: str) -> str:
    """Validate one raw value against its published bounds.

    Returns the canonical digit string, or raises ``PayrollInputError`` with a
    stable code that carries no amount.
    """
    definition = criterion_by_code(code)
    if definition is None:
        raise CodedDomainError(
            "OBSERVATION_METRIC_INVALID",
            "این معیار در مدل ارزیابی وجود ندارد.",
        )
    folded = raw.strip()
    if not folded.isdigit():
        raise CodedDomainError(
            "OBSERVATION_VALUE_INVALID",
            "مقدار مشاهده باید یک عدد صحیح غیرمنفی باشد.",
        )
    value = Decimal(folded)
    if value < Decimal(definition.min_raw) or value > Decimal(definition.max_raw):
        raise CodedDomainError(
            "OBSERVATION_VALUE_INVALID",
            f"مقدار مشاهده خارج از بازهٔ معیار {definition.code} است.",
        )
    return folded


__all__ = [
    "CRITERIA",
    "METRIC_CODES",
    "MISSING_POLICY_FA",
    "RULE_SET_STATUS",
    "RULE_SET_VERSION",
    "WEIGHTS_SUM_BP",
    "CriterionDef",
    "CriterionScore",
    "ScoreInput",
    "ScoreResult",
    "criterion_by_code",
    "normalise_to_bp",
    "score_observations",
    "validate_observation_value",
]
