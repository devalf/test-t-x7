import type { AxiosResponse } from 'axios';

import { axiosClient } from '@/lib/axiosClient';
import type { ApiAdCampaign, ApiMediaPlan } from '@/types';

export interface CampaignFilters {
  platform?: string;
  campaign_type?: string;
}

export const fetchCampaigns = async (filters?: CampaignFilters): Promise<ApiAdCampaign[]> => {
  const { data }: AxiosResponse<ApiAdCampaign[]> = await axiosClient.get('/api/campaigns', {
    params: filters,
  });
  return data;
};

export const createAllCampaigns = async (plan: ApiMediaPlan): Promise<ApiAdCampaign[]> => {
  const { data }: AxiosResponse<ApiAdCampaign[]> = await axiosClient.post(
    '/api/campaigns/create-all',
    plan,
  );
  return data;
};
