import { Link, Navigate, Route, Routes } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { AppBar, Box, Button, Toolbar, Typography } from '@mui/material';
import api from './api';
import Login from './login';
import Register from './register';
import ViewPortfolio from './view-portfolio';
import CreatePortfolio from './create-portfolio';
import Welcome from './welcome';

function getStoredToken() {
  const t = localStorage.getItem('access_token');
  if (t === null || t === 'null' || t === 'undefined') return null;
  return t;
}

function NavBar({ isAuthenticated, onLogout }) {
  return (
    <AppBar position="static" color="primary" sx={{ mb: 2 }}>
      <Toolbar>
        <Button
          component={Link}
          to="/welcome"
          color="inherit"
          sx={{ flexGrow: 1, justifyContent: 'flex-start', p: 0, minWidth: 0, textTransform: 'none' }}
        >
          <Typography variant="h6" component="span" sx={{ fontWeight: 700 }}>
            Portfolio Tracker
          </Typography>
        </Button>

        {isAuthenticated ? (
          <>
            <Button component={Link} to="/create-portfolio" color="inherit">Create Portfolio</Button>
            <Button component={Link} to="/portfolio" color="inherit">Portfolio</Button>
            <Button color="inherit" onClick={onLogout}>Logout</Button>
          </>
        ) : (
          <>
            <Button component={Link} to="/register" color="inherit">Register</Button>
            <Button component={Link} to="/login" color="inherit">Login</Button>
          </>
        )}
      </Toolbar>
    </AppBar>
  );
}

function App() {
  const [token, setToken] = useState(() => getStoredToken());
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const syncAuthState = () => setToken(getStoredToken());
    window.addEventListener('auth-change', syncAuthState);
    window.addEventListener('storage', syncAuthState);

    return () => {
      window.removeEventListener('auth-change', syncAuthState);
      window.removeEventListener('storage', syncAuthState);
    };
  }, []);

  // Silent refresh on startup using api.post (sends to configured baseURL)
  useEffect(() => {
    let mounted = true;
    const tryRefresh = async () => {
      const refresh = localStorage.getItem('refresh_token');
      if (!refresh || refresh === 'null' || refresh === 'undefined') {
        if (mounted) setReady(true);
        return;
      }

      try {
        const resp = await api.post('/auth/refresh', {}, {
          headers: { Authorization: `Bearer ${refresh}` },
        });
        const newAccess = resp.data?.access_token;
        if (newAccess) {
          localStorage.setItem('access_token', newAccess);
          if (mounted) setToken(newAccess);
          window.dispatchEvent(new Event('auth-change'));
        } else {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          if (mounted) setToken(null);
          window.dispatchEvent(new Event('auth-change'));
        }
      } catch (e) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        if (mounted) setToken(null);
        window.dispatchEvent(new Event('auth-change'));
      } finally {
        if (mounted) setReady(true);
      }
    };
    tryRefresh();
    return () => { mounted = false; };
  }, []);

  const isAuthenticated = Boolean(token);
  if (!ready) return null;

  const updateToken = (nextToken) => {
    if (nextToken) {
      localStorage.setItem('access_token', nextToken);
    } else {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }

    setToken(nextToken || null);
    window.dispatchEvent(new Event('auth-change'));
  };

  const handleLogout = async () => {
    try {
      if (token) {
        await api.delete('/auth/logout');
      }
    } catch (error) {
      console.warn('Logout request failed, clearing local session anyway:', error);
    } finally {
      updateToken(null);
    }
  };

  return (
    <Routes>
      <Route path="/login" element={<Login onLogin={updateToken} />} />
      <Route path="/register" element={<Register />} />
      <Route
        path="/create-portfolio"
        element={
          isAuthenticated ? (
            <Box>
              <NavBar isAuthenticated={isAuthenticated} onLogout={handleLogout} />
              <CreatePortfolio />
            </Box>
          ) : (
            <Navigate to="/welcome" replace />
          )
        }
      />
      <Route
        path="/portfolio"
        element={
          isAuthenticated ? (
            <Box>
              <NavBar isAuthenticated={isAuthenticated} onLogout={handleLogout} />
              <ViewPortfolio />
            </Box>
          ) : (
            <Navigate to="/welcome" replace />
          )
        }
      />
      <Route path="/welcome" element={<Welcome onLogin={updateToken} />} />
      <Route path="/" element={<Navigate to={isAuthenticated ? '/portfolio' : '/welcome'} replace />} />
      <Route path="*" element={<Navigate to={isAuthenticated ? '/portfolio' : '/welcome'} replace />} />
    </Routes>
  );
}

export default App;