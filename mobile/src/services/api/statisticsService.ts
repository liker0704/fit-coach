import apiClient from './apiClient';

export interface StatisticsResponse {
  weight: Array<{ date: string; value: number }>;
  calories: Array<{ date: string; value: number }>;
  water: Array<{ date: string; value: number }>;
  sleep: Array<{ date: string; value: number }>;
  exercise: Array<{ date: string; value: number }>;
  mood: Array<{ date: string; value: number }>;
}

export const statisticsService = {
  /**
   * Get statistics for a date range
   */
  async getStatistics(
    startDate: string,
    endDate: string
  ): Promise<StatisticsResponse> {
    const response = await apiClient.get('/statistics/custom', {
      params: {
        start_date: startDate,
        end_date: endDate,
      },
    });
    return response.data;
  },

  /**
   * Get weekly statistics
   */
  async getWeeklyStatistics(): Promise<StatisticsResponse> {
    const response = await apiClient.get('/statistics/week');
    return response.data;
  },

  /**
   * Get monthly statistics
   */
  async getMonthlyStatistics(): Promise<StatisticsResponse> {
    const response = await apiClient.get('/statistics/month');
    return response.data;
  },
};
