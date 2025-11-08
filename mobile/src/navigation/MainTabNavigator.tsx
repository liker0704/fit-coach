import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import CalendarScreen from '../screens/calendar/CalendarScreen';
import { colors } from '../theme/colors';

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
    <div style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <p style={{ fontSize: 24, fontWeight: '700' }}>{title}</p>
      <p style={{ color: colors.textSecondary, marginTop: 8 }}>
        This screen will be implemented in Phase 2-4
      </p>
    </div>
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
        headerShown: true,
      }}
      initialRouteName="CalendarTab"
    >
      <Tab.Screen
        name="CalendarTab"
        component={CalendarScreen}
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
        }}
      />
    </Tab.Navigator>
  );
}
