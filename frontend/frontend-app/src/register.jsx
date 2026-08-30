import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Card, CardContent, TextField, Button, Typography, Stack } from '@mui/material';
import api from './api';

export default function Register() {
  const navigate = useNavigate();
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleRegister = async (event) => {
    event.preventDefault();
    setError('');
    setSuccess('');

    const formData = new FormData(event.currentTarget);
    const payload = {
      username: String(formData.get('username') || '').trim(),
      email: String(formData.get('email') || '').trim(),
      password: String(formData.get('password') || '')
    };

    if (!payload.username || !payload.email || !payload.password) {
      setError('Please fill in all fields.');
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await api.post('/auth/register', payload);

      if (response.status === 201) {
        setSuccess('Account created successfully. Redirecting to login...');
        setTimeout(() => navigate('/login'), 1000);
      }
    } catch (err) {
      const message = err?.response?.data?.Error || err?.response?.data?.message || 'Registration failed.';
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Box sx={{ minHeight: '100vh', backgroundColor: '#e6f7ff', display: 'flex', alignItems: 'center', justifyContent: 'center', p: 2 }}>
      <Card sx={{ maxWidth: 440, width: '100%', mx: 2, borderRadius: 2, boxShadow: 6 }}>
        <CardContent>
          <Typography variant="h5" component="h1" align="center" gutterBottom>
            Create account
          </Typography>
          <Box component="form" onSubmit={handleRegister} noValidate>
            <Stack spacing={2}>
              <TextField name="username" label="Username" placeholder="Enter username" fullWidth autoFocus />
              <TextField name="email" label="Email" placeholder="Enter email" type="email" fullWidth />
              <TextField name="password" label="Password" placeholder="Enter password" type="password" fullWidth />

              {error && <Typography color="error">{error}</Typography>}
              {success && <Typography color="success.main">{success}</Typography>}

              <Button type="submit" variant="contained" color="primary" size="large" fullWidth disabled={isSubmitting}>
                {isSubmitting ? 'Creating account...' : 'Register'}
              </Button>

              <Button variant="text" onClick={() => navigate('/login')}>
                Already have an account? Log in
              </Button>
            </Stack>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}
