import { useMutation } from '@tanstack/react-query'
import api from './api'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Box, Card, CardContent, TextField, Button, Typography, Stack } from '@mui/material'

export default function Login({ onLogin }) {
    const navigate = useNavigate()
    const [error, setError] = useState('')
    const loginMutation = useMutation({
        mutationFn: (loginData) => api.post('/auth/login', loginData),
        onSuccess: (response) => {
            const token = response.data.access_token
            const refresh = response.data.refresh_token
            if (!token) {
                setError('Login failed: missing access token')
                return
            }
            localStorage.setItem('access_token', token)
            if (refresh) localStorage.setItem('refresh_token', refresh)
            if (typeof onLogin === 'function') onLogin(token)
            navigate('/portfolio')
        }
    })

    function handleLogin(event) {
        event.preventDefault()
        const formData = new FormData(event.currentTarget)
        const username = formData.get('username')
        const password = formData.get('password')
        if (!password || !username) {
            setError('password or username field empty')
            return
        }
        setError('')
        loginMutation.mutate({ username, password })
    }

    return (
        <Box sx={{ minHeight: '100vh', backgroundColor: '#e6f7ff', display: 'flex', alignItems: 'center', justifyContent: 'center', p: 2 }}>
            <Card sx={{ maxWidth: 440, width: '100%', mx: 2, borderRadius: 2, boxShadow: 6 }}>
                <CardContent>
                    <Typography variant="h5" component="h1" align="center" gutterBottom>
                        Sign in
                    </Typography>
                    <Box component="form" onSubmit={handleLogin} noValidate>
                        <Stack spacing={2}>
                            <TextField name="username" label="Username" placeholder="Enter username" fullWidth autoFocus />
                            <TextField name="password" label="Password" placeholder="Enter password" type="password" fullWidth />
                            {error && <Typography color="error">{error}</Typography>}
                            {loginMutation.isError && <Typography color="error">{loginMutation.error?.message}</Typography>}
                            <Button type="submit" variant="contained" color="primary" size="large" fullWidth disabled={loginMutation.isLoading || loginMutation.isPending}>
                                {loginMutation.isLoading || loginMutation.isPending ? 'Logging in...' : 'Login'}
                            </Button>
                        </Stack>
                    </Box>
                </CardContent>
            </Card>
        </Box>
    )
}

