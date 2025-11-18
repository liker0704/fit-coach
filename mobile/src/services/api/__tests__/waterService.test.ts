import { waterService } from '../waterService';
import { apiClient } from '../apiClient';
import type { WaterIntake } from '../../../types/models/health';
import type { CreateWaterIntakeDto } from '../waterService';

jest.mock('../apiClient');

const mockedApiClient = apiClient as jest.Mocked<typeof apiClient>;

describe('waterService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getAll', () => {
    it('should get all water intakes for a day', async () => {
      const mockWaterIntakes: WaterIntake[] = [
        {
          id: 1,
          day_id: 1,
          amount: 250,
          time: '08:00',
          created_at: '2025-01-15T08:00:00Z',
        } as WaterIntake,
        {
          id: 2,
          day_id: 1,
          amount: 500,
          time: '12:00',
          created_at: '2025-01-15T12:00:00Z',
        } as WaterIntake,
      ];

      mockedApiClient.get.mockResolvedValueOnce({ data: mockWaterIntakes });

      const result = await waterService.getAll(1);

      expect(mockedApiClient.get).toHaveBeenCalledWith('/days/1/water-intakes');
      expect(result).toEqual(mockWaterIntakes);
      expect(result).toHaveLength(2);
    });

    it('should return empty array when no water intakes', async () => {
      mockedApiClient.get.mockResolvedValueOnce({ data: [] });

      const result = await waterService.getAll(1);

      expect(result).toEqual([]);
    });
  });

  describe('create', () => {
    it('should create new water intake with time', async () => {
      const createDto: CreateWaterIntakeDto = {
        amount: 300,
        time: '10:30',
      };

      const mockCreatedWaterIntake: WaterIntake = {
        id: 3,
        day_id: 1,
        amount: 300,
        time: '10:30',
        created_at: '2025-01-15T10:30:00Z',
      } as WaterIntake;

      mockedApiClient.post.mockResolvedValueOnce({ data: mockCreatedWaterIntake });

      const result = await waterService.create(1, createDto);

      expect(mockedApiClient.post).toHaveBeenCalledWith(
        '/days/1/water-intakes',
        createDto
      );
      expect(result).toEqual(mockCreatedWaterIntake);
    });

    it('should create water intake without time', async () => {
      const createDto: CreateWaterIntakeDto = {
        amount: 250,
      };

      const mockWaterIntake: WaterIntake = {
        id: 4,
        day_id: 2,
        amount: 250,
        created_at: '2025-01-15T14:00:00Z',
      } as WaterIntake;

      mockedApiClient.post.mockResolvedValueOnce({ data: mockWaterIntake });

      const result = await waterService.create(2, createDto);

      expect(result.amount).toBe(250);
    });

    it('should create large water intake (1L)', async () => {
      const createDto: CreateWaterIntakeDto = {
        amount: 1000,
        time: '18:00',
      };

      const mockWaterIntake: WaterIntake = {
        id: 5,
        day_id: 1,
        amount: 1000,
        time: '18:00',
        created_at: '2025-01-15T18:00:00Z',
      } as WaterIntake;

      mockedApiClient.post.mockResolvedValueOnce({ data: mockWaterIntake });

      const result = await waterService.create(1, createDto);

      expect(result.amount).toBe(1000);
    });

    it('should handle creation error', async () => {
      const createDto: CreateWaterIntakeDto = {
        amount: 250,
      };

      mockedApiClient.post.mockRejectedValueOnce(new Error('Creation failed'));

      await expect(waterService.create(1, createDto)).rejects.toThrow(
        'Creation failed'
      );
    });
  });

  describe('delete', () => {
    it('should delete water intake', async () => {
      mockedApiClient.delete.mockResolvedValueOnce({ data: undefined });

      await waterService.delete(1);

      expect(mockedApiClient.delete).toHaveBeenCalledWith('/water-intakes/1');
    });

    it('should handle delete error', async () => {
      mockedApiClient.delete.mockRejectedValueOnce(new Error('Delete failed'));

      await expect(waterService.delete(999)).rejects.toThrow('Delete failed');
    });
  });
});
