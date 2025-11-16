import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Alert,
} from 'react-native';
import { TextInput, Button, Text, HelperText } from 'react-native-paper';
import { useAuthStore } from '../../store/authStore';
import { colors, spacing, fontSizes } from '../../theme/colors';

export default function LoginScreen({ navigation }: any) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [emailError, setEmailError] = useState('');
  const [passwordError, setPasswordError] = useState('');

  const { login, isLoading } = useAuthStore();

  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email) {
      setEmailError('Email is required');
      return false;
    }
    if (!emailRegex.test(email)) {
      setEmailError('Please enter a valid email');
      return false;
    }
    setEmailError('');
    return true;
  };

  const validatePassword = (password: string): boolean => {
    if (!password) {
      setPasswordError('Password is required');
      return false;
    }
    if (password.length < 6) {
      setPasswordError('Password must be at least 6 characters');
      return false;
    }
    setPasswordError('');
    return true;
  };

  const handleLogin = async () => {
    const isEmailValid = validateEmail(email);
    const isPasswordValid = validatePassword(password);

    if (!isEmailValid || !isPasswordValid) {
      return;
    }

    try {
      await login(email, password);
      // Navigation handled by root navigator when isAuthenticated changes
    } catch (error) {
      Alert.alert(
        'Login Failed',
        error instanceof Error ? error.message : 'Please check your credentials and try again.',
        [{ text: 'OK' }]
      );
    }
  };

  const handleGoToRegister = () => {
    navigation.navigate('Register');
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 64 : 0}
    >
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
      >
        <View style={styles.content}>
          {/* Header */}
          <View style={styles.header}>
            <Text style={styles.title}>Welcome Back</Text>
            <Text style={styles.subtitle}>Sign in to continue to FitCoach</Text>
          </View>

          {/* Form */}
          <View style={styles.form}>
            <TextInput
              label="Email"
              value={email}
              onChangeText={setEmail}
              onBlur={() => validateEmail(email)}
              mode="outlined"
              keyboardType="email-address"
              autoCapitalize="none"
              autoComplete="email"
              error={!!emailError}
              disabled={isLoading}
              style={styles.input}
            />
            <HelperText type="error" visible={!!emailError}>
              {emailError}
            </HelperText>

            <TextInput
              label="Password"
              value={password}
              onChangeText={setPassword}
              onBlur={() => validatePassword(password)}
              mode="outlined"
              secureTextEntry={!showPassword}
              autoCapitalize="none"
              autoComplete="password"
              error={!!passwordError}
              disabled={isLoading}
              right={
                <TextInput.Icon
                  icon={showPassword ? 'eye-off' : 'eye'}
                  onPress={() => setShowPassword(!showPassword)}
                />
              }
              style={styles.input}
            />
            <HelperText type="error" visible={!!passwordError}>
              {passwordError}
            </HelperText>
          </View>

          {/* Actions */}
          <Button
            mode="contained"
            onPress={handleLogin}
            loading={isLoading}
            disabled={isLoading}
            style={styles.loginButton}
            contentStyle={styles.loginButtonContent}
          >
            Login
          </Button>

          {/* Register Link */}
          <View style={styles.registerContainer}>
            <Text style={styles.registerText}>Don't have an account? </Text>
            <Button
              mode="text"
              onPress={handleGoToRegister}
              disabled={isLoading}
              compact
            >
              Sign Up
            </Button>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
  },
  content: {
    padding: spacing.lg,
  },
  header: {
    marginBottom: spacing.xl,
    alignItems: 'center',
  },
  title: {
    fontSize: fontSizes.xxxl,
    fontWeight: '700',
    color: colors.text,
    marginBottom: spacing.sm,
  },
  subtitle: {
    fontSize: fontSizes.md,
    color: colors.textSecondary,
  },
  form: {
    marginBottom: spacing.lg,
  },
  input: {
    marginBottom: spacing.xs,
  },
  loginButton: {
    marginTop: spacing.md,
  },
  loginButtonContent: {
    paddingVertical: spacing.sm,
  },
  registerContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: spacing.lg,
  },
  registerText: {
    fontSize: fontSizes.md,
    color: colors.textSecondary,
  },
});
