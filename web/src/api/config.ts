const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
import axios from 'axios';


export const createApiClient = () => {
  const token = localStorage.getItem('auth_token');
  
  return axios.create({
    baseURL: API_BASE,
    headers: {
      'Authorization': token ? `Bearer ${token}` : undefined,
      'Content-Type': 'application/json'
    }
  });
};