import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import { colors } from '../theme/colors';

// Import Training screens
import ProgramsScreen from '../screens/training/ProgramsScreen';
import CreateProgramScreen from '../screens/training/CreateProgramScreen';
import ProgramDetailScreen from '../screens/training/ProgramDetailScreen';

const Stack = createStackNavigator();

export default function TrainingStackNavigator() {
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
      initialRouteName="Programs"
    >
      <Stack.Screen
        name="Programs"
        component={ProgramsScreen}
        options={{
          title: 'Training Programs',
          headerShown: true,
        }}
      />
      <Stack.Screen
        name="CreateProgram"
        component={CreateProgramScreen}
        options={{
          title: 'Create Program',
          headerShown: true,
        }}
      />
      <Stack.Screen
        name="ProgramDetail"
        component={ProgramDetailScreen}
        options={{
          title: 'Program Details',
          headerShown: true,
        }}
      />
    </Stack.Navigator>
  );
}
