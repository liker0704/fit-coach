import { apiClient } from '../api/client';
import type { Meal } from '@/types/models/health';

export interface CreateMealDto {
  name: string;
  meal_time?: string;
  category?: string;
  calories?: number;
  protein?: number;
  carbs?: number;
  fats?: number;
  notes?: string;
}

export interface UpdateMealDto {
  name?: string;
  meal_time?: string;
  category?: string;
  calories?: number;
  protein?: number;
  carbs?: number;
  fats?: number;
  notes?: string;
}

export const mealsService = {
  getAll: async (dayId: number): Promise<Meal[]> => {
    const response = await apiClient.get(`/days/${dayId}/meals`);
    return response.data;
  },

  get: async (mealId: number): Promise<Meal> => {
    const response = await apiClient.get(`/meals/${mealId}`);
    return response.data;
  },

  create: async (dayId: number, data: CreateMealDto): Promise<Meal> => {
    const response = await apiClient.post(`/days/${dayId}/meals`, data);
    return response.data;
  },

  update: async (mealId: number, data: UpdateMealDto): Promise<Meal> => {
    const response = await apiClient.put(`/meals/${mealId}`, data);
    return response.data;
  },

  delete: async (mealId: number): Promise<void> => {
    await apiClient.delete(`/meals/${mealId}`);
  },
};
