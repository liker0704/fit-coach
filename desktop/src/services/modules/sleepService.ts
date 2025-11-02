import { apiClient } from '../api/client';
import type { SleepRecord } from '@/types/models/health';

export interface CreateSleepDto {
  bedtime?: string;     // HH:MM format (optional)
  wake_time?: string;   // HH:MM format (optional)
  duration?: number;    // hours (calculated)
  quality?: number;     // 1-5
  notes?: string;
}

export const sleepService = {
  getAll: async (dayId: number): Promise<SleepRecord[]> => {
    const response = await apiClient.get(`/days/${dayId}/sleep`);
    return response.data;
  },

  create: async (dayId: number, data: CreateSleepDto): Promise<SleepRecord> => {
    const response = await apiClient.post(`/days/${dayId}/sleep`, data);
    return response.data;
  },

  update: async (sleepId: number, data: Partial<CreateSleepDto>): Promise<SleepRecord> => {
    const response = await apiClient.put(`/sleep/${sleepId}`, data);
    return response.data;
  },

  delete: async (sleepId: number): Promise<void> => {
    await apiClient.delete(`/sleep/${sleepId}`);
  }
};
