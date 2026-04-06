import { useQuery } from '@tanstack/react-query';

import { fetchMetrics } from '@/repository';
import type { ApiCampaignMetrics } from '@/types';

export const useMetrics = (days = 7) => {
  const { isPending, error, data } = useQuery<ApiCampaignMetrics[], Error>({
    queryKey: ['metrics', days],
    queryFn: () => fetchMetrics(days),
    refetchInterval: 30_000,
  });
  return { data, error, isLoading: isPending };
};
