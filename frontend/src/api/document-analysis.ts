/**
 * Document Analysis and Career Evidence Verification API Client (ADR-013 / ADR-014).
 *
 * Authority: docs/AI_ANALYSIS_SPEC.md §2, §3; AGENTS.md §2 Domain invariants 1, 4, 7.
 */

import type { ApiClient } from '@/api/client';
import { CONTRACTS } from '@/api/contracts';

export type ForensicStatus = 'pass' | 'warning' | 'fail' | 'info';

export type ForensicIndicator = {
  name: string;
  status: ForensicStatus;
  detail: string;
};

export type ExtractedDocumentFacts = {
  document_type: string;
  document_type_fa: string;
  issuing_organization: string | null;
  document_number: string | null;
  issue_date_shamsi: string | null;
  verified_experience_years: number | null;
  verified_last_salary_rial: number | null;
  verified_education_level: string | null;
  verified_skills: string[];
  employer_names: string[];
};

export type SalaryImpact = {
  confidence_boost_percent: number;
  market_quartile_recommendation: 'upper_half' | 'top_quartile' | 'median' | 'adjusted';
  recommended_experience_years: number | null;
  discrepancy_detected: boolean;
  discrepancy_message_fa: string | null;
  explanation_fa: string;
};

export type DocumentAnalysisRequest = {
  file_base64: string;
  file_name: string;
  mime_type?: string;
  claimed_job_title?: string | null;
  claimed_experience_years?: number | null;
  claimed_education?: string | null;
  gemini_api_key?: string | null;
};

export type DocumentAnalysisResponse = {
  authenticity_score: number;
  authenticity_verdict: 'verified' | 'needs_human_review' | 'inconclusive' | 'suspicious';
  authenticity_verdict_fa: string;
  forensic_indicators: ForensicIndicator[];
  extracted_facts: ExtractedDocumentFacts;
  salary_impact: SalaryImpact;
  analysis_timestamp: string;
};

export function analyzeCareerDocument(
  client: ApiClient,
  request: DocumentAnalysisRequest,
): Promise<DocumentAnalysisResponse> {
  return client
    .request<DocumentAnalysisResponse>({
      method: 'POST',
      path: CONTRACTS.documentAnalysis.path,
      body: request,
    })
    .then((response) => response.data);
}
