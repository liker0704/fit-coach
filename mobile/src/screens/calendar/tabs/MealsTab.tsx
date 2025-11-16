import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import { Text, FAB, Card, Button, Portal, Dialog, TextInput, SegmentedButtons } from 'react-native-paper';
import { useDayStore } from '../../../store/dayStore';
import { colors, spacing, fontSizes } from '../../../theme/colors';
import { MaterialCommunityIcons } from '@expo/vector-icons';

export default function MealsTab() {
  const { currentDay, meals, isMealsLoading, addMeal, deleteMeal } = useDayStore();
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [category, setCategory] = useState<'breakfast' | 'lunch' | 'dinner' | 'snack'>('breakfast');
  const [calories, setCalories] = useState('');
  const [protein, setProtein] = useState('');
  const [carbs, setCarbs] = useState('');
  const [fat, setFat] = useState('');
  const [notes, setNotes] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  const handleAddMeal = async () => {
    if (!currentDay || !calories) {
      Alert.alert('Error', 'Please enter at least calories');
      return;
    }

    setIsSaving(true);
    try {
      await addMeal(currentDay.id, {
        category,
        calories: parseFloat(calories),
        protein: protein ? parseFloat(protein) : undefined,
        carbs: carbs ? parseFloat(carbs) : undefined,
        fat: fat ? parseFloat(fat) : undefined,
        notes: notes || undefined,
      });

      // Reset form
      setCategory('breakfast');
      setCalories('');
      setProtein('');
      setCarbs('');
      setFat('');
      setNotes('');
      setShowAddDialog(false);
    } catch (error) {
      Alert.alert('Error', 'Failed to add meal');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeleteMeal = (mealId: number) => {
    Alert.alert(
      'Delete Meal',
      'Are you sure you want to delete this meal?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: () => deleteMeal(mealId),
        },
      ]
    );
  };

  const getMealIcon = (category: string) => {
    switch (category) {
      case 'breakfast': return 'coffee';
      case 'lunch': return 'food';
      case 'dinner': return 'food-variant';
      case 'snack': return 'cookie';
      default: return 'silverware-fork-knife';
    }
  };

  const totalCalories = meals.reduce((sum, meal) => sum + (meal.calories || 0), 0);

  return (
    <View style={styles.container}>
      <ScrollView style={styles.scrollView}>
        <View style={styles.content}>
          {/* Total Card */}
          <Card style={styles.totalCard}>
            <Card.Content>
              <Text style={styles.totalLabel}>Total Calories</Text>
              <Text style={styles.totalValue}>{totalCalories.toFixed(0)}</Text>
            </Card.Content>
          </Card>

          {/* Meals List */}
          {meals.length === 0 ? (
            <View style={styles.emptyContainer}>
              <MaterialCommunityIcons
                name="food-off"
                size={64}
                color={colors.textTertiary}
              />
              <Text style={styles.emptyText}>No meals logged yet</Text>
              <Text style={styles.emptySubtext}>Tap + to add your first meal</Text>
            </View>
          ) : (
            meals.map((meal) => (
              <Card key={meal.id} style={styles.mealCard}>
                <Card.Content>
                  <View style={styles.mealHeader}>
                    <View style={styles.mealTitle}>
                      <MaterialCommunityIcons
                        name={getMealIcon(meal.category)}
                        size={24}
                        color={colors.primary}
                      />
                      <Text style={styles.categoryText}>
                        {meal.category.charAt(0).toUpperCase() + meal.category.slice(1)}
                      </Text>
                    </View>
                    <Button
                      mode="text"
                      textColor={colors.error}
                      onPress={() => handleDeleteMeal(meal.id)}
                    >
                      Delete
                    </Button>
                  </View>

                  <View style={styles.macrosRow}>
                    <View style={styles.macroItem}>
                      <Text style={styles.macroValue}>{meal.calories || 0}</Text>
                      <Text style={styles.macroLabel}>cal</Text>
                    </View>
                    {meal.protein !== null && meal.protein !== undefined && (
                      <View style={styles.macroItem}>
                        <Text style={styles.macroValue}>{meal.protein}g</Text>
                        <Text style={styles.macroLabel}>protein</Text>
                      </View>
                    )}
                    {meal.carbs !== null && meal.carbs !== undefined && (
                      <View style={styles.macroItem}>
                        <Text style={styles.macroValue}>{meal.carbs}g</Text>
                        <Text style={styles.macroLabel}>carbs</Text>
                      </View>
                    )}
                    {meal.fat !== null && meal.fat !== undefined && (
                      <View style={styles.macroItem}>
                        <Text style={styles.macroValue}>{meal.fat}g</Text>
                        <Text style={styles.macroLabel}>fat</Text>
                      </View>
                    )}
                  </View>

                  {meal.notes && (
                    <Text style={styles.notes}>{meal.notes}</Text>
                  )}
                </Card.Content>
              </Card>
            ))
          )}
        </View>
      </ScrollView>

      {/* Add Button */}
      <FAB
        icon="plus"
        style={styles.fab}
        onPress={() => setShowAddDialog(true)}
      />

      {/* Add Meal Dialog */}
      <Portal>
        <Dialog visible={showAddDialog} onDismiss={() => setShowAddDialog(false)}>
          <Dialog.Title>Add Meal</Dialog.Title>
          <Dialog.ScrollArea>
            <ScrollView>
              <SegmentedButtons
                value={category}
                onValueChange={(value: any) => setCategory(value)}
                buttons={[
                  { value: 'breakfast', label: 'Breakfast' },
                  { value: 'lunch', label: 'Lunch' },
                  { value: 'dinner', label: 'Dinner' },
                  { value: 'snack', label: 'Snack' },
                ]}
                style={styles.segmentedButtons}
              />

              <TextInput
                label="Calories *"
                value={calories}
                onChangeText={setCalories}
                keyboardType="numeric"
                mode="outlined"
                style={styles.dialogInput}
              />

              <View style={styles.macrosInputRow}>
                <TextInput
                  label="Protein (g)"
                  value={protein}
                  onChangeText={setProtein}
                  keyboardType="numeric"
                  mode="outlined"
                  style={styles.macroInput}
                />
                <TextInput
                  label="Carbs (g)"
                  value={carbs}
                  onChangeText={setCarbs}
                  keyboardType="numeric"
                  mode="outlined"
                  style={styles.macroInput}
                />
                <TextInput
                  label="Fat (g)"
                  value={fat}
                  onChangeText={setFat}
                  keyboardType="numeric"
                  mode="outlined"
                  style={styles.macroInput}
                />
              </View>

              <TextInput
                label="Notes"
                value={notes}
                onChangeText={setNotes}
                mode="outlined"
                multiline
                numberOfLines={3}
                style={styles.dialogInput}
              />
            </ScrollView>
          </Dialog.ScrollArea>
          <Dialog.Actions>
            <Button onPress={() => setShowAddDialog(false)}>Cancel</Button>
            <Button onPress={handleAddMeal} loading={isSaving}>Add</Button>
          </Dialog.Actions>
        </Dialog>
      </Portal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  scrollView: {
    flex: 1,
  },
  content: {
    padding: spacing.lg,
    paddingBottom: 80,
  },
  totalCard: {
    marginBottom: spacing.lg,
    backgroundColor: colors.primary,
  },
  totalLabel: {
    fontSize: fontSizes.md,
    color: colors.background,
    opacity: 0.9,
  },
  totalValue: {
    fontSize: fontSizes.xxxl,
    fontWeight: '700',
    color: colors.background,
    marginTop: spacing.xs,
  },
  emptyContainer: {
    alignItems: 'center',
    paddingVertical: spacing.xxl,
  },
  emptyText: {
    fontSize: fontSizes.lg,
    color: colors.textSecondary,
    marginTop: spacing.md,
  },
  emptySubtext: {
    fontSize: fontSizes.sm,
    color: colors.textTertiary,
    marginTop: spacing.xs,
  },
  mealCard: {
    marginBottom: spacing.md,
  },
  mealHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  mealTitle: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  categoryText: {
    fontSize: fontSizes.lg,
    fontWeight: '600',
    color: colors.text,
  },
  macrosRow: {
    flexDirection: 'row',
    gap: spacing.md,
  },
  macroItem: {
    alignItems: 'center',
  },
  macroValue: {
    fontSize: fontSizes.md,
    fontWeight: '600',
    color: colors.text,
  },
  macroLabel: {
    fontSize: fontSizes.xs,
    color: colors.textSecondary,
    marginTop: spacing.xs / 2,
  },
  notes: {
    fontSize: fontSizes.sm,
    color: colors.textSecondary,
    marginTop: spacing.md,
    fontStyle: 'italic',
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
    backgroundColor: colors.primary,
  },
  segmentedButtons: {
    marginBottom: spacing.md,
  },
  dialogInput: {
    marginBottom: spacing.md,
  },
  macrosInputRow: {
    flexDirection: 'row',
    gap: spacing.sm,
  },
  macroInput: {
    flex: 1,
    marginBottom: spacing.md,
  },
});
