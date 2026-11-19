/**
 * Prototype domain types — the manager evaluation flow.
 *
 * Authority
 * ---------
 * `docs/PROJECT_BIBLE.md` §9–§12, `docs/ARCHITECTURE.md` §6–§9,
 * `docs/MVP_SCOPE.md`, and the server contracts in
 * `backend/app/schemas/manager.py` (camelCase keys, integer Rial). The API
 * adapter (`./api.ts`) converts every server integer Rial into a digit string
 * at the boundary, so a monetary amount is never handled as a JavaScript
 * number in a component.
 *
 * Scope
 * -----
 * No national ID, mobile, Sheba or bank data. Every figure here is the
 * server's; the browser performs no scoring and no statutory calculation.
 */

export type MetricCode = 'sales' | 'quality' | 'attendance' | 'responsibility';

export type ObservationState = 'valid' | 'corrected' | 'rejected';

export type ObservationSource = 'manual' | 'import';

export type Person = {
  id: string;
  name: string;
  role: string;
  /** Gregorian ISO date; Jalali conversion waits on DEC-006. */
  startDate: string;
  createdAt: string;
};

export type Observation = {
  id: string;
  personId: string;
  code: MetricCode;
  /** Free-form evaluation period label, e.g. `1404-Q2`. */
  period: string;
  /** Integer digit string in the criterion's own unit. */
  raw: string;
  state: ObservationState;
  source: ObservationSource;
  createdAt: string;
};

export type Evidence = {
  id: string;
  employeeId: string;
  fileName: string;
  contentType: string;
  byteSize: number;
  sha256: string;
  note: string | null;
  createdAt: string;
};

export type CriterionScore = {
  code: MetricCode;
  labelFa: string;
  weightBp: number;
  missing: boolean;
  /** The raw value actually used, or null when the criterion is missing. */
  raw: string | null;
  /** Normalised to 0…10000 basis points of the criterion range. */
  normalisedBp: number;
  /** weightBp × normalisedBp ÷ 10000, in basis points of the whole score. */
  contributionBp: number;
};

export type ForecastBand = {
  minRial: string;
  maxRial: string;
  currentRial: string | null;
  /** Score position inside the band, 0…10000 basis points. */
  positionBp: number;
};

/** One criterion as it entered the score, with its period for traceability. */
export type ObservationUsed = {
  id: string;
  code: MetricCode;
  period: string;
  raw: string;
};

/**
 * The statutory costing block computed by the backend payroll engine.
 * Field names are the engine's own snake_case payload; the UI renders them
 * verbatim so a value can always be traced to its rule set and hash.
 */
export type StatutoryCost = {
  request: Record<string, unknown>;
  calculation_hash: string;
  statutory_version: string;
  rule_set_fingerprint: string;
  rule_set_status: string;
  is_verified: boolean;
  engine_version: string;
  gross_monthly_rial: number;
  employee_sso_7pct_rial: number;
  sso_insurable_ceiling_applied: boolean;
  income_tax_rial: number;
  net_rial: number;
  monthly_sanavat_accrual_rial: number;
  monthly_eydi_accrual_rial: number;
  total_monthly_employer_cost_rial: number;
  annual_ctc_12month_rial: number;
  rounding_residual_rial: number;
};

export type Explanation = {
  reasons: string[];
  warnings: string[];
  dataQuality: string[];
  advisory: boolean;
  statutoryStatus: string;
};

export type DecisionAction = 'approve' | 'edit' | 'reject';

export type Decision = {
  id: string;
  recommendationId: string;
  action: DecisionAction;
  editedGrossRial: string | null;
  comment: string;
  decidedAt: string;
};

export type Recommendation = {
  id: string;
  personId: string;
  personName: string;
  period: string;
  ruleSetVersion: string;
  /** `PROVISIONAL_DRAFT`: the weights are not approved rules. */
  ruleSetStatus: string;
  score100: number;
  totalBp: number;
  contributions: CriterionScore[];
  missingCriteria: MetricCode[];
  observationsUsed: ObservationUsed[];
  band: ForecastBand;
  /** Proposed monthly gross, integer Rial digit string. */
  suggestedGrossRial: string;
  /** suggested − current, when the manager supplied a current amount. */
  deltaRial: string | null;
  statutory: StatutoryCost;
  currentStatutory: StatutoryCost | null;
  explanation: Explanation;
  engineVersion: string;
  /** SHA-256 over the canonical inputs (server-side). */
  calculationHash: string;
  /** Always true: the recommendation is advisory, never a legal entitlement. */
  advisory: true;
  status: 'pending' | 'decided';
  decision: Decision | null;
  createdAt: string;
};

export type RecommendationSummary = {
  id: string;
  personId: string;
  personName: string;
  period: string;
  score100: number;
  suggestedGrossRial: string;
  deltaRial: string | null;
  status: 'pending' | 'decided';
  decisionAction: DecisionAction | null;
  createdAt: string;
};

export type DashboardSummary = {
  peopleCount: number;
  validObservationCount: number;
  pendingCount: number;
  decidedCount: number;
  recentDecisions: Array<Decision & { personName: string; score100: number }>;
};

/** One published criterion, served by `GET /api/v1/manager/rules`. */
export type EvaluationCriterion = {
  code: MetricCode;
  labelFa: string;
  unitFa: string;
  weightBp: number;
  minRaw: string;
  maxRaw: string;
  guidanceFa: string;
};

export type EvaluationRules = {
  ruleSetVersion: string;
  ruleSetStatus: string;
  statusLabelFa: string;
  weightsSumBp: number;
  missingPolicyFa: string;
  criteria: EvaluationCriterion[];
  advisory: true;
};

export type ImportRowError = { row: number; reason: string };

export type ImportSummary = { imported: number; rejected: ImportRowError[] };
