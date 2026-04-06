import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { createAllCampaigns, fetchCampaigns } from '@/repository';
import type { ApiAdCampaign, ApiMediaPlan } from '@/types';
import type { CampaignFilters } from '@/repository/campaigns';

export const useCampaigns = (filters?: CampaignFilters) => {
  const { isPending, error, data } = useQuery<ApiAdCampaign[], Error>({
    queryKey: ['campaigns', filters],
    queryFn: () => fetchCampaigns(filters),
  });
  return { data, error, isLoading: isPending };
};

export const useCreateAllCampaigns = () => {
  const queryClient = useQueryClient();
  return useMutation<ApiAdCampaign[], Error, ApiMediaPlan>({
    mutationFn: createAllCampaigns,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['campaigns'] }),
  });
};
