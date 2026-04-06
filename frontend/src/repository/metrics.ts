import type { AxiosResponse } from 'axios';

import { axiosClient } from '@/lib/axiosClient';
import type { ApiCampaignMetrics, ApiOptimizationSuggestion } from '@/types';

export const fetchMetrics = async (days = 7): Promise<ApiCampaignMetrics[]> => {
  const { data }: AxiosResponse<ApiCampaignMetrics[]> = await axiosClient.get('/api/metrics', {
    params: { days },
  });
  return data;
};

export const fetchSuggestions = async (): Promise<ApiOptimizationSuggestion[]> => {
  const { data }: AxiosResponse<ApiOptimizationSuggestion[]> = await axiosClient.get(
    '/api/metrics/suggestions',
  );
  return data;
};

export const approveSuggestion = async (id: string): Promise<ApiOptimizationSuggestion> => {
  const { data }: AxiosResponse<ApiOptimizationSuggestion> = await axiosClient.post(
    `/api/metrics/suggestions/${id}/approve`,
  );
  return data;
};
