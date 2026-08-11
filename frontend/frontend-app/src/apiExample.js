// Minimal single-function example to fetch portfolios from the backend
// Usage: import { fetchPortfolios } from './apiExample'
// Call: const data = await fetchPortfolios(accessToken)

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

export async function fetchPortfolios(accessToken) {
  const headers = {};
  if (accessToken) headers['Authorization'] = `Bearer ${accessToken}`;

  const res = await fetch(`${API_BASE}/portfolio/read_portfolio`, { headers });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
