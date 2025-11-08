import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Text, Button } from 'react-native-paper';
import { useAuthStore } from '../../store/authStore';
import { colors, spacing, fontSizes } from '../../theme/colors';

export default function CalendarScreen() {
  const { user, logout } = useAuthStore();

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>Calendar</Text>
        <Text style={styles.subtitle}>Welcome, {user?.full_name || 'User'}!</Text>
        <Text style={styles.email}>{user?.email}</Text>

        <Text style={styles.placeholder}>
          Calendar view will be implemented here.
          This will show a monthly calendar grid with days that have logged data.
        </Text>

        <Button
          mode="outlined"
          onPress={logout}
          style={styles.logoutButton}
        >
          Logout
        </Button>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    flex: 1,
    padding: spacing.lg,
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    fontSize: fontSizes.xxxl,
    fontWeight: '700',
    color: colors.text,
    marginBottom: spacing.sm,
  },
  subtitle: {
    fontSize: fontSizes.lg,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  email: {
    fontSize: fontSizes.md,
    color: colors.textTertiary,
    marginBottom: spacing.xl,
  },
  placeholder: {
    fontSize: fontSizes.md,
    color: colors.textSecondary,
    textAlign: 'center',
    marginBottom: spacing.xl,
    paddingHorizontal: spacing.lg,
  },
  logoutButton: {
    marginTop: spacing.lg,
  },
});
