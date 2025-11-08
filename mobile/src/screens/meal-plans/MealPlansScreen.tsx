import React, { useState, useEffect, useCallback } from 'react';
import { View, StyleSheet, ScrollView, RefreshControl } from 'react-native';
import {
  Text,
  Card,
  Button,
  FAB,
  IconButton,
  Chip,
  ActivityIndicator,
} from 'react-native-paper';
import { useNavigation, useFocusEffect } from '@react-navigation/native';
import { colors, spacing, fontSizes } from '../../theme/colors';
import {
  mealPlanService,
  type MealPlan,
} from '../../services/api/mealPlanService';

export default function MealPlansScreen() {
  const navigation = useNavigation();
  const [mealPlans, setMealPlans] = useState<MealPlan[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const loadMealPlans = async () => {
    try {
      const plans = await mealPlanService.getAll();
      setMealPlans(plans);
    } catch (error) {
      console.error('Error loading meal plans:', error);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      setIsLoading(true);
      loadMealPlans();
    }, [])
  );

  const handleRefresh = () => {
    setIsRefreshing(true);
    loadMealPlans();
  };

  const handleActivate = async (planId: number) => {
    try {
      await mealPlanService.activate(planId);
      loadMealPlans();
    } catch (error) {
      console.error('Error activating plan:', error);
    }
  };

  const handleDelete = async (planId: number) => {
    try {
      await mealPlanService.delete(planId);
      loadMealPlans();
    } catch (error) {
      console.error('Error deleting plan:', error);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Loading meal plans...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
        }
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>Meal Plans</Text>
          <Text style={styles.subtitle}>
            AI-generated 7-day meal plans tailored to your goals
          </Text>
        </View>

        {/* Empty State */}
        {mealPlans.length === 0 && (
          <Card style={styles.emptyCard}>
            <Card.Content>
              <Text style={styles.emptyTitle}>No Meal Plans Yet</Text>
              <Text style={styles.emptyText}>
                Create your first personalized 7-day meal plan using our AI
                nutritionist. Just tap the + button below to get started!
              </Text>
            </Card.Content>
          </Card>
        )}

        {/* Meal Plans List */}
        {mealPlans.map((plan) => (
          <Card key={plan.id} style={styles.planCard}>
            <Card.Content>
              {/* Title and Active Badge */}
              <View style={styles.planHeader}>
                <Text style={styles.planName}>{plan.name}</Text>
                {plan.is_active && (
                  <Chip icon="check-circle" style={styles.activeChip}>
                    Active
                  </Chip>
                )}
              </View>

              {/* Calorie Target */}
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Daily Calories:</Text>
                <Text style={styles.infoValue}>
                  {plan.calorie_target} kcal
                </Text>
              </View>

              {/* Dietary Preferences */}
              {plan.dietary_preferences &&
                plan.dietary_preferences.length > 0 && (
                  <View style={styles.infoRow}>
                    <Text style={styles.infoLabel}>Diet:</Text>
                    <Text style={styles.infoValue}>
                      {plan.dietary_preferences.join(', ')}
                    </Text>
                  </View>
                )}

              {/* Created Date */}
              <Text style={styles.dateText}>
                Created: {formatDate(plan.created_at)}
              </Text>
            </Card.Content>

            <Card.Actions style={styles.cardActions}>
              <Button
                mode="outlined"
                onPress={() =>
                  navigation.navigate('MealPlanDetail' as never, { planId: plan.id } as never)
                }
              >
                View Details
              </Button>
              {!plan.is_active && (
                <Button mode="contained" onPress={() => handleActivate(plan.id)}>
                  Activate
                </Button>
              )}
              <IconButton
                icon="delete"
                size={20}
                onPress={() => handleDelete(plan.id)}
              />
            </Card.Actions>
          </Card>
        ))}
      </ScrollView>

      {/* FAB for Creating New Plan */}
      <FAB
        icon="plus"
        style={styles.fab}
        onPress={() => navigation.navigate('CreateMealPlan' as never)}
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
  content: {
    flex: 1,
  },
  header: {
    padding: spacing.lg,
    paddingBottom: spacing.md,
  },
  title: {
    fontSize: fontSizes.xxl,
    fontWeight: '700',
    color: colors.text,
  },
  subtitle: {
    fontSize: fontSizes.md,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  emptyCard: {
    margin: spacing.lg,
    backgroundColor: colors.backgroundSecondary,
  },
  emptyTitle: {
    fontSize: fontSizes.xl,
    fontWeight: '600',
    color: colors.text,
    marginBottom: spacing.sm,
    textAlign: 'center',
  },
  emptyText: {
    fontSize: fontSizes.md,
    color: colors.textSecondary,
    textAlign: 'center',
    lineHeight: 22,
  },
  planCard: {
    marginHorizontal: spacing.lg,
    marginBottom: spacing.md,
    backgroundColor: colors.backgroundSecondary,
  },
  planHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  planName: {
    fontSize: fontSizes.lg,
    fontWeight: '600',
    color: colors.text,
    flex: 1,
  },
  activeChip: {
    backgroundColor: colors.success,
  },
  infoRow: {
    flexDirection: 'row',
    marginBottom: spacing.xs,
  },
  infoLabel: {
    fontSize: fontSizes.md,
    color: colors.textSecondary,
    width: 120,
  },
  infoValue: {
    fontSize: fontSizes.md,
    color: colors.text,
    fontWeight: '500',
    flex: 1,
  },
  dateText: {
    fontSize: fontSizes.sm,
    color: colors.textSecondary,
    marginTop: spacing.sm,
  },
  cardActions: {
    justifyContent: 'flex-start',
    gap: spacing.xs,
  },
  fab: {
    position: 'absolute',
    right: spacing.lg,
    bottom: spacing.lg,
    backgroundColor: colors.primary,
  },
});
