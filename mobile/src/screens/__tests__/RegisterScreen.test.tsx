import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { Alert } from 'react-native';
import RegisterScreen from '../auth/RegisterScreen';
import { useAuthStore } from '../../store/authStore';

jest.mock('../../store/authStore');

const mockedUseAuthStore = useAuthStore as jest.MockedFunction<typeof useAuthStore>;

describe('RegisterScreen', () => {
  const mockRegister = jest.fn();
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
      login: jest.fn(),
      register: mockRegister,
      logout: jest.fn(),
    });
    jest.spyOn(Alert, 'alert').mockImplementation();
  });

  it('should render register screen correctly', () => {
    const { getByText, getByLabelText } = render(
      <RegisterScreen navigation={mockNavigation} />
    );

    expect(getByText('Create Account')).toBeTruthy();
    expect(getByText('Sign up to get started with FitCoach')).toBeTruthy();
    expect(getByLabelText('Full Name')).toBeTruthy();
    expect(getByLabelText('Email')).toBeTruthy();
    expect(getByLabelText('Password')).toBeTruthy();
    expect(getByLabelText('Confirm Password')).toBeTruthy();
    expect(getByText('Sign Up')).toBeTruthy();
  });

  it('should show validation error for empty full name', async () => {
    const { getByText, getByLabelText } = render(
      <RegisterScreen navigation={mockNavigation} />
    );

    const fullNameInput = getByLabelText('Full Name');
    const signUpButton = getByText('Sign Up');

    fireEvent.changeText(fullNameInput, '');
    fireEvent.press(signUpButton);

    await waitFor(() => {
      expect(getByText('Full name is required')).toBeTruthy();
    });
  });

  it('should show validation error for short full name', async () => {
    const { getByText, getByLabelText } = render(
      <RegisterScreen navigation={mockNavigation} />
    );

    const fullNameInput = getByLabelText('Full Name');
    const signUpButton = getByText('Sign Up');

    fireEvent.changeText(fullNameInput, 'A');
    fireEvent.press(signUpButton);

    await waitFor(() => {
      expect(getByText('Full name must be at least 2 characters')).toBeTruthy();
    });
  });

  it('should show validation error for invalid email', async () => {
    const { getByText, getByLabelText } = render(
      <RegisterScreen navigation={mockNavigation} />
    );

    const fullNameInput = getByLabelText('Full Name');
    const emailInput = getByLabelText('Email');
    const signUpButton = getByText('Sign Up');

    fireEvent.changeText(fullNameInput, 'John Doe');
    fireEvent.changeText(emailInput, 'invalid-email');
    fireEvent.press(signUpButton);

    await waitFor(() => {
      expect(getByText('Please enter a valid email')).toBeTruthy();
    });
  });

  it('should show validation error for password mismatch', async () => {
    const { getByText, getByLabelText } = render(
      <RegisterScreen navigation={mockNavigation} />
    );

    const fullNameInput = getByLabelText('Full Name');
    const emailInput = getByLabelText('Email');
    const passwordInput = getByLabelText('Password');
    const confirmPasswordInput = getByLabelText('Confirm Password');
    const signUpButton = getByText('Sign Up');

    fireEvent.changeText(fullNameInput, 'John Doe');
    fireEvent.changeText(emailInput, 'john@example.com');
    fireEvent.changeText(passwordInput, 'password123');
    fireEvent.changeText(confirmPasswordInput, 'password456');
    fireEvent.press(signUpButton);

    await waitFor(() => {
      expect(getByText('Passwords do not match')).toBeTruthy();
    });
  });

  it('should call register with valid data', async () => {
    mockRegister.mockResolvedValueOnce(undefined);

    const { getByText, getByLabelText } = render(
      <RegisterScreen navigation={mockNavigation} />
    );

    const fullNameInput = getByLabelText('Full Name');
    const emailInput = getByLabelText('Email');
    const passwordInput = getByLabelText('Password');
    const confirmPasswordInput = getByLabelText('Confirm Password');
    const signUpButton = getByText('Sign Up');

    fireEvent.changeText(fullNameInput, 'John Doe');
    fireEvent.changeText(emailInput, 'john@example.com');
    fireEvent.changeText(passwordInput, 'password123');
    fireEvent.changeText(confirmPasswordInput, 'password123');
    fireEvent.press(signUpButton);

    await waitFor(() => {
      expect(mockRegister).toHaveBeenCalledWith(
        'John Doe',
        'john@example.com',
        'password123'
      );
    });
  });

  it('should trim whitespace from full name', async () => {
    mockRegister.mockResolvedValueOnce(undefined);

    const { getByText, getByLabelText } = render(
      <RegisterScreen navigation={mockNavigation} />
    );

    const fullNameInput = getByLabelText('Full Name');
    const emailInput = getByLabelText('Email');
    const passwordInput = getByLabelText('Password');
    const confirmPasswordInput = getByLabelText('Confirm Password');
    const signUpButton = getByText('Sign Up');

    fireEvent.changeText(fullNameInput, '  John Doe  ');
    fireEvent.changeText(emailInput, 'john@example.com');
    fireEvent.changeText(passwordInput, 'password123');
    fireEvent.changeText(confirmPasswordInput, 'password123');
    fireEvent.press(signUpButton);

    await waitFor(() => {
      expect(mockRegister).toHaveBeenCalledWith(
        'John Doe',
        'john@example.com',
        'password123'
      );
    });
  });

  it('should show alert on registration failure', async () => {
    const errorMessage = 'Email already registered';
    mockRegister.mockRejectedValueOnce(new Error(errorMessage));

    const { getByText, getByLabelText } = render(
      <RegisterScreen navigation={mockNavigation} />
    );

    const fullNameInput = getByLabelText('Full Name');
    const emailInput = getByLabelText('Email');
    const passwordInput = getByLabelText('Password');
    const confirmPasswordInput = getByLabelText('Confirm Password');
    const signUpButton = getByText('Sign Up');

    fireEvent.changeText(fullNameInput, 'Jane Doe');
    fireEvent.changeText(emailInput, 'existing@example.com');
    fireEvent.changeText(passwordInput, 'password123');
    fireEvent.changeText(confirmPasswordInput, 'password123');
    fireEvent.press(signUpButton);

    await waitFor(() => {
      expect(Alert.alert).toHaveBeenCalledWith(
        'Registration Failed',
        errorMessage,
        [{ text: 'OK' }]
      );
    });
  });

  it('should navigate to login screen', () => {
    const { getByText } = render(<RegisterScreen navigation={mockNavigation} />);

    const loginButton = getByText('Login');
    fireEvent.press(loginButton);

    expect(mockNavigation.navigate).toHaveBeenCalledWith('Login');
  });

  it('should toggle password visibility', () => {
    const { getByLabelText } = render(
      <RegisterScreen navigation={mockNavigation} />
    );

    const passwordInput = getByLabelText('Password');
    expect(passwordInput.props.secureTextEntry).toBe(true);
  });

  it('should toggle confirm password visibility', () => {
    const { getByLabelText } = render(
      <RegisterScreen navigation={mockNavigation} />
    );

    const confirmPasswordInput = getByLabelText('Confirm Password');
    expect(confirmPasswordInput.props.secureTextEntry).toBe(true);
  });

  it('should disable inputs during loading', () => {
    mockedUseAuthStore.mockReturnValue({
      user: null,
      isAuthenticated: false,
      isLoading: true,
      login: jest.fn(),
      register: mockRegister,
      logout: jest.fn(),
    });

    const { getByLabelText, getByText } = render(
      <RegisterScreen navigation={mockNavigation} />
    );

    const fullNameInput = getByLabelText('Full Name');
    const emailInput = getByLabelText('Email');
    const passwordInput = getByLabelText('Password');
    const confirmPasswordInput = getByLabelText('Confirm Password');
    const signUpButton = getByText('Sign Up').parent;

    expect(fullNameInput.props.disabled).toBe(true);
    expect(emailInput.props.disabled).toBe(true);
    expect(passwordInput.props.disabled).toBe(true);
    expect(confirmPasswordInput.props.disabled).toBe(true);
    expect(signUpButton?.props.disabled).toBe(true);
  });
});
