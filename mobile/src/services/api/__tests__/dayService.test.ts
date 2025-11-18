import { dayService } from '../dayService';
import { apiClient } from '../apiClient';
import type { Day } from '../../../types/models/health';

jest.mock('../apiClient');

const mockedApiClient = apiClient as jest.Mocked<typeof apiClient>;

describe('dayService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getDays', () => {
    it('should get days within date range', async () => {
      const mockDays: Day[] = [
        {
          id: 1,
          user_id: 1,
          date: '2025-01-15',
          tag: 'workout',
          feeling: 8,
        } as Day,
        {
          id: 2,
          user_id: 1,
          date: '2025-01-16',
          tag: 'rest',
          feeling: 7,
        } as Day,
      ];

      mockedApiClient.get.mockResolvedValueOnce({ data: mockDays });

      const result = await dayService.getDays('2025-01-15', '2025-01-16');

      expect(mockedApiClient.get).toHaveBeenCalledWith(
        '/days?start_date=2025-01-15&end_date=2025-01-16'
      );
      expect(result).toEqual(mockDays);
      expect(result).toHaveLength(2);
    });

    it('should get days without date range', async () => {
      const mockDays: Day[] = [];

      mockedApiClient.get.mockResolvedValueOnce({ data: mockDays });

      const result = await dayService.getDays();

      expect(mockedApiClient.get).toHaveBeenCalledWith('/days?');
      expect(result).toEqual([]);
    });

    it('should get days with only start date', async () => {
      const mockDays: Day[] = [
        { id: 1, user_id: 1, date: '2025-01-15' } as Day,
      ];

      mockedApiClient.get.mockResolvedValueOnce({ data: mockDays });

      const result = await dayService.getDays('2025-01-15');

      expect(mockedApiClient.get).toHaveBeenCalledWith('/days?start_date=2025-01-15');
    });
  });

  describe('getDay', () => {
    it('should get single day by ID', async () => {
      const mockDay: Day = {
        id: 1,
        user_id: 1,
        date: '2025-01-15',
        tag: 'workout',
        feeling: 8,
        effort_score: 7,
        weight: 75.5,
        summary: 'Great day!',
      } as Day;

      mockedApiClient.get.mockResolvedValueOnce({ data: mockDay });

      const result = await dayService.getDay(1);

      expect(mockedApiClient.get).toHaveBeenCalledWith('/days/id/1');
      expect(result).toEqual(mockDay);
    });

    it('should throw error when day not found', async () => {
      mockedApiClient.get.mockRejectedValueOnce(new Error('Day not found'));

      await expect(dayService.getDay(999)).rejects.toThrow('Day not found');
    });
  });

  describe('getDayByDate', () => {
    it('should get day by date', async () => {
      const mockDay: Day = {
        id: 1,
        user_id: 1,
        date: '2025-01-15',
        tag: 'workout',
      } as Day;

      mockedApiClient.get.mockResolvedValueOnce({ data: mockDay });

      const result = await dayService.getDayByDate('2025-01-15');

      expect(mockedApiClient.get).toHaveBeenCalledWith('/days/date/2025-01-15');
      expect(result).toEqual(mockDay);
    });

    it('should return null when day not found (404)', async () => {
      const error: any = new Error('Not found');
      error.response = { status: 404 };
      mockedApiClient.get.mockRejectedValueOnce(error);

      const result = await dayService.getDayByDate('2025-01-01');

      expect(result).toBeNull();
    });

    it('should throw error for non-404 errors', async () => {
      const error: any = new Error('Server error');
      error.response = { status: 500 };
      mockedApiClient.get.mockRejectedValueOnce(error);

      await expect(dayService.getDayByDate('2025-01-15')).rejects.toThrow(
        'Server error'
      );
    });
  });

  describe('createDay', () => {
    it('should create new day', async () => {
      const mockCreatedDay: Day = {
        id: 3,
        user_id: 1,
        date: '2025-01-17',
      } as Day;

      mockedApiClient.post.mockResolvedValueOnce({ data: mockCreatedDay });

      const result = await dayService.createDay('2025-01-17');

      expect(mockedApiClient.post).toHaveBeenCalledWith('/days', {
        date: '2025-01-17',
      });
      expect(result).toEqual(mockCreatedDay);
    });

    it('should handle duplicate day creation error', async () => {
      mockedApiClient.post.mockRejectedValueOnce(
        new Error('Day already exists')
      );

      await expect(dayService.createDay('2025-01-15')).rejects.toThrow(
        'Day already exists'
      );
    });
  });

  describe('updateDay', () => {
    it('should update day with all fields', async () => {
      const updateData = {
        tag: 'rest',
        feeling: 9,
        effort_score: 3,
        weight: 76.0,
        summary: 'Rest day, feeling good',
      };

      const mockUpdatedDay: Day = {
        id: 1,
        user_id: 1,
        date: '2025-01-15',
        ...updateData,
      } as Day;

      mockedApiClient.put.mockResolvedValueOnce({ data: mockUpdatedDay });

      const result = await dayService.updateDay(1, updateData);

      expect(mockedApiClient.put).toHaveBeenCalledWith('/days/1', updateData);
      expect(result).toEqual(mockUpdatedDay);
    });

    it('should update partial day data', async () => {
      const updateData = {
        feeling: 8,
      };

      const mockDay: Day = {
        id: 1,
        user_id: 1,
        date: '2025-01-15',
        feeling: 8,
      } as Day;

      mockedApiClient.put.mockResolvedValueOnce({ data: mockDay });

      const result = await dayService.updateDay(1, updateData);

      expect(result.feeling).toBe(8);
    });

    it('should update only weight', async () => {
      const updateData = {
        weight: 75.2,
      };

      const mockDay: Day = {
        id: 1,
        user_id: 1,
        date: '2025-01-15',
        weight: 75.2,
      } as Day;

      mockedApiClient.put.mockResolvedValueOnce({ data: mockDay });

      const result = await dayService.updateDay(1, updateData);

      expect(result.weight).toBe(75.2);
    });

    it('should update only summary', async () => {
      const updateData = {
        summary: 'Updated summary text',
      };

      const mockDay: Day = {
        id: 1,
        user_id: 1,
        date: '2025-01-15',
        summary: 'Updated summary text',
      } as Day;

      mockedApiClient.put.mockResolvedValueOnce({ data: mockDay });

      const result = await dayService.updateDay(1, updateData);

      expect(result.summary).toBe('Updated summary text');
    });
  });

  describe('deleteDay', () => {
    it('should delete day', async () => {
      mockedApiClient.delete.mockResolvedValueOnce({ data: undefined });

      await dayService.deleteDay(1);

      expect(mockedApiClient.delete).toHaveBeenCalledWith('/days/1');
    });

    it('should handle delete error', async () => {
      mockedApiClient.delete.mockRejectedValueOnce(new Error('Delete failed'));

      await expect(dayService.deleteDay(999)).rejects.toThrow('Delete failed');
    });
  });
});
