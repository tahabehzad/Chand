import { managerRequest } from '@/prototype/api';
import { authHeaders } from '@/prototype/session';
import { readApiBaseUrl } from '@/api/client';
import type { GrossToNetRequest, PayrollResponse } from '@/api/payroll-types';

export type WorkProfile = {
  job_title: string; education: string; education_subject: string; qualifications: string;
  total_experience_months: number | null; relevant_experience_months: number | null;
  insurance_months: number | null; employer_tenure_months: number | null;
  recognised_seniority_months: number | null; daily_hours: string | null;
  schedule_period: 'weekly' | 'monthly'; weekly_days: number | null;
  monthly_paid_days: number | null; workshop_type: 'unclassified' | 'classified';
  documented_daily_seniority_rial: number | null;
};
export const EMPTY_WORK_PROFILE: WorkProfile = {
  job_title: '', education: '', education_subject: '', qualifications: '',
  total_experience_months: null, relevant_experience_months: null, insurance_months: null,
  employer_tenure_months: null, recognised_seniority_months: null, daily_hours: null,
  schedule_period: 'weekly', weekly_days: null, monthly_paid_days: null,
  workshop_type: 'unclassified', documented_daily_seniority_rial: null,
};
export type SavedProfile = { profile: WorkProfile; revision: number };
export type WorkDocument = { id: string; fileName: string; contentType: string; byteSize: number; sha256: string };
export type WorkResult = {
  payroll: PayrollResponse;
  work_context: { ratio: string; gross_rial: number; seniority_rial: number; rounding_residual_rial: number };
  profile_revision: number; work_calculation_hash: string;
  full_time_inputs: GrossToNetRequest;
};
function base(id: string): string { return `/api/v1/manager/employees/${encodeURIComponent(id)}`; }
export const getWorkProfile = (id: string) => managerRequest<SavedProfile | null>(`${base(id)}/work-profile`);
export const saveWorkProfile = (id: string, profile: WorkProfile, revision: number) =>
  managerRequest<SavedProfile>(`${base(id)}/work-profile`, { method: 'PUT', body: { profile, expected_revision: revision } });
export const getWorkDocuments = (id: string) => managerRequest<WorkDocument[]>(`${base(id)}/work-documents`);
export const getLatestWorkResult = (id: string) => managerRequest<WorkResult | null>(`${base(id)}/work-profile/calculations/latest`);
export const calculateWorkProfile = (id: string, payroll: GrossToNetRequest) =>
  managerRequest<WorkResult>(`${base(id)}/work-profile/calculate`, { method: 'POST', body: { payroll } });
export async function uploadWorkDocument(id: string, file: File): Promise<WorkDocument> {
  const form = new FormData(); form.set('file', file);
  return managerRequest<WorkDocument>(`${base(id)}/work-documents`, { method: 'POST', form });
}
export async function downloadWorkDocument(id: string, document: WorkDocument): Promise<void> {
  const response = await fetch(`${readApiBaseUrl()}${base(id)}/work-documents/${encodeURIComponent(document.id)}/content`, { headers: authHeaders(), credentials: 'same-origin' });
  if (!response.ok) throw new Error('دریافت مدرک ناموفق بود.');
  const url = URL.createObjectURL(await response.blob());
  const link = window.document.createElement('a'); link.href = url; link.download = document.fileName;
  link.click(); window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}
