import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import CalendarScreen from '../screens/calendar/CalendarScreen';
import DayScreen from '../screens/calendar/DayScreen';
import { colors } from '../theme/colors';

export type CalendarStackParamList = {
  CalendarMain: undefined;
  DayScreen: { date: string };
};

const Stack = createStackNavigator<CalendarStackParamList>();

export default function CalendarStackNavigator() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: {
          backgroundColor: colors.primary,
        },
        headerTintColor: colors.background,
        headerTitleStyle: {
          fontWeight: '600',
        },
      }}
    >
      <Stack.Screen
        name="CalendarMain"
        component={CalendarScreen}
        options={{ title: 'Calendar', headerShown: false }}
      />
      <Stack.Screen
        name="DayScreen"
        component={DayScreen}
        options={({ route }) => ({
          title: route.params.date,
        })}
      />
    </Stack.Navigator>
  );
}
