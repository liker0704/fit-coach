import { useEffect } from 'react';
import { useStore } from '@/store';

const applyThemeToDOM = (theme: 'light' | 'dark' | 'system') => {
  const root = document.documentElement;

  if (theme === 'dark') {
    root.classList.add('dark');
  } else if (theme === 'light') {
    root.classList.remove('dark');
  } else {
    // System preference
    const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (isDark) {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }
};

export const ThemeProvider = ({ children }: { children: React.ReactNode }) => {
  const theme = useStore(state => state.theme);

  useEffect(() => {
    // Apply theme when it changes
    applyThemeToDOM(theme);
  }, [theme]);

  useEffect(() => {
    // Listen for system theme changes (only if theme is 'system')
    if (theme !== 'system') return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = () => {
      applyThemeToDOM('system');
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [theme]);

  return <>{children}</>;
};
