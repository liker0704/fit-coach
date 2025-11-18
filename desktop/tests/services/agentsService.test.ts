import { agentsService } from '@/services/modules/agentsService';
import { apiClient } from '@/services/api/client';
import type {
  DailySummaryRequest,
  DailySummaryResponse,
  ChatRequest,
  ChatResponse,
  CoachRequest,
  CoachResponse,
} from '@/services/modules/agentsService';

jest.mock('@/services/api/client', () => ({
  apiClient: {
    post: jest.fn(),
  },
}));

describe('agentsService', () => {
  const mockApiClient = apiClient as jest.Mocked<typeof apiClient>;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('generateDailySummary', () => {
    it('should generate daily summary with default date', async () => {
      const mockResponse: DailySummaryResponse = {
        summary: 'Great day with balanced nutrition and good exercise.',
        date: '2024-01-15',
        highlights: ['Completed morning run', 'Met protein goals'],
        recommendations: ['Increase water intake', 'Add more vegetables'],
        generated_at: '2024-01-15T18:00:00Z',
      };

      mockApiClient.post.mockResolvedValueOnce({ data: mockResponse });

      const result = await agentsService.generateDailySummary();

      expect(mockApiClient.post).toHaveBeenCalledWith('/agents/daily-summary', {});
      expect(result).toEqual(mockResponse);
    });

    it('should generate daily summary for specific date', async () => {
      const request: DailySummaryRequest = {
        date: '2024-01-10',
      };

      const mockResponse: DailySummaryResponse = {
        summary: 'Rest day with light activities.',
        date: '2024-01-10',
        highlights: ['Good sleep quality'],
        recommendations: ['Plan workout for tomorrow'],
        generated_at: '2024-01-15T18:00:00Z',
      };

      mockApiClient.post.mockResolvedValueOnce({ data: mockResponse });

      const result = await agentsService.generateDailySummary(request);

      expect(mockApiClient.post).toHaveBeenCalledWith('/agents/daily-summary', request);
      expect(result).toEqual(mockResponse);
    });

    it('should handle errors when generating summary', async () => {
      mockApiClient.post.mockRejectedValueOnce(new Error('Failed to generate summary'));

      await expect(agentsService.generateDailySummary()).rejects.toThrow(
        'Failed to generate summary'
      );
    });
  });

  describe('chat', () => {
    it('should send chat message and receive response', async () => {
      const request: ChatRequest = {
        message: 'What are the benefits of protein?',
      };

      const mockResponse: ChatResponse = {
        response: 'Protein helps build and repair muscles, supports immune function...',
        generated_at: '2024-01-15T18:00:00Z',
      };

      mockApiClient.post.mockResolvedValueOnce({ data: mockResponse });

      const result = await agentsService.chat(request);

      expect(mockApiClient.post).toHaveBeenCalledWith('/agents/chat', request);
      expect(result).toEqual(mockResponse);
    });

    it('should send chat message with conversation history', async () => {
      const request: ChatRequest = {
        message: 'What about carbs?',
        conversation_history: [
          { role: 'user', content: 'What are the benefits of protein?' },
          {
            role: 'assistant',
            content: 'Protein helps build and repair muscles...',
          },
        ],
      };

      const mockResponse: ChatResponse = {
        response: 'Carbohydrates are your body primary source of energy...',
        generated_at: '2024-01-15T18:00:00Z',
      };

      mockApiClient.post.mockResolvedValueOnce({ data: mockResponse });

      const result = await agentsService.chat(request);

      expect(mockApiClient.post).toHaveBeenCalledWith('/agents/chat', request);
      expect(result).toEqual(mockResponse);
    });

    it('should handle empty message', async () => {
      const request: ChatRequest = {
        message: '',
      };

      mockApiClient.post.mockRejectedValueOnce(new Error('Message cannot be empty'));

      await expect(agentsService.chat(request)).rejects.toThrow('Message cannot be empty');
    });

    it('should handle API errors', async () => {
      const request: ChatRequest = {
        message: 'Test message',
      };

      mockApiClient.post.mockRejectedValueOnce(new Error('API error'));

      await expect(agentsService.chat(request)).rejects.toThrow('API error');
    });
  });

  describe('getNutritionCoaching', () => {
    it('should get nutrition coaching advice', async () => {
      const request: CoachRequest = {
        message: 'I want to build muscle',
      };

      const mockResponse: CoachResponse = {
        response: 'For muscle building, focus on high protein intake...',
        generated_at: '2024-01-15T18:00:00Z',
      };

      mockApiClient.post.mockResolvedValueOnce({ data: mockResponse });

      const result = await agentsService.getNutritionCoaching(request);

      expect(mockApiClient.post).toHaveBeenCalledWith('/agents/nutrition-coach', request);
      expect(result).toEqual(mockResponse);
    });

    it('should get nutrition coaching with date context', async () => {
      const request: CoachRequest = {
        message: 'Review my meals today',
        date: '2024-01-15',
      };

      const mockResponse: CoachResponse = {
        response: 'Looking at your meals today, you had a good balance...',
        generated_at: '2024-01-15T18:00:00Z',
      };

      mockApiClient.post.mockResolvedValueOnce({ data: mockResponse });

      const result = await agentsService.getNutritionCoaching(request);

      expect(mockApiClient.post).toHaveBeenCalledWith('/agents/nutrition-coach', request);
      expect(result).toEqual(mockResponse);
    });

    it('should handle nutrition coaching errors', async () => {
      const request: CoachRequest = {
        message: 'Test',
      };

      mockApiClient.post.mockRejectedValueOnce(new Error('Coaching service unavailable'));

      await expect(agentsService.getNutritionCoaching(request)).rejects.toThrow(
        'Coaching service unavailable'
      );
    });
  });

  describe('getWorkoutCoaching', () => {
    it('should get workout coaching advice', async () => {
      const request: CoachRequest = {
        message: 'I want to improve my cardio',
      };

      const mockResponse: CoachResponse = {
        response: 'For cardio improvement, consider interval training...',
        generated_at: '2024-01-15T18:00:00Z',
      };

      mockApiClient.post.mockResolvedValueOnce({ data: mockResponse });

      const result = await agentsService.getWorkoutCoaching(request);

      expect(mockApiClient.post).toHaveBeenCalledWith('/agents/workout-coach', request);
      expect(result).toEqual(mockResponse);
    });

    it('should get workout coaching with date context', async () => {
      const request: CoachRequest = {
        message: 'Review my workout today',
        date: '2024-01-15',
      };

      const mockResponse: CoachResponse = {
        response: 'Your workout today shows good intensity...',
        generated_at: '2024-01-15T18:00:00Z',
      };

      mockApiClient.post.mockResolvedValueOnce({ data: mockResponse });

      const result = await agentsService.getWorkoutCoaching(request);

      expect(mockApiClient.post).toHaveBeenCalledWith('/agents/workout-coach', request);
      expect(result).toEqual(mockResponse);
    });

    it('should handle workout coaching errors', async () => {
      const request: CoachRequest = {
        message: 'Test',
      };

      mockApiClient.post.mockRejectedValueOnce(new Error('Coaching failed'));

      await expect(agentsService.getWorkoutCoaching(request)).rejects.toThrow('Coaching failed');
    });
  });
});
