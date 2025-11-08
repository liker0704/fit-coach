import { apiClient } from './apiClient';
import type { MoodRecord } from '../../types/models/health';

export interface CreateMoodDto {
  time: string;         // ISO datetime string
  rating: number;       // 1-5
  energy_level?: number;
  stress_level?: number;
  anxiety_level?: number;
  tags?: string[];
  notes?: string;
}

export interface UpdateMoodDto {
  time?: string;
  rating?: number;
  energy_level?: number;
  stress_level?: number;
  anxiety_level?: number;
  tags?: string[];
  notes?: string;
}

export const moodService = {
  /**
   * Get all mood records for a day
   */
  getAll: async (dayId: number): Promise<MoodRecord[]> => {
    const response = await apiClient.get(`/days/${dayId}/moods`);
    return response.data;
  },

  /**
   * Create new mood record
   */
  create: async (dayId: number, data: CreateMoodDto): Promise<MoodRecord> => {
    const response = await apiClient.post(`/days/${dayId}/moods`, {
      ...data,
      day_id: dayId,
    });
    return response.data;
  },

  /**
   * Update mood record
   */
  update: async (moodId: number, data: UpdateMoodDto): Promise<MoodRecord> => {
    const response = await apiClient.put(`/moods/${moodId}`, data);
    return response.data;
  },

  /**
   * Delete mood record
   */
  delete: async (moodId: number): Promise<void> => {
    await apiClient.delete(`/moods/${moodId}`);
  },
};
