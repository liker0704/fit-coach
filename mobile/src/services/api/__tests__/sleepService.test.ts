import { sleepService } from '../sleepService';
import { apiClient } from '../apiClient';
import type { SleepRecord } from '../../../types/models/health';
import type { CreateSleepDto, UpdateSleepDto } from '../sleepService';

jest.mock('../apiClient');

const mockedApiClient = apiClient as jest.Mocked<typeof apiClient>;

describe('sleepService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getAll', () => {
    it('should get all sleep records for a day', async () => {
      const mockSleepRecords: SleepRecord[] = [
        {
          id: 1,
          day_id: 1,
          bedtime: '22:30',
          wake_time: '06:30',
          duration: 8,
          quality: 4,
          notes: 'Good sleep',
        } as SleepRecord,
      ];

      mockedApiClient.get.mockResolvedValueOnce({ data: mockSleepRecords });

      const result = await sleepService.getAll(1);

      expect(mockedApiClient.get).toHaveBeenCalledWith('/days/1/sleep');
      expect(result).toEqual(mockSleepRecords);
      expect(result).toHaveLength(1);
    });

    it('should return empty array when no sleep records', async () => {
      mockedApiClient.get.mockResolvedValueOnce({ data: [] });

      const result = await sleepService.getAll(1);

      expect(result).toEqual([]);
    });
  });

  describe('create', () => {
    it('should create new sleep record with full data', async () => {
      const createDto: CreateSleepDto = {
        bedtime: '23:00',
        wake_time: '07:00',
        duration: 8,
        quality: 5,
        notes: 'Excellent sleep',
      };

      const mockCreatedSleep: SleepRecord = {
        id: 2,
        day_id: 1,
        ...createDto,
      } as SleepRecord;

      mockedApiClient.post.mockResolvedValueOnce({ data: mockCreatedSleep });

      const result = await sleepService.create(1, createDto);

      expect(mockedApiClient.post).toHaveBeenCalledWith('/days/1/sleep', createDto);
      expect(result).toEqual(mockCreatedSleep);
    });

    it('should create sleep record with minimal data', async () => {
      const createDto: CreateSleepDto = {
        duration: 7,
        quality: 3,
      };

      const mockSleep: SleepRecord = {
        id: 3,
        day_id: 2,
        duration: 7,
        quality: 3,
      } as SleepRecord;

      mockedApiClient.post.mockResolvedValueOnce({ data: mockSleep });

      const result = await sleepService.create(2, createDto);

      expect(result.duration).toBe(7);
      expect(result.quality).toBe(3);
    });

    it('should create sleep record with poor quality', async () => {
      const createDto: CreateSleepDto = {
        bedtime: '01:00',
        wake_time: '05:00',
        duration: 4,
        quality: 1,
        notes: 'Insomnia, very bad sleep',
      };

      const mockSleep: SleepRecord = {
        id: 4,
        day_id: 1,
        ...createDto,
      } as SleepRecord;

      mockedApiClient.post.mockResolvedValueOnce({ data: mockSleep });

      const result = await sleepService.create(1, createDto);

      expect(result.quality).toBe(1);
      expect(result.duration).toBe(4);
    });
  });

  describe('update', () => {
    it('should update sleep record', async () => {
      const updateDto: UpdateSleepDto = {
        wake_time: '07:30',
        duration: 8.5,
        quality: 4,
        notes: 'Updated: woke up 30 min later',
      };

      const mockUpdatedSleep: SleepRecord = {
        id: 1,
        day_id: 1,
        bedtime: '23:00',
        wake_time: '07:30',
        duration: 8.5,
        quality: 4,
        notes: 'Updated: woke up 30 min later',
      } as SleepRecord;

      mockedApiClient.put.mockResolvedValueOnce({ data: mockUpdatedSleep });

      const result = await sleepService.update(1, updateDto);

      expect(mockedApiClient.put).toHaveBeenCalledWith('/sleep/1', updateDto);
      expect(result).toEqual(mockUpdatedSleep);
    });

    it('should update partial sleep data', async () => {
      const updateDto: UpdateSleepDto = {
        quality: 5,
      };

      const mockSleep: SleepRecord = {
        id: 1,
        day_id: 1,
        quality: 5,
      } as SleepRecord;

      mockedApiClient.put.mockResolvedValueOnce({ data: mockSleep });

      const result = await sleepService.update(1, updateDto);

      expect(result.quality).toBe(5);
    });

    it('should update only notes', async () => {
      const updateDto: UpdateSleepDto = {
        notes: 'Woke up refreshed',
      };

      const mockSleep: SleepRecord = {
        id: 1,
        day_id: 1,
        notes: 'Woke up refreshed',
      } as SleepRecord;

      mockedApiClient.put.mockResolvedValueOnce({ data: mockSleep });

      const result = await sleepService.update(1, updateDto);

      expect(result.notes).toBe('Woke up refreshed');
    });
  });

  describe('delete', () => {
    it('should delete sleep record', async () => {
      mockedApiClient.delete.mockResolvedValueOnce({ data: undefined });

      await sleepService.delete(1);

      expect(mockedApiClient.delete).toHaveBeenCalledWith('/sleep/1');
    });

    it('should handle delete error', async () => {
      mockedApiClient.delete.mockRejectedValueOnce(new Error('Delete failed'));

      await expect(sleepService.delete(999)).rejects.toThrow('Delete failed');
    });
  });
});
