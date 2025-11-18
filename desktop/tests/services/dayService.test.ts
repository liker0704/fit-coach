import { dayService } from '@/services/modules/dayService';
import { apiClient } from '@/services/api/client';
import type { Day } from '@/types/models/health';

jest.mock('@/services/api/client', () => ({
  apiClient: {
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
  },
}));

describe('dayService', () => {
  const mockApiClient = apiClient as jest.Mocked<typeof apiClient>;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getDays', () => {
    it('should fetch all days without date filters', async () => {
      const mockDays: Day[] = [
        {
          id: 1,
          user_id: 1,
          date: '2024-01-15',
          tag: 'workout',
          feeling: 'energetic',
          effort_score: 8,
          created_at: '2024-01-15T00:00:00Z',
        },
        {
          id: 2,
          user_id: 1,
          date: '2024-01-16',
          tag: 'rest',
          feeling: 'relaxed',
          effort_score: 3,
          created_at: '2024-01-16T00:00:00Z',
        },
      ];

      mockApiClient.get.mockResolvedValueOnce({ data: mockDays });

      const result = await dayService.getDays();

      expect(mockApiClient.get).toHaveBeenCalledWith('/days?');
      expect(result).toEqual(mockDays);
      expect(result).toHaveLength(2);
    });

    it('should fetch days with date range', async () => {
      const startDate = '2024-01-01';
      const endDate = '2024-01-31';
      const mockDays: Day[] = [
        {
          id: 1,
          user_id: 1,
          date: '2024-01-15',
          created_at: '2024-01-15T00:00:00Z',
        },
      ];

      mockApiClient.get.mockResolvedValueOnce({ data: mockDays });

      const result = await dayService.getDays(startDate, endDate);

      expect(mockApiClient.get).toHaveBeenCalledWith(
        `/days?start_date=${startDate}&end_date=${endDate}`
      );
      expect(result).toEqual(mockDays);
    });

    it('should fetch days with only start date', async () => {
      const startDate = '2024-01-01';
      const mockDays: Day[] = [];

      mockApiClient.get.mockResolvedValueOnce({ data: mockDays });

      const result = await dayService.getDays(startDate);

      expect(mockApiClient.get).toHaveBeenCalledWith(`/days?start_date=${startDate}`);
      expect(result).toEqual([]);
    });

    it('should handle API errors', async () => {
      mockApiClient.get.mockRejectedValueOnce(new Error('Failed to fetch days'));

      await expect(dayService.getDays()).rejects.toThrow('Failed to fetch days');
    });
  });

  describe('getDay', () => {
    it('should fetch a single day by id', async () => {
      const dayId = 1;
      const mockDay: Day = {
        id: dayId,
        user_id: 1,
        date: '2024-01-15',
        tag: 'workout',
        feeling: 'energetic',
        effort_score: 8,
        weight: 75.5,
        summary: 'Great workout day',
        created_at: '2024-01-15T00:00:00Z',
      };

      mockApiClient.get.mockResolvedValueOnce({ data: mockDay });

      const result = await dayService.getDay(dayId);

      expect(mockApiClient.get).toHaveBeenCalledWith(`/days/id/${dayId}`);
      expect(result).toEqual(mockDay);
    });

    it('should throw error when day not found', async () => {
      const dayId = 999;
      mockApiClient.get.mockRejectedValueOnce(new Error('Day not found'));

      await expect(dayService.getDay(dayId)).rejects.toThrow('Day not found');
    });
  });

  describe('createDay', () => {
    it('should create a new day', async () => {
      const date = '2024-01-20';
      const mockDay: Day = {
        id: 1,
        user_id: 1,
        date: date,
        created_at: '2024-01-20T00:00:00Z',
      };

      mockApiClient.post.mockResolvedValueOnce({ data: mockDay });

      const result = await dayService.createDay(date);

      expect(mockApiClient.post).toHaveBeenCalledWith('/days', { date });
      expect(result).toEqual(mockDay);
      expect(result.date).toBe(date);
    });

    it('should handle duplicate day creation', async () => {
      const date = '2024-01-15';
      mockApiClient.post.mockRejectedValueOnce(new Error('Day already exists'));

      await expect(dayService.createDay(date)).rejects.toThrow('Day already exists');
    });

    it('should validate date format', async () => {
      const date = 'invalid-date';
      mockApiClient.post.mockRejectedValueOnce(new Error('Invalid date format'));

      await expect(dayService.createDay(date)).rejects.toThrow('Invalid date format');
    });
  });

  describe('updateDay', () => {
    it('should update day with all fields', async () => {
      const dayId = 1;
      const updateData = {
        tag: 'rest' as const,
        feeling: 'relaxed' as const,
        effort_score: 5,
        weight: 74.5,
        summary: 'Rest day, light activities',
      };

      const mockDay: Day = {
        id: dayId,
        user_id: 1,
        date: '2024-01-15',
        ...updateData,
        created_at: '2024-01-15T00:00:00Z',
      };

      mockApiClient.put.mockResolvedValueOnce({ data: mockDay });

      const result = await dayService.updateDay(dayId, updateData);

      expect(mockApiClient.put).toHaveBeenCalledWith(`/days/${dayId}`, updateData);
      expect(result).toEqual(mockDay);
    });

    it('should update only specified fields', async () => {
      const dayId = 1;
      const updateData = {
        effort_score: 7,
      };

      const mockDay: Day = {
        id: dayId,
        user_id: 1,
        date: '2024-01-15',
        effort_score: 7,
        created_at: '2024-01-15T00:00:00Z',
      };

      mockApiClient.put.mockResolvedValueOnce({ data: mockDay });

      const result = await dayService.updateDay(dayId, updateData);

      expect(result.effort_score).toBe(7);
    });

    it('should handle update errors', async () => {
      const dayId = 999;
      const updateData = { tag: 'workout' as const };

      mockApiClient.put.mockRejectedValueOnce(new Error('Day not found'));

      await expect(dayService.updateDay(dayId, updateData)).rejects.toThrow('Day not found');
    });
  });

  describe('deleteDay', () => {
    it('should delete a day', async () => {
      const dayId = 1;
      mockApiClient.delete.mockResolvedValueOnce({ data: undefined });

      await dayService.deleteDay(dayId);

      expect(mockApiClient.delete).toHaveBeenCalledWith(`/days/${dayId}`);
    });

    it('should handle delete errors', async () => {
      const dayId = 999;
      mockApiClient.delete.mockRejectedValueOnce(new Error('Day not found'));

      await expect(dayService.deleteDay(dayId)).rejects.toThrow('Day not found');
    });

    it('should successfully delete even with associated data', async () => {
      const dayId = 1;
      mockApiClient.delete.mockResolvedValueOnce({ data: undefined });

      await expect(dayService.deleteDay(dayId)).resolves.toBeUndefined();
    });
  });
});
