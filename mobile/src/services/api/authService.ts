import { apiClient, tokenManager } from './apiClient';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  full_name: string;
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  age?: number;
  gender?: string;
  height?: number;
  weight?: number;
  activity_level?: string;
  goal?: string;
}

export const authService = {
  /**
   * Login user with email and password
   */
  async login(email: string, password: string): Promise<AuthResponse> {
    // FastAPI OAuth2 expects form data with username field
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await apiClient.post<AuthResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    // Store tokens securely
    await tokenManager.setTokens(response.data.access_token, response.data.refresh_token);

    return response.data;
  },

  /**
   * Register new user
   */
  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/register', data);

    // Store tokens securely
    await tokenManager.setTokens(response.data.access_token, response.data.refresh_token);

    return response.data;
  },

  /**
   * Logout user - clear tokens
   */
  async logout(): Promise<void> {
    await tokenManager.clearTokens();
  },

  /**
   * Get current user profile
   */
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/users/me');
    return response.data;
  },

  /**
   * Update user profile
   */
  async updateProfile(data: Partial<User>): Promise<User> {
    const response = await apiClient.put<User>('/users/me', data);
    return response.data;
  },

  /**
   * Check if user is authenticated (has valid access token)
   */
  async isAuthenticated(): Promise<boolean> {
    const token = await tokenManager.getAccessToken();
    return token !== null;
  },
};
