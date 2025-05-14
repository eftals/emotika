import axios from 'axios';
import { getSessionToken } from './sessionManager';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5000',
});

// Add session token to all requests
api.interceptors.request.use((config) => {
  const sessionToken = getSessionToken();
  if (sessionToken) {
    config.headers['X-Session-Token'] = sessionToken;
  }
  return config;
});

export default api; 