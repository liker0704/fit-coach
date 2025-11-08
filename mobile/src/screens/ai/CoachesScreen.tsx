import React, { useState } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import {
  Text,
  Card,
  Button,
  Portal,
  Modal,
  TextInput,
  ActivityIndicator,
} from 'react-native-paper';
import { colors, spacing, fontSizes } from '../../theme/colors';
import { agentService, CoachResponse } from '../../services/api/agentService';

type CoachType = 'nutrition' | 'workout' | null;

export default function CoachesScreen() {
  const [selectedCoach, setSelectedCoach] = useState<CoachType>(null);
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState<CoachResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleAskCoach = async (type: 'nutrition' | 'workout') => {
    setIsLoading(true);
    setResponse(null);

    try {
      const today = new Date().toISOString().split('T')[0];
      let data: CoachResponse;

      if (type === 'nutrition') {
        data = await agentService.getNutritionAdvice(today, question || undefined);
      } else {
        data = await agentService.getWorkoutAdvice(today, question || undefined);
      }

      setResponse(data);
    } catch (error) {
      console.error('Coach error:', error);
      setResponse({
        advice:
          'Sorry, I encountered an error. Please try again or check your connection.',
        recommendations: [],
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCloseModal = () => {
    setSelectedCoach(null);
    setQuestion('');
    setResponse(null);
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        {/* Header */}
        <Text style={styles.title}>AI Coaches</Text>
        <Text style={styles.subtitle}>
          Get personalized advice from our AI-powered coaches
        </Text>

        {/* Nutrition Coach Card */}
        <Card style={styles.coachCard}>
          <Card.Cover
            source={{
              uri: 'https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=400',
            }}
            style={styles.coachImage}
          />
          <Card.Title
            title="Nutrition Coach"
            titleVariant="titleLarge"
            subtitle="Expert advice on your diet and nutrition"
          />
          <Card.Content>
            <Text style={styles.description}>
              Get personalized nutrition advice based on your daily food intake.
              Ask questions about calories, macros, meal timing, and more.
            </Text>
          </Card.Content>
          <Card.Actions>
            <Button
              mode="contained"
              onPress={() => setSelectedCoach('nutrition')}
              icon="food-apple"
            >
              Talk to Nutrition Coach
            </Button>
          </Card.Actions>
        </Card>

        {/* Workout Coach Card */}
        <Card style={styles.coachCard}>
          <Card.Cover
            source={{
              uri: 'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=400',
            }}
            style={styles.coachImage}
          />
          <Card.Title
            title="Workout Coach"
            titleVariant="titleLarge"
            subtitle="Optimize your training and recovery"
          />
          <Card.Content>
            <Text style={styles.description}>
              Get expert guidance on your workouts, exercise form, training
              volume, recovery, and performance optimization.
            </Text>
          </Card.Content>
          <Card.Actions>
            <Button
              mode="contained"
              onPress={() => setSelectedCoach('workout')}
              icon="dumbbell"
            >
              Talk to Workout Coach
            </Button>
          </Card.Actions>
        </Card>
      </View>

      {/* Coach Modal */}
      <Portal>
        <Modal
          visible={selectedCoach !== null}
          onDismiss={handleCloseModal}
          contentContainerStyle={styles.modal}
        >
          <ScrollView>
            <Text style={styles.modalTitle}>
              {selectedCoach === 'nutrition' ? 'Nutrition' : 'Workout'} Coach
            </Text>

            {/* Question Input */}
            {!response && (
              <View style={styles.questionSection}>
                <TextInput
                  label="Ask a question (optional)"
                  value={question}
                  onChangeText={setQuestion}
                  mode="outlined"
                  multiline
                  numberOfLines={3}
                  placeholder="e.g., Should I increase my protein intake?"
                  style={styles.questionInput}
                />
                <Button
                  mode="contained"
                  onPress={() =>
                    handleAskCoach(selectedCoach as 'nutrition' | 'workout')
                  }
                  loading={isLoading}
                  disabled={isLoading}
                  style={styles.askButton}
                >
                  {question ? 'Ask Question' : 'Get General Advice'}
                </Button>
              </View>
            )}

            {/* Loading */}
            {isLoading && (
              <View style={styles.loadingContainer}>
                <ActivityIndicator size="large" color={colors.primary} />
                <Text style={styles.loadingText}>
                  Analyzing your data...
                </Text>
              </View>
            )}

            {/* Response */}
            {response && !isLoading && (
              <View style={styles.responseSection}>
                <Card style={styles.responseCard}>
                  <Card.Content>
                    <Text style={styles.adviceTitle}>Advice:</Text>
                    <Text style={styles.adviceText}>{response.advice}</Text>

                    {response.recommendations.length > 0 && (
                      <>
                        <Text style={styles.recommendationsTitle}>
                          Recommendations:
                        </Text>
                        {response.recommendations.map((rec, index) => (
                          <Text key={index} style={styles.recommendation}>
                            • {rec}
                          </Text>
                        ))}
                      </>
                    )}
                  </Card.Content>
                </Card>

                <View style={styles.modalActions}>
                  <Button
                    mode="outlined"
                    onPress={() => {
                      setResponse(null);
                      setQuestion('');
                    }}
                  >
                    Ask Another Question
                  </Button>
                  <Button mode="contained" onPress={handleCloseModal}>
                    Close
                  </Button>
                </View>
              </View>
            )}
          </ScrollView>
        </Modal>
      </Portal>
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
    marginBottom: spacing.xl,
  },
  coachCard: {
    marginBottom: spacing.lg,
    backgroundColor: colors.backgroundSecondary,
  },
  coachImage: {
    height: 160,
  },
  description: {
    fontSize: fontSizes.md,
    color: colors.textSecondary,
    lineHeight: 22,
  },
  modal: {
    backgroundColor: colors.background,
    margin: spacing.lg,
    padding: spacing.lg,
    borderRadius: 12,
    maxHeight: '80%',
  },
  modalTitle: {
    fontSize: fontSizes.xl,
    fontWeight: '700',
    color: colors.text,
    marginBottom: spacing.lg,
  },
  questionSection: {
    marginBottom: spacing.lg,
  },
  questionInput: {
    marginBottom: spacing.md,
  },
  askButton: {
    marginTop: spacing.sm,
  },
  loadingContainer: {
    alignItems: 'center',
    paddingVertical: spacing.xl,
  },
  loadingText: {
    marginTop: spacing.md,
    fontSize: fontSizes.md,
    color: colors.textSecondary,
  },
  responseSection: {
    marginTop: spacing.md,
  },
  responseCard: {
    backgroundColor: colors.backgroundSecondary,
    marginBottom: spacing.lg,
  },
  adviceTitle: {
    fontSize: fontSizes.lg,
    fontWeight: '600',
    color: colors.text,
    marginBottom: spacing.sm,
  },
  adviceText: {
    fontSize: fontSizes.md,
    color: colors.text,
    lineHeight: 22,
    marginBottom: spacing.lg,
  },
  recommendationsTitle: {
    fontSize: fontSizes.md,
    fontWeight: '600',
    color: colors.text,
    marginBottom: spacing.sm,
  },
  recommendation: {
    fontSize: fontSizes.md,
    color: colors.text,
    marginBottom: spacing.xs,
    paddingLeft: spacing.sm,
  },
  modalActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: spacing.md,
  },
});
