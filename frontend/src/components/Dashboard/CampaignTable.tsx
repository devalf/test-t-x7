import {
  Chip,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';

import type { ApiAdCampaign, ApiCampaignMetrics } from '@/types';

interface AggregatedMetrics {
  spend: number;
  impressions: number;
  clicks: number;
  ctr: number;
  conversions: number;
  conversion_value: number;
}

interface CampaignTableProps {
  campaigns: ApiAdCampaign[];
  metrics: ApiCampaignMetrics[];
}

const PLATFORM_COLOR: Record<string, 'primary' | 'secondary' | 'warning'> = {
  google: 'primary',
  meta: 'secondary',
  amazon: 'warning',
};

const STATUS_COLOR: Record<string, 'success' | 'default' | 'error'> = {
  created: 'success',
  pending: 'default',
  failed: 'error',
};

const TYPE_LABEL: Record<string, string> = {
  pmax: 'PMax',
  shopping: 'Shopping',
  sponsored_brands: 'Sponsored Brands',
};

function aggregateMetrics(
  campaignId: string,
  metrics: ApiCampaignMetrics[],
): AggregatedMetrics {
  const rows = metrics.filter((m) => m.campaign_id === campaignId);
  if (rows.length === 0) return { spend: 0, impressions: 0, clicks: 0, ctr: 0, conversions: 0, conversion_value: 0 };

  const spend = rows.reduce((s, r) => s + r.spend, 0);
  const impressions = rows.reduce((s, r) => s + r.impressions, 0);
  const clicks = rows.reduce((s, r) => s + r.clicks, 0);
  const conversions = rows.reduce((s, r) => s + r.conversions, 0);
  const conversion_value = rows.reduce((s, r) => s + r.conversion_value, 0);
  const ctr = impressions > 0 ? clicks / impressions : 0;

  return { spend, impressions, clicks, ctr, conversions, conversion_value };
}

export function CampaignTable({ campaigns, metrics }: CampaignTableProps) {
  if (campaigns.length === 0) {
    return (
      <Typography color="text.secondary" sx={{ py: 4, textAlign: 'center' }}>
        No campaigns yet. Create your first campaign to get started.
      </Typography>
    );
  }

  return (
    <TableContainer component={Paper} variant="outlined">
      <Table size="small">
        <TableHead>
          <TableRow sx={{ '& th': { fontWeight: 600 } }}>
            <TableCell>Platform</TableCell>
            <TableCell>Campaign Name</TableCell>
            <TableCell>Type</TableCell>
            <TableCell>Status</TableCell>
            <TableCell align="right">Spend</TableCell>
            <TableCell align="right">Impressions</TableCell>
            <TableCell align="right">Clicks</TableCell>
            <TableCell align="right">CTR</TableCell>
            <TableCell align="right">Conv. Value</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {campaigns.map((campaign) => {
            const agg = aggregateMetrics(campaign.id, metrics);
            return (
              <TableRow key={campaign.id} hover>
                <TableCell>
                  <Chip
                    label={campaign.platform.charAt(0).toUpperCase() + campaign.platform.slice(1)}
                    color={PLATFORM_COLOR[campaign.platform] ?? 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell>{campaign.campaign_name}</TableCell>
                <TableCell>{TYPE_LABEL[campaign.campaign_type] ?? campaign.campaign_type}</TableCell>
                <TableCell>
                  <Chip
                    label={campaign.status}
                    color={STATUS_COLOR[campaign.status] ?? 'default'}
                    size="small"
                    variant="outlined"
                  />
                </TableCell>
                <TableCell align="right">
                  {agg.spend.toLocaleString('en-US', { style: 'currency', currency: 'USD' })}
                </TableCell>
                <TableCell align="right">{agg.impressions.toLocaleString()}</TableCell>
                <TableCell align="right">{agg.clicks.toLocaleString()}</TableCell>
                <TableCell align="right">{(agg.ctr * 100).toFixed(2)}%</TableCell>
                <TableCell align="right">
                  {agg.conversion_value.toLocaleString('en-US', { style: 'currency', currency: 'USD' })}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
