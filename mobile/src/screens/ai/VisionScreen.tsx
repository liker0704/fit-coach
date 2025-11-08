import React, { useState } from 'react';
import { View, StyleSheet, Image, ScrollView, Alert } from 'react-native';
import {
  Text,
  Button,
  Card,
  ActivityIndicator,
  IconButton,
} from 'react-native-paper';
import * as ImagePicker from 'expo-image-picker';
import { colors, spacing, fontSizes } from '../../theme/colors';
import { agentService, VisionAnalysisResult } from '../../services/api/agentService';
import { mealService } from '../../services/api/mealService';

export default function VisionScreen({ navigation }: any) {
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<VisionAnalysisResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // Request permissions
  const requestPermissions = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert(
        'Permission Required',
        'Please grant photo library permissions to use this feature.'
      );
      return false;
    }
    return true;
  };

  // Pick image from gallery
  const pickImage = async () => {
    const hasPermission = await requestPermissions();
    if (!hasPermission) return;

    const result = await ImagePicker.launchImagePickerAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      quality: 0.8,
      base64: true,
    });

    if (!result.canceled && result.assets[0]) {
      setImageUri(result.assets[0].uri);
      analyzeImage(result.assets[0].base64!);
    }
  };

  // Take photo
  const takePhoto = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert(
        'Permission Required',
        'Please grant camera permissions to use this feature.'
      );
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      allowsEditing: true,
      quality: 0.8,
      base64: true,
    });

    if (!result.canceled && result.assets[0]) {
      setImageUri(result.assets[0].uri);
      analyzeImage(result.assets[0].base64!);
    }
  };

  // Analyze image
  const analyzeImage = async (base64: string) => {
    setIsLoading(true);
    setAnalysis(null);

    try {
      const result = await agentService.analyzeFood(base64);
      setAnalysis(result);
    } catch (error) {
      console.error('Vision analysis error:', error);
      Alert.alert(
        'Analysis Failed',
        'Could not analyze the image. Please try again.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  // Save meal to today
  const saveMeal = async () => {
    if (!analysis) return;

    setIsSaving(true);

    try {
      const today = new Date().toISOString().split('T')[0];

      await mealService.createMeal(today, {
        name: analysis.meal_name,
        category: 'dinner',
        calories: analysis.calories,
        protein: analysis.protein,
        carbs: analysis.carbs,
        fats: analysis.fats,
        items: analysis.items,
      });

      Alert.alert(
        'Success',
        'Meal saved to today!',
        [
          {
            text: 'View Day',
            onPress: () =>
              navigation.navigate('Calendar', {
                screen: 'DayScreen',
                params: { date: today },
              }),
          },
          { text: 'OK' },
        ]
      );

      // Reset
      setImageUri(null);
      setAnalysis(null);
    } catch (error) {
      console.error('Save meal error:', error);
      Alert.alert('Error', 'Failed to save meal. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        {/* Header */}
        <Text style={styles.title}>Vision Agent</Text>
        <Text style={styles.subtitle}>
          Take a photo of your meal and I'll analyze its nutrition
        </Text>

        {/* Action Buttons */}
        {!imageUri && (
          <View style={styles.actionButtons}>
            <Button
              mode="contained"
              icon="camera"
              onPress={takePhoto}
              style={styles.actionButton}
            >
              Take Photo
            </Button>
            <Button
              mode="outlined"
              icon="image"
              onPress={pickImage}
              style={styles.actionButton}
            >
              Choose from Gallery
            </Button>
          </View>
        )}

        {/* Image Preview */}
        {imageUri && (
          <Card style={styles.imageCard}>
            <Card.Content>
              <View style={styles.imageContainer}>
                <Image source={{ uri: imageUri }} style={styles.image} />
                <IconButton
                  icon="close-circle"
                  size={32}
                  iconColor={colors.error}
                  onPress={() => {
                    setImageUri(null);
                    setAnalysis(null);
                  }}
                  style={styles.closeButton}
                />
              </View>
            </Card.Content>
          </Card>
        )}

        {/* Loading */}
        {isLoading && (
          <Card style={styles.loadingCard}>
            <Card.Content style={styles.loadingContent}>
              <ActivityIndicator size="large" color={colors.primary} />
              <Text style={styles.loadingText}>Analyzing image...</Text>
            </Card.Content>
          </Card>
        )}

        {/* Analysis Result */}
        {analysis && !isLoading && (
          <Card style={styles.resultCard}>
            <Card.Title
              title={analysis.meal_name}
              titleVariant="titleLarge"
              subtitle={`Confidence: ${(analysis.confidence * 100).toFixed(0)}%`}
            />
            <Card.Content>
              {/* Nutrition Info */}
              <View style={styles.nutritionGrid}>
                <View style={styles.nutritionItem}>
                  <Text style={styles.nutritionValue}>
                    {analysis.calories}
                  </Text>
                  <Text style={styles.nutritionLabel}>kcal</Text>
                </View>
                <View style={styles.nutritionItem}>
                  <Text style={styles.nutritionValue}>{analysis.protein}g</Text>
                  <Text style={styles.nutritionLabel}>Protein</Text>
                </View>
                <View style={styles.nutritionItem}>
                  <Text style={styles.nutritionValue}>{analysis.carbs}g</Text>
                  <Text style={styles.nutritionLabel}>Carbs</Text>
                </View>
                <View style={styles.nutritionItem}>
                  <Text style={styles.nutritionValue}>{analysis.fats}g</Text>
                  <Text style={styles.nutritionLabel}>Fats</Text>
                </View>
              </View>

              {/* Items */}
              {analysis.items && analysis.items.length > 0 && (
                <View style={styles.itemsSection}>
                  <Text style={styles.itemsTitle}>Detected Items:</Text>
                  {analysis.items.map((item, index) => (
                    <Text key={index} style={styles.item}>
                      • {item.name} ({item.amount})
                    </Text>
                  ))}
                </View>
              )}
            </Card.Content>
            <Card.Actions>
              <Button onPress={() => setImageUri(null)}>Try Another</Button>
              <Button
                mode="contained"
                onPress={saveMeal}
                loading={isSaving}
                disabled={isSaving}
              >
                Save to Today
              </Button>
            </Card.Actions>
          </Card>
        )}

        {/* Instructions */}
        {!imageUri && !isLoading && (
          <Card style={styles.instructionsCard}>
            <Card.Content>
              <Text style={styles.instructionsTitle}>Tips for best results:</Text>
              <Text style={styles.instructionItem}>
                • Take photos in good lighting
              </Text>
              <Text style={styles.instructionItem}>
                • Include the entire meal in the frame
              </Text>
              <Text style={styles.instructionItem}>
                • Avoid blurry or dark images
              </Text>
              <Text style={styles.instructionItem}>
                • Take photos from directly above
              </Text>
            </Card.Content>
          </Card>
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
    marginBottom: spacing.xl,
  },
  actionButtons: {
    gap: spacing.md,
    marginBottom: spacing.xl,
  },
  actionButton: {
    paddingVertical: spacing.sm,
  },
  imageCard: {
    marginBottom: spacing.lg,
    backgroundColor: colors.backgroundSecondary,
  },
  imageContainer: {
    position: 'relative',
  },
  image: {
    width: '100%',
    height: 300,
    borderRadius: 12,
  },
  closeButton: {
    position: 'absolute',
    top: -8,
    right: -8,
    backgroundColor: colors.background,
  },
  loadingCard: {
    marginBottom: spacing.lg,
    backgroundColor: colors.backgroundSecondary,
  },
  loadingContent: {
    alignItems: 'center',
    paddingVertical: spacing.xl,
  },
  loadingText: {
    marginTop: spacing.md,
    fontSize: fontSizes.md,
    color: colors.textSecondary,
  },
  resultCard: {
    marginBottom: spacing.lg,
    backgroundColor: colors.backgroundSecondary,
  },
  nutritionGrid: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginVertical: spacing.lg,
  },
  nutritionItem: {
    alignItems: 'center',
  },
  nutritionValue: {
    fontSize: fontSizes.xl,
    fontWeight: '700',
    color: colors.primary,
  },
  nutritionLabel: {
    fontSize: fontSizes.sm,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  itemsSection: {
    marginTop: spacing.lg,
  },
  itemsTitle: {
    fontSize: fontSizes.md,
    fontWeight: '600',
    color: colors.text,
    marginBottom: spacing.sm,
  },
  item: {
    fontSize: fontSizes.md,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  instructionsCard: {
    backgroundColor: colors.backgroundSecondary,
  },
  instructionsTitle: {
    fontSize: fontSizes.md,
    fontWeight: '600',
    color: colors.text,
    marginBottom: spacing.md,
  },
  instructionItem: {
    fontSize: fontSizes.md,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
});
