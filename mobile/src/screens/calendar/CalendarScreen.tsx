import React, { useState, useEffect, useCallback } from 'react';
import { View, StyleSheet, ScrollView, RefreshControl } from 'react-native';
import { Calendar, DateData } from 'react-native-calendars';
import { Text, Button, ActivityIndicator } from 'react-native-paper';
import { useAuthStore } from '../../store/authStore';
import { dayService } from '../../services/api/dayService';
import { colors, spacing, fontSizes } from '../../theme/colors';
import type { Day } from '../../types/models/health';

export default function CalendarScreen({ navigation }: any) {
  const { user, logout } = useAuthStore();
  const [selectedDate, setSelectedDate] = useState('');
  const [markedDates, setMarkedDates] = useState<any>({});
  const [days, setDays] = useState<Day[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Get current month range
  const getCurrentMonthRange = () => {
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth();
    const startDate = new Date(year, month, 1);
    const endDate = new Date(year, month + 1, 0);

    return {
      start: startDate.toISOString().split('T')[0],
      end: endDate.toISOString().split('T')[0],
    };
  };

  // Load days for current month
  const loadDays = useCallback(async () => {
    setIsLoading(true);
    try {
      const { start, end } = getCurrentMonthRange();
      const fetchedDays = await dayService.getDays(start, end);
      setDays(fetchedDays);

      // Mark dates that have data
      const marked: any = {};
      fetchedDays.forEach((day) => {
        marked[day.date] = {
          marked: true,
          dotColor: colors.primary,
        };
      });

      // Add selected date
      if (selectedDate) {
        marked[selectedDate] = {
          ...marked[selectedDate],
          selected: true,
          selectedColor: colors.primary,
        };
      }

      setMarkedDates(marked);
    } catch (error) {
      console.error('Failed to load days:', error);
    } finally {
      setIsLoading(false);
    }
  }, [selectedDate]);

  // Refresh handler
  const handleRefresh = async () => {
    setIsRefreshing(true);
    await loadDays();
    setIsRefreshing(false);
  };

  // Load days on mount
  useEffect(() => {
    loadDays();
  }, [loadDays]);

  // Handle day selection
  const handleDayPress = (day: DateData) => {
    setSelectedDate(day.dateString);

    // Update marked dates with new selection
    const marked = { ...markedDates };
    Object.keys(marked).forEach((date) => {
      marked[date] = {
        ...marked[date],
        selected: date === day.dateString,
        selectedColor: date === day.dateString ? colors.primary : undefined,
      };
    });

    // If date not marked yet, add it
    if (!marked[day.dateString]) {
      marked[day.dateString] = {
        selected: true,
        selectedColor: colors.primary,
      };
    }

    setMarkedDates(marked);

    // Navigate to DayScreen
    navigation.navigate('DayScreen', { date: day.dateString });
  };

  // Handle month change
  const handleMonthChange = (month: DateData) => {
    console.log('Month changed to:', month.dateString);
    // TODO: Load days for new month
  };

  if (isLoading && days.length === 0) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Loading calendar...</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
      }
    >
      <View style={styles.content}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.greeting}>Hello, {user?.full_name || 'User'}!</Text>
          <Text style={styles.subtitle}>Track your health journey</Text>
        </View>

        {/* Calendar */}
        <Calendar
          current={new Date().toISOString().split('T')[0]}
          onDayPress={handleDayPress}
          onMonthChange={handleMonthChange}
          markedDates={markedDates}
          theme={{
            backgroundColor: colors.background,
            calendarBackground: colors.background,
            textSectionTitleColor: colors.textSecondary,
            selectedDayBackgroundColor: colors.primary,
            selectedDayTextColor: colors.background,
            todayTextColor: colors.primary,
            dayTextColor: colors.text,
            textDisabledColor: colors.textTertiary,
            dotColor: colors.primary,
            selectedDotColor: colors.background,
            arrowColor: colors.primary,
            monthTextColor: colors.text,
            textDayFontSize: fontSizes.md,
            textMonthFontSize: fontSizes.lg,
            textDayHeaderFontSize: fontSizes.sm,
          }}
          style={styles.calendar}
        />

        {/* Quick Stats */}
        <View style={styles.statsContainer}>
          <Text style={styles.statsTitle}>This Month</Text>
          <View style={styles.statsGrid}>
            <View style={styles.statCard}>
              <Text style={styles.statNumber}>{days.length}</Text>
              <Text style={styles.statLabel}>Days Logged</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statNumber}>
                {days.filter((d) => d.effort_score !== null).length}
              </Text>
              <Text style={styles.statLabel}>Effort Tracked</Text>
            </View>
          </View>
        </View>

        {/* Logout Button */}
        <Button
          mode="outlined"
          onPress={logout}
          style={styles.logoutButton}
          icon="logout"
        >
          Logout
        </Button>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
  },
  loadingText: {
    marginTop: spacing.md,
    fontSize: fontSizes.md,
    color: colors.textSecondary,
  },
  content: {
    padding: spacing.lg,
  },
  header: {
    marginBottom: spacing.lg,
  },
  greeting: {
    fontSize: fontSizes.xxl,
    fontWeight: '700',
    color: colors.text,
  },
  subtitle: {
    fontSize: fontSizes.md,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  calendar: {
    marginBottom: spacing.lg,
    borderRadius: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  statsContainer: {
    marginBottom: spacing.xl,
  },
  statsTitle: {
    fontSize: fontSizes.lg,
    fontWeight: '600',
    color: colors.text,
    marginBottom: spacing.md,
  },
  statsGrid: {
    flexDirection: 'row',
    gap: spacing.md,
  },
  statCard: {
    flex: 1,
    backgroundColor: colors.backgroundSecondary,
    padding: spacing.lg,
    borderRadius: 12,
    alignItems: 'center',
  },
  statNumber: {
    fontSize: fontSizes.xxxl,
    fontWeight: '700',
    color: colors.primary,
  },
  statLabel: {
    fontSize: fontSizes.sm,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  logoutButton: {
    marginTop: spacing.md,
  },
});
