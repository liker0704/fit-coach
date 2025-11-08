import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import {
  Text,
  Card,
  ActivityIndicator,
  Chip,
  List,
  Divider,
} from 'react-native-paper';
import { useRoute, RouteProp } from '@react-navigation/native';
import { colors, spacing, fontSizes } from '../../theme/colors';
import {
  mealPlanService,
  type MealPlan,
  type DayMeals,
  type MealItem,
} from '../../services/api/mealPlanService';

type RouteParams = {
  params: {
    planId: number;
  };
};

const DAYS_OF_WEEK = [
  'monday',
  'tuesday',
  'wednesday',
  'thursday',
  'friday',
  'saturday',
  'sunday',
] as const;

const MEAL_CATEGORIES = [
  { key: 'breakfast', label: 'Breakfast', icon: 'coffee' },
  { key: 'lunch', label: 'Lunch', icon: 'food' },
  { key: 'dinner', label: 'Dinner', icon: 'food-variant' },
  { key: 'snacks', label: 'Snacks', icon: 'food-apple' },
] as const;

export default function MealPlanDetailScreen() {
  const route = useRoute<RouteProp<RouteParams, 'params'>>();
  const { planId } = route.params;
  const [mealPlan, setMealPlan] = useState<MealPlan | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [expandedDay, setExpandedDay] = useState<string | null>('monday');

  useEffect(() => {
    loadMealPlan();
  }, [planId]);

  const loadMealPlan = async () => {
    try {
      const plan = await mealPlanService.get(planId);
      setMealPlan(plan);
    } catch (error) {
      console.error('Error loading meal plan:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const renderMealItems = (items: MealItem[]) => {
    return items.map((item, index) => (
      <View key={index} style={styles.mealItem}>
        <View style={styles.mealItemHeader}>
          <Text style={styles.mealItemName}>{item.name}</Text>
          <Text style={styles.mealItemCalories}>{item.calories} kcal</Text>
        </View>
        <Text style={styles.mealItemPortion}>{item.portion_size}</Text>
        <View style={styles.macrosRow}>
          <Text style={styles.macroText}>P: {item.protein}g</Text>
          <Text style={styles.macroText}>C: {item.carbs}g</Text>
          <Text style={styles.macroText}>F: {item.fat}g</Text>
        </View>
        {item.recipe_tips && (
          <Text style={styles.recipeTips}>{item.recipe_tips}</Text>
        )}
      </View>
    ));
  };

  const renderDayMeals = (day: string, meals: DayMeals | undefined) => {
    if (!meals) return null;

    const dayLabel = day.charAt(0).toUpperCase() + day.slice(1);
    const isExpanded = expandedDay === day;

    return (
      <List.Accordion
        key={day}
        title={dayLabel}
        expanded={isExpanded}
        onPress={() => setExpandedDay(isExpanded ? null : day)}
        style={styles.dayAccordion}
        titleStyle={styles.dayTitle}
      >
        {MEAL_CATEGORIES.map(({ key, label, icon }) => {
          const mealItems = meals[key as keyof DayMeals];
          if (!mealItems || mealItems.length === 0) return null;

          return (
            <Card key={key} style={styles.mealCard}>
              <Card.Title
                title={label}
                titleVariant="titleMedium"
                left={(props) => <List.Icon {...props} icon={icon} />}
              />
              <Card.Content>
                {renderMealItems(mealItems)}
              </Card.Content>
            </Card>
          );
        })}
      </List.Accordion>
    );
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Loading meal plan...</Text>
      </View>
    );
  }

  if (!mealPlan) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>Meal plan not found</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>{mealPlan.name}</Text>
        {mealPlan.is_active && (
          <Chip icon="check-circle" style={styles.activeChip}>
            Active Plan
          </Chip>
        )}
      </View>

      {/* Summary Card */}
      <Card style={styles.summaryCard}>
        <Card.Content>
          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Daily Calories:</Text>
            <Text style={styles.summaryValue}>
              {mealPlan.calorie_target} kcal
            </Text>
          </View>

          {mealPlan.summary?.protein_target && (
            <View style={styles.summaryRow}>
              <Text style={styles.summaryLabel}>Protein Target:</Text>
              <Text style={styles.summaryValue}>
                {mealPlan.summary.protein_target}
              </Text>
            </View>
          )}

          {mealPlan.summary?.carbs_target && (
            <View style={styles.summaryRow}>
              <Text style={styles.summaryLabel}>Carbs Target:</Text>
              <Text style={styles.summaryValue}>
                {mealPlan.summary.carbs_target}
              </Text>
            </View>
          )}

          {mealPlan.summary?.fat_target && (
            <View style={styles.summaryRow}>
              <Text style={styles.summaryLabel}>Fat Target:</Text>
              <Text style={styles.summaryValue}>
                {mealPlan.summary.fat_target}
              </Text>
            </View>
          )}

          {mealPlan.dietary_preferences &&
            mealPlan.dietary_preferences.length > 0 && (
              <View style={styles.summaryRow}>
                <Text style={styles.summaryLabel}>Diet Type:</Text>
                <Text style={styles.summaryValue}>
                  {mealPlan.dietary_preferences.join(', ')}
                </Text>
              </View>
            )}

          {mealPlan.summary?.notes && (
            <>
              <Divider style={styles.divider} />
              <Text style={styles.notesTitle}>Notes:</Text>
              <Text style={styles.notesText}>{mealPlan.summary.notes}</Text>
            </>
          )}
        </Card.Content>
      </Card>

      {/* Days of Week */}
      <View style={styles.daysContainer}>
        <Text style={styles.sectionTitle}>7-Day Meal Plan</Text>
        <List.Section>
          {DAYS_OF_WEEK.map((day) =>
            renderDayMeals(day, mealPlan.plan_data[day])
          )}
        </List.Section>
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
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
  },
  errorText: {
    fontSize: fontSizes.lg,
    color: colors.error,
  },
  header: {
    padding: spacing.lg,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  title: {
    fontSize: fontSizes.xxl,
    fontWeight: '700',
    color: colors.text,
    flex: 1,
  },
  activeChip: {
    backgroundColor: colors.success,
  },
  summaryCard: {
    marginHorizontal: spacing.lg,
    marginBottom: spacing.lg,
    backgroundColor: colors.backgroundSecondary,
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.sm,
  },
  summaryLabel: {
    fontSize: fontSizes.md,
    color: colors.textSecondary,
  },
  summaryValue: {
    fontSize: fontSizes.md,
    color: colors.text,
    fontWeight: '600',
  },
  divider: {
    marginVertical: spacing.md,
  },
  notesTitle: {
    fontSize: fontSizes.md,
    fontWeight: '600',
    color: colors.text,
    marginBottom: spacing.xs,
  },
  notesText: {
    fontSize: fontSizes.md,
    color: colors.textSecondary,
    lineHeight: 20,
  },
  daysContainer: {
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.xl,
  },
  sectionTitle: {
    fontSize: fontSizes.xl,
    fontWeight: '700',
    color: colors.text,
    marginBottom: spacing.md,
  },
  dayAccordion: {
    backgroundColor: colors.backgroundSecondary,
    marginBottom: spacing.sm,
    borderRadius: 8,
  },
  dayTitle: {
    fontSize: fontSizes.lg,
    fontWeight: '600',
  },
  mealCard: {
    marginVertical: spacing.xs,
    marginHorizontal: spacing.sm,
    backgroundColor: colors.background,
  },
  mealItem: {
    marginBottom: spacing.md,
    paddingBottom: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  mealItemHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.xs,
  },
  mealItemName: {
    fontSize: fontSizes.md,
    fontWeight: '600',
    color: colors.text,
    flex: 1,
  },
  mealItemCalories: {
    fontSize: fontSizes.md,
    fontWeight: '600',
    color: colors.primary,
  },
  mealItemPortion: {
    fontSize: fontSizes.sm,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  macrosRow: {
    flexDirection: 'row',
    gap: spacing.md,
  },
  macroText: {
    fontSize: fontSizes.sm,
    color: colors.text,
    fontWeight: '500',
  },
  recipeTips: {
    fontSize: fontSizes.sm,
    color: colors.textSecondary,
    fontStyle: 'italic',
    marginTop: spacing.xs,
  },
});
