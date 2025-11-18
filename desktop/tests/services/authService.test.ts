import { authService } from '@/services/modules/authService';
import { apiClient } from '@/services/api/client';
import type { LoginRequest, LoginResponse, RegisterRequest, User } from '@/types/api/auth';

// Mock the API client
jest.mock('@/services/api/client', () => ({
  apiClient: {
    post: jest.fn(),
  },
}));

describe('authService', () => {
  const mockApiClient = apiClient as jest.Mocked<typeof apiClient>;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('login', () => {
    it('should successfully login with valid credentials', async () => {
      const loginRequest: LoginRequest = {
        email: 'test@example.com',
        password: 'password123',
      };

      const mockResponse: LoginResponse = {
        access_token: 'mock-access-token',
        refresh_token: 'mock-refresh-token',
        user: {
          id: 1,
          email: 'test@example.com',
          username: 'testuser',
          full_name: 'Test User',
          created_at: '2024-01-01T00:00:00Z',
        },
      };

      mockApiClient.post.mockResolvedValueOnce({ data: mockResponse });

      const result = await authService.login(loginRequest);

      expect(mockApiClient.post).toHaveBeenCalledWith('/auth/login', loginRequest);
      expect(result).toEqual(mockResponse);
    });

    it('should throw error on invalid credentials', async () => {
      const loginRequest: LoginRequest = {
        email: 'invalid@example.com',
        password: 'wrongpassword',
      };

      mockApiClient.post.mockRejectedValueOnce(new Error('Invalid credentials'));

      await expect(authService.login(loginRequest)).rejects.toThrow('Invalid credentials');
      expect(mockApiClient.post).toHaveBeenCalledWith('/auth/login', loginRequest);
    });

    it('should handle network errors', async () => {
      const loginRequest: LoginRequest = {
        email: 'test@example.com',
        password: 'password123',
      };

      mockApiClient.post.mockRejectedValueOnce(new Error('Network error'));

      await expect(authService.login(loginRequest)).rejects.toThrow('Network error');
    });
  });

  describe('register', () => {
    it('should successfully register a new user', async () => {
      const registerRequest: RegisterRequest = {
        email: 'newuser@example.com',
        password: 'password123',
        username: 'newuser',
        full_name: 'New User',
      };

      const mockUser: User = {
        id: 2,
        email: 'newuser@example.com',
        username: 'newuser',
        full_name: 'New User',
        created_at: '2024-01-01T00:00:00Z',
      };

      mockApiClient.post.mockResolvedValueOnce({ data: mockUser });

      const result = await authService.register(registerRequest);

      expect(mockApiClient.post).toHaveBeenCalledWith('/auth/register', registerRequest);
      expect(result).toEqual(mockUser);
    });

    it('should throw error when email already exists', async () => {
      const registerRequest: RegisterRequest = {
        email: 'existing@example.com',
        password: 'password123',
        username: 'existinguser',
        full_name: 'Existing User',
      };

      mockApiClient.post.mockRejectedValueOnce(new Error('Email already exists'));

      await expect(authService.register(registerRequest)).rejects.toThrow('Email already exists');
      expect(mockApiClient.post).toHaveBeenCalledWith('/auth/register', registerRequest);
    });

    it('should validate required fields', async () => {
      const registerRequest: RegisterRequest = {
        email: '',
        password: '',
        username: '',
      };

      mockApiClient.post.mockRejectedValueOnce(new Error('Validation error'));

      await expect(authService.register(registerRequest)).rejects.toThrow('Validation error');
    });
  });

  describe('logout', () => {
    it('should successfully logout', async () => {
      mockApiClient.post.mockResolvedValueOnce({ data: undefined });

      await authService.logout();

      expect(mockApiClient.post).toHaveBeenCalledWith('/auth/logout');
    });

    it('should handle logout errors gracefully', async () => {
      mockApiClient.post.mockRejectedValueOnce(new Error('Logout failed'));

      await expect(authService.logout()).rejects.toThrow('Logout failed');
    });
  });

  describe('refreshToken', () => {
    it('should successfully refresh access token', async () => {
      const refreshToken = 'mock-refresh-token';
      const mockResponse = { access_token: 'new-access-token' };

      mockApiClient.post.mockResolvedValueOnce({ data: mockResponse });

      const result = await authService.refreshToken(refreshToken);

      expect(mockApiClient.post).toHaveBeenCalledWith('/auth/refresh', {
        refresh_token: refreshToken,
      });
      expect(result).toEqual(mockResponse);
    });

    it('should throw error on invalid refresh token', async () => {
      const refreshToken = 'invalid-token';

      mockApiClient.post.mockRejectedValueOnce(new Error('Invalid refresh token'));

      await expect(authService.refreshToken(refreshToken)).rejects.toThrow(
        'Invalid refresh token'
      );
    });

    it('should throw error when refresh token is expired', async () => {
      const refreshToken = 'expired-token';

      mockApiClient.post.mockRejectedValueOnce(new Error('Token expired'));

      await expect(authService.refreshToken(refreshToken)).rejects.toThrow('Token expired');
    });
  });
});
