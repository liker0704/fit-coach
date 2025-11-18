import { statisticsService } from '../statisticsService';
import apiClient from '../apiClient';
import type { StatisticsResponse } from '../statisticsService';

jest.mock('../apiClient');

const mockedApiClient = apiClient as jest.Mocked<typeof apiClient>;

describe('statisticsService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getStatistics', () => {
    it('should get statistics for custom date range', async () => {
      const mockStats: StatisticsResponse = {
        weight: [
          { date: '2025-01-15', value: 75.5 },
          { date: '2025-01-16', value: 75.3 },
          { date: '2025-01-17', value: 75.0 },
        ],
        calories: [
          { date: '2025-01-15', value: 2000 },
          { date: '2025-01-16', value: 2100 },
          { date: '2025-01-17', value: 1950 },
        ],
        water: [
          { date: '2025-01-15', value: 2500 },
          { date: '2025-01-16', value: 3000 },
          { date: '2025-01-17', value: 2800 },
        ],
        sleep: [
          { date: '2025-01-15', value: 7.5 },
          { date: '2025-01-16', value: 8 },
          { date: '2025-01-17', value: 7 },
        ],
        exercise: [
          { date: '2025-01-15', value: 45 },
          { date: '2025-01-16', value: 60 },
          { date: '2025-01-17', value: 30 },
        ],
        mood: [
          { date: '2025-01-15', value: 4 },
          { date: '2025-01-16', value: 5 },
          { date: '2025-01-17', value: 4 },
        ],
      };

      mockedApiClient.get.mockResolvedValueOnce({ data: mockStats });

      const result = await statisticsService.getStatistics(
        '2025-01-15',
        '2025-01-17'
      );

      expect(mockedApiClient.get).toHaveBeenCalledWith('/statistics/custom', {
        params: {
          start_date: '2025-01-15',
          end_date: '2025-01-17',
        },
      });
      expect(result).toEqual(mockStats);
      expect(result.weight).toHaveLength(3);
      expect(result.calories).toHaveLength(3);
    });

    it('should get statistics with single day range', async () => {
      const mockStats: StatisticsResponse = {
        weight: [{ date: '2025-01-15', value: 75.5 }],
        calories: [{ date: '2025-01-15', value: 2000 }],
        water: [{ date: '2025-01-15', value: 2500 }],
        sleep: [{ date: '2025-01-15', value: 8 }],
        exercise: [{ date: '2025-01-15', value: 45 }],
        mood: [{ date: '2025-01-15', value: 4 }],
      };

      mockedApiClient.get.mockResolvedValueOnce({ data: mockStats });

      const result = await statisticsService.getStatistics(
        '2025-01-15',
        '2025-01-15'
      );

      expect(result.weight).toHaveLength(1);
    });

    it('should handle empty statistics data', async () => {
      const mockStats: StatisticsResponse = {
        weight: [],
        calories: [],
        water: [],
        sleep: [],
        exercise: [],
        mood: [],
      };

      mockedApiClient.get.mockResolvedValueOnce({ data: mockStats });

      const result = await statisticsService.getStatistics(
        '2025-01-01',
        '2025-01-05'
      );

      expect(result.weight).toEqual([]);
      expect(result.calories).toEqual([]);
    });

    it('should handle API error', async () => {
      mockedApiClient.get.mockRejectedValueOnce(new Error('API error'));

      await expect(
        statisticsService.getStatistics('2025-01-15', '2025-01-17')
      ).rejects.toThrow('API error');
    });
  });

  describe('getWeeklyStatistics', () => {
    it('should get weekly statistics', async () => {
      const mockStats: StatisticsResponse = {
        weight: [
          { date: '2025-01-13', value: 76.0 },
          { date: '2025-01-14', value: 75.8 },
          { date: '2025-01-15', value: 75.5 },
          { date: '2025-01-16', value: 75.3 },
          { date: '2025-01-17', value: 75.0 },
          { date: '2025-01-18', value: 74.8 },
          { date: '2025-01-19', value: 74.5 },
        ],
        calories: Array(7)
          .fill(null)
          .map((_, i) => ({
            date: `2025-01-${13 + i}`,
            value: 2000 + Math.random() * 200,
          })),
        water: Array(7)
          .fill(null)
          .map((_, i) => ({
            date: `2025-01-${13 + i}`,
            value: 2500,
          })),
        sleep: Array(7)
          .fill(null)
          .map((_, i) => ({
            date: `2025-01-${13 + i}`,
            value: 7 + Math.random() * 2,
          })),
        exercise: Array(7)
          .fill(null)
          .map((_, i) => ({
            date: `2025-01-${13 + i}`,
            value: 30 + Math.random() * 40,
          })),
        mood: Array(7)
          .fill(null)
          .map((_, i) => ({
            date: `2025-01-${13 + i}`,
            value: 3 + Math.floor(Math.random() * 3),
          })),
      };

      mockedApiClient.get.mockResolvedValueOnce({ data: mockStats });

      const result = await statisticsService.getWeeklyStatistics();

      expect(mockedApiClient.get).toHaveBeenCalledWith('/statistics/week');
      expect(result).toEqual(mockStats);
      expect(result.weight).toHaveLength(7);
    });

    it('should handle empty week data', async () => {
      const mockStats: StatisticsResponse = {
        weight: [],
        calories: [],
        water: [],
        sleep: [],
        exercise: [],
        mood: [],
      };

      mockedApiClient.get.mockResolvedValueOnce({ data: mockStats });

      const result = await statisticsService.getWeeklyStatistics();

      expect(result.weight).toEqual([]);
    });
  });

  describe('getMonthlyStatistics', () => {
    it('should get monthly statistics', async () => {
      const mockStats: StatisticsResponse = {
        weight: Array(30)
          .fill(null)
          .map((_, i) => ({
            date: `2025-01-${String(i + 1).padStart(2, '0')}`,
            value: 76.0 - i * 0.05,
          })),
        calories: Array(30)
          .fill(null)
          .map((_, i) => ({
            date: `2025-01-${String(i + 1).padStart(2, '0')}`,
            value: 2000 + Math.random() * 300,
          })),
        water: Array(30)
          .fill(null)
          .map((_, i) => ({
            date: `2025-01-${String(i + 1).padStart(2, '0')}`,
            value: 2500,
          })),
        sleep: Array(30)
          .fill(null)
          .map((_, i) => ({
            date: `2025-01-${String(i + 1).padStart(2, '0')}`,
            value: 7 + Math.random() * 2,
          })),
        exercise: Array(30)
          .fill(null)
          .map((_, i) => ({
            date: `2025-01-${String(i + 1).padStart(2, '0')}`,
            value: Math.random() * 60,
          })),
        mood: Array(30)
          .fill(null)
          .map((_, i) => ({
            date: `2025-01-${String(i + 1).padStart(2, '0')}`,
            value: 3 + Math.floor(Math.random() * 3),
          })),
      };

      mockedApiClient.get.mockResolvedValueOnce({ data: mockStats });

      const result = await statisticsService.getMonthlyStatistics();

      expect(mockedApiClient.get).toHaveBeenCalledWith('/statistics/month');
      expect(result).toEqual(mockStats);
      expect(result.weight).toHaveLength(30);
      expect(result.calories).toHaveLength(30);
    });

    it('should handle partial month data', async () => {
      const mockStats: StatisticsResponse = {
        weight: Array(15)
          .fill(null)
          .map((_, i) => ({
            date: `2025-01-${String(i + 1).padStart(2, '0')}`,
            value: 75.5,
          })),
        calories: Array(15)
          .fill(null)
          .map((_, i) => ({
            date: `2025-01-${String(i + 1).padStart(2, '0')}`,
            value: 2000,
          })),
        water: [],
        sleep: [],
        exercise: [],
        mood: [],
      };

      mockedApiClient.get.mockResolvedValueOnce({ data: mockStats });

      const result = await statisticsService.getMonthlyStatistics();

      expect(result.weight).toHaveLength(15);
      expect(result.water).toEqual([]);
    });

    it('should handle API error', async () => {
      mockedApiClient.get.mockRejectedValueOnce(new Error('Server error'));

      await expect(statisticsService.getMonthlyStatistics()).rejects.toThrow(
        'Server error'
      );
    });
  });
});
