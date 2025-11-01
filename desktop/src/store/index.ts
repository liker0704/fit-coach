import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { createAuthSlice, AuthSlice } from './slices/authSlice';
import { createHealthSlice, HealthSlice } from './slices/healthSlice';
import { createThemeSlice, ThemeSlice } from './slices/themeSlice';

type StoreState = AuthSlice & HealthSlice & ThemeSlice;

export const useStore = create<StoreState>()(
  persist(
    (...a) => ({
      ...createAuthSlice(...a),
      ...createHealthSlice(...a),
      ...createThemeSlice(...a),
    }),
    {
      name: 'fitcoach-storage',
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
        theme: state.theme,
      }),
    }
  )
);
