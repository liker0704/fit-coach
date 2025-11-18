import { exercisesService } from '@/services/modules/exercisesService';
import { apiClient } from '@/services/api/client';
import type { Exercise } from '@/types/models/health';
import type { CreateExerciseDto, UpdateExerciseDto } from '@/services/modules/exercisesService';

jest.mock('@/services/api/client', () => ({
  apiClient: {
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
  },
}));

describe('exercisesService', () => {
  const mockApiClient = apiClient as jest.Mocked<typeof apiClient>;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getAll', () => {
    it('should fetch all exercises for a day', async () => {
      const dayId = 1;
      const mockExercises: Exercise[] = [
        {
          id: 1,
          day_id: dayId,
          type: 'running',
          name: 'Morning Run',
          start_time: '07:00',
          duration: 30,
          distance: 5.0,
          calories_burned: 300,
          created_at: '2024-01-15T07:00:00Z',
        },
        {
          id: 2,
          day_id: dayId,
          type: 'strength',
          name: 'Weight Training',
          start_time: '18:00',
          duration: 45,
          calories_burned: 250,
          created_at: '2024-01-15T18:00:00Z',
        },
      ];

      mockApiClient.get.mockResolvedValueOnce({ data: mockExercises });

      const result = await exercisesService.getAll(dayId);

      expect(mockApiClient.get).toHaveBeenCalledWith(`/days/${dayId}/exercises`);
      expect(result).toEqual(mockExercises);
      expect(result).toHaveLength(2);
    });

    it('should return empty array when no exercises exist', async () => {
      const dayId = 1;
      mockApiClient.get.mockResolvedValueOnce({ data: [] });

      const result = await exercisesService.getAll(dayId);

      expect(result).toEqual([]);
    });

    it('should handle API errors', async () => {
      const dayId = 1;
      mockApiClient.get.mockRejectedValueOnce(new Error('Failed to fetch exercises'));

      await expect(exercisesService.getAll(dayId)).rejects.toThrow('Failed to fetch exercises');
    });
  });

  describe('get', () => {
    it('should fetch a single exercise by id', async () => {
      const exerciseId = 1;
      const mockExercise: Exercise = {
        id: exerciseId,
        day_id: 1,
        type: 'running',
        name: 'Morning Run',
        start_time: '07:00',
        duration: 30,
        distance: 5.0,
        intensity: 7,
        calories_burned: 300,
        heart_rate_avg: 145,
        heart_rate_max: 165,
        notes: 'Good pace, felt strong',
        created_at: '2024-01-15T07:00:00Z',
      };

      mockApiClient.get.mockResolvedValueOnce({ data: mockExercise });

      const result = await exercisesService.get(exerciseId);

      expect(mockApiClient.get).toHaveBeenCalledWith(`/exercises/${exerciseId}`);
      expect(result).toEqual(mockExercise);
    });

    it('should throw error when exercise not found', async () => {
      const exerciseId = 999;
      mockApiClient.get.mockRejectedValueOnce(new Error('Exercise not found'));

      await expect(exercisesService.get(exerciseId)).rejects.toThrow('Exercise not found');
    });
  });

  describe('create', () => {
    it('should create a new exercise with full data', async () => {
      const createData: CreateExerciseDto = {
        day_id: 1,
        type: 'running',
        name: 'Evening Run',
        start_time: '18:00',
        duration: 40,
        distance: 6.5,
        intensity: 8,
        calories_burned: 400,
        heart_rate_avg: 155,
        heart_rate_max: 175,
        notes: 'Interval training',
      };

      const mockExercise: Exercise = {
        id: 1,
        ...createData,
        created_at: '2024-01-15T18:00:00Z',
      };

      mockApiClient.post.mockResolvedValueOnce({ data: mockExercise });

      const result = await exercisesService.create(createData);

      expect(mockApiClient.post).toHaveBeenCalledWith(`/days/${createData.day_id}/exercises`, createData);
      expect(result).toEqual(mockExercise);
    });

    it('should create exercise with minimal data', async () => {
      const createData: CreateExerciseDto = {
        day_id: 1,
        type: 'yoga',
      };

      const mockExercise: Exercise = {
        id: 1,
        day_id: 1,
        type: 'yoga',
        created_at: '2024-01-15T10:00:00Z',
      };

      mockApiClient.post.mockResolvedValueOnce({ data: mockExercise });

      const result = await exercisesService.create(createData);

      expect(result).toEqual(mockExercise);
    });

    it('should handle validation errors', async () => {
      const createData: CreateExerciseDto = {
        day_id: 1,
        type: '',
      };

      mockApiClient.post.mockRejectedValueOnce(new Error('Type is required'));

      await expect(exercisesService.create(createData)).rejects.toThrow('Type is required');
    });
  });

  describe('update', () => {
    it('should update an exercise', async () => {
      const exerciseId = 1;
      const updateData: UpdateExerciseDto = {
        duration: 45,
        distance: 7.0,
        calories_burned: 420,
        notes: 'Updated: Felt great!',
      };

      const mockExercise: Exercise = {
        id: exerciseId,
        day_id: 1,
        type: 'running',
        name: 'Morning Run',
        ...updateData,
        created_at: '2024-01-15T07:00:00Z',
      };

      mockApiClient.put.mockResolvedValueOnce({ data: mockExercise });

      const result = await exercisesService.update(exerciseId, updateData);

      expect(mockApiClient.put).toHaveBeenCalledWith(`/exercises/${exerciseId}`, updateData);
      expect(result).toEqual(mockExercise);
    });

    it('should update only specified fields', async () => {
      const exerciseId = 1;
      const updateData: UpdateExerciseDto = {
        notes: 'Quick update',
      };

      const mockExercise: Exercise = {
        id: exerciseId,
        day_id: 1,
        type: 'cycling',
        duration: 30,
        notes: 'Quick update',
        created_at: '2024-01-15T07:00:00Z',
      };

      mockApiClient.put.mockResolvedValueOnce({ data: mockExercise });

      const result = await exercisesService.update(exerciseId, updateData);

      expect(result.notes).toBe('Quick update');
    });

    it('should handle update errors', async () => {
      const exerciseId = 999;
      const updateData: UpdateExerciseDto = {
        duration: 30,
      };

      mockApiClient.put.mockRejectedValueOnce(new Error('Exercise not found'));

      await expect(exercisesService.update(exerciseId, updateData)).rejects.toThrow(
        'Exercise not found'
      );
    });
  });

  describe('delete', () => {
    it('should delete an exercise', async () => {
      const exerciseId = 1;
      mockApiClient.delete.mockResolvedValueOnce({ data: undefined });

      await exercisesService.delete(exerciseId);

      expect(mockApiClient.delete).toHaveBeenCalledWith(`/exercises/${exerciseId}`);
    });

    it('should handle delete errors', async () => {
      const exerciseId = 999;
      mockApiClient.delete.mockRejectedValueOnce(new Error('Exercise not found'));

      await expect(exercisesService.delete(exerciseId)).rejects.toThrow('Exercise not found');
    });
  });
});
