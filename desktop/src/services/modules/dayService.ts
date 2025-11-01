import { apiClient } from '../api/client';
import type { Day } from '@/types/models/health';

export const dayService = {
  getDays: async (startDate?: string, endDate?: string): Promise<Day[]> => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);

    const response = await apiClient.get(`/days?${params.toString()}`);
    return response.data;
  },

  getDay: async (dayId: number): Promise<Day> => {
    const response = await apiClient.get(`/days/id/${dayId}`);
    return response.data;
  },

  createDay: async (date: string): Promise<Day> => {
    const response = await apiClient.post('/days', { date });
    return response.data;
  },

  deleteDay: async (dayId: number): Promise<void> => {
    await apiClient.delete(`/days/${dayId}`);
  },
};
