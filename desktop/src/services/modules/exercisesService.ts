import { apiClient } from '../api/client';
import type { Exercise } from '@/types/models/health';

export interface CreateExerciseDto {
  name: string;
  exercise_type?: string;
  start_time?: string;
  duration?: number;
  distance?: number;
  intensity?: number;
  calories_burned?: number;
  heart_rate?: number;
  notes?: string;
}

export interface UpdateExerciseDto {
  name?: string;
  exercise_type?: string;
  start_time?: string;
  duration?: number;
  distance?: number;
  intensity?: number;
  calories_burned?: number;
  heart_rate?: number;
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

  create: async (dayId: number, data: CreateExerciseDto): Promise<Exercise> => {
    const response = await apiClient.post(`/days/${dayId}/exercises`, data);
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
