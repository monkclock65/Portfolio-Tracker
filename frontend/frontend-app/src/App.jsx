import { Navigate, Route, Routes } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { AppBar, Box, Button, Toolbar, Typography } from '@mui/material';
import Login from './login';
import Register from './register';
import ViewPortfolio from './view-portfolio';
import CreatePortfolio from './create-portfolio';
import Welcome from './welcome';

function getStoredToken() {
  return localStorage.getItem('access_token');
}

function NavBar({ isAuthenticated, onLogout }) {
  return (
    <AppBar position="static" color="primary" sx={{ mb: 2 }}>
      <Toolbar>
        <Button
          color="inherit"
          href="/welcome"
          sx={{ flexGrow: 1, justifyContent: 'flex-start', p: 0, minWidth: 0, textTransform: 'none' }}
        >
          <Typography variant="h6" component="span" sx={{ fontWeight: 700 }}>
            Portfolio Tracker
          </Typography>
        </Button>

        {isAuthenticated ? (
          <>
            <Button color="inherit" href="/create-portfolio">Create Portfolio</Button>
            <Button color="inherit" href="/portfolio">Portfolio</Button>
            <Button color="inherit" onClick={onLogout}>Logout</Button>
          </>
        ) : (
          <>
            <Button color="inherit" href="/register">Register</Button>
            <Button color="inherit" href="/login">Login</Button>
          </>
        )}
      </Toolbar>
    </AppBar>
  );
}

function App() {
  const [token, setToken] = useState(() => getStoredToken());

  useEffect(() => {
    const syncAuthState = () => setToken(getStoredToken());
    window.addEventListener('auth-change', syncAuthState);
    window.addEventListener('storage', syncAuthState);

    return () => {
      window.removeEventListener('auth-change', syncAuthState);
      window.removeEventListener('storage', syncAuthState);
    };
  }, []);

  const isAuthenticated = Boolean(token);

  const updateToken = (nextToken) => {
    if (nextToken) {
      localStorage.setItem('access_token', nextToken);
    } else {
      localStorage.removeItem('access_token');
    }

    setToken(nextToken || null);
    window.dispatchEvent(new Event('auth-change'));
  };

  const handleLogout = () => {
    updateToken(null);
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