import AddIcon from '@mui/icons-material/Add';
import RefreshIcon from '@mui/icons-material/Refresh';
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  IconButton,
  Stack,
  Tooltip,
  Typography,
} from '@mui/material';
import { useState } from 'react';

import { useCampaigns } from '@/hooks/data/useCampaigns';
import { useMetrics } from '@/hooks/data/useMetrics';
import { useSuggestions } from '@/hooks/data/useSuggestions';
import type { CampaignFilters } from '@/repository/campaigns';

import { CreateCampaignModal } from '../CreateCampaign/Modal';
import { SuggestionCard } from '../Optimization/SuggestionCard';
import { CampaignTable } from './CampaignTable';
import { Filters } from './Filters';

export function Dashboard() {
  const [filters, setFilters] = useState<CampaignFilters>({});
  const [modalOpen, setModalOpen] = useState(false);

  const { data: campaigns = [], isLoading: loadingCampaigns, error: campaignsError } = useCampaigns(filters);
  const { data: metrics = [], isLoading: loadingMetrics, refetch: refetchMetrics } = useMetrics(7);
  const { data: suggestions = [], isLoading: loadingSuggestions } = useSuggestions();

  const isLoading = loadingCampaigns || loadingMetrics;

  return (
    <Box sx={{ maxWidth: 1400, mx: 'auto', px: 3, py: 4 }}>
      {/* Header */}
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
        <Typography variant="h5" fontWeight={700}>
          AdPilot Dashboard
        </Typography>
        <Stack direction="row" spacing={1}>
          <Tooltip title="Refresh metrics">
            <IconButton onClick={() => refetchMetrics()} disabled={loadingMetrics}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setModalOpen(true)}
          >
            Create Campaigns
          </Button>
        </Stack>
      </Box>

      {/* Filters */}
      <Box mb={2}>
        <Filters filters={filters} onChange={setFilters} />
      </Box>

      {/* Error */}
      {campaignsError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          Failed to load campaigns: {campaignsError.message}
        </Alert>
      )}

      {/* Campaign Table */}
      {isLoading ? (
        <Box display="flex" justifyContent="center" py={6}>
          <CircularProgress />
        </Box>
      ) : (
        <CampaignTable campaigns={campaigns} metrics={metrics} />
      )}

      {/* Optimization Suggestions */}
      {!loadingSuggestions && suggestions.length > 0 && (
        <Box mt={4}>
          <Typography variant="h6" fontWeight={600} mb={2}>
            Optimization Suggestions
          </Typography>
          {suggestions.map((s) => (
            <SuggestionCard key={s.id} suggestion={s} />
          ))}
        </Box>
      )}

      {/* Create Campaign Modal */}
      <CreateCampaignModal open={modalOpen} onClose={() => setModalOpen(false)} />
    </Box>
  );
}
