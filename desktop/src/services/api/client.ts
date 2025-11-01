import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { useStore } from '@/store';

const API_BASE_URL = 'http://localhost:8001/api/v1';
const REQUEST_TIMEOUT = 30000;

// Extend Axios request config to include _retry flag
interface CustomAxiosRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: REQUEST_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add JWT token
apiClient.interceptors.request.use(
  (config) => {
    const token = useStore.getState().accessToken;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor - handle 401 and refresh token
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as CustomAxiosRequestConfig;

    // Handle network errors
    if (!error.response) {
      console.error('Network error:', error.message);
      return Promise.reject(new Error('Network error. Please check your connection.'));
    }

    // Handle 401 Unauthorized - try to refresh token
    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = useStore.getState().refreshToken;
        if (!refreshToken) {
          console.warn('No refresh token available, logging out');
          useStore.getState().logout();
          return Promise.reject(new Error('Session expired. Please login again.'));
        }

        const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        });

        const { access_token } = response.data;
        useStore.getState().setTokens(access_token, refreshToken);

        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
        useStore.getState().logout();
        return Promise.reject(new Error('Session expired. Please login again.'));
      }
    }

    // Handle other HTTP errors
    const status = error.response?.status;
    const errorData = error.response?.data as { detail?: string } | undefined;
    const errorMessage = errorData?.detail || error.message;

    console.error(`API error (${status}):`, errorMessage);

    // Provide user-friendly error messages
    if (status === 403) {
      return Promise.reject(new Error('You do not have permission to perform this action.'));
    } else if (status === 404) {
      return Promise.reject(new Error('The requested resource was not found.'));
    } else if (status === 500) {
      return Promise.reject(new Error('Server error. Please try again later.'));
    } else if (status === 503) {
      return Promise.reject(new Error('Service unavailable. Please try again later.'));
    }

    return Promise.reject(error);
  }
);
