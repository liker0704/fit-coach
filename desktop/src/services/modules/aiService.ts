import { apiClient } from '../api/client';

export interface AISummaryResponse {
  summary: string;
  period: string;
  date_range: {
    start: string;
    end: string;
  };
  generated_at: string;
}

export const aiService = {
  generateSummary: async (dayId: number): Promise<string> => {
    const response = await apiClient.post('/ai/summary', {
      period: 'daily',
      day_id: dayId
    });
    return response.data.summary;
  }
};
