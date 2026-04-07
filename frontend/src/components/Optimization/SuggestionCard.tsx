import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import {
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  Chip,
  LinearProgress,
  Typography,
} from '@mui/material';

import { useApproveSuggestion } from '@/hooks/data';
import type { ApiOptimizationSuggestion } from '@/types';

interface SuggestionCardProps {
  suggestion: ApiOptimizationSuggestion;
}

export function SuggestionCard({ suggestion }: SuggestionCardProps) {
  const approveMutation = useApproveSuggestion();

  return (
    <Card variant="outlined" sx={{ mb: 1 }}>
      <CardContent sx={{ pb: 0 }}>
        <Box display="flex" alignItems="center" gap={1} mb={1}>
          <Chip label={suggestion.issue_detected} color="warning" size="small" />
          <Typography variant="caption" color="text.secondary">
            Confidence: {Math.round(suggestion.confidence * 100)}%
          </Typography>
          {suggestion.approved && <CheckCircleIcon color="success" fontSize="small" />}
        </Box>

        <LinearProgress
          variant="determinate"
          value={suggestion.confidence * 100}
          sx={{ mb: 1.5, borderRadius: 1 }}
        />

        <Typography variant="body2" color="text.secondary" gutterBottom>
          {suggestion.reasoning}
        </Typography>

        <Typography variant="body2" fontWeight={500}>
          {suggestion.recommended_action}
        </Typography>
      </CardContent>

      <CardActions>
        {suggestion.approved ? (
          <Typography variant="caption" color="success.main" sx={{ ml: 1 }}>
            Approved
          </Typography>
        ) : (
          <Button
            size="small"
            variant="contained"
            disabled={approveMutation.isPending}
            onClick={() => approveMutation.mutate(suggestion.id)}
          >
            Approve
          </Button>
        )}
      </CardActions>
    </Card>
  );
}
