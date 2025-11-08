import { apiClient } from './apiClient';
import type { SleepRecord } from '../../types/models/health';

export interface CreateSleepDto {
  bedtime?: string;     // HH:MM format (optional)
  wake_time?: string;   // HH:MM format (optional)
  duration?: number;    // hours (calculated)
  quality?: number;     // 1-5
  notes?: string;
}

export interface UpdateSleepDto {
  bedtime?: string;
  wake_time?: string;
  duration?: number;
  quality?: number;
  notes?: string;
}

export const sleepService = {
  /**
   * Get all sleep records for a day
   */
  getAll: async (dayId: number): Promise<SleepRecord[]> => {
    const response = await apiClient.get(`/days/${dayId}/sleep`);
    return response.data;
  },

  /**
   * Create new sleep record
   */
  create: async (dayId: number, data: CreateSleepDto): Promise<SleepRecord> => {
    const response = await apiClient.post(`/days/${dayId}/sleep`, data);
    return response.data;
  },

  /**
   * Update sleep record
   */
  update: async (sleepId: number, data: UpdateSleepDto): Promise<SleepRecord> => {
    const response = await apiClient.put(`/sleep/${sleepId}`, data);
    return response.data;
  },

  /**
   * Delete sleep record
   */
  delete: async (sleepId: number): Promise<void> => {
    await apiClient.delete(`/sleep/${sleepId}`);
  },
};
