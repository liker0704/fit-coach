import React, { useEffect, useState } from 'react';
import { View, StyleSheet, ScrollView, Dimensions } from 'react-native';
import { TabView, SceneMap, TabBar } from 'react-native-tab-view';
import { ActivityIndicator, Text } from 'react-native-paper';
import { useDayStore } from '../../store/dayStore';
import { colors, spacing, fontSizes } from '../../theme/colors';

// Import tab screens
import OverviewTab from './tabs/OverviewTab';
import MealsTab from './tabs/MealsTab';
import ExerciseTab from './tabs/ExerciseTab';
import WaterTab from './tabs/WaterTab';
import SleepTab from './tabs/SleepTab';
import MoodTab from './tabs/MoodTab';
import NotesTab from './tabs/NotesTab';

const initialLayout = { width: Dimensions.get('window').width };

export default function DayScreen({ route }: any) {
  const { date } = route.params;
  const { currentDay, isLoading, loadDay } = useDayStore();

  const [index, setIndex] = useState(0);
  const [routes] = useState([
    { key: 'overview', title: 'Overview' },
    { key: 'meals', title: 'Meals' },
    { key: 'exercise', title: 'Exercise' },
    { key: 'water', title: 'Water' },
    { key: 'sleep', title: 'Sleep' },
    { key: 'mood', title: 'Mood' },
    { key: 'notes', title: 'Notes' },
  ]);

  // Load day data on mount
  useEffect(() => {
    loadDay(date);
  }, [date, loadDay]);

  // Render scene
  const renderScene = SceneMap({
    overview: OverviewTab,
    meals: MealsTab,
    exercise: ExerciseTab,
    water: WaterTab,
    sleep: SleepTab,
    mood: MoodTab,
    notes: NotesTab,
  });

  // Custom tab bar
  const renderTabBar = (props: any) => (
    <TabBar
      {...props}
      scrollEnabled
      indicatorStyle={styles.tabIndicator}
      style={styles.tabBar}
      labelStyle={styles.tabLabel}
      activeColor={colors.primary}
      inactiveColor={colors.textSecondary}
      tabStyle={styles.tab}
    />
  );

  if (isLoading && !currentDay) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Loading day...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <TabView
        navigationState={{ index, routes }}
        renderScene={renderScene}
        onIndexChange={setIndex}
        initialLayout={initialLayout}
        renderTabBar={renderTabBar}
      />
    </View>
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
  tabBar: {
    backgroundColor: colors.background,
    elevation: 0,
    shadowOpacity: 0,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  tab: {
    width: 'auto',
    minWidth: 80,
  },
  tabIndicator: {
    backgroundColor: colors.primary,
    height: 3,
  },
  tabLabel: {
    fontSize: fontSizes.sm,
    fontWeight: '600',
    textTransform: 'none',
  },
});
