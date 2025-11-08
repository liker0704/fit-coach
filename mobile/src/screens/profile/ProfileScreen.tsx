import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import {
  Text,
  TextInput,
  Button,
  Card,
  Switch,
  SegmentedButtons,
  Divider,
  List,
} from 'react-native-paper';
import { useAuthStore } from '../../store/authStore';
import { colors, spacing, fontSizes } from '../../theme/colors';
import apiClient from '../../services/api/apiClient';

export default function ProfileScreen({ navigation }: any) {
  const { user, logout, updateUser } = useAuthStore();

  // Profile fields
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [email, setEmail] = useState(user?.email || '');
  const [age, setAge] = useState(user?.age?.toString() || '');
  const [height, setHeight] = useState(user?.height?.toString() || '');
  const [weight, setWeight] = useState(user?.weight_kg?.toString() || '');

  // Settings
  const [language, setLanguage] = useState('en');
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [darkMode, setDarkMode] = useState(false);

  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (user) {
      setFullName(user.full_name || '');
      setEmail(user.email || '');
      setAge(user.age?.toString() || '');
      setHeight(user.height?.toString() || '');
      setWeight(user.weight_kg?.toString() || '');
    }
  }, [user]);

  const handleSaveProfile = async () => {
    setIsSaving(true);

    try {
      const response = await apiClient.put('/users/me', {
        full_name: fullName,
        age: age ? parseInt(age) : null,
        height: height ? parseFloat(height) : null,
        weight_kg: weight ? parseFloat(weight) : null,
      });

      updateUser(response.data);

      Alert.alert('Success', 'Profile updated successfully!');
    } catch (error) {
      console.error('Profile update error:', error);
      Alert.alert('Error', 'Failed to update profile. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleLogout = () => {
    Alert.alert('Logout', 'Are you sure you want to logout?', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Logout',
        style: 'destructive',
        onPress: logout,
      },
    ]);
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        {/* Profile Section */}
        <Text style={styles.sectionTitle}>Profile Information</Text>

        <Card style={styles.card}>
          <Card.Content>
            <TextInput
              label="Full Name"
              value={fullName}
              onChangeText={setFullName}
              mode="outlined"
              style={styles.input}
            />

            <TextInput
              label="Email"
              value={email}
              mode="outlined"
              style={styles.input}
              disabled
              right={<TextInput.Icon icon="lock" />}
            />

            <TextInput
              label="Age"
              value={age}
              onChangeText={setAge}
              mode="outlined"
              keyboardType="numeric"
              style={styles.input}
              placeholder="e.g., 30"
            />

            <TextInput
              label="Height (cm)"
              value={height}
              onChangeText={setHeight}
              mode="outlined"
              keyboardType="numeric"
              style={styles.input}
              placeholder="e.g., 175"
            />

            <TextInput
              label="Weight (kg)"
              value={weight}
              onChangeText={setWeight}
              mode="outlined"
              keyboardType="numeric"
              style={styles.input}
              placeholder="e.g., 70"
            />

            <Button
              mode="contained"
              onPress={handleSaveProfile}
              loading={isSaving}
              disabled={isSaving}
              style={styles.saveButton}
            >
              Save Changes
            </Button>
          </Card.Content>
        </Card>

        {/* Settings Section */}
        <Text style={styles.sectionTitle}>Settings</Text>

        <Card style={styles.card}>
          <Card.Content>
            {/* Language */}
            <View style={styles.settingItem}>
              <Text style={styles.settingLabel}>Language</Text>
              <SegmentedButtons
                value={language}
                onValueChange={setLanguage}
                buttons={[
                  { value: 'en', label: 'EN' },
                  { value: 'ru', label: 'RU' },
                  { value: 'cz', label: 'CZ' },
                ]}
                style={styles.languageSelector}
              />
            </View>

            <Divider style={styles.divider} />

            {/* Notifications */}
            <View style={styles.settingRow}>
              <View style={styles.settingInfo}>
                <Text style={styles.settingLabel}>Notifications</Text>
                <Text style={styles.settingDescription}>
                  Daily reminders and insights
                </Text>
              </View>
              <Switch
                value={notificationsEnabled}
                onValueChange={setNotificationsEnabled}
                color={colors.primary}
              />
            </View>

            <Divider style={styles.divider} />

            {/* Dark Mode */}
            <View style={styles.settingRow}>
              <View style={styles.settingInfo}>
                <Text style={styles.settingLabel}>Dark Mode</Text>
                <Text style={styles.settingDescription}>
                  Switch to dark theme
                </Text>
              </View>
              <Switch
                value={darkMode}
                onValueChange={setDarkMode}
                color={colors.primary}
                disabled
              />
            </View>
          </Card.Content>
        </Card>

        {/* About Section */}
        <Text style={styles.sectionTitle}>About</Text>

        <Card style={styles.card}>
          <List.Item
            title="Version"
            description="1.0.0"
            left={(props) => <List.Icon {...props} icon="information" />}
          />
          <Divider />
          <List.Item
            title="Privacy Policy"
            left={(props) => <List.Icon {...props} icon="shield-lock" />}
            right={(props) => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => {
              // Navigate to privacy policy
            }}
          />
          <Divider />
          <List.Item
            title="Terms of Service"
            left={(props) => <List.Icon {...props} icon="file-document" />}
            right={(props) => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => {
              // Navigate to terms
            }}
          />
        </Card>

        {/* Logout Button */}
        <Button
          mode="outlined"
          onPress={handleLogout}
          icon="logout"
          style={styles.logoutButton}
          textColor={colors.error}
        >
          Logout
        </Button>

        <View style={styles.footer}>
          <Text style={styles.footerText}>Made with ❤️ by FitCoach Team</Text>
        </View>
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
  sectionTitle: {
    fontSize: fontSizes.lg,
    fontWeight: '700',
    color: colors.text,
    marginTop: spacing.lg,
    marginBottom: spacing.md,
  },
  card: {
    marginBottom: spacing.lg,
    backgroundColor: colors.backgroundSecondary,
  },
  input: {
    marginBottom: spacing.md,
  },
  saveButton: {
    marginTop: spacing.md,
  },
  settingItem: {
    marginBottom: spacing.md,
  },
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: spacing.sm,
  },
  settingInfo: {
    flex: 1,
  },
  settingLabel: {
    fontSize: fontSizes.md,
    fontWeight: '600',
    color: colors.text,
  },
  settingDescription: {
    fontSize: fontSizes.sm,
    color: colors.textSecondary,
    marginTop: 2,
  },
  languageSelector: {
    marginTop: spacing.sm,
  },
  divider: {
    marginVertical: spacing.md,
  },
  logoutButton: {
    marginTop: spacing.xl,
    marginBottom: spacing.xl,
    borderColor: colors.error,
  },
  footer: {
    alignItems: 'center',
    paddingVertical: spacing.xl,
  },
  footerText: {
    fontSize: fontSizes.sm,
    color: colors.textTertiary,
  },
});
