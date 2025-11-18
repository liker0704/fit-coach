import { trainingProgramService } from '../trainingProgramService';
import { apiClient } from '../apiClient';
import type {
  TrainingProgram,
  GenerateTrainingProgramRequest,
  GenerateTrainingProgramResponse,
} from '../trainingProgramService';

jest.mock('../apiClient');

const mockedApiClient = apiClient as jest.Mocked<typeof apiClient>;

describe('trainingProgramService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('generate', () => {
    it('should generate new training program successfully', async () => {
      const request: GenerateTrainingProgramRequest = {
        goal: 'muscle_gain',
        experience_level: 'intermediate',
        days_per_week: 4,
        equipment: ['barbell', 'dumbbells', 'bench'],
      };

      const mockResponse: GenerateTrainingProgramResponse = {
        success: true,
        program_id: 1,
        program: {
          id: 1,
          user_id: 1,
          name: 'Intermediate Muscle Gain Program',
          goal: 'muscle_gain',
          experience_level: 'intermediate',
          days_per_week: 4,
          duration_weeks: 12,
          equipment: ['barbell', 'dumbbells', 'bench'],
          program_data: [
            {
              week_number: 1,
              focus: 'Foundation',
              workouts: [],
            },
          ],
          is_active: false,
          created_at: '2025-01-15T10:00:00Z',
        } as TrainingProgram,
        message: 'Training program generated successfully',
      };

      mockedApiClient.post.mockResolvedValueOnce({ data: mockResponse });

      const result = await trainingProgramService.generate(request);

      expect(mockedApiClient.post).toHaveBeenCalledWith(
        '/training-programs/generate',
        request
      );
      expect(result).toEqual(mockResponse);
      expect(result.success).toBe(true);
    });

    it('should generate program with minimal parameters', async () => {
      const request: GenerateTrainingProgramRequest = {
        goal: 'weight_loss',
      };

      const mockResponse: GenerateTrainingProgramResponse = {
        success: true,
        program_id: 2,
      };

      mockedApiClient.post.mockResolvedValueOnce({ data: mockResponse });

      const result = await trainingProgramService.generate(request);

      expect(result.success).toBe(true);
    });

    it('should generate beginner bodyweight program', async () => {
      const request: GenerateTrainingProgramRequest = {
        goal: 'general_fitness',
        experience_level: 'beginner',
        days_per_week: 3,
        equipment: ['bodyweight'],
      };

      const mockResponse: GenerateTrainingProgramResponse = {
        success: true,
        program_id: 3,
        program: {
          id: 3,
          user_id: 1,
          name: 'Beginner Bodyweight Program',
          goal: 'general_fitness',
          experience_level: 'beginner',
          days_per_week: 3,
          duration_weeks: 8,
          equipment: ['bodyweight'],
          program_data: [],
          is_active: false,
          created_at: '2025-01-15T10:00:00Z',
        } as TrainingProgram,
      };

      mockedApiClient.post.mockResolvedValueOnce({ data: mockResponse });

      const result = await trainingProgramService.generate(request);

      expect(result.program?.experience_level).toBe('beginner');
      expect(result.program?.equipment).toContain('bodyweight');
    });

    it('should handle generation failure', async () => {
      const request: GenerateTrainingProgramRequest = {
        goal: 'strength',
      };

      const mockResponse: GenerateTrainingProgramResponse = {
        success: false,
        message: 'AI service unavailable',
      };

      mockedApiClient.post.mockResolvedValueOnce({ data: mockResponse });

      const result = await trainingProgramService.generate(request);

      expect(result.success).toBe(false);
    });
  });

  describe('getAll', () => {
    it('should get all training programs for user', async () => {
      const mockPrograms: TrainingProgram[] = [
        {
          id: 1,
          user_id: 1,
          name: 'Strength Building',
          goal: 'strength',
          experience_level: 'advanced',
          days_per_week: 5,
          duration_weeks: 12,
          is_active: true,
          created_at: '2025-01-10T10:00:00Z',
        } as TrainingProgram,
        {
          id: 2,
          user_id: 1,
          name: 'Fat Loss Program',
          goal: 'weight_loss',
          experience_level: 'intermediate',
          days_per_week: 4,
          duration_weeks: 8,
          is_active: false,
          created_at: '2025-01-01T10:00:00Z',
        } as TrainingProgram,
      ];

      mockedApiClient.get.mockResolvedValueOnce({ data: mockPrograms });

      const result = await trainingProgramService.getAll();

      expect(mockedApiClient.get).toHaveBeenCalledWith('/training-programs');
      expect(result).toEqual(mockPrograms);
      expect(result).toHaveLength(2);
    });

    it('should return empty array when no programs', async () => {
      mockedApiClient.get.mockResolvedValueOnce({ data: [] });

      const result = await trainingProgramService.getAll();

      expect(result).toEqual([]);
    });
  });

  describe('get', () => {
    it('should get training program by ID', async () => {
      const mockProgram: TrainingProgram = {
        id: 1,
        user_id: 1,
        name: 'Push Pull Legs',
        goal: 'muscle_gain',
        experience_level: 'intermediate',
        days_per_week: 6,
        duration_weeks: 12,
        equipment: ['barbell', 'dumbbells', 'cable'],
        program_data: [
          {
            week_number: 1,
            focus: 'Volume',
            workouts: [
              {
                day_name: 'Push Day',
                focus: 'Chest, Shoulders, Triceps',
                exercises: [
                  {
                    name: 'Bench Press',
                    sets: 4,
                    reps: '8-10',
                    rest_seconds: 90,
                    intensity: 'heavy',
                  },
                ],
              },
            ],
          },
        ],
        summary: {
          goal: 'Build muscle mass',
          experience_level: 'intermediate',
          equipment_needed: ['barbell', 'dumbbells', 'cable'],
          progression_strategy: 'Progressive overload',
        },
        is_active: true,
        created_at: '2025-01-15T10:00:00Z',
      } as TrainingProgram;

      mockedApiClient.get.mockResolvedValueOnce({ data: mockProgram });

      const result = await trainingProgramService.get(1);

      expect(mockedApiClient.get).toHaveBeenCalledWith('/training-programs/1');
      expect(result).toEqual(mockProgram);
      expect(result.name).toBe('Push Pull Legs');
    });

    it('should throw error when program not found', async () => {
      mockedApiClient.get.mockRejectedValueOnce(new Error('Program not found'));

      await expect(trainingProgramService.get(999)).rejects.toThrow(
        'Program not found'
      );
    });
  });

  describe('delete', () => {
    it('should delete training program', async () => {
      mockedApiClient.delete.mockResolvedValueOnce({ data: undefined });

      await trainingProgramService.delete(1);

      expect(mockedApiClient.delete).toHaveBeenCalledWith('/training-programs/1');
    });

    it('should handle delete error', async () => {
      mockedApiClient.delete.mockRejectedValueOnce(new Error('Delete failed'));

      await expect(trainingProgramService.delete(999)).rejects.toThrow(
        'Delete failed'
      );
    });
  });

  describe('activate', () => {
    it('should activate training program', async () => {
      const mockActivatedProgram: TrainingProgram = {
        id: 1,
        user_id: 1,
        name: 'Active Program',
        goal: 'strength',
        experience_level: 'intermediate',
        days_per_week: 4,
        duration_weeks: 12,
        program_data: [],
        is_active: true,
        created_at: '2025-01-15T10:00:00Z',
      } as TrainingProgram;

      mockedApiClient.patch.mockResolvedValueOnce({ data: mockActivatedProgram });

      const result = await trainingProgramService.activate(1);

      expect(mockedApiClient.patch).toHaveBeenCalledWith(
        '/training-programs/1/activate'
      );
      expect(result).toEqual(mockActivatedProgram);
      expect(result.is_active).toBe(true);
    });

    it('should handle activation error', async () => {
      mockedApiClient.patch.mockRejectedValueOnce(
        new Error('Activation failed')
      );

      await expect(trainingProgramService.activate(999)).rejects.toThrow(
        'Activation failed'
      );
    });
  });
});
