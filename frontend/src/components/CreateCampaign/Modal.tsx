import {
  Box,
  Dialog,
  DialogContent,
  DialogTitle,
  Divider,
  IconButton,
  Step,
  StepLabel,
  Stepper,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { useState } from 'react';

import { useCreateAllCampaigns, useGeneratePlan } from '@/hooks/data';
import type { ApiAdCampaign, ApiCreateCampaignRequest, ApiMediaPlan } from '@/types';

import { InputForm } from './InputForm';
import { PlanPreview } from './PlanPreview';

interface CreateCampaignModalProps {
  open: boolean;
  onClose: () => void;
}

const STEPS = ['Configure', 'Review & Create'];

export function CreateCampaignModal({ open, onClose }: CreateCampaignModalProps) {
  const [step, setStep] = useState(0);
  const [plan, setPlan] = useState<ApiMediaPlan | null>(null);
  const [results, setResults] = useState<ApiAdCampaign[]>([]);

  const generatePlan = useGeneratePlan();
  const createAll = useCreateAllCampaigns();

  const handleGenerate = async (request: ApiCreateCampaignRequest) => {
    const generated = await generatePlan.mutateAsync(request);
    setPlan(generated);
    setStep(1);
  };

  const handleCreateAll = async () => {
    if (!plan) return;
    const campaigns = await createAll.mutateAsync(plan);
    setResults(campaigns);
  };

  const handleClose = () => {
    setStep(0);
    setPlan(null);
    setResults([]);
    generatePlan.reset();
    createAll.reset();
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          Create Campaigns
          <IconButton onClick={handleClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <Box px={3} pb={1}>
        <Stepper activeStep={step} alternativeLabel>
          {STEPS.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
      </Box>

      <Divider />

      <DialogContent>
        {step === 0 && <InputForm onSubmit={handleGenerate} isLoading={generatePlan.isPending} />}
        {step === 1 && plan && (
          <PlanPreview
            plan={plan}
            onCreateAll={handleCreateAll}
            isCreating={createAll.isPending}
            results={results}
          />
        )}
      </DialogContent>
    </Dialog>
  );
}
