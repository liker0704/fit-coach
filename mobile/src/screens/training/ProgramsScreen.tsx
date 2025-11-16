import React, { useState, useCallback } from 'react';
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
  trainingProgramService,
  type TrainingProgram,
} from '../../services/api/trainingProgramService';

export default function ProgramsScreen() {
  const navigation = useNavigation();
  const [programs, setPrograms] = useState<TrainingProgram[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const loadPrograms = async () => {
    try {
      const data = await trainingProgramService.getAll();
      setPrograms(data);
    } catch (error) {
      console.error('Error loading programs:', error);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      setIsLoading(true);
      loadPrograms();
    }, [])
  );

  const handleRefresh = () => {
    setIsRefreshing(true);
    loadPrograms();
  };

  const handleActivate = async (programId: number) => {
    try {
      await trainingProgramService.activate(programId);
      loadPrograms();
    } catch (error) {
      console.error('Error activating program:', error);
    }
  };

  const handleDelete = async (programId: number) => {
    try {
      await trainingProgramService.delete(programId);
      loadPrograms();
    } catch (error) {
      console.error('Error deleting program:', error);
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
        <Text style={styles.loadingText}>Loading programs...</Text>
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
          <Text style={styles.title}>Training Programs</Text>
          <Text style={styles.subtitle}>
            AI-generated 12-week training programs designed for your goals
          </Text>
        </View>

        {/* Empty State */}
        {programs.length === 0 && (
          <Card style={styles.emptyCard}>
            <Card.Content>
              <Text style={styles.emptyTitle}>No Programs Yet</Text>
              <Text style={styles.emptyText}>
                Create your first personalized 12-week training program using our
                AI coach. Just tap the + button below to get started!
              </Text>
            </Card.Content>
          </Card>
        )}

        {/* Programs List */}
        {programs.map((program) => (
          <Card key={program.id} style={styles.programCard}>
            <Card.Content>
              {/* Title and Active Badge */}
              <View style={styles.programHeader}>
                <Text style={styles.programName}>{program.name}</Text>
                {program.is_active && (
                  <Chip icon="check-circle" style={styles.activeChip}>
                    Active
                  </Chip>
                )}
              </View>

              {/* Goal */}
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Goal:</Text>
                <Text style={styles.infoValue}>{program.goal}</Text>
              </View>

              {/* Duration */}
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Duration:</Text>
                <Text style={styles.infoValue}>
                  {program.duration_weeks} weeks, {program.days_per_week}{' '}
                  days/week
                </Text>
              </View>

              {/* Experience Level */}
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Level:</Text>
                <Text style={styles.infoValue}>
                  {program.experience_level.charAt(0).toUpperCase() +
                    program.experience_level.slice(1)}
                </Text>
              </View>

              {/* Equipment */}
              {program.equipment && program.equipment.length > 0 && (
                <View style={styles.infoRow}>
                  <Text style={styles.infoLabel}>Equipment:</Text>
                  <Text style={styles.infoValue}>
                    {program.equipment.join(', ')}
                  </Text>
                </View>
              )}

              {/* Created Date */}
              <Text style={styles.dateText}>
                Created: {formatDate(program.created_at)}
              </Text>
            </Card.Content>

            <Card.Actions style={styles.cardActions}>
              <Button
                mode="outlined"
                onPress={() =>
                  navigation.navigate('ProgramDetail' as never, {
                    programId: program.id,
                  } as never)
                }
              >
                View Details
              </Button>
              {!program.is_active && (
                <Button
                  mode="contained"
                  onPress={() => handleActivate(program.id)}
                >
                  Activate
                </Button>
              )}
              <IconButton
                icon="delete"
                size={20}
                onPress={() => handleDelete(program.id)}
              />
            </Card.Actions>
          </Card>
        ))}
      </ScrollView>

      {/* FAB for Creating New Program */}
      <FAB
        icon="plus"
        style={styles.fab}
        onPress={() => navigation.navigate('CreateProgram' as never)}
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
  programCard: {
    marginHorizontal: spacing.lg,
    marginBottom: spacing.md,
    backgroundColor: colors.backgroundSecondary,
  },
  programHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  programName: {
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
    width: 100,
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
