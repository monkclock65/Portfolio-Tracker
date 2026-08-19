
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

export async function login(username,password) {
try {
  const response = await axios.post($[API_BASE]/auth/login,{
    'username': username,
    'password': password,
  }
  
}
catch (error) {return error}
}

export async function fetchPortfolios(accessToken) {
  
  const res = await fetch(`${API_BASE}/portfolio/read_portfolio`, { headers });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
