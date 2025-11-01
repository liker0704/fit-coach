import { apiClient } from '../api/client';
import type { User } from '@/types/api/auth';

export const userService = {
  getProfile: async (): Promise<User> => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },

  updateProfile: async (data: Partial<User>): Promise<User> => {
    const response = await apiClient.put('/users/me', data);
    return response.data;
  },
};
