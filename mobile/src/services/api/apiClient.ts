import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import * as SecureStore from 'expo-secure-store';
import Constants from 'expo-constants';

// Environment-based API URL configuration with fallback
const API_BASE_URL = Constants.expoConfig?.extra?.apiBaseUrl ||
                     process.env.EXPO_PUBLIC_API_BASE_URL ||
                     'http://localhost:8001/api/v1';
const REQUEST_TIMEOUT = 30000;

// SecureStore keys
const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

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

// Token management functions
export const tokenManager = {
  async getAccessToken(): Promise<string | null> {
    return await SecureStore.getItemAsync(ACCESS_TOKEN_KEY);
  },

  async getRefreshToken(): Promise<string | null> {
    return await SecureStore.getItemAsync(REFRESH_TOKEN_KEY);
  },

  async setTokens(accessToken: string, refreshToken: string): Promise<void> {
    await SecureStore.setItemAsync(ACCESS_TOKEN_KEY, accessToken);
    await SecureStore.setItemAsync(REFRESH_TOKEN_KEY, refreshToken);
  },

  async clearTokens(): Promise<void> {
    await SecureStore.deleteItemAsync(ACCESS_TOKEN_KEY);
    await SecureStore.deleteItemAsync(REFRESH_TOKEN_KEY);
  },
};

// Request interceptor - add JWT token
apiClient.interceptors.request.use(
  async (config) => {
    const token = await tokenManager.getAccessToken();
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
        const refreshToken = await tokenManager.getRefreshToken();
        if (!refreshToken) {
          console.warn('No refresh token available, logging out');
          await tokenManager.clearTokens();
          return Promise.reject(new Error('Session expired. Please login again.'));
        }

        const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        });

        const { access_token } = response.data;
        await tokenManager.setTokens(access_token, refreshToken);

        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
        await tokenManager.clearTokens();
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
