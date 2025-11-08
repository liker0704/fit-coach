import { apiClient } from './apiClient';
import type { WaterIntake } from '../../types/models/health';

export interface CreateWaterIntakeDto {
  amount: number;
  time?: string;
}

export const waterService = {
  /**
   * Get all water intakes for a day
   */
  getAll: async (dayId: number): Promise<WaterIntake[]> => {
    const response = await apiClient.get(`/days/${dayId}/water-intakes`);
    return response.data;
  },

  /**
   * Create new water intake
   */
  create: async (dayId: number, data: CreateWaterIntakeDto): Promise<WaterIntake> => {
    const response = await apiClient.post(`/days/${dayId}/water-intakes`, data);
    return response.data;
  },

  /**
   * Delete water intake
   */
  delete: async (waterIntakeId: number): Promise<void> => {
    await apiClient.delete(`/water-intakes/${waterIntakeId}`);
  },
};
