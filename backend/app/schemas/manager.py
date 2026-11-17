"""Pydantic contracts for the manager workspace API.

Authority
---------
``AGENTS.md`` §2 Financial invariants (integer Rial in JSON, never a float);
``docs/adr/ADR-009`` (``advisory: true`` on every response);
``frontend/src/prototype/types.ts`` (the client contract mirrored here,
camelCase keys and digit-string money).

Contract notes
--------------
* Every monetary field is a JSON integer in Rial.
* ``advisory`` is always ``true`` and the statutory costing carries the
  engine's review status verbatim: an unreviewed engine is never presented
  as an approved authority.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class EmployeeCreateRequest(BaseModel):
    """Create one employee.  No national ID, mobile or bank field exists."""

    model_config = ConfigDict(extra="forbid")

    name: str
    role: str
    startDate: str


class EmployeePatchRequest(BaseModel):
    """Edit any subset of the editable profile fields."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    role: str | None = None
    startDate: str | None = None


class EmployeeResponse(BaseModel):
    """One employee as the client stores it."""

    id: str
    name: str
    role: str
    startDate: str
    createdAt: str


class ObservationCreateRequest(BaseModel):
    """One observation draft."""

    model_config = ConfigDict(extra="forbid")

    code: str
    period: str
    raw: str


class ObservationPatchRequest(BaseModel):
    """One correction."""

    model_config = ConfigDict(extra="forbid")

    raw: str


class ObservationResponse(BaseModel):
    """One observation as the client stores it."""

    id: str
    personId: str
    code: str
    period: str
    raw: str
    state: str
    source: str
    createdAt: str


class EvidenceResponse(BaseModel):
    """Evidence metadata (the bytes are never echoed)."""

    id: str
    employeeId: str
    fileName: str
    contentType: str
    byteSize: int
    sha256: str
    note: str | None
    createdAt: str


class CriterionScoreResponse(BaseModel):
    """One criterion contribution (AC-07)."""

    code: str
    labelFa: str
    weightBp: int
    missing: bool
    raw: str | None
    normalisedBp: int
    contributionBp: int


class ObservationUsedResponse(BaseModel):
    """One observation as it entered the score (AC-04 traceability)."""

    id: str
    code: str
    period: str
    raw: str


class BandResponse(BaseModel):
    """The manager-supplied envelope and the score position inside it."""

    minRial: int
    maxRial: int
    currentRial: int | None
    positionBp: int


class StatutoryCostResponse(BaseModel):
    """The statutory costing block produced by the existing engine."""

    request: dict[str, Any]
    calculation_hash: str
    statutory_version: str
    rule_set_fingerprint: str
    rule_set_status: str
    is_verified: bool
    engine_version: str
    gross_monthly_rial: int
    employee_sso_7pct_rial: int
    sso_insurable_ceiling_applied: bool
    income_tax_rial: int
    net_rial: int
    monthly_sanavat_accrual_rial: int
    monthly_eydi_accrual_rial: int
    total_monthly_employer_cost_rial: int
    annual_ctc_12month_rial: int
    rounding_residual_rial: int


class ExplanationResponse(BaseModel):
    """Reasons, warnings and data-quality limitations (AC-09)."""

    reasons: list[str]
    warnings: list[str]
    dataQuality: list[str]
    advisory: bool
    statutoryStatus: str


class DecisionResponse(BaseModel):
    """One decision as the client stores it."""

    id: str
    recommendationId: str
    action: str
    editedGrossRial: int | None
    comment: str
    decidedAt: str


class RecommendationResponse(BaseModel):
    """The complete explainable recommendation."""

    id: str
    personId: str
    personName: str
    period: str
    ruleSetVersion: str
    ruleSetStatus: str
    score100: int
    totalBp: int
    contributions: list[CriterionScoreResponse]
    missingCriteria: list[str]
    observationsUsed: list[ObservationUsedResponse]
    band: BandResponse
    suggestedGrossRial: int
    deltaRial: int | None
    statutory: StatutoryCostResponse
    currentStatutory: StatutoryCostResponse | None
    explanation: ExplanationResponse
    engineVersion: str
    calculationHash: str
    advisory: Literal[True]
    status: str
    decision: DecisionResponse | None = None
    createdAt: str


class RecommendationSummaryResponse(BaseModel):
    """A recommendation in a list: counters, the amount and the outcome."""

    id: str
    personId: str
    personName: str
    period: str
    score100: int
    suggestedGrossRial: int
    deltaRial: int | None
    status: str
    decisionAction: str | None
    createdAt: str


class EvaluationCriterionResponse(BaseModel):
    """One published criterion of the evaluation rule set."""

    code: str
    labelFa: str
    unitFa: str
    weightBp: int
    minRaw: str
    maxRaw: str
    guidanceFa: str


class EvaluationRulesResponse(BaseModel):
    """The published evaluation rule set the client renders its form from."""

    ruleSetVersion: str
    ruleSetStatus: str
    statusLabelFa: str
    weightsSumBp: int
    missingPolicyFa: str
    criteria: list[EvaluationCriterionResponse]
    advisory: Literal[True] = True


class EvaluationRequest(BaseModel):
    """Evaluate and produce the recommendation in one call.

    The band is the only money source and is never guessed; the current pay is
    optional and its absence is reported in the data-quality block.
    """

    model_config = ConfigDict(extra="forbid")

    bandMinRial: int
    bandMaxRial: int
    currentRial: int | None = None


class DecisionRequest(BaseModel):
    """One manager decision on a pending recommendation."""

    model_config = ConfigDict(extra="forbid")

    action: str
    comment: str = ""
    editedGrossRial: int | None = None


class RecentDecisionResponse(BaseModel):
    """One history entry for the dashboard."""

    id: str
    recommendationId: str
    action: str
    editedGrossRial: int | None
    comment: str
    decidedAt: str
    personName: str
    score100: int


class DashboardResponse(BaseModel):
    """The dashboard counters (AC-01/AC-10)."""

    peopleCount: int
    validObservationCount: int
    pendingCount: int
    decidedCount: int
    recentDecisions: list[RecentDecisionResponse]


class ImportRowError(BaseModel):
    """One rejected import row and its reason."""

    row: int
    reason: str


class ImportSummaryResponse(BaseModel):
    """The result of one CSV observation import."""

    imported: int
    rejected: list[ImportRowError]


__all__ = [name for name in dir() if name.endswith(("Request", "Response"))]
