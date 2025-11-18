import { agentService } from '../agentService';
import apiClient from '../apiClient';
import { getToken } from '../../authService';
import type { VisionAnalysisResult, CoachResponse } from '../agentService';

jest.mock('../apiClient');
jest.mock('../../authService');

const mockedApiClient = apiClient as jest.Mocked<typeof apiClient>;
const mockedGetToken = getToken as jest.MockedFunction<typeof getToken>;

// Mock global fetch
global.fetch = jest.fn();

describe('agentService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('sendChatMessage', () => {
    it('should send chat message and return response', async () => {
      const mockResponse = {
        response: 'Hello! How can I help you today?',
      };

      mockedApiClient.post.mockResolvedValueOnce({ data: mockResponse });

      const result = await agentService.sendChatMessage('Hello');

      expect(mockedApiClient.post).toHaveBeenCalledWith('/agents/chat', {
        message: 'Hello',
      });
      expect(result).toBe('Hello! How can I help you today?');
    });

    it('should handle error in chat message', async () => {
      mockedApiClient.post.mockRejectedValueOnce(new Error('Network error'));

      await expect(agentService.sendChatMessage('Test')).rejects.toThrow(
        'Network error'
      );
    });

    it('should send multiple messages sequentially', async () => {
      mockedApiClient.post
        .mockResolvedValueOnce({ data: { response: 'Response 1' } })
        .mockResolvedValueOnce({ data: { response: 'Response 2' } });

      const result1 = await agentService.sendChatMessage('Message 1');
      const result2 = await agentService.sendChatMessage('Message 2');

      expect(result1).toBe('Response 1');
      expect(result2).toBe('Response 2');
      expect(mockedApiClient.post).toHaveBeenCalledTimes(2);
    });
  });

  describe('streamChatMessage', () => {
    it('should stream chat message chunks', async () => {
      const chunks: string[] = [];
      const onChunk = jest.fn((chunk: string) => chunks.push(chunk));
      const onComplete = jest.fn();
      const onError = jest.fn();

      mockedGetToken.mockResolvedValueOnce('mock-token');
      mockedApiClient.defaults = { baseURL: 'http://localhost:8001/api/v1' } as any;

      const mockReader = {
        read: jest
          .fn()
          .mockResolvedValueOnce({
            done: false,
            value: new TextEncoder().encode('data: Hello\n'),
          })
          .mockResolvedValueOnce({
            done: false,
            value: new TextEncoder().encode('data: World\n'),
          })
          .mockResolvedValueOnce({
            done: false,
            value: new TextEncoder().encode('data: [DONE]\n'),
          }),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        body: {
          getReader: () => mockReader,
        },
      });

      await agentService.streamChatMessage(
        'Test message',
        onChunk,
        onComplete,
        onError
      );

      expect(onChunk).toHaveBeenCalledWith('Hello');
      expect(onChunk).toHaveBeenCalledWith('World');
      expect(onComplete).toHaveBeenCalled();
      expect(onError).not.toHaveBeenCalled();
    });

    it('should handle stream errors', async () => {
      const onChunk = jest.fn();
      const onComplete = jest.fn();
      const onError = jest.fn();

      mockedGetToken.mockResolvedValueOnce('mock-token');
      mockedApiClient.defaults = { baseURL: 'http://localhost:8001/api/v1' } as any;

      (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Stream error'));

      await agentService.streamChatMessage(
        'Test',
        onChunk,
        onComplete,
        onError
      );

      expect(onError).toHaveBeenCalledWith(expect.any(Error));
      expect(onComplete).not.toHaveBeenCalled();
    });
  });

  describe('analyzeFood', () => {
    it('should analyze food image and return nutritional data', async () => {
      const mockAnalysis: VisionAnalysisResult = {
        meal_name: 'Grilled Chicken Salad',
        calories: 350,
        protein: 35,
        carbs: 20,
        fats: 15,
        confidence: 0.85,
        items: [
          { name: 'Grilled Chicken', amount: '150g' },
          { name: 'Mixed Greens', amount: '100g' },
        ],
      };

      mockedApiClient.post.mockResolvedValueOnce({ data: mockAnalysis });

      const result = await agentService.analyzeFood('base64-encoded-image');

      expect(mockedApiClient.post).toHaveBeenCalledWith('/agents/vision/analyze', {
        image: 'base64-encoded-image',
      });
      expect(result).toEqual(mockAnalysis);
    });

    it('should handle low confidence results', async () => {
      const mockAnalysis: VisionAnalysisResult = {
        meal_name: 'Unknown Food',
        calories: 200,
        protein: 10,
        carbs: 25,
        fats: 8,
        confidence: 0.3,
        items: [],
      };

      mockedApiClient.post.mockResolvedValueOnce({ data: mockAnalysis });

      const result = await agentService.analyzeFood('low-quality-image');

      expect(result.confidence).toBeLessThan(0.5);
    });
  });

  describe('getNutritionAdvice', () => {
    it('should get nutrition advice for a specific date', async () => {
      const mockAdvice: CoachResponse = {
        advice:
          'Great job tracking your meals! Try to increase your protein intake.',
        recommendations: [
          'Add lean protein to breakfast',
          'Include more vegetables',
          'Stay hydrated',
        ],
      };

      mockedApiClient.post.mockResolvedValueOnce({ data: mockAdvice });

      const result = await agentService.getNutritionAdvice('2025-01-15');

      expect(mockedApiClient.post).toHaveBeenCalledWith('/agents/coach/nutrition', {
        date: '2025-01-15',
        question: undefined,
      });
      expect(result).toEqual(mockAdvice);
    });

    it('should get nutrition advice with custom question', async () => {
      const mockAdvice: CoachResponse = {
        advice: 'To lose weight, maintain a caloric deficit of 300-500 calories.',
        recommendations: ['Track calories daily', 'Increase protein', 'Exercise 3x/week'],
      };

      mockedApiClient.post.mockResolvedValueOnce({ data: mockAdvice });

      const result = await agentService.getNutritionAdvice(
        '2025-01-15',
        'How can I lose weight?'
      );

      expect(mockedApiClient.post).toHaveBeenCalledWith('/agents/coach/nutrition', {
        date: '2025-01-15',
        question: 'How can I lose weight?',
      });
      expect(result.recommendations).toHaveLength(3);
    });
  });

  describe('streamNutritionAdvice', () => {
    it('should stream nutrition advice', async () => {
      const onChunk = jest.fn();
      const onComplete = jest.fn();
      const onError = jest.fn();

      mockedGetToken.mockResolvedValueOnce('mock-token');
      mockedApiClient.defaults = { baseURL: 'http://localhost:8001/api/v1' } as any;

      const mockReader = {
        read: jest
          .fn()
          .mockResolvedValueOnce({
            done: false,
            value: new TextEncoder().encode('data: Nutrition advice...\n'),
          })
          .mockResolvedValueOnce({
            done: false,
            value: new TextEncoder().encode('data: [DONE]\n'),
          }),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        body: { getReader: () => mockReader },
      });

      await agentService.streamNutritionAdvice(
        'What should I eat?',
        '2025-01-15',
        onChunk,
        onComplete,
        onError
      );

      expect(onChunk).toHaveBeenCalledWith('Nutrition advice...');
      expect(onComplete).toHaveBeenCalled();
    });
  });

  describe('getWorkoutAdvice', () => {
    it('should get workout advice for a specific date', async () => {
      const mockAdvice: CoachResponse = {
        advice: 'Good workout today! Focus on progressive overload.',
        recommendations: [
          'Increase weights by 5%',
          'Add one more set',
          'Rest 48 hours between sessions',
        ],
      };

      mockedApiClient.post.mockResolvedValueOnce({ data: mockAdvice });

      const result = await agentService.getWorkoutAdvice('2025-01-15');

      expect(mockedApiClient.post).toHaveBeenCalledWith('/agents/coach/workout', {
        date: '2025-01-15',
        question: undefined,
      });
      expect(result).toEqual(mockAdvice);
    });
  });

  describe('getDailySummary', () => {
    it('should get daily summary for a date', async () => {
      const mockSummary = {
        summary:
          'Today you consumed 2000 calories, exercised for 45 minutes, and drank 2L of water.',
      };

      mockedApiClient.get.mockResolvedValueOnce({ data: mockSummary });

      const result = await agentService.getDailySummary('2025-01-15');

      expect(mockedApiClient.get).toHaveBeenCalledWith('/agents/summary/2025-01-15');
      expect(result).toBe(mockSummary.summary);
    });

    it('should handle empty summary', async () => {
      const mockSummary = {
        summary: 'No data recorded for this day.',
      };

      mockedApiClient.get.mockResolvedValueOnce({ data: mockSummary });

      const result = await agentService.getDailySummary('2025-01-01');

      expect(result).toContain('No data');
    });
  });
});
