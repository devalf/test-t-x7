import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { approveSuggestion, fetchSuggestions } from '@/repository';
import type { ApiOptimizationSuggestion } from '@/types';

export const useSuggestions = () => {
  const { isPending, error, data } = useQuery<ApiOptimizationSuggestion[], Error>({
    queryKey: ['suggestions'],
    queryFn: fetchSuggestions,
  });
  return { data, error, isLoading: isPending };
};

export const useApproveSuggestion = () => {
  const queryClient = useQueryClient();
  return useMutation<ApiOptimizationSuggestion, Error, string>({
    mutationFn: approveSuggestion,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['suggestions'] }),
  });
};
