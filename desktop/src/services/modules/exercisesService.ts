import { apiClient } from '../api/client';
import type { Exercise } from '@/types/models/health';

export interface CreateExerciseDto {
  day_id: number;
  type: string;
  name?: string;
  start_time?: string;
  duration?: number;
  distance?: number;
  intensity?: number;
  calories_burned?: number;
  heart_rate_avg?: number;
  heart_rate_max?: number;
  notes?: string;
}

export interface UpdateExerciseDto {
  type?: string;
  name?: string;
  start_time?: string;
  duration?: number;
  distance?: number;
  intensity?: number;
  calories_burned?: number;
  heart_rate_avg?: number;
  heart_rate_max?: number;
  notes?: string;
}

export const exercisesService = {
  getAll: async (dayId: number): Promise<Exercise[]> => {
    const response = await apiClient.get(`/days/${dayId}/exercises`);
    return response.data;
  },

  get: async (exerciseId: number): Promise<Exercise> => {
    const response = await apiClient.get(`/exercises/${exerciseId}`);
    return response.data;
  },

  create: async (data: CreateExerciseDto): Promise<Exercise> => {
    const response = await apiClient.post(`/days/${data.day_id}/exercises`, data);
    return response.data;
  },

  update: async (exerciseId: number, data: UpdateExerciseDto): Promise<Exercise> => {
    const response = await apiClient.put(`/exercises/${exerciseId}`, data);
    return response.data;
  },

  delete: async (exerciseId: number): Promise<void> => {
    await apiClient.delete(`/exercises/${exerciseId}`);
  },
};
