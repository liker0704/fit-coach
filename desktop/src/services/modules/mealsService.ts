import { apiClient } from '../api/client';
import type { Meal } from '@/types/models/health';

export interface CreateMealDto {
  day_id: number;
  category: 'breakfast' | 'lunch' | 'dinner' | 'snack';
  time?: string;
  calories?: number;
  protein?: number;
  carbs?: number;
  fat?: number;
  fiber?: number;
  sugar?: number;
  sodium?: number;
  notes?: string;
  photo_url?: string;
}

export interface UpdateMealDto {
  category?: 'breakfast' | 'lunch' | 'dinner' | 'snack';
  time?: string;
  calories?: number;
  protein?: number;
  carbs?: number;
  fat?: number;
  fiber?: number;
  sugar?: number;
  sodium?: number;
  notes?: string;
  photo_url?: string;
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

  create: async (dayId: number, data: Omit<CreateMealDto, 'day_id'>): Promise<Meal> => {
    const response = await apiClient.post(`/days/${dayId}/meals`, {
      ...data,
      day_id: dayId,
    });
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
