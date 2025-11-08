export const colors = {
  primary: '#3B82F6', // blue-500
  primaryDark: '#2563EB', // blue-600
  primaryLight: '#60A5FA', // blue-400

  secondary: '#10B981', // green-500
  secondaryDark: '#059669', // green-600
  secondaryLight: '#34D399', // green-400

  error: '#EF4444', // red-500
  errorDark: '#DC2626', // red-600
  errorLight: '#F87171', // red-400

  warning: '#F59E0B', // amber-500
  success: '#10B981', // green-500
  info: '#3B82F6', // blue-500

  background: '#FFFFFF',
  backgroundSecondary: '#F9FAFB', // gray-50
  backgroundTertiary: '#F3F4F6', // gray-100

  text: '#111827', // gray-900
  textSecondary: '#6B7280', // gray-500
  textTertiary: '#9CA3AF', // gray-400

  border: '#E5E7EB', // gray-200
  borderDark: '#D1D5DB', // gray-300

  // Chart colors
  chart: {
    blue: '#3B82F6',
    green: '#10B981',
    yellow: '#F59E0B',
    purple: '#8B5CF6',
    pink: '#EC4899',
    orange: '#F97316',
  },
};

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

export const borderRadius = {
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  full: 9999,
};

export const fontSizes = {
  xs: 12,
  sm: 14,
  md: 16,
  lg: 18,
  xl: 20,
  xxl: 24,
  xxxl: 30,
};

export const fontWeights = {
  normal: '400' as const,
  medium: '500' as const,
  semibold: '600' as const,
  bold: '700' as const,
};
