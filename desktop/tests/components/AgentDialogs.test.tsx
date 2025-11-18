// Tests for ChatbotDialog and CoachDialog components
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ChatbotDialog from '@/components/agents/ChatbotDialog';
import CoachDialog from '@/components/agents/CoachDialog';
import { agentsService } from '@/services/modules/agentsService';

// Mock dependencies
jest.mock('@/services/modules/agentsService');

jest.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: jest.fn(),
  }),
}));

describe('ChatbotDialog', () => {
  const mockOnOpenChange = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('rendering', () => {
    it('should render when open', () => {
      render(<ChatbotDialog open={true} onOpenChange={mockOnOpenChange} />);

      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/ask me anything/i)).toBeInTheDocument();
    });

    it('should not render when closed', () => {
      render(<ChatbotDialog open={false} onOpenChange={mockOnOpenChange} />);

      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });

    it('should render send button', () => {
      render(<ChatbotDialog open={true} onOpenChange={mockOnOpenChange} />);

      expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument();
    });
  });

  describe('message sending', () => {
    it('should send message when send button clicked', async () => {
      const mockResponse = {
        response: 'This is a test response from the chatbot.',
        generated_at: '2024-01-15T10:00:00Z',
      };

      (agentsService.chat as jest.Mock).mockResolvedValueOnce(mockResponse);

      render(<ChatbotDialog open={true} onOpenChange={mockOnOpenChange} />);

      const input = screen.getByPlaceholderText(/ask me anything/i);
      const sendButton = screen.getByRole('button', { name: /send/i });

      await userEvent.type(input, 'What are the benefits of protein?');
      await userEvent.click(sendButton);

      await waitFor(() => {
        expect(agentsService.chat).toHaveBeenCalledWith({
          message: 'What are the benefits of protein?',
          conversation_history: [],
        });
      });
    });

    it('should clear input after sending message', async () => {
      const mockResponse = {
        response: 'Response',
        generated_at: '2024-01-15T10:00:00Z',
      };

      (agentsService.chat as jest.Mock).mockResolvedValueOnce(mockResponse);

      render(<ChatbotDialog open={true} onOpenChange={mockOnOpenChange} />);

      const input = screen.getByPlaceholderText(/ask me anything/i) as HTMLInputElement;
      const sendButton = screen.getByRole('button', { name: /send/i });

      await userEvent.type(input, 'Test message');
      expect(input.value).toBe('Test message');

      await userEvent.click(sendButton);

      await waitFor(() => {
        expect(input.value).toBe('');
      });
    });

    it('should not send empty message', async () => {
      render(<ChatbotDialog open={true} onOpenChange={mockOnOpenChange} />);

      const sendButton = screen.getByRole('button', { name: /send/i });
      await userEvent.click(sendButton);

      expect(agentsService.chat).not.toHaveBeenCalled();
    });

    it('should disable send button while loading', async () => {
      (agentsService.chat as jest.Mock).mockImplementationOnce(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      );

      render(<ChatbotDialog open={true} onOpenChange={mockOnOpenChange} />);

      const input = screen.getByPlaceholderText(/ask me anything/i);
      const sendButton = screen.getByRole('button', { name: /send/i });

      await userEvent.type(input, 'Test message');
      await userEvent.click(sendButton);

      expect(sendButton).toBeDisabled();
    });
  });

  describe('conversation history', () => {
    it('should maintain conversation history', async () => {
      const mockResponse1 = {
        response: 'First response',
        generated_at: '2024-01-15T10:00:00Z',
      };

      const mockResponse2 = {
        response: 'Second response',
        generated_at: '2024-01-15T10:01:00Z',
      };

      (agentsService.chat as jest.Mock)
        .mockResolvedValueOnce(mockResponse1)
        .mockResolvedValueOnce(mockResponse2);

      render(<ChatbotDialog open={true} onOpenChange={mockOnOpenChange} />);

      const input = screen.getByPlaceholderText(/ask me anything/i);
      const sendButton = screen.getByRole('button', { name: /send/i });

      // Send first message
      await userEvent.type(input, 'First question');
      await userEvent.click(sendButton);

      await waitFor(() => {
        expect(agentsService.chat).toHaveBeenCalledWith({
          message: 'First question',
          conversation_history: [],
        });
      });

      // Send second message
      await userEvent.type(input, 'Second question');
      await userEvent.click(sendButton);

      await waitFor(() => {
        expect(agentsService.chat).toHaveBeenCalledWith({
          message: 'Second question',
          conversation_history: expect.arrayContaining([
            { role: 'user', content: 'First question' },
            { role: 'assistant', content: 'First response' },
          ]),
        });
      });
    });
  });
});

