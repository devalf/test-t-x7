import type { AxiosResponse } from 'axios';

import { axiosClient } from '@/lib/axiosClient';
import type { ApiCreateCampaignRequest, ApiMediaPlan } from '@/types';

export const fetchGeneratePlan = async (
  request: ApiCreateCampaignRequest,
): Promise<ApiMediaPlan> => {
  const { data }: AxiosResponse<ApiMediaPlan> = await axiosClient.post(
    '/api/plans/generate',
    request,
  );
  return data;
};
