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

export interface PhotoUploadResponse {
  meal_id: number;
  status: 'processing' | 'completed' | 'failed';
  message: string;
  photo_path?: string;
}

export interface RecognizedItem {
  name: string;
  quantity: number;
  unit: string;
  preparation?: string;
  confidence: 'high' | 'medium' | 'low';
}

export interface MealProcessingStatus {
  meal_id: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  error?: string;
  recognized_items?: RecognizedItem[];
  meal_data?: Meal;
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

  /**
   * Upload a meal photo and process it with Vision Agent.
   * Returns immediately with status='processing'.
   * Use getProcessingStatus() to poll for results.
   */
  uploadPhoto: async (
    dayId: number,
    category: 'breakfast' | 'lunch' | 'dinner' | 'snack',
    file: File
  ): Promise<PhotoUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post(
      `/meals/upload-photo?day_id=${dayId}&category=${category}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  /**
   * Get the processing status of a meal photo.
   * Poll this endpoint every 2-3 seconds until status is 'completed' or 'failed'.
   */
  getProcessingStatus: async (mealId: number): Promise<MealProcessingStatus> => {
    const response = await apiClient.get(`/meals/${mealId}/processing-status`);
    return response.data;
  },
};
