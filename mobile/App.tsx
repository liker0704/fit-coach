import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { PaperProvider } from 'react-native-paper';
import AppNavigator from './src/navigation/AppNavigator';
import { colors } from './src/theme/colors';

export default function App() {
  return (
    <PaperProvider
      theme={{
        colors: {
          primary: colors.primary,
          secondary: colors.secondary,
          error: colors.error,
          background: colors.background,
          surface: colors.backgroundSecondary,
          text: colors.text,
        },
      }}
    >
      <AppNavigator />
      <StatusBar style="auto" />
    </PaperProvider>
  );
}
