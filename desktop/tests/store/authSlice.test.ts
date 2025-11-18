import { create } from 'zustand';
import { createAuthSlice, AuthSlice } from '@/store/slices/authSlice';
import type { User } from '@/types/api/auth';

describe('authSlice', () => {
  let useAuthStore: ReturnType<typeof create<AuthSlice>>;

  beforeEach(() => {
    // Create a fresh store for each test
    useAuthStore = create<AuthSlice>()(createAuthSlice);
  });

  describe('initial state', () => {
    it('should have correct initial values', () => {
      const state = useAuthStore.getState();

      expect(state.user).toBeNull();
      expect(state.accessToken).toBeNull();
      expect(state.refreshToken).toBeNull();
      expect(state.isAuthenticated).toBe(false);
    });
  });

  describe('setUser', () => {
    it('should set user and mark as authenticated', () => {
      const mockUser: User = {
        id: 1,
        email: 'test@example.com',
        username: 'testuser',
        full_name: 'Test User',
        created_at: '2024-01-01T00:00:00Z',
      };

      useAuthStore.getState().setUser(mockUser);

      const state = useAuthStore.getState();
      expect(state.user).toEqual(mockUser);
      expect(state.isAuthenticated).toBe(true);
    });

    it('should replace existing user', () => {
      const user1: User = {
        id: 1,
        email: 'user1@example.com',
        username: 'user1',
        created_at: '2024-01-01T00:00:00Z',
      };

      const user2: User = {
        id: 2,
        email: 'user2@example.com',
        username: 'user2',
        created_at: '2024-01-02T00:00:00Z',
      };

      useAuthStore.getState().setUser(user1);
      useAuthStore.getState().setUser(user2);

      const state = useAuthStore.getState();
      expect(state.user).toEqual(user2);
      expect(state.user?.id).toBe(2);
    });
  });

  describe('setTokens', () => {
    it('should set access and refresh tokens', () => {
      const accessToken = 'mock-access-token';
      const refreshToken = 'mock-refresh-token';

      useAuthStore.getState().setTokens(accessToken, refreshToken);

      const state = useAuthStore.getState();
      expect(state.accessToken).toBe(accessToken);
      expect(state.refreshToken).toBe(refreshToken);
    });

    it('should update tokens when called multiple times', () => {
      useAuthStore.getState().setTokens('old-access', 'old-refresh');
      useAuthStore.getState().setTokens('new-access', 'new-refresh');

      const state = useAuthStore.getState();
      expect(state.accessToken).toBe('new-access');
      expect(state.refreshToken).toBe('new-refresh');
    });

    it('should not affect authentication status', () => {
      const { setTokens } = useAuthStore.getState();

      setTokens('access', 'refresh');

      const state = useAuthStore.getState();
      expect(state.isAuthenticated).toBe(false);
    });
  });

  describe('logout', () => {
    it('should clear all auth state', () => {
      const mockUser: User = {
        id: 1,
        email: 'test@example.com',
        username: 'testuser',
        created_at: '2024-01-01T00:00:00Z',
      };

      // Set up authenticated state
      useAuthStore.getState().setUser(mockUser);
      useAuthStore.getState().setTokens('access-token', 'refresh-token');

      // Verify state is set
      expect(useAuthStore.getState().isAuthenticated).toBe(true);

      // Logout
      useAuthStore.getState().logout();

      // Verify state is cleared
      const state = useAuthStore.getState();
      expect(state.user).toBeNull();
      expect(state.accessToken).toBeNull();
      expect(state.refreshToken).toBeNull();
      expect(state.isAuthenticated).toBe(false);
    });

    it('should be safe to call when already logged out', () => {
      useAuthStore.getState().logout();

      const state = useAuthStore.getState();
      expect(state.user).toBeNull();
      expect(state.isAuthenticated).toBe(false);
    });
  });

  describe('complete authentication flow', () => {
    it('should handle full login flow', () => {
      const mockUser: User = {
        id: 1,
        email: 'test@example.com',
        username: 'testuser',
        full_name: 'Test User',
        created_at: '2024-01-01T00:00:00Z',
      };

      // Initial state
      expect(useAuthStore.getState().isAuthenticated).toBe(false);

      // Login
      useAuthStore.getState().setUser(mockUser);
      useAuthStore.getState().setTokens('access', 'refresh');

      // Verify authenticated state
      let state = useAuthStore.getState();
      expect(state.user).toEqual(mockUser);
      expect(state.accessToken).toBe('access');
      expect(state.refreshToken).toBe('refresh');
      expect(state.isAuthenticated).toBe(true);

      // Logout
      useAuthStore.getState().logout();

      // Verify logged out
      state = useAuthStore.getState();
      expect(state.isAuthenticated).toBe(false);
      expect(state.user).toBeNull();
    });

    it('should handle token refresh', () => {
      const mockUser: User = {
        id: 1,
        email: 'test@example.com',
        username: 'testuser',
        created_at: '2024-01-01T00:00:00Z',
      };

      // Initial login
      useAuthStore.getState().setUser(mockUser);
      useAuthStore.getState().setTokens('old-access', 'refresh-token');

      // Refresh access token
      useAuthStore.getState().setTokens('new-access', 'refresh-token');

      const state = useAuthStore.getState();
      expect(state.accessToken).toBe('new-access');
      expect(state.refreshToken).toBe('refresh-token');
      expect(state.isAuthenticated).toBe(true);
      expect(state.user).toEqual(mockUser);
    });
  });
});
