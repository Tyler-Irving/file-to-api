import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add API key to requests if available
apiClient.interceptors.request.use((config) => {
  const apiKey = localStorage.getItem('api_key');
  console.log('[Interceptor] API key from localStorage:', apiKey?.substring(0, 20));
  if (apiKey) {
    config.headers.Authorization = `Api-Key ${apiKey}`;
    console.log('[Interceptor] Added Authorization header:', config.headers.Authorization?.substring(0, 30));
  } else {
    console.warn('[Interceptor] No API key found in localStorage!');
  }
  return config;
});

// Handle errors globally
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear invalid API key
      localStorage.removeItem('api_key');
    }
    return Promise.reject(error);
  }
);

export default apiClient;
