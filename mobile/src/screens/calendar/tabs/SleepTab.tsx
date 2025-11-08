import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Text } from 'react-native-paper';
import { colors, spacing, fontSizes } from '../../../theme/colors';

export default function SleepTab() {
  return (
    <View style={styles.container}>
      <Text style={styles.text}>Sleep tracking - Phase 2B</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background, justifyContent: 'center', alignItems: 'center', padding: spacing.lg },
  text: { fontSize: fontSizes.lg, color: colors.textSecondary },
});
