import {
  Box,
  Button,
  CircularProgress,
  FormControl,
  FormControlLabel,
  FormLabel,
  Radio,
  RadioGroup,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import { useState } from 'react';

import type { ApiCreateCampaignRequest } from '@/types';

interface InputFormProps {
  onSubmit: (request: ApiCreateCampaignRequest) => void;
  isLoading: boolean;
}

export function InputForm({ onSubmit, isLoading }: InputFormProps) {
  const [objective, setObjective] = useState<'sales' | 'leads'>('sales');
  const [dailyBudget, setDailyBudget] = useState('');
  const [categories, setCategories] = useState('');
  const [geo, setGeo] = useState('US');
  const [lang, setLang] = useState('en');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const budget = parseFloat(dailyBudget);
    if (isNaN(budget) || budget <= 0) return;

    const productCategories = categories
      .split(',')
      .map((c) => c.trim())
      .filter(Boolean);

    if (productCategories.length === 0) return;

    onSubmit({
      objective,
      daily_budget: budget,
      product_categories: productCategories,
      geo: geo
        .split(',')
        .map((g) => g.trim())
        .filter(Boolean),
      lang: lang
        .split(',')
        .map((l) => l.trim())
        .filter(Boolean),
    });
  };

  return (
    <Box component="form" onSubmit={handleSubmit}>
      <Stack spacing={3}>
        <FormControl>
          <FormLabel>Objective</FormLabel>
          <RadioGroup
            row
            value={objective}
            onChange={(e) => setObjective(e.target.value as 'sales' | 'leads')}
          >
            <FormControlLabel value="sales" control={<Radio />} label="Sales" />
            <FormControlLabel value="leads" control={<Radio />} label="Leads" />
          </RadioGroup>
        </FormControl>

        <TextField
          label="Daily Budget (USD)"
          type="number"
          required
          inputProps={{ min: 1, step: 0.01 }}
          value={dailyBudget}
          onChange={(e) => setDailyBudget(e.target.value)}
          helperText="Minimum $1/day"
        />

        <TextField
          label="Product Categories"
          required
          value={categories}
          onChange={(e) => setCategories(e.target.value)}
          helperText="Comma-separated (e.g. shoes, apparel, accessories)"
          placeholder="shoes, apparel"
        />

        <Stack direction="row" spacing={2}>
          <TextField
            label="Country"
            value={geo}
            onChange={(e) => setGeo(e.target.value)}
            helperText="Comma-separated ISO codes"
            placeholder="US"
            fullWidth
          />
          <TextField
            label="Language"
            value={lang}
            onChange={(e) => setLang(e.target.value)}
            helperText="Comma-separated language codes"
            placeholder="en"
            fullWidth
          />
        </Stack>

        {isLoading && (
          <Box display="flex" alignItems="center" gap={1}>
            <CircularProgress size={20} />
            <Typography variant="body2" color="text.secondary">
              Generating plan with AI…
            </Typography>
          </Box>
        )}

        <Button
          type="submit"
          variant="contained"
          disabled={isLoading}
          sx={{ alignSelf: 'flex-start' }}
        >
          Generate Plan
        </Button>
      </Stack>
    </Box>
  );
}
