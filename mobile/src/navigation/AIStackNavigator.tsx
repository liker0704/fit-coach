import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import { colors } from '../theme/colors';

// Import AI screens
import ChatbotScreen from '../screens/ai/ChatbotScreen';
import VisionScreen from '../screens/ai/VisionScreen';
import CoachesScreen from '../screens/ai/CoachesScreen';

const Stack = createStackNavigator();

export default function AIStackNavigator() {
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
      initialRouteName="Chatbot"
    >
      <Stack.Screen
        name="Chatbot"
        component={ChatbotScreen}
        options={{
          title: 'AI Chatbot',
          headerShown: true,
        }}
      />
      <Stack.Screen
        name="Vision"
        component={VisionScreen}
        options={{
          title: 'Vision Agent',
          headerShown: true,
        }}
      />
      <Stack.Screen
        name="Coaches"
        component={CoachesScreen}
        options={{
          title: 'AI Coaches',
          headerShown: true,
        }}
      />
    </Stack.Navigator>
  );
}
