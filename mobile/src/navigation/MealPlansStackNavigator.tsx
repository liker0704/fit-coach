import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import { colors } from '../theme/colors';

// Import Meal Plans screens
import MealPlansScreen from '../screens/meal-plans/MealPlansScreen';
import CreateMealPlanScreen from '../screens/meal-plans/CreateMealPlanScreen';
import MealPlanDetailScreen from '../screens/meal-plans/MealPlanDetailScreen';

const Stack = createStackNavigator();

export default function MealPlansStackNavigator() {
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
      initialRouteName="MealPlans"
    >
      <Stack.Screen
        name="MealPlans"
        component={MealPlansScreen}
        options={{
          title: 'Meal Plans',
          headerShown: true,
        }}
      />
      <Stack.Screen
        name="CreateMealPlan"
        component={CreateMealPlanScreen}
        options={{
          title: 'Create Meal Plan',
          headerShown: true,
        }}
      />
      <Stack.Screen
        name="MealPlanDetail"
        component={MealPlanDetailScreen}
        options={{
          title: 'Meal Plan Details',
          headerShown: true,
        }}
      />
    </Stack.Navigator>
  );
}
