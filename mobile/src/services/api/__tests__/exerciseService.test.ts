import { exerciseService } from '../exerciseService';
import { apiClient } from '../apiClient';
import type { Exercise } from '../../../types/models/health';
import type { CreateExerciseDto, UpdateExerciseDto } from '../exerciseService';

jest.mock('../apiClient');

const mockedApiClient = apiClient as jest.Mocked<typeof apiClient>;

describe('exerciseService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getAll', () => {
    it('should get all exercises for a day', async () => {
      const mockExercises: Exercise[] = [
        {
          id: 1,
          day_id: 1,
          type: 'running',
          name: 'Morning Run',
          start_time: '06:00',
          duration: 30,
          distance: 5,
          calories_burned: 300,
        } as Exercise,
        {
          id: 2,
          day_id: 1,
          type: 'strength',
          name: 'Weight Training',
          start_time: '18:00',
          duration: 45,
          calories_burned: 250,
        } as Exercise,
      ];

      mockedApiClient.get.mockResolvedValueOnce({ data: mockExercises });

      const result = await exerciseService.getAll(1);

      expect(mockedApiClient.get).toHaveBeenCalledWith('/days/1/exercises');
      expect(result).toEqual(mockExercises);
      expect(result).toHaveLength(2);
    });

    it('should return empty array when no exercises', async () => {
      mockedApiClient.get.mockResolvedValueOnce({ data: [] });

      const result = await exerciseService.getAll(1);

      expect(result).toEqual([]);
    });
  });

  describe('get', () => {
    it('should get single exercise by ID', async () => {
      const mockExercise: Exercise = {
        id: 1,
        day_id: 1,
        type: 'cycling',
        name: 'Evening Bike Ride',
        start_time: '17:00',
        duration: 60,
        distance: 20,
        calories_burned: 400,
        heart_rate_avg: 140,
        heart_rate_max: 165,
        notes: 'Great ride!',
      } as Exercise;

      mockedApiClient.get.mockResolvedValueOnce({ data: mockExercise });

      const result = await exerciseService.get(1);

      expect(mockedApiClient.get).toHaveBeenCalledWith('/exercises/1');
      expect(result).toEqual(mockExercise);
    });

    it('should throw error when exercise not found', async () => {
      mockedApiClient.get.mockRejectedValueOnce(new Error('Exercise not found'));

      await expect(exerciseService.get(999)).rejects.toThrow('Exercise not found');
    });
  });

  describe('create', () => {
    it('should create new exercise with full data', async () => {
      const createDto: CreateExerciseDto = {
        type: 'running',
        name: 'Morning Run',
        start_time: '06:00',
        duration: 30,
        distance: 5,
        intensity: 7,
        calories_burned: 300,
        heart_rate_avg: 145,
        heart_rate_max: 170,
        notes: 'Felt great!',
      };

      const mockCreatedExercise: Exercise = {
        id: 3,
        day_id: 1,
        ...createDto,
      } as Exercise;

      mockedApiClient.post.mockResolvedValueOnce({ data: mockCreatedExercise });

      const result = await exerciseService.create(1, createDto);

      expect(mockedApiClient.post).toHaveBeenCalledWith('/days/1/exercises', {
        ...createDto,
        day_id: 1,
      });
      expect(result).toEqual(mockCreatedExercise);
    });

    it('should create exercise with minimal data', async () => {
      const createDto: CreateExerciseDto = {
        type: 'yoga',
      };

      const mockExercise: Exercise = {
        id: 4,
        day_id: 2,
        type: 'yoga',
      } as Exercise;

      mockedApiClient.post.mockResolvedValueOnce({ data: mockExercise });

      const result = await exerciseService.create(2, createDto);

      expect(result.type).toBe('yoga');
    });

    it('should create strength training exercise', async () => {
      const createDto: CreateExerciseDto = {
        type: 'strength',
        name: 'Upper Body Workout',
        start_time: '18:00',
        duration: 45,
        intensity: 8,
        calories_burned: 250,
      };

      const mockExercise: Exercise = {
        id: 5,
        day_id: 1,
        ...createDto,
      } as Exercise;

      mockedApiClient.post.mockResolvedValueOnce({ data: mockExercise });

      const result = await exerciseService.create(1, createDto);

      expect(result.type).toBe('strength');
      expect(result.intensity).toBe(8);
    });
  });

  describe('update', () => {
    it('should update exercise', async () => {
      const updateDto: UpdateExerciseDto = {
        duration: 35,
        distance: 5.5,
        calories_burned: 320,
        notes: 'Updated notes',
      };

      const mockUpdatedExercise: Exercise = {
        id: 1,
        day_id: 1,
        type: 'running',
        duration: 35,
        distance: 5.5,
        calories_burned: 320,
        notes: 'Updated notes',
      } as Exercise;

      mockedApiClient.put.mockResolvedValueOnce({ data: mockUpdatedExercise });

      const result = await exerciseService.update(1, updateDto);

      expect(mockedApiClient.put).toHaveBeenCalledWith('/exercises/1', updateDto);
      expect(result).toEqual(mockUpdatedExercise);
    });

    it('should update partial exercise data', async () => {
      const updateDto: UpdateExerciseDto = {
        intensity: 9,
      };

      const mockExercise: Exercise = {
        id: 1,
        day_id: 1,
        type: 'running',
        intensity: 9,
      } as Exercise;

      mockedApiClient.put.mockResolvedValueOnce({ data: mockExercise });

      const result = await exerciseService.update(1, updateDto);

      expect(result.intensity).toBe(9);
    });

    it('should update heart rate data', async () => {
      const updateDto: UpdateExerciseDto = {
        heart_rate_avg: 155,
        heart_rate_max: 180,
      };

      const mockExercise: Exercise = {
        id: 1,
        day_id: 1,
        type: 'running',
        heart_rate_avg: 155,
        heart_rate_max: 180,
      } as Exercise;

      mockedApiClient.put.mockResolvedValueOnce({ data: mockExercise });

      const result = await exerciseService.update(1, updateDto);

      expect(result.heart_rate_avg).toBe(155);
      expect(result.heart_rate_max).toBe(180);
    });
  });

  describe('delete', () => {
    it('should delete exercise', async () => {
      mockedApiClient.delete.mockResolvedValueOnce({ data: undefined });

      await exerciseService.delete(1);

      expect(mockedApiClient.delete).toHaveBeenCalledWith('/exercises/1');
    });

    it('should handle delete error', async () => {
      mockedApiClient.delete.mockRejectedValueOnce(new Error('Delete failed'));

      await expect(exerciseService.delete(999)).rejects.toThrow('Delete failed');
    });
  });
});
