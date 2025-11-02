import { apiClient } from '../api/client';
import type { MoodRecord } from '@/types/models/health';

export interface CreateMoodDto {
  day_id: number;
  time: string;         // Required, ISO datetime string
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
  getAll: async (dayId: number): Promise<MoodRecord[]> => {
    const response = await apiClient.get(`/days/${dayId}/moods`);
    return response.data;
  },

  create: async (dayId: number, data: Omit<CreateMoodDto, 'day_id'>): Promise<MoodRecord> => {
    const response = await apiClient.post(`/days/${dayId}/moods`, { ...data, day_id: dayId });
    return response.data;
  },

  update: async (moodId: number, data: UpdateMoodDto): Promise<MoodRecord> => {
    const response = await apiClient.put(`/moods/${moodId}`, data);
    return response.data;
  },

  delete: async (moodId: number): Promise<void> => {
    await apiClient.delete(`/moods/${moodId}`);
  }
};
