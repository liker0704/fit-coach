import { mealsService } from '@/services/modules/mealsService';
import { apiClient } from '@/services/api/client';
import type { Meal } from '@/types/models/health';
import type {
  CreateMealDto,
  UpdateMealDto,
  PhotoUploadResponse,
  MealProcessingStatus,
} from '@/services/modules/mealsService';

jest.mock('@/services/api/client', () => ({
  apiClient: {
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
  },
}));

describe('mealsService', () => {
  const mockApiClient = apiClient as jest.Mocked<typeof apiClient>;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getAll', () => {
    it('should fetch all meals for a day', async () => {
      const dayId = 1;
      const mockMeals: Meal[] = [
        {
          id: 1,
          day_id: dayId,
          category: 'breakfast',
          time: '08:00',
          calories: 500,
          protein: 25,
          carbs: 60,
          fat: 15,
          created_at: '2024-01-15T08:00:00Z',
        },
        {
          id: 2,
          day_id: dayId,
          category: 'lunch',
          time: '12:00',
          calories: 700,
          protein: 35,
          carbs: 80,
          fat: 20,
          created_at: '2024-01-15T12:00:00Z',
        },
      ];

      mockApiClient.get.mockResolvedValueOnce({ data: mockMeals });

      const result = await mealsService.getAll(dayId);

      expect(mockApiClient.get).toHaveBeenCalledWith(`/days/${dayId}/meals`);
      expect(result).toEqual(mockMeals);
    });

    it('should return empty array when no meals exist', async () => {
      const dayId = 1;
      mockApiClient.get.mockResolvedValueOnce({ data: [] });

      const result = await mealsService.getAll(dayId);

      expect(result).toEqual([]);
    });
  });

  describe('get', () => {
    it('should fetch a single meal by id', async () => {
      const mealId = 1;
      const mockMeal: Meal = {
        id: mealId,
        day_id: 1,
        category: 'breakfast',
        time: '08:00',
        calories: 500,
        protein: 25,
        carbs: 60,
        fat: 15,
        notes: 'Oatmeal with fruits',
        created_at: '2024-01-15T08:00:00Z',
      };

      mockApiClient.get.mockResolvedValueOnce({ data: mockMeal });

      const result = await mealsService.get(mealId);

      expect(mockApiClient.get).toHaveBeenCalledWith(`/meals/${mealId}`);
      expect(result).toEqual(mockMeal);
    });

    it('should throw error when meal not found', async () => {
      const mealId = 999;
      mockApiClient.get.mockRejectedValueOnce(new Error('Meal not found'));

      await expect(mealsService.get(mealId)).rejects.toThrow('Meal not found');
    });
  });

  describe('create', () => {
    it('should create a new meal', async () => {
      const dayId = 1;
      const createData: Omit<CreateMealDto, 'day_id'> = {
        category: 'breakfast',
        time: '08:00',
        calories: 500,
        protein: 25,
        carbs: 60,
        fat: 15,
        notes: 'Healthy breakfast',
      };

      const mockMeal: Meal = {
        id: 1,
        day_id: dayId,
        ...createData,
        created_at: '2024-01-15T08:00:00Z',
      };

      mockApiClient.post.mockResolvedValueOnce({ data: mockMeal });

      const result = await mealsService.create(dayId, createData);

      expect(mockApiClient.post).toHaveBeenCalledWith(`/days/${dayId}/meals`, {
        ...createData,
        day_id: dayId,
      });
      expect(result).toEqual(mockMeal);
    });

    it('should create meal with minimal data', async () => {
      const dayId = 1;
      const createData: Omit<CreateMealDto, 'day_id'> = {
        category: 'snack',
      };

      const mockMeal: Meal = {
        id: 1,
        day_id: dayId,
        category: 'snack',
        created_at: '2024-01-15T15:00:00Z',
      };

      mockApiClient.post.mockResolvedValueOnce({ data: mockMeal });

      const result = await mealsService.create(dayId, createData);

      expect(result).toEqual(mockMeal);
    });

    it('should handle validation errors', async () => {
      const dayId = 1;
      const createData: Omit<CreateMealDto, 'day_id'> = {
        category: 'invalid_category' as any,
      };

      mockApiClient.post.mockRejectedValueOnce(new Error('Invalid category'));

      await expect(mealsService.create(dayId, createData)).rejects.toThrow('Invalid category');
    });
  });

  describe('update', () => {
    it('should update a meal', async () => {
      const mealId = 1;
      const updateData: UpdateMealDto = {
        calories: 550,
        protein: 30,
        notes: 'Updated notes',
      };

      const mockMeal: Meal = {
        id: mealId,
        day_id: 1,
        category: 'breakfast',
        ...updateData,
        created_at: '2024-01-15T08:00:00Z',
      };

      mockApiClient.put.mockResolvedValueOnce({ data: mockMeal });

      const result = await mealsService.update(mealId, updateData);

      expect(mockApiClient.put).toHaveBeenCalledWith(`/meals/${mealId}`, updateData);
      expect(result).toEqual(mockMeal);
    });

    it('should update only specified fields', async () => {
      const mealId = 1;
      const updateData: UpdateMealDto = {
        notes: 'New notes only',
      };

      const mockMeal: Meal = {
        id: mealId,
        day_id: 1,
        category: 'lunch',
        calories: 700,
        notes: 'New notes only',
        created_at: '2024-01-15T12:00:00Z',
      };

      mockApiClient.put.mockResolvedValueOnce({ data: mockMeal });

      const result = await mealsService.update(mealId, updateData);

      expect(result.notes).toBe('New notes only');
    });
  });

  describe('delete', () => {
    it('should delete a meal', async () => {
      const mealId = 1;
      mockApiClient.delete.mockResolvedValueOnce({ data: undefined });

      await mealsService.delete(mealId);

      expect(mockApiClient.delete).toHaveBeenCalledWith(`/meals/${mealId}`);
    });

    it('should handle delete errors', async () => {
      const mealId = 999;
      mockApiClient.delete.mockRejectedValueOnce(new Error('Meal not found'));

      await expect(mealsService.delete(mealId)).rejects.toThrow('Meal not found');
    });
  });

  describe('uploadPhoto', () => {
    it('should upload meal photo successfully', async () => {
      const dayId = 1;
      const category = 'lunch';
      const file = new File(['test'], 'meal.jpg', { type: 'image/jpeg' });

      const mockResponse: PhotoUploadResponse = {
        meal_id: 1,
        status: 'processing',
        message: 'Photo uploaded successfully',
        photo_path: '/uploads/meal_1.jpg',
      };

      mockApiClient.post.mockResolvedValueOnce({ data: mockResponse });

      const result = await mealsService.uploadPhoto(dayId, category, file);

      expect(mockApiClient.post).toHaveBeenCalledWith(
        `/meals/upload-photo?day_id=${dayId}&category=${category}`,
        expect.any(FormData),
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      expect(result).toEqual(mockResponse);
    });

    it('should handle upload errors', async () => {
      const dayId = 1;
      const category = 'lunch';
      const file = new File(['test'], 'meal.jpg', { type: 'image/jpeg' });

      mockApiClient.post.mockRejectedValueOnce(new Error('Upload failed'));

      await expect(mealsService.uploadPhoto(dayId, category, file)).rejects.toThrow(
        'Upload failed'
      );
    });
  });

  describe('getProcessingStatus', () => {
    it('should get processing status for completed meal', async () => {
      const mealId = 1;
      const mockStatus: MealProcessingStatus = {
        meal_id: mealId,
        status: 'completed',
        recognized_items: [
          {
            name: 'Chicken breast',
            quantity: 200,
            unit: 'grams',
            confidence: 'high',
          },
        ],
        meal_data: {
          id: mealId,
          day_id: 1,
          category: 'lunch',
          calories: 330,
          protein: 62,
          created_at: '2024-01-15T12:00:00Z',
        },
      };

      mockApiClient.get.mockResolvedValueOnce({ data: mockStatus });

      const result = await mealsService.getProcessingStatus(mealId);

      expect(mockApiClient.get).toHaveBeenCalledWith(`/meals/${mealId}/processing-status`);
      expect(result).toEqual(mockStatus);
      expect(result.status).toBe('completed');
    });

    it('should get processing status for pending meal', async () => {
      const mealId = 1;
      const mockStatus: MealProcessingStatus = {
        meal_id: mealId,
        status: 'processing',
      };

      mockApiClient.get.mockResolvedValueOnce({ data: mockStatus });

      const result = await mealsService.getProcessingStatus(mealId);

      expect(result.status).toBe('processing');
    });

    it('should get processing status for failed meal', async () => {
      const mealId = 1;
      const mockStatus: MealProcessingStatus = {
        meal_id: mealId,
        status: 'failed',
        error: 'Unable to recognize food items',
      };

      mockApiClient.get.mockResolvedValueOnce({ data: mockStatus });

      const result = await mealsService.getProcessingStatus(mealId);

      expect(result.status).toBe('failed');
      expect(result.error).toBeDefined();
    });
  });
});
