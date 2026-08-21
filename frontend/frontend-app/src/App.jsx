import { Routes, Route, Navigate } from 'react-router-dom';
import { useState } from 'react';
import Login from './login';
import ViewPortfolio from './view-portfolio';

export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem('access_token'));

  return (
    <Routes>
      <Route path="/login" element={<Login onLogin={setToken} />} />
      <Route
        path="/portfolio"
        element={token ? <ViewPortfolio /> : <Navigate to="/login" replace />}
      />
      <Route path="/" element={<Navigate to={token ? '/portfolio' : '/login'} replace />} />
    </Routes>
  );
}