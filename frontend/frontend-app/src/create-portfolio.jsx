import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Card, CardContent, TextField, Button, Typography, Stack, MenuItem } from '@mui/material';
import api from './api';

export default function CreatePortfolio() {
  const navigate = useNavigate();
  const [formError, setFormError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [accountType, setAccountType] = useState('taxable');

  const handleSubmit = async (event) => {
    event.preventDefault();
    setFormError('');

    const formData = new FormData(event.currentTarget);
    const payload = {
      name: String(formData.get('name') || '').trim(),
      account_type: accountType
    };

    if (!payload.name) {
      setFormError('Portfolio name is required.');
      return;
    }

    setIsSubmitting(true);

    try {
      await api.post('/portfolio/add_portfolio', payload);
      navigate('/portfolio');
    } catch (error) {
      const message = error?.response?.data?.message || error?.response?.data?.Error || 'Could not create portfolio.';
      setFormError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Box sx={{ minHeight: 'calc(100vh - 72px)', backgroundColor: '#f3f9ff', p: 3 }}>
      <Box sx={{ maxWidth: 520, mx: 'auto' }}>
        <Card>
          <CardContent>
            <Typography variant="h4" component="h1" sx={{ mb: 3, fontWeight: 700 }}>
              Create portfolio
            </Typography>

            <Box component="form" onSubmit={handleSubmit} noValidate>
              <Stack spacing={2}>
                <TextField name="name" label="Portfolio name" placeholder="My Investment Portfolio" fullWidth required />

                <TextField
                  label="Account type"
                  select
                  value={accountType}
                  onChange={(event) => setAccountType(event.target.value)}
                  fullWidth
                >
                  <MenuItem value="taxable">Taxable</MenuItem>
                  <MenuItem value="Roth">Roth</MenuItem>
                  <MenuItem value="401k">401k</MenuItem>
                </TextField>

                {formError ? <Typography color="error">{formError}</Typography> : null}

                <Stack direction="row" spacing={2}>
                  <Button type="submit" variant="contained" fullWidth disabled={isSubmitting}>
                    {isSubmitting ? 'Creating...' : 'Create portfolio'}
                  </Button>
                  <Button variant="outlined" fullWidth onClick={() => navigate('/portfolio')}>
                    Cancel
                  </Button>
                </Stack>
              </Stack>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
}
