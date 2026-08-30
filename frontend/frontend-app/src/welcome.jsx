import { useNavigate } from 'react-router-dom';
import { Box, Card, CardContent, Button, Typography, Stack } from '@mui/material';
import api from './api';

const DEMO_USER = {
    username: 'Demo_User',
    password: 'Password123'
};

export default function Welcome({ onLogin }) {
    const navigate = useNavigate();

    const handleDemoLogin = async () => {
        try {
            const response = await api.post('/auth/demo-login', DEMO_USER);
            const token = response.data?.access_token;

            if (!token) {
                return;
            }

            if (typeof onLogin === 'function') {
                onLogin(token);
            }

            navigate('/portfolio');
        } catch (error) {
            console.error('Demo login failed:', error);
        }
    };

    return (
        <Box sx={{ minHeight: '100vh', backgroundColor: '#9fb4d6', display: 'flex', alignItems: 'center', justifyContent: 'center', p: 2 }}>
            <Card sx={{ maxWidth: 440, width: '100%', borderRadius: 2 }}>
                <CardContent>
                    <Typography variant="h5" component="h1" align="center" gutterBottom>
                        Welcome to Portfolio Tracker
                    </Typography>
                    <Stack spacing={2}>
                        <Button variant='contained' onClick={handleDemoLogin}>
                            Try Demo
                        </Button>
                        <Button variant='contained' onClick={() => navigate('/login')}>
                            Login
                        </Button>
                        <Button variant='outlined' onClick={() => navigate('/register')}>
                            Register
                        </Button>
                    </Stack>
                </CardContent>
            </Card>
        </Box>
    );
}