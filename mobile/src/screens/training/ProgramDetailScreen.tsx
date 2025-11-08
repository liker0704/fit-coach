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
  trainingProgramService,
  type TrainingProgram,
  type TrainingWeek,
  type WorkoutDay,
  type Exercise,
} from '../../services/api/trainingProgramService';

type RouteParams = {
  params: {
    programId: number;
  };
};

export default function ProgramDetailScreen() {
  const route = useRoute<RouteProp<RouteParams, 'params'>>();
  const { programId } = route.params;
  const [program, setProgram] = useState<TrainingProgram | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [expandedWeek, setExpandedWeek] = useState<number | null>(1);

  useEffect(() => {
    loadProgram();
  }, [programId]);

  const loadProgram = async () => {
    try {
      const data = await trainingProgramService.get(programId);
      setProgram(data);
    } catch (error) {
      console.error('Error loading program:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const renderExercise = (exercise: Exercise, index: number) => {
    return (
      <View key={index} style={styles.exerciseItem}>
        <View style={styles.exerciseHeader}>
          <Text style={styles.exerciseNumber}>{index + 1}.</Text>
          <View style={styles.exerciseInfo}>
            <Text style={styles.exerciseName}>{exercise.name}</Text>
            <View style={styles.exerciseDetails}>
              <Text style={styles.exerciseDetail}>
                {exercise.sets} sets × {exercise.reps} reps
              </Text>
              <Text style={styles.exerciseDetail}>
                Rest: {exercise.rest_seconds}s
              </Text>
            </View>
            {exercise.intensity && (
              <Text style={styles.exerciseIntensity}>
                Intensity: {exercise.intensity}
              </Text>
            )}
            {exercise.notes && (
              <Text style={styles.exerciseNotes}>{exercise.notes}</Text>
            )}
          </View>
        </View>
      </View>
    );
  };

  const renderWorkoutDay = (workout: WorkoutDay, index: number) => {
    return (
      <Card key={index} style={styles.workoutCard}>
        <Card.Title
          title={workout.day_name}
          subtitle={workout.focus}
          titleVariant="titleMedium"
          left={(props) => <List.Icon {...props} icon="weight-lifter" />}
        />
        <Card.Content>
          {workout.warm_up && (
            <View style={styles.workoutSection}>
              <Text style={styles.workoutSectionTitle}>Warm-up:</Text>
              <Text style={styles.workoutSectionText}>{workout.warm_up}</Text>
            </View>
          )}

          <View style={styles.exercisesSection}>
            <Text style={styles.workoutSectionTitle}>Exercises:</Text>
            {workout.exercises.map((exercise, idx) =>
              renderExercise(exercise, idx)
            )}
          </View>

          {workout.cool_down && (
            <View style={styles.workoutSection}>
              <Text style={styles.workoutSectionTitle}>Cool-down:</Text>
              <Text style={styles.workoutSectionText}>{workout.cool_down}</Text>
            </View>
          )}

          {workout.estimated_duration_minutes && (
            <Text style={styles.durationText}>
              Duration: ~{workout.estimated_duration_minutes} minutes
            </Text>
          )}
        </Card.Content>
      </Card>
    );
  };

  const renderWeek = (week: TrainingWeek) => {
    const isExpanded = expandedWeek === week.week_number;

    return (
      <List.Accordion
        key={week.week_number}
        title={`Week ${week.week_number}`}
        description={week.focus}
        expanded={isExpanded}
        onPress={() =>
          setExpandedWeek(isExpanded ? null : week.week_number)
        }
        style={styles.weekAccordion}
        titleStyle={styles.weekTitle}
      >
        {week.notes && (
          <Card style={styles.notesCard}>
            <Card.Content>
              <Text style={styles.weekNotes}>{week.notes}</Text>
            </Card.Content>
          </Card>
        )}
        {week.workouts.map((workout, index) =>
          renderWorkoutDay(workout, index)
        )}
      </List.Accordion>
    );
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Loading program...</Text>
      </View>
    );
  }

  if (!program) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>Program not found</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>{program.name}</Text>
        {program.is_active && (
          <Chip icon="check-circle" style={styles.activeChip}>
            Active Program
          </Chip>
        )}
      </View>

      {/* Summary Card */}
      <Card style={styles.summaryCard}>
        <Card.Content>
          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Goal:</Text>
            <Text style={styles.summaryValue}>{program.goal}</Text>
          </View>

          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Duration:</Text>
            <Text style={styles.summaryValue}>
              {program.duration_weeks} weeks
            </Text>
          </View>

          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Frequency:</Text>
            <Text style={styles.summaryValue}>
              {program.days_per_week} days/week
            </Text>
          </View>

          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Level:</Text>
            <Text style={styles.summaryValue}>
              {program.experience_level.charAt(0).toUpperCase() +
                program.experience_level.slice(1)}
            </Text>
          </View>

          {program.equipment && program.equipment.length > 0 && (
            <View style={styles.summaryRow}>
              <Text style={styles.summaryLabel}>Equipment:</Text>
              <Text style={styles.summaryValue}>
                {program.equipment.join(', ')}
              </Text>
            </View>
          )}

          {program.summary?.progression_strategy && (
            <>
              <Divider style={styles.divider} />
              <Text style={styles.progressionTitle}>
                Progression Strategy:
              </Text>
              <Text style={styles.progressionText}>
                {program.summary.progression_strategy}
              </Text>
            </>
          )}

          {program.summary?.notes && (
            <>
              <Divider style={styles.divider} />
              <Text style={styles.notesTitle}>Notes:</Text>
              <Text style={styles.notesText}>{program.summary.notes}</Text>
            </>
          )}
        </Card.Content>
      </Card>

      {/* Weeks */}
      <View style={styles.weeksContainer}>
        <Text style={styles.sectionTitle}>12-Week Program</Text>
        <List.Section>
          {program.program_data.map((week) => renderWeek(week))}
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
    marginBottom: spacing.sm,
  },
  summaryLabel: {
    fontSize: fontSizes.md,
    color: colors.textSecondary,
    width: 100,
  },
  summaryValue: {
    fontSize: fontSizes.md,
    color: colors.text,
    fontWeight: '600',
    flex: 1,
  },
  divider: {
    marginVertical: spacing.md,
  },
  progressionTitle: {
    fontSize: fontSizes.md,
    fontWeight: '600',
    color: colors.text,
    marginBottom: spacing.xs,
  },
  progressionText: {
    fontSize: fontSizes.md,
    color: colors.textSecondary,
    lineHeight: 20,
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
  weeksContainer: {
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.xl,
  },
  sectionTitle: {
    fontSize: fontSizes.xl,
    fontWeight: '700',
    color: colors.text,
    marginBottom: spacing.md,
  },
  weekAccordion: {
    backgroundColor: colors.backgroundSecondary,
    marginBottom: spacing.sm,
    borderRadius: 8,
  },
  weekTitle: {
    fontSize: fontSizes.lg,
    fontWeight: '600',
  },
  notesCard: {
    marginVertical: spacing.xs,
    marginHorizontal: spacing.sm,
    backgroundColor: colors.background,
  },
  weekNotes: {
    fontSize: fontSizes.sm,
    color: colors.textSecondary,
    fontStyle: 'italic',
  },
  workoutCard: {
    marginVertical: spacing.xs,
    marginHorizontal: spacing.sm,
    backgroundColor: colors.background,
  },
  workoutSection: {
    marginBottom: spacing.md,
  },
  workoutSectionTitle: {
    fontSize: fontSizes.md,
    fontWeight: '600',
    color: colors.text,
    marginBottom: spacing.xs,
  },
  workoutSectionText: {
    fontSize: fontSizes.sm,
    color: colors.textSecondary,
    lineHeight: 20,
  },
  exercisesSection: {
    marginBottom: spacing.md,
  },
  exerciseItem: {
    marginBottom: spacing.md,
    paddingBottom: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  exerciseHeader: {
    flexDirection: 'row',
  },
  exerciseNumber: {
    fontSize: fontSizes.md,
    fontWeight: '600',
    color: colors.primary,
    marginRight: spacing.sm,
    width: 24,
  },
  exerciseInfo: {
    flex: 1,
  },
  exerciseName: {
    fontSize: fontSizes.md,
    fontWeight: '600',
    color: colors.text,
    marginBottom: spacing.xs,
  },
  exerciseDetails: {
    flexDirection: 'row',
    gap: spacing.md,
    marginBottom: spacing.xs,
  },
  exerciseDetail: {
    fontSize: fontSizes.sm,
    color: colors.text,
    fontWeight: '500',
  },
  exerciseIntensity: {
    fontSize: fontSizes.sm,
    color: colors.primary,
    marginBottom: spacing.xs,
  },
  exerciseNotes: {
    fontSize: fontSizes.sm,
    color: colors.textSecondary,
    fontStyle: 'italic',
  },
  durationText: {
    fontSize: fontSizes.sm,
    color: colors.textSecondary,
    marginTop: spacing.sm,
    textAlign: 'right',
  },
});
