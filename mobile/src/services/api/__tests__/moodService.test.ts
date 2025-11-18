import { moodService } from '../moodService';
import { apiClient } from '../apiClient';
import type { MoodRecord } from '../../../types/models/health';
import type { CreateMoodDto, UpdateMoodDto } from '../moodService';

jest.mock('../apiClient');

const mockedApiClient = apiClient as jest.Mocked<typeof apiClient>;

describe('moodService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getAll', () => {
    it('should get all mood records for a day', async () => {
      const mockMoodRecords: MoodRecord[] = [
        {
          id: 1,
          day_id: 1,
          time: '2025-01-15T08:00:00Z',
          rating: 4,
          energy_level: 7,
          stress_level: 3,
          anxiety_level: 2,
          tags: ['morning', 'energized'],
          notes: 'Feeling great',
        } as MoodRecord,
        {
          id: 2,
          day_id: 1,
          time: '2025-01-15T18:00:00Z',
          rating: 3,
          energy_level: 5,
          stress_level: 6,
          tags: ['tired'],
        } as MoodRecord,
      ];

      mockedApiClient.get.mockResolvedValueOnce({ data: mockMoodRecords });

      const result = await moodService.getAll(1);

      expect(mockedApiClient.get).toHaveBeenCalledWith('/days/1/moods');
      expect(result).toEqual(mockMoodRecords);
      expect(result).toHaveLength(2);
    });

    it('should return empty array when no mood records', async () => {
      mockedApiClient.get.mockResolvedValueOnce({ data: [] });

      const result = await moodService.getAll(1);

      expect(result).toEqual([]);
    });
  });

  describe('create', () => {
    it('should create new mood record with full data', async () => {
      const createDto: CreateMoodDto = {
        time: '2025-01-15T10:00:00Z',
        rating: 5,
        energy_level: 8,
        stress_level: 2,
        anxiety_level: 1,
        tags: ['happy', 'productive', 'focused'],
        notes: 'Great mood today!',
      };

      const mockCreatedMood: MoodRecord = {
        id: 3,
        day_id: 1,
        ...createDto,
      } as MoodRecord;

      mockedApiClient.post.mockResolvedValueOnce({ data: mockCreatedMood });

      const result = await moodService.create(1, createDto);

      expect(mockedApiClient.post).toHaveBeenCalledWith('/days/1/moods', {
        ...createDto,
        day_id: 1,
      });
      expect(result).toEqual(mockCreatedMood);
    });

    it('should create mood record with minimal data', async () => {
      const createDto: CreateMoodDto = {
        time: '2025-01-15T14:00:00Z',
        rating: 3,
      };

      const mockMood: MoodRecord = {
        id: 4,
        day_id: 2,
        time: '2025-01-15T14:00:00Z',
        rating: 3,
      } as MoodRecord;

      mockedApiClient.post.mockResolvedValueOnce({ data: mockMood });

      const result = await moodService.create(2, createDto);

      expect(result.rating).toBe(3);
    });

    it('should create mood record with low mood', async () => {
      const createDto: CreateMoodDto = {
        time: '2025-01-15T20:00:00Z',
        rating: 1,
        energy_level: 2,
        stress_level: 9,
        anxiety_level: 8,
        tags: ['stressed', 'anxious', 'overwhelmed'],
        notes: 'Very difficult day',
      };

      const mockMood: MoodRecord = {
        id: 5,
        day_id: 1,
        ...createDto,
      } as MoodRecord;

      mockedApiClient.post.mockResolvedValueOnce({ data: mockMood });

      const result = await moodService.create(1, createDto);

      expect(result.rating).toBe(1);
      expect(result.stress_level).toBe(9);
      expect(result.anxiety_level).toBe(8);
    });

    it('should create mood record with custom tags', async () => {
      const createDto: CreateMoodDto = {
        time: '2025-01-15T12:00:00Z',
        rating: 4,
        tags: ['workout', 'motivated', 'post-gym'],
      };

      const mockMood: MoodRecord = {
        id: 6,
        day_id: 1,
        ...createDto,
      } as MoodRecord;

      mockedApiClient.post.mockResolvedValueOnce({ data: mockMood });

      const result = await moodService.create(1, createDto);

      expect(result.tags).toEqual(['workout', 'motivated', 'post-gym']);
    });
  });

  describe('update', () => {
    it('should update mood record', async () => {
      const updateDto: UpdateMoodDto = {
        rating: 4,
        energy_level: 7,
        notes: 'Feeling better now',
      };

      const mockUpdatedMood: MoodRecord = {
        id: 1,
        day_id: 1,
        time: '2025-01-15T10:00:00Z',
        rating: 4,
        energy_level: 7,
        notes: 'Feeling better now',
      } as MoodRecord;

      mockedApiClient.put.mockResolvedValueOnce({ data: mockUpdatedMood });

      const result = await moodService.update(1, updateDto);

      expect(mockedApiClient.put).toHaveBeenCalledWith('/moods/1', updateDto);
      expect(result).toEqual(mockUpdatedMood);
    });

    it('should update partial mood data', async () => {
      const updateDto: UpdateMoodDto = {
        stress_level: 4,
      };

      const mockMood: MoodRecord = {
        id: 1,
        day_id: 1,
        time: '2025-01-15T10:00:00Z',
        rating: 3,
        stress_level: 4,
      } as MoodRecord;

      mockedApiClient.put.mockResolvedValueOnce({ data: mockMood });

      const result = await moodService.update(1, updateDto);

      expect(result.stress_level).toBe(4);
    });

    it('should update tags array', async () => {
      const updateDto: UpdateMoodDto = {
        tags: ['relaxed', 'calm', 'peaceful'],
      };

      const mockMood: MoodRecord = {
        id: 1,
        day_id: 1,
        time: '2025-01-15T10:00:00Z',
        rating: 4,
        tags: ['relaxed', 'calm', 'peaceful'],
      } as MoodRecord;

      mockedApiClient.put.mockResolvedValueOnce({ data: mockMood });

      const result = await moodService.update(1, updateDto);

      expect(result.tags).toEqual(['relaxed', 'calm', 'peaceful']);
    });
  });

  describe('delete', () => {
    it('should delete mood record', async () => {
      mockedApiClient.delete.mockResolvedValueOnce({ data: undefined });

      await moodService.delete(1);

      expect(mockedApiClient.delete).toHaveBeenCalledWith('/moods/1');
    });

    it('should handle delete error', async () => {
      mockedApiClient.delete.mockRejectedValueOnce(new Error('Delete failed'));

      await expect(moodService.delete(999)).rejects.toThrow('Delete failed');
    });
  });
});
