import { apiClient } from './apiClient';
import type { Exercise } from '../../types/models/health';

export interface CreateExerciseDto {
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

export const exerciseService = {
  /**
   * Get all exercises for a day
   */
  getAll: async (dayId: number): Promise<Exercise[]> => {
    const response = await apiClient.get(`/days/${dayId}/exercises`);
    return response.data;
  },

  /**
   * Get single exercise by ID
   */
  get: async (exerciseId: number): Promise<Exercise> => {
    const response = await apiClient.get(`/exercises/${exerciseId}`);
    return response.data;
  },

  /**
   * Create new exercise
   */
  create: async (dayId: number, data: CreateExerciseDto): Promise<Exercise> => {
    const response = await apiClient.post(`/days/${dayId}/exercises`, {
      ...data,
      day_id: dayId,
    });
    return response.data;
  },

  /**
   * Update exercise
   */
  update: async (exerciseId: number, data: UpdateExerciseDto): Promise<Exercise> => {
    const response = await apiClient.put(`/exercises/${exerciseId}`, data);
    return response.data;
  },

  /**
   * Delete exercise
   */
  delete: async (exerciseId: number): Promise<void> => {
    await apiClient.delete(`/exercises/${exerciseId}`);
  },
};
