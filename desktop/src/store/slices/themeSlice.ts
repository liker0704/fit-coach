import { StateCreator } from 'zustand';

export type Theme = 'light' | 'dark' | 'system';

export interface ThemeSlice {
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

export const createThemeSlice: StateCreator<ThemeSlice> = (set) => ({
  theme: 'system',

  setTheme: (theme: Theme) => {
    set({ theme });
  },
});
