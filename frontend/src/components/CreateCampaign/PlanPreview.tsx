import {
  Box,
  Button,
  Chip,
  CircularProgress,
  Divider,
  Stack,
  Typography,
} from '@mui/material';

import type { ApiAdCampaign, ApiMediaPlan } from '@/types';

interface PlanPreviewProps {
  plan: ApiMediaPlan;
  onCreateAll: () => void;
  isCreating: boolean;
  results: ApiAdCampaign[];
}

const PLATFORM_STATUS_COLOR: Record<string, 'success' | 'error' | 'default'> = {
  created: 'success',
  failed: 'error',
  pending: 'default',
};

export function PlanPreview({ plan, onCreateAll, isCreating, results }: PlanPreviewProps) {
  const resultMap = Object.fromEntries(results.map((r) => [r.platform, r]));

  return (
    <Stack spacing={2}>
      <Stack direction="row" spacing={2} flexWrap="wrap">
        <Box>
          <Typography variant="caption" color="text.secondary">Objective</Typography>
          <Typography variant="body2" fontWeight={500}>{plan.objective}</Typography>
        </Box>
        <Box>
          <Typography variant="caption" color="text.secondary">Daily Budget</Typography>
          <Typography variant="body2" fontWeight={500}>
            ${plan.daily_budget.toFixed(2)}
          </Typography>
        </Box>
        <Box>
          <Typography variant="caption" color="text.secondary">Geo</Typography>
          <Typography variant="body2" fontWeight={500}>{plan.geo.join(', ')}</Typography>
        </Box>
        <Box>
          <Typography variant="caption" color="text.secondary">Language</Typography>
          <Typography variant="body2" fontWeight={500}>{plan.lang.join(', ')}</Typography>
        </Box>
        <Box>
          <Typography variant="caption" color="text.secondary">Bidding</Typography>
          <Typography variant="body2" fontWeight={500}>{plan.bidding_strategy}</Typography>
        </Box>
      </Stack>

      <Divider />

      <Box>
        <Typography variant="subtitle2" gutterBottom>Headlines</Typography>
        <Stack direction="row" spacing={0.5} flexWrap="wrap" useFlexGap>
          {plan.creative_pack.headlines.slice(0, 5).map((h, i) => (
            <Chip key={i} label={h} size="small" variant="outlined" />
          ))}
          {plan.creative_pack.headlines.length > 5 && (
            <Chip
              label={`+${plan.creative_pack.headlines.length - 5} more`}
              size="small"
            />
          )}
        </Stack>
      </Box>

      <Box>
        <Typography variant="subtitle2" gutterBottom>Keywords</Typography>
        <Stack direction="row" spacing={0.5} flexWrap="wrap" useFlexGap>
          {plan.targeting_hints.keywords.slice(0, 8).map((k, i) => (
            <Chip key={i} label={k} size="small" color="primary" variant="outlined" />
          ))}
          {plan.targeting_hints.keywords.length > 8 && (
            <Chip
              label={`+${plan.targeting_hints.keywords.length - 8} more`}
              size="small"
            />
          )}
        </Stack>
      </Box>

      <Box>
        <Typography variant="subtitle2" gutterBottom>Descriptions</Typography>
        {plan.creative_pack.descriptions.slice(0, 2).map((d, i) => (
          <Typography key={i} variant="body2" color="text.secondary">
            • {d}
          </Typography>
        ))}
      </Box>

      <Divider />

      <Box>
        <Typography variant="subtitle2" gutterBottom>Platform Status</Typography>
        <Stack direction="row" spacing={1}>
          {(['google', 'meta', 'amazon'] as const).map((platform) => {
            const result = resultMap[platform];
            return (
              <Chip
                key={platform}
                label={`${platform.charAt(0).toUpperCase() + platform.slice(1)}${result ? `: ${result.status}` : ''}`}
                color={result ? PLATFORM_STATUS_COLOR[result.status] : 'default'}
                size="small"
                variant={result ? 'filled' : 'outlined'}
              />
            );
          })}
        </Stack>
      </Box>

      <Box display="flex" alignItems="center" gap={2}>
        <Button
          variant="contained"
          onClick={onCreateAll}
          disabled={isCreating || results.length > 0}
        >
          {results.length > 0 ? 'Campaigns Created' : 'Create All Campaigns'}
        </Button>
        {isCreating && <CircularProgress size={20} />}
      </Box>
    </Stack>
  );
}
