import apiClient from './apiClient';

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
   * Get daily summary
   */
  async getDailySummary(date: string): Promise<string> {
    const response = await apiClient.get(`/agents/summary/${date}`);
    return response.data.summary;
  },
};
