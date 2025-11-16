import apiClient from './apiClient';
import { getToken } from '../authService';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface VisionAnalysisResult {
  meal_name: string;
  calories: number;
  protein: number;
  carbs: number;
  fats: number;
  confidence: number;
  items: Array<{
    name: string;
    amount: string;
  }>;
}

export interface CoachResponse {
  advice: string;
  recommendations: string[];
}

/**
 * Parse Server-Sent Events stream
 */
async function parseSSEStream(
  response: Response,
  onChunk: (chunk: string) => void,
  onComplete: () => void,
  onError: (error: Error) => void
) {
  try {
    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No response body');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();

      if (done) {
        onComplete();
        break;
      }

      // Decode chunk and add to buffer
      buffer += decoder.decode(value, { stream: true });

      // Split by newlines to get individual SSE messages
      const lines = buffer.split('\n');
      buffer = lines.pop() || ''; // Keep incomplete line in buffer

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6); // Remove 'data: ' prefix

          if (data === '[DONE]') {
            onComplete();
            return;
          }

          if (data.startsWith('[ERROR:')) {
            onError(new Error(data));
            return;
          }

          onChunk(data);
        }
      }
    }
  } catch (error) {
    onError(error as Error);
  }
}

export const agentService = {
  /**
   * Send message to chatbot
   */
  async sendChatMessage(message: string): Promise<string> {
    const response = await apiClient.post('/agents/chat', {
      message,
    });
    return response.data.response;
  },

  /**
   * Stream chat message with real-time response
   */
  async streamChatMessage(
    message: string,
    onChunk: (chunk: string) => void,
    onComplete: () => void,
    onError: (error: Error) => void
  ): Promise<void> {
    try {
      const token = await getToken();
      const baseURL = apiClient.defaults.baseURL || '';

      const response = await fetch(`${baseURL}/agents/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ message }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      await parseSSEStream(response, onChunk, onComplete, onError);
    } catch (error) {
      onError(error as Error);
    }
  },

  /**
   * Analyze food image with Vision Agent
   */
  async analyzeFood(imageBase64: string): Promise<VisionAnalysisResult> {
    const response = await apiClient.post('/agents/vision/analyze', {
      image: imageBase64,
    });
    return response.data;
  },

  /**
   * Get advice from Nutrition Coach
   */
  async getNutritionAdvice(
    date: string,
    question?: string
  ): Promise<CoachResponse> {
    const response = await apiClient.post('/agents/coach/nutrition', {
      date,
      question,
    });
    return response.data;
  },

  /**
   * Stream nutrition coach advice
   */
  async streamNutritionAdvice(
    question: string,
    date: string,
    onChunk: (chunk: string) => void,
    onComplete: () => void,
    onError: (error: Error) => void
  ): Promise<void> {
    try {
      const token = await getToken();
      const baseURL = apiClient.defaults.baseURL || '';

      const response = await fetch(`${baseURL}/agents/nutrition-coach/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ question, date }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      await parseSSEStream(response, onChunk, onComplete, onError);
    } catch (error) {
      onError(error as Error);
    }
  },

  /**
   * Get advice from Workout Coach
   */
  async getWorkoutAdvice(
    date: string,
    question?: string
  ): Promise<CoachResponse> {
    const response = await apiClient.post('/agents/coach/workout', {
      date,
      question,
    });
    return response.data;
  },

  /**
   * Stream workout coach advice
   */
  async streamWorkoutAdvice(
    question: string,
    date: string,
    onChunk: (chunk: string) => void,
    onComplete: () => void,
    onError: (error: Error) => void
  ): Promise<void> {
    try {
      const token = await getToken();
      const baseURL = apiClient.defaults.baseURL || '';

      const response = await fetch(`${baseURL}/agents/workout-coach/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ question, date }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      await parseSSEStream(response, onChunk, onComplete, onError);
    } catch (error) {
      onError(error as Error);
    }
  },

  /**
   * Get daily summary
   */
  async getDailySummary(date: string): Promise<string> {
    const response = await apiClient.get(`/agents/summary/${date}`);
    return response.data.summary;
  },
};
