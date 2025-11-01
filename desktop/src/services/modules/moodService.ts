import { apiClient } from '../api/client';
import type { MoodRecord } from '@/types/models/health';

export interface CreateMoodDto {
  mood_level: number;   // 1-5
  tags?: string[];      // e.g., ["productive", "stressed"]
  notes?: string;
}

export const moodService = {
  getAll: async (dayId: number): Promise<MoodRecord[]> => {
    const response = await apiClient.get(`/days/${dayId}/moods`);
    return response.data;
  },

  create: async (dayId: number, data: CreateMoodDto): Promise<MoodRecord> => {
    const response = await apiClient.post(`/days/${dayId}/moods`, data);
    return response.data;
  },

  update: async (moodId: number, data: Partial<CreateMoodDto>): Promise<MoodRecord> => {
    const response = await apiClient.put(`/moods/${moodId}`, data);
    return response.data;
  },

  delete: async (moodId: number): Promise<void> => {
    await apiClient.delete(`/moods/${moodId}`);
  }
};
