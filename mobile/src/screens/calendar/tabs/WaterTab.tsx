import React, { useState } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Text, FAB, Card, Button, ProgressBar } from 'react-native-paper';
import { useDayStore } from '../../../store/dayStore';
import { colors, spacing, fontSizes } from '../../../theme/colors';

export default function WaterTab() {
  const { currentDay, waterIntakes, addWater, deleteWater } = useDayStore();
  const totalWater = waterIntakes.reduce((sum, w) => sum + w.amount, 0);
  const goal = 2.5;
  const progress = Math.min(totalWater / goal, 1);

  const handleAddWater = async (amount: number) => {
    if (currentDay) {
      await addWater(currentDay.id, amount);
    }
  };

  return (
    <View style={styles.container}>
      <ScrollView style={styles.scrollView}>
        <View style={styles.content}>
          <Card style={styles.progressCard}>
            <Card.Content>
              <Text style={styles.totalText}>{totalWater.toFixed(1)}L / {goal}L</Text>
              <ProgressBar progress={progress} color={colors.primary} style={styles.progressBar} />
            </Card.Content>
          </Card>

          <View style={styles.buttonsRow}>
            <Button mode="contained" onPress={() => handleAddWater(0.25)} style={styles.waterButton}>
              +250ml
            </Button>
            <Button mode="contained" onPress={() => handleAddWater(0.5)} style={styles.waterButton}>
              +500ml
            </Button>
          </View>

          {waterIntakes.map((w) => (
            <Card key={w.id} style={styles.intakeCard}>
              <Card.Content style={styles.intakeRow}>
                <Text>{w.amount}L</Text>
                <Button mode="text" textColor={colors.error} onPress={() => deleteWater(w.id)}>
                  Delete
                </Button>
              </Card.Content>
            </Card>
          ))}
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  scrollView: { flex: 1 },
  content: { padding: spacing.lg },
  progressCard: { marginBottom: spacing.lg },
  totalText: { fontSize: fontSizes.xxl, fontWeight: '700', color: colors.primary, textAlign: 'center' },
  progressBar: { marginTop: spacing.md, height: 10, borderRadius: 5 },
  buttonsRow: { flexDirection: 'row', gap: spacing.md, marginBottom: spacing.lg },
  waterButton: { flex: 1 },
  intakeCard: { marginBottom: spacing.sm },
  intakeRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
});
