import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import CalendarStackNavigator from './CalendarStackNavigator';
import { colors } from '../theme/colors';
import { View, Text, StyleSheet } from 'react-native';
import { fontSizes } from '../theme/colors';

export type MainTabParamList = {
  CalendarTab: undefined;
  StatsTab: undefined;
  AITab: undefined;
  ProfileTab: undefined;
};

const Tab = createBottomTabNavigator<MainTabParamList>();

// Placeholder screens for tabs we haven't built yet
function PlaceholderScreen({ title }: { title: string }) {
  return (
    <View style={styles.placeholderContainer}>
      <MaterialCommunityIcons
        name="clock-outline"
        size={64}
        color={colors.textTertiary}
      />
      <Text style={styles.placeholderTitle}>{title}</Text>
      <Text style={styles.placeholderText}>
        Coming in Phase 3-6
      </Text>
    </View>
  );
}

const StatsScreen = () => <PlaceholderScreen title="Statistics" />;
const AIScreen = () => <PlaceholderScreen title="AI Agents" />;
const ProfileScreen = () => <PlaceholderScreen title="Profile" />;

export default function MainTabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={{
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.textSecondary,
        headerShown: false,
        tabBarStyle: {
          paddingBottom: 4,
          paddingTop: 4,
          height: 60,
        },
      }}
      initialRouteName="CalendarTab"
    >
      <Tab.Screen
        name="CalendarTab"
        component={CalendarStackNavigator}
        options={{
          title: 'Calendar',
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="calendar" size={size} color={color} />
          ),
        }}
      />
      <Tab.Screen
        name="StatsTab"
        component={StatsScreen}
        options={{
          title: 'Stats',
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="chart-line" size={size} color={color} />
          ),
          headerShown: true,
        }}
      />
      <Tab.Screen
        name="AITab"
        component={AIScreen}
        options={{
          title: 'AI Coach',
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="robot" size={size} color={color} />
          ),
          headerShown: true,
        }}
      />
      <Tab.Screen
        name="ProfileTab"
        component={ProfileScreen}
        options={{
          title: 'Profile',
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="account" size={size} color={color} />
          ),
          headerShown: true,
        }}
      />
    </Tab.Navigator>
  );
}

const styles = StyleSheet.create({
  placeholderContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
    padding: 24,
  },
  placeholderTitle: {
    fontSize: fontSizes.xxl,
    fontWeight: '700',
    color: colors.text,
    marginTop: 16,
  },
  placeholderText: {
    fontSize: fontSizes.md,
    color: colors.textSecondary,
    marginTop: 8,
    textAlign: 'center',
  },
});
