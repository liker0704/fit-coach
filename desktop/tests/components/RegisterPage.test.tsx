import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import userEvent from '@testing-library/user-event';
import RegisterPage from '@/pages/auth/RegisterPage';
import { authService } from '@/services/modules/authService';

// Mock dependencies
jest.mock('@/services/modules/authService');
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
}));

jest.mock('@/store', () => ({
  useStore: () => ({
    setTokens: jest.fn(),
    setUser: jest.fn(),
  }),
}));

jest.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: jest.fn(),
  }),
}));

const renderRegisterPage = () => {
  return render(
    <BrowserRouter>
      <RegisterPage />
    </BrowserRouter>
  );
};

describe('RegisterPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('rendering', () => {
    it('should render registration form with all fields', () => {
      renderRegisterPage();

      expect(screen.getByText(/create an account/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /sign up/i })).toBeInTheDocument();
    });

    it('should render link to login page', () => {
      renderRegisterPage();

      const loginLink = screen.getByRole('link', { name: /sign in/i });
      expect(loginLink).toBeInTheDocument();
      expect(loginLink).toHaveAttribute('href', '/login');
    });
  });

  describe('form validation', () => {
    it('should show error for invalid email', async () => {
      renderRegisterPage();

      const emailInput = screen.getByLabelText(/email/i);
      const submitButton = screen.getByRole('button', { name: /sign up/i });

      await userEvent.type(emailInput, 'invalid-email');
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/invalid email address/i)).toBeInTheDocument();
      });
    });

    it('should show error for short username', async () => {
      renderRegisterPage();

      const usernameInput = screen.getByLabelText(/username/i);
      const submitButton = screen.getByRole('button', { name: /sign up/i });

      await userEvent.type(usernameInput, 'ab');
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/username must be at least 3 characters/i)).toBeInTheDocument();
      });
    });

    it('should show error for short password', async () => {
      renderRegisterPage();

      const emailInput = screen.getByLabelText(/email/i);
      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/^password$/i);
      const submitButton = screen.getByRole('button', { name: /sign up/i });

      await userEvent.type(emailInput, 'test@example.com');
      await userEvent.type(usernameInput, 'testuser');
      await userEvent.type(passwordInput, '123');
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/password must be at least 8 characters/i)).toBeInTheDocument();
      });
    });

    it('should clear errors when user starts typing', async () => {
      renderRegisterPage();

      const emailInput = screen.getByLabelText(/email/i);
      const submitButton = screen.getByRole('button', { name: /sign up/i });

      // Trigger validation error
      await userEvent.type(emailInput, 'invalid');
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/invalid email address/i)).toBeInTheDocument();
      });

      // Start typing again
      await userEvent.clear(emailInput);
      await userEvent.type(emailInput, 'test@example.com');

      // Error should be cleared
      expect(screen.queryByText(/invalid email address/i)).not.toBeInTheDocument();
    });
  });

  describe('form submission', () => {
    it('should successfully register with valid data', async () => {
      const mockRegisterResponse = {
        id: 1,
        email: 'newuser@example.com',
        username: 'newuser',
        created_at: '2024-01-01T00:00:00Z',
      };

      const mockLoginResponse = {
        access_token: 'mock-access-token',
        refresh_token: 'mock-refresh-token',
        user: mockRegisterResponse,
      };

      (authService.register as jest.Mock).mockResolvedValueOnce(mockRegisterResponse);
      (authService.login as jest.Mock).mockResolvedValueOnce(mockLoginResponse);

      renderRegisterPage();

      const emailInput = screen.getByLabelText(/email/i);
      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/^password$/i);
      const submitButton = screen.getByRole('button', { name: /sign up/i });

      await userEvent.type(emailInput, 'newuser@example.com');
      await userEvent.type(usernameInput, 'newuser');
      await userEvent.type(passwordInput, 'password123');
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(authService.register).toHaveBeenCalledWith({
          email: 'newuser@example.com',
          username: 'newuser',
          password: 'password123',
        });
      });
    });

    it('should show loading state during submission', async () => {
      (authService.register as jest.Mock).mockImplementationOnce(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      );

      renderRegisterPage();

      const emailInput = screen.getByLabelText(/email/i);
      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/^password$/i);
      const submitButton = screen.getByRole('button', { name: /sign up/i });

      await userEvent.type(emailInput, 'test@example.com');
      await userEvent.type(usernameInput, 'testuser');
      await userEvent.type(passwordInput, 'password123');
      await userEvent.click(submitButton);

      // Should show loading state
      expect(screen.getByText(/creating account/i)).toBeInTheDocument();
      expect(submitButton).toBeDisabled();
    });

    it('should disable form fields during submission', async () => {
      (authService.register as jest.Mock).mockImplementationOnce(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      );

      renderRegisterPage();

      const emailInput = screen.getByLabelText(/email/i);
      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/^password$/i);
      const submitButton = screen.getByRole('button', { name: /sign up/i });

      await userEvent.type(emailInput, 'test@example.com');
      await userEvent.type(usernameInput, 'testuser');
      await userEvent.type(passwordInput, 'password123');
      await userEvent.click(submitButton);

      // Fields should be disabled
      expect(emailInput).toBeDisabled();
      expect(usernameInput).toBeDisabled();
      expect(passwordInput).toBeDisabled();
      expect(submitButton).toBeDisabled();
    });

    it('should handle registration failure', async () => {
      (authService.register as jest.Mock).mockRejectedValueOnce(
        new Error('Email already exists')
      );

      renderRegisterPage();

      const emailInput = screen.getByLabelText(/email/i);
      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/^password$/i);
      const submitButton = screen.getByRole('button', { name: /sign up/i });

      await userEvent.type(emailInput, 'existing@example.com');
      await userEvent.type(usernameInput, 'testuser');
      await userEvent.type(passwordInput, 'password123');
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(authService.register).toHaveBeenCalled();
      });

      // Form should be enabled again after error
      await waitFor(() => {
        expect(submitButton).not.toBeDisabled();
      });
    });
  });

  describe('password visibility toggle', () => {
    it('should toggle password visibility', async () => {
      renderRegisterPage();

      const passwordInput = screen.getByLabelText(/^password$/i);
      const toggleButtons = screen.getAllByRole('button', { name: '' });

      // Initially password type
      expect(passwordInput).toHaveAttribute('type', 'password');

      // Click to show (first toggle button for password)
      await userEvent.click(toggleButtons[0]);
      expect(passwordInput).toHaveAttribute('type', 'text');

      // Click to hide
      await userEvent.click(toggleButtons[0]);
      expect(passwordInput).toHaveAttribute('type', 'password');
    });
  });
});
