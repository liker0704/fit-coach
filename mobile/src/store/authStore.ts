import { create } from 'zustand';
import { authService, User } from '../services/api/authService';
import { tokenManager } from '../services/api/apiClient';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (email: string, password: string) => Promise<void>;
  register: (fullName: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  loadUser: () => Promise<void>;
  clearError: () => void;
  checkAuth: () => Promise<boolean>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  /**
   * Login user
   */
  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      await authService.login(email, password);
      const user = await authService.getCurrentUser();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Login failed';
      set({ error: errorMessage, isLoading: false, isAuthenticated: false });
      throw error;
    }
  },

  /**
   * Register new user
   */
  register: async (fullName: string, email: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      await authService.register({ full_name: fullName, email, password });
      const user = await authService.getCurrentUser();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Registration failed';
      set({ error: errorMessage, isLoading: false, isAuthenticated: false });
      throw error;
    }
  },

  /**
   * Logout user
   */
  logout: async () => {
    set({ isLoading: true });
    try {
      await authService.logout();
      set({ user: null, isAuthenticated: false, isLoading: false, error: null });
    } catch (error) {
      console.error('Logout error:', error);
      // Force logout even if API call fails
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },

  /**
   * Load current user profile
   */
  loadUser: async () => {
    set({ isLoading: true, error: null });
    try {
      const user = await authService.getCurrentUser();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load user';
      set({ error: errorMessage, isLoading: false, isAuthenticated: false });
      throw error;
    }
  },

  /**
   * Clear error message
   */
  clearError: () => {
    set({ error: null });
  },

  /**
   * Check if user is authenticated on app launch
   */
  checkAuth: async () => {
    const token = await tokenManager.getAccessToken();
    if (token) {
      try {
        const user = await authService.getCurrentUser();
        set({ user, isAuthenticated: true });
        return true;
      } catch (error) {
        console.error('Auth check failed:', error);
        await tokenManager.clearTokens();
        set({ user: null, isAuthenticated: false });
        return false;
      }
    }
    set({ isAuthenticated: false });
    return false;
  },
}));
