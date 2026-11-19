/**
 * Market salary estimation API service — ADR-014 contract.
 *
 * Calls ``POST /api/v1/simulations/salary-estimation`` through the typed client.
 * Components never call ``fetch`` directly and never recompute a figure: every
 * amount arrives as an integer Rial that is an exact multiple of 10 Rial, so the
 * UI can render Toman without rounding (`lib/money.ts`).
 */

import type { ApiClient } from '@/api/client';
import { CONTRACTS } from '@/api/contracts';

export type SalaryEstimationRequest = {
  job_title: string;
  experience_years: number;
  seniority_level: 'junior' | 'mid' | 'senior';
  employment_type: 'full_time' | 'part_time' | 'contract' | 'freelance';
  city: string;
  province?: string | null;
  work_condition?: 'on_site' | 'remote' | 'hybrid';
  job_description?: string | null;
  currency_unit?: 'rial' | 'toman';
  skills?: { name: string; level?: 'beginner' | 'intermediate' | 'advanced' }[];
  education?: string | null;
  certifications?: string[];
  previous_jobs?: unknown[];
  gemini_api_key?: string;
};

export type ConfidenceLevel = 'high' | 'medium' | 'low' | 'insufficient_data';

export type MarketDataRow = {
  source: string;
  job_title: string;
  city: string;
  seniority_level: string;
  min_salary_rial: number;
  median_salary_rial: number;
  max_salary_rial: number;
  sample_count: number;
  collected_at: string;
  confidence: string;
};

export type DistributionBucket = {
  min_rial: number;
  max_rial: number;
  count: number;
};

export type ConfidenceDetail = {
  data_confidence: string;
  prediction_confidence: string;
  method_ceiling: string;
  components: Record<string, string>;
  weights: Record<string, string>;
  notes_fa: string[];
};

export type MethodologySummary = {
  method: string;
  estimation_version: string;
  engine_version: string;
  cohort_scope: string;
  cohort_definition_fa: string;
  range_source: string;
  percentile_method: string;
  outlier_tests: string[];
  adjustments_applied: string[];
  data_kind: string;
  currency_storage: string;
  currency_display: string;
  quantisation_rial: number;
  warning_codes: string[];
};

export type SalaryEstimationResponse = {
  advisory: boolean;
  statutory: boolean;
  advisory_notes: string[];
  data_source_mode?: 'gemini_live' | 'database_fallback' | 'hybrid';

  model_version: string;
  estimation_version: string;
  engine_version: string;
  calculation_hash: string;
  generated_at: string;

  job_title: string;
  experience_years: number;
  seniority_level: string;
  employment_type: string;
  work_condition: string;
  city: string;
  province: string | null;

  primary_estimate_rial: number;
  min_salary_rial: number;
  median_salary_rial: number;
  max_salary_rial: number;
  rounding_residual_rial: number;
  currency_unit: 'rial' | 'toman';

  valid_sample_count: number;
  quarantined_sample_count: number;
  rejected_sample_count: number;
  data_sources: string[];
  data_collected_at: string | null;
  data_oldest_at: string | null;
  market_rows: MarketDataRow[];
  distribution: DistributionBucket[];

  factors_influence: string[];
  factors_notes: string[];
  confidence_level: ConfidenceLevel;
  confidence_score: string;
  confidence: ConfidenceDetail;
  methodology: MethodologySummary;
  match: {
    family_key?: string;
    family_title_fa?: string;
    score?: string;
    components?: Record<string, string>;
    reasons_fa?: string[];
  };
  warnings: string[];

  legal_minimum_wage_rial: number | null;
};

export function estimateSalary(
  client: ApiClient,
  request: SalaryEstimationRequest,
): Promise<SalaryEstimationResponse> {
  return client
    .request<SalaryEstimationResponse>({
      method: 'POST',
      path: CONTRACTS.salaryEstimation.path,
      body: request,
    })
    .then((response) => response.data);
}

export type CtcDeductions = {
  employee_sso_rial: number;
  income_tax_rial: number;
  total_deductions_rial: number;
};

export type CtcEmployerCosts = {
  employer_sso_rial: number;
  unemployment_rial: number;
  monthly_severance_rial: number;
  monthly_eydi_rial: number;
  total_employer_costs_rial: number;
};

export type SalaryCtcBreakdownRequest = {
  gross_salary_rial: number;
  year?: number;
  month_days?: number;
};

export type SalaryCtcBreakdownResponse = {
  gross_salary_rial: number;
  net_salary_rial: number;
  deductions: CtcDeductions;
  employer_costs: CtcEmployerCosts;
  total_cost_to_employer_rial: number;
  annual_cost_to_employer_rial: number;
  rule_version: string;
  engine_version: string;
  calculation_hash: string;
  generated_at: string;
};

export function getSalaryCtcBreakdown(
  client: ApiClient,
  request: SalaryCtcBreakdownRequest,
): Promise<SalaryCtcBreakdownResponse> {
  return client
    .request<SalaryCtcBreakdownResponse>({
      method: 'POST',
      path: CONTRACTS.salaryCtcBreakdown.path,
      body: request,
    })
    .then((response) => response.data);
}
