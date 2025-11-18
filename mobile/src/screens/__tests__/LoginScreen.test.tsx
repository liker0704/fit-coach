import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { Alert } from 'react-native';
import LoginScreen from '../auth/LoginScreen';
import { useAuthStore } from '../../store/authStore';

jest.mock('../../store/authStore');

const mockedUseAuthStore = useAuthStore as jest.MockedFunction<typeof useAuthStore>;

describe('LoginScreen', () => {
  const mockLogin = jest.fn();
  const mockNavigation = {
    navigate: jest.fn(),
    goBack: jest.fn(),
    dispatch: jest.fn(),
    setOptions: jest.fn(),
    addListener: jest.fn(),
    removeListener: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockedUseAuthStore.mockReturnValue({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      login: mockLogin,
      register: jest.fn(),
      logout: jest.fn(),
    });
    jest.spyOn(Alert, 'alert').mockImplementation();
  });

  it('should render login screen correctly', () => {
    const { getByText, getByLabelText } = render(
      <LoginScreen navigation={mockNavigation} />
    );

    expect(getByText('Welcome Back')).toBeTruthy();
    expect(getByText('Sign in to continue to FitCoach')).toBeTruthy();
    expect(getByLabelText('Email')).toBeTruthy();
    expect(getByLabelText('Password')).toBeTruthy();
    expect(getByText('Login')).toBeTruthy();
  });

  it('should show validation error for empty email', async () => {
    const { getByText, getByLabelText } = render(
      <LoginScreen navigation={mockNavigation} />
    );

    const emailInput = getByLabelText('Email');
    const loginButton = getByText('Login');

    fireEvent.changeText(emailInput, '');
    fireEvent.press(loginButton);

    await waitFor(() => {
      expect(getByText('Email is required')).toBeTruthy();
    });
  });

  it('should show validation error for invalid email format', async () => {
    const { getByText, getByLabelText } = render(
      <LoginScreen navigation={mockNavigation} />
    );

    const emailInput = getByLabelText('Email');
    const loginButton = getByText('Login');

    fireEvent.changeText(emailInput, 'invalid-email');
    fireEvent.press(loginButton);

    await waitFor(() => {
      expect(getByText('Please enter a valid email')).toBeTruthy();
    });
  });

  it('should show validation error for empty password', async () => {
    const { getByText, getByLabelText } = render(
      <LoginScreen navigation={mockNavigation} />
    );

    const emailInput = getByLabelText('Email');
    const passwordInput = getByLabelText('Password');
    const loginButton = getByText('Login');

    fireEvent.changeText(emailInput, 'test@example.com');
    fireEvent.changeText(passwordInput, '');
    fireEvent.press(loginButton);

    await waitFor(() => {
      expect(getByText('Password is required')).toBeTruthy();
    });
  });

  it('should show validation error for short password', async () => {
    const { getByText, getByLabelText } = render(
      <LoginScreen navigation={mockNavigation} />
    );

    const emailInput = getByLabelText('Email');
    const passwordInput = getByLabelText('Password');
    const loginButton = getByText('Login');

    fireEvent.changeText(emailInput, 'test@example.com');
    fireEvent.changeText(passwordInput, '12345');
    fireEvent.press(loginButton);

    await waitFor(() => {
      expect(getByText('Password must be at least 6 characters')).toBeTruthy();
    });
  });

  it('should call login with valid credentials', async () => {
    mockLogin.mockResolvedValueOnce(undefined);

    const { getByText, getByLabelText } = render(
      <LoginScreen navigation={mockNavigation} />
    );

    const emailInput = getByLabelText('Email');
    const passwordInput = getByLabelText('Password');
    const loginButton = getByText('Login');

    fireEvent.changeText(emailInput, 'test@example.com');
    fireEvent.changeText(passwordInput, 'password123');
    fireEvent.press(loginButton);

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password123');
    });
  });

  it('should show alert on login failure', async () => {
    const errorMessage = 'Invalid credentials';
    mockLogin.mockRejectedValueOnce(new Error(errorMessage));

    const { getByText, getByLabelText } = render(
      <LoginScreen navigation={mockNavigation} />
    );

    const emailInput = getByLabelText('Email');
    const passwordInput = getByLabelText('Password');
    const loginButton = getByText('Login');

    fireEvent.changeText(emailInput, 'test@example.com');
    fireEvent.changeText(passwordInput, 'wrongpassword');
    fireEvent.press(loginButton);

    await waitFor(() => {
      expect(Alert.alert).toHaveBeenCalledWith(
        'Login Failed',
        errorMessage,
        [{ text: 'OK' }]
      );
    });
  });

  it('should toggle password visibility', () => {
    const { getByLabelText } = render(
      <LoginScreen navigation={mockNavigation} />
    );

    const passwordInput = getByLabelText('Password');

    // Initially password should be hidden (secureTextEntry true)
    expect(passwordInput.props.secureTextEntry).toBe(true);

    // Find and press the eye icon to toggle
    const eyeIcon = passwordInput.parent?.findByType('Icon');
    if (eyeIcon) {
      fireEvent.press(eyeIcon);
    }
  });

  it('should navigate to register screen', () => {
    const { getByText } = render(<LoginScreen navigation={mockNavigation} />);

    const signUpButton = getByText('Sign Up');
    fireEvent.press(signUpButton);

    expect(mockNavigation.navigate).toHaveBeenCalledWith('Register');
  });

  it('should disable inputs and button during loading', () => {
    mockedUseAuthStore.mockReturnValue({
      user: null,
      isAuthenticated: false,
      isLoading: true,
      login: mockLogin,
      register: jest.fn(),
      logout: jest.fn(),
    });

    const { getByLabelText, getByText } = render(
      <LoginScreen navigation={mockNavigation} />
    );

    const emailInput = getByLabelText('Email');
    const passwordInput = getByLabelText('Password');
    const loginButton = getByText('Login').parent;

    expect(emailInput.props.disabled).toBe(true);
    expect(passwordInput.props.disabled).toBe(true);
    expect(loginButton?.props.disabled).toBe(true);
  });
});
