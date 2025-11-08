import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import {
  Text,
  TextInput,
  Button,
  Chip,
  ActivityIndicator,
  Card,
} from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import { colors, spacing, fontSizes } from '../../theme/colors';
import { mealPlanService } from '../../services/api/mealPlanService';

const DIETARY_OPTIONS = [
  'Vegetarian',
  'Vegan',
  'Keto',
  'Paleo',
  'Mediterranean',
  'Low-Carb',
  'High-Protein',
  'Gluten-Free',
  'Dairy-Free',
];

const COMMON_ALLERGIES = [
  'Peanuts',
  'Tree Nuts',
  'Milk',
  'Eggs',
  'Wheat',
  'Soy',
  'Fish',
  'Shellfish',
];

export default function CreateMealPlanScreen() {
  const navigation = useNavigation();
  const [calorieTarget, setCalorieTarget] = useState('');
  const [selectedDiets, setSelectedDiets] = useState<string[]>([]);
  const [selectedAllergies, setSelectedAllergies] = useState<string[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);

  const toggleDiet = (diet: string) => {
    setSelectedDiets((prev) =>
      prev.includes(diet)
        ? prev.filter((d) => d !== diet)
        : [...prev, diet]
    );
  };

  const toggleAllergy = (allergy: string) => {
    setSelectedAllergies((prev) =>
      prev.includes(allergy)
        ? prev.filter((a) => a !== allergy)
        : [...prev, allergy]
    );
  };

  const handleGenerate = async () => {
    // Validation
    if (calorieTarget && (parseInt(calorieTarget) < 1000 || parseInt(calorieTarget) > 5000)) {
      Alert.alert(
        'Invalid Calories',
        'Please enter a calorie target between 1000 and 5000.'
      );
      return;
    }

    setIsGenerating(true);

    try {
      const response = await mealPlanService.generate({
        calorie_target: calorieTarget ? parseInt(calorieTarget) : undefined,
        dietary_preferences: selectedDiets.length > 0 ? selectedDiets : undefined,
        allergies: selectedAllergies.length > 0 ? selectedAllergies : undefined,
      });

      if (response.success && response.meal_plan_id) {
        Alert.alert(
          'Success!',
          'Your personalized 7-day meal plan has been generated.',
          [
            {
              text: 'View Plan',
              onPress: () => {
                navigation.navigate('MealPlanDetail' as never, {
                  planId: response.meal_plan_id,
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
        Alert.alert('Error', response.message || 'Failed to generate meal plan');
      }
    } catch (error) {
      console.error('Error generating meal plan:', error);
      Alert.alert(
        'Error',
        'Failed to generate meal plan. Please try again.'
      );
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        {/* Header */}
        <Text style={styles.title}>Create Meal Plan</Text>
        <Text style={styles.subtitle}>
          Customize your preferences and let our AI nutritionist create a
          personalized 7-day meal plan for you.
        </Text>

        {/* Calorie Target */}
        <Card style={styles.card}>
          <Card.Content>
            <Text style={styles.sectionTitle}>Calorie Target (Optional)</Text>
            <Text style={styles.sectionDescription}>
              Leave empty to auto-calculate based on your profile
            </Text>
            <TextInput
              label="Daily Calories"
              value={calorieTarget}
              onChangeText={setCalorieTarget}
              keyboardType="numeric"
              mode="outlined"
              placeholder="e.g., 2000"
              style={styles.input}
              disabled={isGenerating}
            />
          </Card.Content>
        </Card>

        {/* Dietary Preferences */}
        <Card style={styles.card}>
          <Card.Content>
            <Text style={styles.sectionTitle}>Dietary Preferences</Text>
            <Text style={styles.sectionDescription}>
              Select all that apply (optional)
            </Text>
            <View style={styles.chipContainer}>
              {DIETARY_OPTIONS.map((diet) => (
                <Chip
                  key={diet}
                  selected={selectedDiets.includes(diet)}
                  onPress={() => toggleDiet(diet)}
                  style={styles.chip}
                  disabled={isGenerating}
                >
                  {diet}
                </Chip>
              ))}
            </View>
          </Card.Content>
        </Card>

        {/* Allergies */}
        <Card style={styles.card}>
          <Card.Content>
            <Text style={styles.sectionTitle}>Allergies & Restrictions</Text>
            <Text style={styles.sectionDescription}>
              Select all that apply (optional)
            </Text>
            <View style={styles.chipContainer}>
              {COMMON_ALLERGIES.map((allergy) => (
                <Chip
                  key={allergy}
                  selected={selectedAllergies.includes(allergy)}
                  onPress={() => toggleAllergy(allergy)}
                  style={styles.chip}
                  disabled={isGenerating}
                >
                  {allergy}
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
              Generating your personalized meal plan...
            </Text>
            <Text style={styles.generatingSubtext}>
              This may take 10-30 seconds
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
              icon="chef-hat"
            >
              Generate Plan
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
