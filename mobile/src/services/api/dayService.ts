import { apiClient } from './apiClient';
import type { Day } from '../../types/models/health';

export const dayService = {
  /**
   * Get days within date range
   */
  getDays: async (startDate?: string, endDate?: string): Promise<Day[]> => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);

    const response = await apiClient.get(`/days?${params.toString()}`);
    return response.data;
  },

  /**
   * Get single day by ID
   */
  getDay: async (dayId: number): Promise<Day> => {
    const response = await apiClient.get(`/days/id/${dayId}`);
    return response.data;
  },

  /**
   * Get day by date (YYYY-MM-DD)
   */
  getDayByDate: async (date: string): Promise<Day | null> => {
    try {
      const response = await apiClient.get(`/days/date/${date}`);
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null;
      }
      throw error;
    }
  },

  /**
   * Create new day
   */
  createDay: async (date: string): Promise<Day> => {
    const response = await apiClient.post('/days', { date });
    return response.data;
  },

  /**
   * Update day fields (tag, feeling, effort_score, weight, summary)
   */
  updateDay: async (
    dayId: number,
    data: Partial<Pick<Day, 'tag' | 'feeling' | 'effort_score' | 'weight' | 'summary'>>
  ): Promise<Day> => {
    const response = await apiClient.put(`/days/${dayId}`, data);
    return response.data;
  },

  /**
   * Delete day
   */
  deleteDay: async (dayId: number): Promise<void> => {
    await apiClient.delete(`/days/${dayId}`);
  },
};
