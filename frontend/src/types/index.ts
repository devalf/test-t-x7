// Re-export only the Api* interfaces — the generated scalar aliases clash across modules.
export type { ApiCreativePack, ApiMediaPlan, ApiTargetingHints } from '@shared/plan';
export type {
  ApiAdCampaign,
  ApiCampaignStatus,
  ApiCreateCampaignRequest,
} from '@shared/campaign';
export type { ApiCampaignMetrics, ApiOptimizationSuggestion } from '@shared/metrics';
