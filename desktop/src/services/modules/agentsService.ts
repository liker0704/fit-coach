import { apiClient } from '../api/client';

// ============================================================
// Types
// ============================================================

export interface DailySummaryRequest {
  date?: string; // ISO format date, defaults to today
}

export interface DailySummaryResponse {
  summary: string;
  date: string;
  highlights: string[];
  recommendations: string[];
  generated_at: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  message: string;
  conversation_history?: ChatMessage[];
}

export interface ChatResponse {
  response: string;
  generated_at: string;
}

export interface CoachRequest {
  message: string;
  date?: string; // ISO format date for context
}

export interface CoachResponse {
  response: string;
  generated_at: string;
}

// ============================================================
// Service
// ============================================================

export const agentsService = {
  /**
   * Generate a daily summary using the Daily Summary Agent
   */
  generateDailySummary: async (
    request: DailySummaryRequest = {}
  ): Promise<DailySummaryResponse> => {
    const response = await apiClient.post('/agents/daily-summary', request);
    return response.data;
  },

  /**
   * Chat with the general fitness assistant chatbot
   */
  chat: async (request: ChatRequest): Promise<ChatResponse> => {
    const response = await apiClient.post('/agents/chat', request);
    return response.data;
  },

  /**
   * Get nutrition coaching advice
   */
  getNutritionCoaching: async (request: CoachRequest): Promise<CoachResponse> => {
    const response = await apiClient.post('/agents/nutrition-coach', request);
    return response.data;
  },

  /**
   * Get workout coaching advice
   */
  getWorkoutCoaching: async (request: CoachRequest): Promise<CoachResponse> => {
    const response = await apiClient.post('/agents/workout-coach', request);
    return response.data;
  },
};
