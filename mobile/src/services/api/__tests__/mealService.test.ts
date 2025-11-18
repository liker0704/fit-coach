import { mealService } from '../mealService';
import { apiClient } from '../apiClient';
import type { Meal } from '../../../types/models/health';
import type {
  CreateMealDto,
  UpdateMealDto,
  PhotoUploadResponse,
  MealProcessingStatus,
} from '../mealService';

jest.mock('../apiClient');

const mockedApiClient = apiClient as jest.Mocked<typeof apiClient>;

describe('mealService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getAll', () => {
    it('should get all meals for a day', async () => {
      const mockMeals: Meal[] = [
        {
          id: 1,
          day_id: 1,
          category: 'breakfast',
          time: '08:00',
          calories: 350,
          protein: 20,
          carbs: 40,
          fat: 10,
        } as Meal,
        {
          id: 2,
          day_id: 1,
          category: 'lunch',
          time: '12:30',
          calories: 550,
          protein: 35,
          carbs: 60,
          fat: 18,
        } as Meal,
      ];

      mockedApiClient.get.mockResolvedValueOnce({ data: mockMeals });

      const result = await mealService.getAll(1);

      expect(mockedApiClient.get).toHaveBeenCalledWith('/days/1/meals');
      expect(result).toEqual(mockMeals);
      expect(result).toHaveLength(2);
    });

    it('should return empty array when no meals', async () => {
      mockedApiClient.get.mockResolvedValueOnce({ data: [] });

      const result = await mealService.getAll(1);

      expect(result).toEqual([]);
    });
  });

  describe('get', () => {
    it('should get single meal by ID', async () => {
      const mockMeal: Meal = {
        id: 1,
        day_id: 1,
        category: 'breakfast',
        time: '08:00',
        calories: 350,
        protein: 20,
        carbs: 40,
        fat: 10,
        notes: 'Healthy breakfast',
      } as Meal;

      mockedApiClient.get.mockResolvedValueOnce({ data: mockMeal });

      const result = await mealService.get(1);

      expect(mockedApiClient.get).toHaveBeenCalledWith('/meals/1');
      expect(result).toEqual(mockMeal);
    });

    it('should throw error when meal not found', async () => {
      mockedApiClient.get.mockRejectedValueOnce(new Error('Meal not found'));

      await expect(mealService.get(999)).rejects.toThrow('Meal not found');
    });
  });

  describe('create', () => {
    it('should create new meal', async () => {
      const createDto: CreateMealDto = {
        category: 'lunch',
        time: '12:30',
        calories: 550,
        protein: 35,
        carbs: 60,
        fat: 18,
        notes: 'Chicken and rice',
      };

      const mockCreatedMeal: Meal = {
        id: 3,
        day_id: 1,
        ...createDto,
      } as Meal;

      mockedApiClient.post.mockResolvedValueOnce({ data: mockCreatedMeal });

      const result = await mealService.create(1, createDto);

      expect(mockedApiClient.post).toHaveBeenCalledWith('/days/1/meals', {
        ...createDto,
        day_id: 1,
      });
      expect(result).toEqual(mockCreatedMeal);
    });

    it('should create meal with minimal data', async () => {
      const createDto: CreateMealDto = {
        category: 'snack',
      };

      const mockMeal: Meal = {
        id: 4,
        day_id: 2,
        category: 'snack',
      } as Meal;

      mockedApiClient.post.mockResolvedValueOnce({ data: mockMeal });

      const result = await mealService.create(2, createDto);

      expect(result.category).toBe('snack');
    });
  });

  describe('update', () => {
    it('should update meal', async () => {
      const updateDto: UpdateMealDto = {
        calories: 600,
        notes: 'Updated notes',
      };

      const mockUpdatedMeal: Meal = {
        id: 1,
        day_id: 1,
        category: 'lunch',
        calories: 600,
        notes: 'Updated notes',
      } as Meal;

      mockedApiClient.put.mockResolvedValueOnce({ data: mockUpdatedMeal });

      const result = await mealService.update(1, updateDto);

      expect(mockedApiClient.put).toHaveBeenCalledWith('/meals/1', updateDto);
      expect(result).toEqual(mockUpdatedMeal);
    });

    it('should update partial meal data', async () => {
      const updateDto: UpdateMealDto = {
        protein: 40,
      };

      const mockMeal: Meal = {
        id: 1,
        day_id: 1,
        category: 'lunch',
        protein: 40,
      } as Meal;

      mockedApiClient.put.mockResolvedValueOnce({ data: mockMeal });

      const result = await mealService.update(1, updateDto);

      expect(result.protein).toBe(40);
    });
  });

  describe('delete', () => {
    it('should delete meal', async () => {
      mockedApiClient.delete.mockResolvedValueOnce({ data: undefined });

      await mealService.delete(1);

      expect(mockedApiClient.delete).toHaveBeenCalledWith('/meals/1');
    });

    it('should handle delete error', async () => {
      mockedApiClient.delete.mockRejectedValueOnce(new Error('Delete failed'));

      await expect(mealService.delete(999)).rejects.toThrow('Delete failed');
    });
  });

  describe('uploadPhoto', () => {
    it('should upload meal photo successfully', async () => {
      const mockResponse: PhotoUploadResponse = {
        meal_id: 1,
        status: 'processing',
        message: 'Photo uploaded, processing with AI',
        photo_path: '/uploads/meal_1.jpg',
      };

      mockedApiClient.post.mockResolvedValueOnce({ data: mockResponse });

      const result = await mealService.uploadPhoto(
        1,
        'lunch',
        'file:///path/to/photo.jpg'
      );

      expect(mockedApiClient.post).toHaveBeenCalledWith(
        '/meals/upload-photo?day_id=1&category=lunch',
        expect.any(FormData),
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      expect(result).toEqual(mockResponse);
      expect(result.status).toBe('processing');
    });

    it('should handle photo upload error', async () => {
      mockedApiClient.post.mockRejectedValueOnce(new Error('Upload failed'));

      await expect(
        mealService.uploadPhoto(1, 'breakfast', 'file:///invalid.jpg')
      ).rejects.toThrow('Upload failed');
    });

    it('should extract filename from URI correctly', async () => {
      const mockResponse: PhotoUploadResponse = {
        meal_id: 2,
        status: 'processing',
        message: 'Processing',
      };

      mockedApiClient.post.mockResolvedValueOnce({ data: mockResponse });

      await mealService.uploadPhoto(1, 'dinner', 'file:///storage/photos/dinner.jpg');

      const callArgs = mockedApiClient.post.mock.calls[0];
      expect(callArgs[0]).toContain('upload-photo');
    });
  });

  describe('getProcessingStatus', () => {
    it('should get processing status - completed', async () => {
      const mockStatus: MealProcessingStatus = {
        meal_id: 1,
        status: 'completed',
        recognized_items: [
          {
            name: 'Chicken Breast',
            quantity: 200,
            unit: 'g',
            confidence: 'high',
          },
          {
            name: 'Brown Rice',
            quantity: 150,
            unit: 'g',
            confidence: 'high',
          },
        ],
        meal_data: {
          id: 1,
          calories: 450,
          protein: 45,
          carbs: 50,
          fat: 8,
        } as Meal,
      };

      mockedApiClient.get.mockResolvedValueOnce({ data: mockStatus });

      const result = await mealService.getProcessingStatus(1);

      expect(mockedApiClient.get).toHaveBeenCalledWith(
        '/meals/1/processing-status'
      );
      expect(result).toEqual(mockStatus);
      expect(result.status).toBe('completed');
      expect(result.recognized_items).toHaveLength(2);
    });

    it('should get processing status - still processing', async () => {
      const mockStatus: MealProcessingStatus = {
        meal_id: 2,
        status: 'processing',
      };

      mockedApiClient.get.mockResolvedValueOnce({ data: mockStatus });

      const result = await mealService.getProcessingStatus(2);

      expect(result.status).toBe('processing');
      expect(result.recognized_items).toBeUndefined();
    });

    it('should get processing status - failed', async () => {
      const mockStatus: MealProcessingStatus = {
        meal_id: 3,
        status: 'failed',
        error: 'Could not recognize food in image',
      };

      mockedApiClient.get.mockResolvedValueOnce({ data: mockStatus });

      const result = await mealService.getProcessingStatus(3);

      expect(result.status).toBe('failed');
      expect(result.error).toBeDefined();
    });
  });
});
