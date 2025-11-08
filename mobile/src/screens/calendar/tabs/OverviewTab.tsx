import React, { useState } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Text, TextInput, Button, Card } from 'react-native-paper';
import { useDayStore } from '../../../store/dayStore';
import { colors, spacing, fontSizes } from '../../../theme/colors';

export default function OverviewTab() {
  const { currentDay, meals, exercises, waterIntakes, updateDay } = useDayStore();

  const [feeling, setFeeling] = useState(currentDay?.feeling || '');
  const [effortScore, setEffortScore] = useState(
    currentDay?.effort_score?.toString() || ''
  );
  const [weight, setWeight] = useState(currentDay?.weight?.toString() || '');
  const [isSaving, setIsSaving] = useState(false);

  // Calculate totals
  const totalCalories = meals.reduce((sum, meal) => sum + (meal.calories || 0), 0);
  const totalWater = waterIntakes.reduce((sum, intake) => sum + intake.amount, 0);
  const totalExerciseTime = exercises.reduce(
    (sum, ex) => sum + (ex.duration || 0),
    0
  );

  const handleSave = async () => {
    if (!currentDay) return;

    setIsSaving(true);
    try {
      await updateDay(currentDay.id, {
        feeling: feeling || null,
        effort_score: effortScore ? parseInt(effortScore) : null,
        weight: weight ? parseFloat(weight) : null,
      });
    } catch (error) {
      console.error('Failed to save:', error);
    } finally {
      setIsSaving(false);
    }
  };

  if (!currentDay) {
    return (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyText}>No day selected</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        {/* Date Header */}
        <Text style={styles.dateHeader}>{currentDay.date}</Text>

        {/* Quick Stats */}
        <Card style={styles.statsCard}>
          <Card.Content>
            <Text style={styles.sectionTitle}>Daily Summary</Text>
            <View style={styles.statsGrid}>
              <View style={styles.statItem}>
                <Text style={styles.statNumber}>{totalCalories}</Text>
                <Text style={styles.statLabel}>Calories</Text>
              </View>
              <View style={styles.statItem}>
                <Text style={styles.statNumber}>{totalWater.toFixed(1)}L</Text>
                <Text style={styles.statLabel}>Water</Text>
              </View>
              <View style={styles.statItem}>
                <Text style={styles.statNumber}>{totalExerciseTime}</Text>
                <Text style={styles.statLabel}>Minutes</Text>
              </View>
              <View style={styles.statItem}>
                <Text style={styles.statNumber}>{meals.length}</Text>
                <Text style={styles.statLabel}>Meals</Text>
              </View>
            </View>
          </Card.Content>
        </Card>

        {/* Day Inputs */}
        <Card style={styles.card}>
          <Card.Content>
            <Text style={styles.sectionTitle}>Day Details</Text>

            <TextInput
              label="How are you feeling?"
              value={feeling}
              onChangeText={setFeeling}
              mode="outlined"
              style={styles.input}
              placeholder="Great, tired, energetic..."
            />

            <TextInput
              label="Effort Score (1-10)"
              value={effortScore}
              onChangeText={setEffortScore}
              mode="outlined"
              keyboardType="numeric"
              style={styles.input}
              placeholder="1-10"
            />

            <TextInput
              label="Weight (kg)"
              value={weight}
              onChangeText={setWeight}
              mode="outlined"
              keyboardType="decimal-pad"
              style={styles.input}
              placeholder="75.5"
            />

            <Button
              mode="contained"
              onPress={handleSave}
              loading={isSaving}
              disabled={isSaving}
              style={styles.saveButton}
            >
              Save
            </Button>
          </Card.Content>
        </Card>

        {/* Activity Summary */}
        <Card style={styles.card}>
          <Card.Content>
            <Text style={styles.sectionTitle}>Activity Summary</Text>
            <View style={styles.summaryRow}>
              <Text style={styles.summaryLabel}>Meals logged:</Text>
              <Text style={styles.summaryValue}>{meals.length}</Text>
            </View>
            <View style={styles.summaryRow}>
              <Text style={styles.summaryLabel}>Exercises:</Text>
              <Text style={styles.summaryValue}>{exercises.length}</Text>
            </View>
            <View style={styles.summaryRow}>
              <Text style={styles.summaryLabel}>Water intakes:</Text>
              <Text style={styles.summaryValue}>{waterIntakes.length}</Text>
            </View>
          </Card.Content>
        </Card>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    padding: spacing.lg,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
  },
  emptyText: {
    fontSize: fontSizes.lg,
    color: colors.textSecondary,
  },
  dateHeader: {
    fontSize: fontSizes.xxl,
    fontWeight: '700',
    color: colors.text,
    marginBottom: spacing.lg,
  },
  statsCard: {
    marginBottom: spacing.lg,
    backgroundColor: colors.backgroundSecondary,
  },
  card: {
    marginBottom: spacing.lg,
  },
  sectionTitle: {
    fontSize: fontSizes.lg,
    fontWeight: '600',
    color: colors.text,
    marginBottom: spacing.md,
  },
  statsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    flexWrap: 'wrap',
    gap: spacing.md,
  },
  statItem: {
    alignItems: 'center',
    minWidth: 70,
  },
  statNumber: {
    fontSize: fontSizes.xl,
    fontWeight: '700',
    color: colors.primary,
  },
  statLabel: {
    fontSize: fontSizes.sm,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  input: {
    marginBottom: spacing.md,
  },
  saveButton: {
    marginTop: spacing.sm,
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  summaryLabel: {
    fontSize: fontSizes.md,
    color: colors.textSecondary,
  },
  summaryValue: {
    fontSize: fontSizes.md,
    fontWeight: '600',
    color: colors.text,
  },
});
