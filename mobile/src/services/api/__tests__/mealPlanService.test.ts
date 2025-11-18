import { mealPlanService } from '../mealPlanService';
import { apiClient } from '../apiClient';
import type {
  MealPlan,
  GenerateMealPlanRequest,
  GenerateMealPlanResponse,
} from '../mealPlanService';

jest.mock('../apiClient');

const mockedApiClient = apiClient as jest.Mocked<typeof apiClient>;

describe('mealPlanService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('generate', () => {
    it('should generate new meal plan successfully', async () => {
      const request: GenerateMealPlanRequest = {
        dietary_preferences: ['vegetarian', 'high-protein'],
        calorie_target: 2000,
        allergies: ['nuts', 'dairy'],
      };

      const mockResponse: GenerateMealPlanResponse = {
        success: true,
        meal_plan_id: 1,
        meal_plan: {
          id: 1,
          user_id: 1,
          name: 'Vegetarian High-Protein Plan',
          calorie_target: 2000,
          dietary_preferences: ['vegetarian', 'high-protein'],
          allergies: ['nuts', 'dairy'],
          plan_data: {
            monday: {
              breakfast: [],
              lunch: [],
              dinner: [],
              snacks: [],
            },
          },
          is_active: false,
          created_at: '2025-01-15T10:00:00Z',
        } as MealPlan,
        message: 'Meal plan generated successfully',
      };

      mockedApiClient.post.mockResolvedValueOnce({ data: mockResponse });

      const result = await mealPlanService.generate(request);

      expect(mockedApiClient.post).toHaveBeenCalledWith(
        '/meal-plans/generate',
        request
      );
      expect(result).toEqual(mockResponse);
      expect(result.success).toBe(true);
    });

    it('should generate meal plan with minimal parameters', async () => {
      const request: GenerateMealPlanRequest = {
        calorie_target: 1800,
      };

      const mockResponse: GenerateMealPlanResponse = {
        success: true,
        meal_plan_id: 2,
      };

      mockedApiClient.post.mockResolvedValueOnce({ data: mockResponse });

      const result = await mealPlanService.generate(request);

      expect(result.success).toBe(true);
    });

    it('should handle generation failure', async () => {
      const request: GenerateMealPlanRequest = {
        calorie_target: 2500,
      };

      const mockResponse: GenerateMealPlanResponse = {
        success: false,
        message: 'AI service unavailable',
      };

      mockedApiClient.post.mockResolvedValueOnce({ data: mockResponse });

      const result = await mealPlanService.generate(request);

      expect(result.success).toBe(false);
      expect(result.message).toContain('unavailable');
    });

    it('should handle network error during generation', async () => {
      const request: GenerateMealPlanRequest = {
        calorie_target: 2000,
      };

      mockedApiClient.post.mockRejectedValueOnce(new Error('Network error'));

      await expect(mealPlanService.generate(request)).rejects.toThrow(
        'Network error'
      );
    });
  });

  describe('getAll', () => {
    it('should get all meal plans for user', async () => {
      const mockPlans: MealPlan[] = [
        {
          id: 1,
          user_id: 1,
          name: 'Weight Loss Plan',
          calorie_target: 1800,
          is_active: true,
          created_at: '2025-01-10T10:00:00Z',
        } as MealPlan,
        {
          id: 2,
          user_id: 1,
          name: 'Muscle Gain Plan',
          calorie_target: 2500,
          is_active: false,
          created_at: '2025-01-01T10:00:00Z',
        } as MealPlan,
      ];

      mockedApiClient.get.mockResolvedValueOnce({ data: mockPlans });

      const result = await mealPlanService.getAll();

      expect(mockedApiClient.get).toHaveBeenCalledWith('/meal-plans');
      expect(result).toEqual(mockPlans);
      expect(result).toHaveLength(2);
    });

    it('should return empty array when no plans', async () => {
      mockedApiClient.get.mockResolvedValueOnce({ data: [] });

      const result = await mealPlanService.getAll();

      expect(result).toEqual([]);
    });
  });

  describe('get', () => {
    it('should get meal plan by ID', async () => {
      const mockPlan: MealPlan = {
        id: 1,
        user_id: 1,
        name: 'Keto Plan',
        calorie_target: 2000,
        dietary_preferences: ['keto', 'low-carb'],
        plan_data: {
          monday: {
            breakfast: [
              {
                name: 'Eggs and Avocado',
                portion_size: '2 eggs + 1/2 avocado',
                calories: 350,
                protein: 18,
                carbs: 10,
                fat: 28,
              },
            ],
            lunch: [],
            dinner: [],
            snacks: [],
          },
        },
        summary: {
          total_calories_per_day: 2000,
          protein_target: '150g',
          carbs_target: '50g',
          fat_target: '150g',
        },
        is_active: true,
        created_at: '2025-01-15T10:00:00Z',
      } as MealPlan;

      mockedApiClient.get.mockResolvedValueOnce({ data: mockPlan });

      const result = await mealPlanService.get(1);

      expect(mockedApiClient.get).toHaveBeenCalledWith('/meal-plans/1');
      expect(result).toEqual(mockPlan);
      expect(result.name).toBe('Keto Plan');
    });

    it('should throw error when plan not found', async () => {
      mockedApiClient.get.mockRejectedValueOnce(new Error('Plan not found'));

      await expect(mealPlanService.get(999)).rejects.toThrow('Plan not found');
    });
  });

  describe('delete', () => {
    it('should delete meal plan', async () => {
      mockedApiClient.delete.mockResolvedValueOnce({ data: undefined });

      await mealPlanService.delete(1);

      expect(mockedApiClient.delete).toHaveBeenCalledWith('/meal-plans/1');
    });

    it('should handle delete error', async () => {
      mockedApiClient.delete.mockRejectedValueOnce(new Error('Delete failed'));

      await expect(mealPlanService.delete(999)).rejects.toThrow('Delete failed');
    });
  });

  describe('activate', () => {
    it('should activate meal plan', async () => {
      const mockActivatedPlan: MealPlan = {
        id: 1,
        user_id: 1,
        name: 'Active Plan',
        calorie_target: 2000,
        is_active: true,
        created_at: '2025-01-15T10:00:00Z',
      } as MealPlan;

      mockedApiClient.patch.mockResolvedValueOnce({ data: mockActivatedPlan });

      const result = await mealPlanService.activate(1);

      expect(mockedApiClient.patch).toHaveBeenCalledWith('/meal-plans/1/activate');
      expect(result).toEqual(mockActivatedPlan);
      expect(result.is_active).toBe(true);
    });

    it('should deactivate other plans when activating one', async () => {
      const mockPlan: MealPlan = {
        id: 2,
        user_id: 1,
        name: 'New Active Plan',
        calorie_target: 1800,
        is_active: true,
        created_at: '2025-01-16T10:00:00Z',
      } as MealPlan;

      mockedApiClient.patch.mockResolvedValueOnce({ data: mockPlan });

      const result = await mealPlanService.activate(2);

      expect(result.is_active).toBe(true);
    });

    it('should handle activation error', async () => {
      mockedApiClient.patch.mockRejectedValueOnce(
        new Error('Activation failed')
      );

      await expect(mealPlanService.activate(999)).rejects.toThrow(
        'Activation failed'
      );
    });
  });
});
