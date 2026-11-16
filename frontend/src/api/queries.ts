import { useQuery, type UseQueryResult } from '@tanstack/react-query';
import { apiClient } from './instance';
import { CONTRACTS } from './contracts';

export const queryKeys = {
  healthLive: ['health', 'live'] as const,
};

/** `GET /health/live` — the only endpoint the backend currently serves. */
export type HealthLiveResponse = { status: string };

export function useHealthLive(): UseQueryResult<HealthLiveResponse> {
  return useQuery({
    queryKey: queryKeys.healthLive,
    queryFn: async () => {
      const response = await apiClient.request<HealthLiveResponse>({
        path: CONTRACTS.healthLive.path,
      });
      return response.data;
    },
    staleTime: 15_000,
  });
}
