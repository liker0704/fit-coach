import { authService } from '../authService';
import { apiClient, tokenManager } from '../apiClient';
import type { AuthResponse, User, RegisterRequest } from '../authService';

jest.mock('../apiClient');

const mockedApiClient = apiClient as jest.Mocked<typeof apiClient>;
const mockedTokenManager = tokenManager as jest.Mocked<typeof tokenManager>;

describe('authService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('login', () => {
    it('should login with email and password successfully', async () => {
      const mockResponse: AuthResponse = {
        access_token: 'mock-access-token',
        refresh_token: 'mock-refresh-token',
        token_type: 'bearer',
      };

      mockedApiClient.post.mockResolvedValueOnce({ data: mockResponse });
      mockedTokenManager.setTokens.mockResolvedValueOnce();

      const result = await authService.login('test@example.com', 'password123');

      expect(mockedApiClient.post).toHaveBeenCalledWith(
        '/auth/login',
        expect.any(URLSearchParams),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );
      expect(mockedTokenManager.setTokens).toHaveBeenCalledWith(
        'mock-access-token',
        'mock-refresh-token'
      );
      expect(result).toEqual(mockResponse);
    });

    it('should throw error on failed login', async () => {
      mockedApiClient.post.mockRejectedValueOnce(new Error('Invalid credentials'));

      await expect(authService.login('test@example.com', 'wrong')).rejects.toThrow(
        'Invalid credentials'
      );
    });

    it('should format form data correctly for OAuth2', async () => {
      const mockResponse: AuthResponse = {
        access_token: 'token',
        refresh_token: 'refresh',
        token_type: 'bearer',
      };

      mockedApiClient.post.mockResolvedValueOnce({ data: mockResponse });

      await authService.login('user@test.com', 'pass');

      const callArgs = mockedApiClient.post.mock.calls[0];
      const formData = callArgs[1] as URLSearchParams;

      expect(formData.get('username')).toBe('user@test.com');
      expect(formData.get('password')).toBe('pass');
    });
  });

  describe('register', () => {
    it('should register new user successfully', async () => {
      const mockRequest: RegisterRequest = {
        full_name: 'John Doe',
        email: 'john@example.com',
        password: 'password123',
      };

      const mockResponse: AuthResponse = {
        access_token: 'new-access-token',
        refresh_token: 'new-refresh-token',
        token_type: 'bearer',
      };

      mockedApiClient.post.mockResolvedValueOnce({ data: mockResponse });
      mockedTokenManager.setTokens.mockResolvedValueOnce();

      const result = await authService.register(mockRequest);

      expect(mockedApiClient.post).toHaveBeenCalledWith('/auth/register', mockRequest);
      expect(mockedTokenManager.setTokens).toHaveBeenCalledWith(
        'new-access-token',
        'new-refresh-token'
      );
      expect(result).toEqual(mockResponse);
    });

    it('should throw error when email already exists', async () => {
      const mockRequest: RegisterRequest = {
        full_name: 'Jane Doe',
        email: 'existing@example.com',
        password: 'password123',
      };

      mockedApiClient.post.mockRejectedValueOnce(
        new Error('Email already registered')
      );

      await expect(authService.register(mockRequest)).rejects.toThrow(
        'Email already registered'
      );
    });
  });

  describe('logout', () => {
    it('should clear tokens on logout', async () => {
      mockedTokenManager.clearTokens.mockResolvedValueOnce();

      await authService.logout();

      expect(mockedTokenManager.clearTokens).toHaveBeenCalled();
    });
  });

  describe('getCurrentUser', () => {
    it('should get current user profile', async () => {
      const mockUser: User = {
        id: 1,
        email: 'test@example.com',
        full_name: 'Test User',
        age: 25,
        gender: 'male',
        height: 180,
        weight: 75,
        activity_level: 'moderate',
        goal: 'maintain',
      };

      mockedApiClient.get.mockResolvedValueOnce({ data: mockUser });

      const result = await authService.getCurrentUser();

      expect(mockedApiClient.get).toHaveBeenCalledWith('/users/me');
      expect(result).toEqual(mockUser);
    });

    it('should throw error when user not authenticated', async () => {
      mockedApiClient.get.mockRejectedValueOnce(new Error('Unauthorized'));

      await expect(authService.getCurrentUser()).rejects.toThrow('Unauthorized');
    });
  });

  describe('updateProfile', () => {
    it('should update user profile successfully', async () => {
      const updateData: Partial<User> = {
        age: 26,
        weight: 76,
        height: 180,
      };

      const mockUpdatedUser: User = {
        id: 1,
        email: 'test@example.com',
        full_name: 'Test User',
        age: 26,
        weight: 76,
        height: 180,
      };

      mockedApiClient.put.mockResolvedValueOnce({ data: mockUpdatedUser });

      const result = await authService.updateProfile(updateData);

      expect(mockedApiClient.put).toHaveBeenCalledWith('/users/me', updateData);
      expect(result).toEqual(mockUpdatedUser);
    });

    it('should update partial profile data', async () => {
      const updateData: Partial<User> = {
        goal: 'lose_weight',
      };

      const mockUser: User = {
        id: 1,
        email: 'test@example.com',
        full_name: 'Test User',
        goal: 'lose_weight',
      };

      mockedApiClient.put.mockResolvedValueOnce({ data: mockUser });

      const result = await authService.updateProfile(updateData);

      expect(result.goal).toBe('lose_weight');
    });
  });

  describe('isAuthenticated', () => {
    it('should return true when access token exists', async () => {
      mockedTokenManager.getAccessToken.mockResolvedValueOnce('valid-token');

      const result = await authService.isAuthenticated();

      expect(result).toBe(true);
      expect(mockedTokenManager.getAccessToken).toHaveBeenCalled();
    });

    it('should return false when no access token', async () => {
      mockedTokenManager.getAccessToken.mockResolvedValueOnce(null);

      const result = await authService.isAuthenticated();

      expect(result).toBe(false);
    });
  });
});
