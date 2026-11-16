/**
 * Type definitions for the gross-to-net payroll simulation API.
 * Matches backend/schemas/payroll.py and the ADR-008 v1 scope.
 */

export type TaxPosture = 'conservative_inta' | 'court_precedent';

export interface AllowancesInput {
  housing: number;
  grocery: number;
  marriage: number;
  child: number;
  continuous_attraction: number;
}

export interface GrossToNetRequest {
  gross_monthly_rial: number;
  rule_year?: number;
  days_in_month?: 29 | 30 | 31;
  tax_posture?: TaxPosture;
  allowances?: AllowancesInput;
  overtime_hours?: number;
  night_hours?: number;
  continuous_attraction_taxable?: boolean;
  probation_months?: number | null;
  tenure_months?: number | null;
  accumulated_unused_leave_days?: number | null;
  probation_days_worked?: number | null;
}

export interface SlabLine {
  slab: number;
  /** The band rate as a decimal string, e.g. "0.10" — never a float. */
  rate: string;
  taxed_amount_rial: number;
  tax_rial: number;
}

export interface PostureTaxView {
  posture: TaxPosture;
  art137_deduction_rial: number;
  welfare_allowances_taxable: boolean;
  taxable_income_rial: number;
  income_tax_rial: number;
  tax_slabs_applied: string[];
  slab_breakdown: SlabLine[];
  net_rial: number;
}

export interface SsoView {
  insurable_wage_rial: number;
  insurable_ceiling_rial: number;
  sso_insurable_ceiling_applied: boolean;
  employee_share_7pct_rial: number;
  employer_share_20pct_rial: number;
  unemployment_fund_3pct_rial: number;
}

export interface ProvenanceEntry {
  rule_id: string;
  rule_year_shamsi: number;
  formula_ref: string;
}

export interface BasesView {
  /** Art. 36 Note 3 welfare total, excluded from *Mozd-e Saabet*. */
  welfare_total_rial: number;
  /** *Mozd-e Saabet* — the statutory base of severance, overtime and Eydi. */
  mozd_e_saabet_rial: number;
  /** The paid-hours divisor, as a decimal string (e.g. "220.00"). */
  overtime_divisor: string;
  overtime_pay_rial: number;
  night_shift_pay_rial: number;
  /** Gross plus the overtime and night-shift premiums. */
  total_gross_rial: number;
}

export interface PayrollInputsView {
  gross_monthly_rial: number;
  allowances_rial: {
    housing: number;
    grocery: number;
    marriage: number;
    child: number;
    continuous_attraction: number;
  };
  overtime_hours: number;
  night_hours: number;
  continuous_attraction_taxable: boolean;
}

export interface PayrollResponse {
  statutory_version: string;
  rule_set_status: string;
  is_verified: boolean;
  engine_version: string;
  calculation_hash: string;
  generated_at: string;
  rule_year_shamsi: number;
  days_in_month: number;
  primary_tax_posture: TaxPosture;
  inputs: PayrollInputsView;
  bases: BasesView;
  sso: SsoView;
  tax_postures: Record<TaxPosture, PostureTaxView>;
  net_rial: number;
  alternate_posture_net_rial: number;
  employee_deductions: {
    employee_sso_7pct_rial: number;
    income_tax_rial: number;
  };
  severance_sanavat: {
    monthly_accrual_rial: number;
  };
  eydi: {
    annual_gross_rial: number;
    at_cap: boolean;
    monthly_accrual_rial: number;
    annual_tax_rial: number;
    annual_net_rial: number;
  };
  employer_cost: {
    total_monthly_employer_cost_rial: number;
    annual_ctc_12month_rial: number;
    includes_26day_leave_reserve: boolean;
  };
  rounding_residual_rial: number;
  provenance: Record<string, ProvenanceEntry>;
  termination_liability?: {
    probation_months: number;
    employer_initiated_probation_liability_rial: number;
    employee_initiated_probation_liability_rial: number | null;
    tenure_months: number;
    exit_severance_rial: number;
    leave_carryover_cap_days: number;
    effective_buyout_days: number;
    leave_buyout_rial: number;
    total_separation_rial: number;
  } | null;
}