import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import {
  Text,
  TextInput,
  Button,
  Chip,
  ActivityIndicator,
  Card,
  RadioButton,
} from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import { colors, spacing, fontSizes } from '../../theme/colors';
import { trainingProgramService } from '../../services/api/trainingProgramService';

const EXPERIENCE_LEVELS = [
  { value: 'beginner', label: 'Beginner' },
  { value: 'intermediate', label: 'Intermediate' },
  { value: 'advanced', label: 'Advanced' },
];

const DAYS_PER_WEEK = [3, 4, 5, 6];

const EQUIPMENT_OPTIONS = [
  'Dumbbells',
  'Barbell',
  'Kettlebells',
  'Resistance Bands',
  'Pull-up Bar',
  'Bench',
  'Squat Rack',
  'Cardio Equipment',
  'Bodyweight Only',
];

export default function CreateProgramScreen() {
  const navigation = useNavigation();
  const [goal, setGoal] = useState('');
  const [experienceLevel, setExperienceLevel] = useState('beginner');
  const [daysPerWeek, setDaysPerWeek] = useState(3);
  const [selectedEquipment, setSelectedEquipment] = useState<string[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);

  const toggleEquipment = (equipment: string) => {
    setSelectedEquipment((prev) =>
      prev.includes(equipment)
        ? prev.filter((e) => e !== equipment)
        : [...prev, equipment]
    );
  };

  const handleGenerate = async () => {
    // Validation
    if (!goal.trim()) {
      Alert.alert('Missing Goal', 'Please enter your training goal.');
      return;
    }

    setIsGenerating(true);

    try {
      const response = await trainingProgramService.generate({
        goal: goal.trim(),
        experience_level: experienceLevel,
        days_per_week: daysPerWeek,
        equipment:
          selectedEquipment.length > 0 ? selectedEquipment : undefined,
      });

      if (response.success && response.program_id) {
        Alert.alert(
          'Success!',
          'Your personalized 12-week training program has been generated.',
          [
            {
              text: 'View Program',
              onPress: () => {
                navigation.navigate('ProgramDetail' as never, {
                  programId: response.program_id,
                } as never);
              },
            },
            {
              text: 'Back to List',
              onPress: () => navigation.goBack(),
            },
          ]
        );
      } else {
        Alert.alert(
          'Error',
          response.message || 'Failed to generate training program'
        );
      }
    } catch (error) {
      console.error('Error generating program:', error);
      Alert.alert(
        'Error',
        'Failed to generate training program. Please try again.'
      );
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        {/* Header */}
        <Text style={styles.title}>Create Training Program</Text>
        <Text style={styles.subtitle}>
          Customize your preferences and let our AI coach create a personalized
          12-week training program for you.
        </Text>

        {/* Goal */}
        <Card style={styles.card}>
          <Card.Content>
            <Text style={styles.sectionTitle}>Training Goal</Text>
            <Text style={styles.sectionDescription}>
              What do you want to achieve? (e.g., Build Muscle, Lose Fat, Improve
              Strength, Marathon Training)
            </Text>
            <TextInput
              label="Goal"
              value={goal}
              onChangeText={setGoal}
              mode="outlined"
              placeholder="e.g., Build muscle and increase strength"
              style={styles.input}
              disabled={isGenerating}
              multiline
              numberOfLines={2}
            />
          </Card.Content>
        </Card>

        {/* Experience Level */}
        <Card style={styles.card}>
          <Card.Content>
            <Text style={styles.sectionTitle}>Experience Level</Text>
            <Text style={styles.sectionDescription}>
              Select your training experience
            </Text>
            <RadioButton.Group
              onValueChange={(value) => setExperienceLevel(value)}
              value={experienceLevel}
            >
              {EXPERIENCE_LEVELS.map((level) => (
                <View key={level.value} style={styles.radioItem}>
                  <RadioButton.Item
                    label={level.label}
                    value={level.value}
                    disabled={isGenerating}
                    style={styles.radioButton}
                  />
                </View>
              ))}
            </RadioButton.Group>
          </Card.Content>
        </Card>

        {/* Days per Week */}
        <Card style={styles.card}>
          <Card.Content>
            <Text style={styles.sectionTitle}>Training Frequency</Text>
            <Text style={styles.sectionDescription}>
              How many days per week can you train?
            </Text>
            <View style={styles.chipContainer}>
              {DAYS_PER_WEEK.map((days) => (
                <Chip
                  key={days}
                  selected={daysPerWeek === days}
                  onPress={() => setDaysPerWeek(days)}
                  style={styles.chip}
                  disabled={isGenerating}
                >
                  {days} days
                </Chip>
              ))}
            </View>
          </Card.Content>
        </Card>

        {/* Equipment */}
        <Card style={styles.card}>
          <Card.Content>
            <Text style={styles.sectionTitle}>Available Equipment</Text>
            <Text style={styles.sectionDescription}>
              Select all equipment you have access to (optional)
            </Text>
            <View style={styles.chipContainer}>
              {EQUIPMENT_OPTIONS.map((equipment) => (
                <Chip
                  key={equipment}
                  selected={selectedEquipment.includes(equipment)}
                  onPress={() => toggleEquipment(equipment)}
                  style={styles.chip}
                  disabled={isGenerating}
                >
                  {equipment}
                </Chip>
              ))}
            </View>
          </Card.Content>
        </Card>

        {/* Generate Button */}
        {isGenerating ? (
          <View style={styles.generatingContainer}>
            <ActivityIndicator size="large" color={colors.primary} />
            <Text style={styles.generatingText}>
              Generating your personalized training program...
            </Text>
            <Text style={styles.generatingSubtext}>
              This may take 15-40 seconds
            </Text>
          </View>
        ) : (
          <View style={styles.buttonContainer}>
            <Button
              mode="outlined"
              onPress={() => navigation.goBack()}
              style={styles.button}
            >
              Cancel
            </Button>
            <Button
              mode="contained"
              onPress={handleGenerate}
              style={styles.button}
              icon="dumbbell"
            >
              Generate Program
            </Button>
          </View>
        )}
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
  title: {
    fontSize: fontSizes.xxl,
    fontWeight: '700',
    color: colors.text,
  },
  subtitle: {
    fontSize: fontSizes.md,
    color: colors.textSecondary,
    marginTop: spacing.xs,
    marginBottom: spacing.lg,
    lineHeight: 22,
  },
  card: {
    marginBottom: spacing.lg,
    backgroundColor: colors.backgroundSecondary,
  },
  sectionTitle: {
    fontSize: fontSizes.lg,
    fontWeight: '600',
    color: colors.text,
    marginBottom: spacing.xs,
  },
  sectionDescription: {
    fontSize: fontSizes.sm,
    color: colors.textSecondary,
    marginBottom: spacing.md,
  },
  input: {
    backgroundColor: colors.background,
  },
  radioItem: {
    marginBottom: spacing.xs,
  },
  radioButton: {
    paddingVertical: 0,
  },
  chipContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
  },
  chip: {
    marginRight: spacing.xs,
    marginBottom: spacing.xs,
  },
  generatingContainer: {
    alignItems: 'center',
    paddingVertical: spacing.xl,
  },
  generatingText: {
    marginTop: spacing.md,
    fontSize: fontSizes.lg,
    fontWeight: '600',
    color: colors.text,
    textAlign: 'center',
  },
  generatingSubtext: {
    marginTop: spacing.xs,
    fontSize: fontSizes.sm,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  buttonContainer: {
    flexDirection: 'row',
    gap: spacing.md,
    marginTop: spacing.md,
  },
  button: {
    flex: 1,
  },
});
