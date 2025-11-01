import { apiClient } from '../api/client';
import type { WaterIntake } from '@/types/models/health';

export interface CreateWaterIntakeDto {
  amount: number;
  time?: string;
}

export const waterService = {
  getAll: async (dayId: number): Promise<WaterIntake[]> => {
    const response = await apiClient.get(`/days/${dayId}/water-intakes`);
    return response.data;
  },

  create: async (dayId: number, data: CreateWaterIntakeDto): Promise<WaterIntake> => {
    const response = await apiClient.post(`/days/${dayId}/water-intakes`, data);
    return response.data;
  },

  delete: async (waterIntakeId: number): Promise<void> => {
    await apiClient.delete(`/water-intakes/${waterIntakeId}`);
  },
};