describe('CoachDialog', () => {
  const mockOnOpenChange = jest.fn();
  const defaultProps = {
    open: true,
    onOpenChange: mockOnOpenChange,
    coachType: 'nutrition' as const,
    currentDate: '2024-01-15',
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('rendering', () => {
    it('should render nutrition coach dialog', () => {
      render(<CoachDialog {...defaultProps} coachType="nutrition" />);

      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/ask nutrition coach/i)).toBeInTheDocument();
    });

    it('should render workout coach dialog', () => {
      render(<CoachDialog {...defaultProps} coachType="workout" />);

      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/ask workout coach/i)).toBeInTheDocument();
    });

    it('should not render when closed', () => {
      render(<CoachDialog {...defaultProps} open={false} />);

      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });
  });

  describe('nutrition coach', () => {
    it('should send message to nutrition coach', async () => {
      const mockResponse = {
        response: 'Nutrition advice here',
        generated_at: '2024-01-15T10:00:00Z',
      };

      (agentsService.getNutritionCoaching as jest.Mock).mockResolvedValueOnce(mockResponse);

      render(<CoachDialog {...defaultProps} coachType="nutrition" />);

      const input = screen.getByPlaceholderText(/ask nutrition coach/i);
      const sendButton = screen.getByRole('button', { name: /send/i });

      await userEvent.type(input, 'What should I eat for muscle gain?');
      await userEvent.click(sendButton);

      await waitFor(() => {
        expect(agentsService.getNutritionCoaching).toHaveBeenCalledWith({
          message: 'What should I eat for muscle gain?',
          date: '2024-01-15',
        });
      });
    });

    it('should handle nutrition coach errors', async () => {
      (agentsService.getNutritionCoaching as jest.Mock).mockRejectedValueOnce(
        new Error('Service unavailable')
      );

      render(<CoachDialog {...defaultProps} coachType="nutrition" />);

      const input = screen.getByPlaceholderText(/ask nutrition coach/i);
      const sendButton = screen.getByRole('button', { name: /send/i });

      await userEvent.type(input, 'Test question');
      await userEvent.click(sendButton);

      await waitFor(() => {
        expect(agentsService.getNutritionCoaching).toHaveBeenCalled();
      });
    });
  });

  describe('workout coach', () => {
    it('should send message to workout coach', async () => {
      const mockResponse = {
        response: 'Workout advice here',
        generated_at: '2024-01-15T10:00:00Z',
      };

      (agentsService.getWorkoutCoaching as jest.Mock).mockResolvedValueOnce(mockResponse);

      render(<CoachDialog {...defaultProps} coachType="workout" />);

      const input = screen.getByPlaceholderText(/ask workout coach/i);
      const sendButton = screen.getByRole('button', { name: /send/i });

      await userEvent.type(input, 'How can I improve my cardio?');
      await userEvent.click(sendButton);

      await waitFor(() => {
        expect(agentsService.getWorkoutCoaching).toHaveBeenCalledWith({
          message: 'How can I improve my cardio?',
          date: '2024-01-15',
        });
      });
    });

    it('should handle workout coach errors', async () => {
      (agentsService.getWorkoutCoaching as jest.Mock).mockRejectedValueOnce(
        new Error('Service unavailable')
      );

      render(<CoachDialog {...defaultProps} coachType="workout" />);

      const input = screen.getByPlaceholderText(/ask workout coach/i);
      const sendButton = screen.getByRole('button', { name: /send/i });

      await userEvent.type(input, 'Test question');
      await userEvent.click(sendButton);

      await waitFor(() => {
        expect(agentsService.getWorkoutCoaching).toHaveBeenCalled();
      });
    });
  });

  describe('message input', () => {
    it('should not send empty message', async () => {
      render(<CoachDialog {...defaultProps} coachType="nutrition" />);

      const sendButton = screen.getByRole('button', { name: /send/i });
      await userEvent.click(sendButton);

      expect(agentsService.getNutritionCoaching).not.toHaveBeenCalled();
    });

    it('should clear input after sending', async () => {
      const mockResponse = {
        response: 'Response',
        generated_at: '2024-01-15T10:00:00Z',
      };

      (agentsService.getNutritionCoaching as jest.Mock).mockResolvedValueOnce(mockResponse);

      render(<CoachDialog {...defaultProps} coachType="nutrition" />);

      const input = screen.getByPlaceholderText(/ask nutrition coach/i) as HTMLInputElement;
      const sendButton = screen.getByRole('button', { name: /send/i });

      await userEvent.type(input, 'Test message');
      expect(input.value).toBe('Test message');

      await userEvent.click(sendButton);

      await waitFor(() => {
        expect(input.value).toBe('');
      });
    });
  });
});
