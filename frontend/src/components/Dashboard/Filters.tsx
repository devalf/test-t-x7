import { FormControl, InputLabel, MenuItem, Select, Stack } from '@mui/material';

import type { CampaignFilters } from '@/repository/campaigns';

interface FiltersProps {
  filters: CampaignFilters;
  onChange: (filters: CampaignFilters) => void;
}

export function Filters({ filters, onChange }: FiltersProps) {
  return (
    <Stack direction="row" spacing={2}>
      <FormControl size="small" sx={{ minWidth: 160 }}>
        <InputLabel>Platform</InputLabel>
        <Select
          label="Platform"
          value={filters.platform ?? ''}
          onChange={(e) => onChange({ ...filters, platform: e.target.value || undefined })}
        >
          <MenuItem value="">All platforms</MenuItem>
          <MenuItem value="google">Google</MenuItem>
          <MenuItem value="meta">Meta</MenuItem>
          <MenuItem value="amazon">Amazon</MenuItem>
        </Select>
      </FormControl>

      <FormControl size="small" sx={{ minWidth: 200 }}>
        <InputLabel>Campaign Type</InputLabel>
        <Select
          label="Campaign Type"
          value={filters.campaign_type ?? ''}
          onChange={(e) => onChange({ ...filters, campaign_type: e.target.value || undefined })}
        >
          <MenuItem value="">All types</MenuItem>
          <MenuItem value="pmax">Performance Max</MenuItem>
          <MenuItem value="shopping">Shopping</MenuItem>
          <MenuItem value="sponsored_brands">Sponsored Brands</MenuItem>
        </Select>
      </FormControl>
    </Stack>
  );
}
