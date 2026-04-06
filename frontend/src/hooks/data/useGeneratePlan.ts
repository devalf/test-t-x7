import { useMutation } from '@tanstack/react-query';

import { fetchGeneratePlan } from '@/repository';
import type { ApiCreateCampaignRequest, ApiMediaPlan } from '@/types';

export const useGeneratePlan = () => {
  return useMutation<ApiMediaPlan, Error, ApiCreateCampaignRequest>({
    mutationFn: fetchGeneratePlan,
  });
};
