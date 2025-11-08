import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import { Text, FAB, Card, Button, Portal, Dialog, TextInput } from 'react-native-paper';
import { useDayStore } from '../../../store/dayStore';
import { colors, spacing, fontSizes } from '../../../theme/colors';
import { MaterialCommunityIcons } from '@expo/vector-icons';

export default function ExerciseTab() {
  const { currentDay, exercises, addExercise, deleteExercise } = useDayStore();
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [type, setType] = useState('');
  const [duration, setDuration] = useState('');
  const [distance, setDistance] = useState('');
  const [calories, setCalories] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  const handleAddExercise = async () => {
    if (!currentDay || !type) {
      Alert.alert('Error', 'Please enter exercise type');
      return;
    }

    setIsSaving(true);
    try {
      await addExercise(currentDay.id, {
        type,
        duration: duration ? parseInt(duration) : undefined,
        distance: distance ? parseFloat(distance) : undefined,
        calories_burned: calories ? parseInt(calories) : undefined,
      });

      setType('');
      setDuration('');
      setDistance('');
      setCalories('');
      setShowAddDialog(false);
    } catch (error) {
      Alert.alert('Error', 'Failed to add exercise');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeleteExercise = (exerciseId: number) => {
    Alert.alert(
      'Delete Exercise',
      'Are you sure?',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Delete', style: 'destructive', onPress: () => deleteExercise(exerciseId) },
      ]
    );
  };

  const totalDuration = exercises.reduce((sum, ex) => sum + (ex.duration || 0), 0);
  const totalCalories = exercises.reduce((sum, ex) => sum + (ex.calories_burned || 0), 0);

  return (
    <View style={styles.container}>
      <ScrollView style={styles.scrollView}>
        <View style={styles.content}>
          <Card style={styles.totalCard}>
            <Card.Content>
              <View style={styles.totalsRow}>
                <View>
                  <Text style={styles.totalLabel}>Duration</Text>
                  <Text style={styles.totalValue}>{totalDuration} min</Text>
                </View>
                <View>
                  <Text style={styles.totalLabel}>Burned</Text>
                  <Text style={styles.totalValue}>{totalCalories} cal</Text>
                </View>
              </View>
            </Card.Content>
          </Card>

          {exercises.length === 0 ? (
            <View style={styles.emptyContainer}>
              <MaterialCommunityIcons name="run" size={64} color={colors.textTertiary} />
              <Text style={styles.emptyText}>No exercises logged</Text>
            </View>
          ) : (
            exercises.map((exercise) => (
              <Card key={exercise.id} style={styles.exerciseCard}>
                <Card.Content>
                  <View style={styles.exerciseHeader}>
                    <Text style={styles.exerciseType}>{exercise.type}</Text>
                    <Button
                      mode="text"
                      textColor={colors.error}
                      onPress={() => handleDeleteExercise(exercise.id)}
                    >
                      Delete
                    </Button>
                  </View>
                  <View style={styles.detailsRow}>
                    {exercise.duration && (
                      <Text style={styles.detailText}>{exercise.duration} min</Text>
                    )}
                    {exercise.distance && (
                      <Text style={styles.detailText}>{exercise.distance} km</Text>
                    )}
                    {exercise.calories_burned && (
                      <Text style={styles.detailText}>{exercise.calories_burned} cal</Text>
                    )}
                  </View>
                </Card.Content>
              </Card>
            ))
          )}
        </View>
      </ScrollView>

      <FAB icon="plus" style={styles.fab} onPress={() => setShowAddDialog(true)} />

      <Portal>
        <Dialog visible={showAddDialog} onDismiss={() => setShowAddDialog(false)}>
          <Dialog.Title>Add Exercise</Dialog.Title>
          <Dialog.ScrollArea>
            <ScrollView>
              <TextInput label="Type *" value={type} onChangeText={setType} mode="outlined" style={styles.input} />
              <TextInput label="Duration (min)" value={duration} onChangeText={setDuration} keyboardType="numeric" mode="outlined" style={styles.input} />
              <TextInput label="Distance (km)" value={distance} onChangeText={setDistance} keyboardType="decimal-pad" mode="outlined" style={styles.input} />
              <TextInput label="Calories" value={calories} onChangeText={setCalories} keyboardType="numeric" mode="outlined" style={styles.input} />
            </ScrollView>
          </Dialog.ScrollArea>
          <Dialog.Actions>
            <Button onPress={() => setShowAddDialog(false)}>Cancel</Button>
            <Button onPress={handleAddExercise} loading={isSaving}>Add</Button>
          </Dialog.Actions>
        </Dialog>
      </Portal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  scrollView: { flex: 1 },
  content: { padding: spacing.lg, paddingBottom: 80 },
  totalCard: { marginBottom: spacing.lg, backgroundColor: colors.secondary },
  totalsRow: { flexDirection: 'row', justifyContent: 'space-around' },
  totalLabel: { fontSize: fontSizes.md, color: colors.background, opacity: 0.9 },
  totalValue: { fontSize: fontSizes.xxl, fontWeight: '700', color: colors.background, marginTop: spacing.xs },
  emptyContainer: { alignItems: 'center', paddingVertical: spacing.xxl },
  emptyText: { fontSize: fontSizes.lg, color: colors.textSecondary, marginTop: spacing.md },
  exerciseCard: { marginBottom: spacing.md },
  exerciseHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: spacing.sm },
  exerciseType: { fontSize: fontSizes.lg, fontWeight: '600', color: colors.text },
  detailsRow: { flexDirection: 'row', gap: spacing.md },
  detailText: { fontSize: fontSizes.sm, color: colors.textSecondary },
  fab: { position: 'absolute', margin: 16, right: 0, bottom: 0, backgroundColor: colors.primary },
  input: { marginBottom: spacing.md },
});
