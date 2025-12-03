import axios from 'axios';
import { toast } from 'sonner';

// Use relative path to leverage Next.js proxy (avoids CORS/Cookie issues)
const API_URL = '/api/v1';

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true, // Still needed for cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor removed as we use cookies now

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Ignore 401s from /auth/me as they are expected when checking auth status
    if (error.response?.status === 401 && !error.config.url?.includes('/auth/me')) {
      toast.error('Session Expired', {
        description: 'Your session has expired. Please log in again.',
      });
      // Redirect to login after a short delay
      setTimeout(() => {
        window.location.href = '/login';
      }, 2000);
    }
    return Promise.reject(error);
  }
);

export default api;
