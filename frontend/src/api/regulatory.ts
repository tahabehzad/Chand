/**
 * Regulatory statutory sync and official sources API client.
 *
 * Authority: ADR-007, ADR-008, ADR-014; WBS P4-T04.
 */

import { CONTRACTS, requireDelivered } from '@/api/contracts';
import { apiClient } from '@/api/instance';
import type { ApiClient } from '@/api/client';

export type RegulatoryStatusResponse = {
  active_version: string;
  year_shamsi: number;
  effective_date: string;
  last_synced_at: string;
  sources: string[];
  source_urls: string[];
};

export async function fetchRegulatoryStatus(
  client: ApiClient = apiClient,
): Promise<RegulatoryStatusResponse> {
  requireDelivered(CONTRACTS.regulatoryStatus);
  const response = await client.request<RegulatoryStatusResponse>({
    path: CONTRACTS.regulatoryStatus.path,
    method: CONTRACTS.regulatoryStatus.method,
  });
  return response.data;
}
