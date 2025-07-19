const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
import axios from 'axios';


export const createApiClient = () => {
  const token = localStorage.getItem('auth_token');
  
  const apiClient = axios.create({
    baseURL: API_BASE,
    headers: {
      'Authorization': token ? `Bearer ${token}` : undefined,
      'Content-Type': 'application/json'
    }
  });

  // Add debug logging to your API client
  apiClient.interceptors.request.use((config) => {
    const token = localStorage.getItem('auth_token');
    console.log('🔍 API Request - Token found:', token ? 'Yes' : 'No');
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('✅ Added Bearer token to request');
    }
    return config;
  });

  // Check response interceptor
  apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
      console.log('❌ API Error:', error.response?.status, error.response?.data);
      if (error.response?.status === 401) {
        console.log('🔓 401 Unauthorized - Clearing auth');
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_data');
        window.location.href = '/login';
      }
      return Promise.reject(error);
    }
  );

  return apiClient;
};