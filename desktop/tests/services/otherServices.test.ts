// Tests for moodService, sleepService, waterService, notesService, and userService
import { apiClient } from '@/services/api/client';

jest.mock('@/services/api/client', () => ({
  apiClient: {
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
  },
}));

const mockApiClient = apiClient as jest.Mocked<typeof apiClient>;

beforeEach(() => {
  jest.clearAllMocks();
});

// ===========================================
// moodService Tests
// ===========================================
describe('moodService', () => {
  const { moodService } = require('@/services/modules/moodService');

  describe('getAll', () => {
    it('should fetch all mood records for a day', async () => {
      const dayId = 1;
      const mockMoods = [
        {
          id: 1,
          day_id: dayId,
          time: '2024-01-15T08:00:00Z',
          rating: 4,
          energy_level: 7,
          stress_level: 3,
          created_at: '2024-01-15T08:00:00Z',
        },
      ];

      mockApiClient.get.mockResolvedValueOnce({ data: mockMoods });

      const result = await moodService.getAll(dayId);

      expect(mockApiClient.get).toHaveBeenCalledWith(`/days/${dayId}/moods`);
      expect(result).toEqual(mockMoods);
    });
  });

  describe('create', () => {
    it('should create a new mood record', async () => {
      const dayId = 1;
      const createData = {
        time: '2024-01-15T08:00:00Z',
        rating: 4,
        energy_level: 7,
        stress_level: 3,
        tags: ['happy', 'productive'],
        notes: 'Feeling great this morning',
      };

      const mockMood = {
        id: 1,
        day_id: dayId,
        ...createData,
        created_at: '2024-01-15T08:00:00Z',
      };

      mockApiClient.post.mockResolvedValueOnce({ data: mockMood });

      const result = await moodService.create(dayId, createData);

      expect(mockApiClient.post).toHaveBeenCalledWith(`/days/${dayId}/moods`, {
        ...createData,
        day_id: dayId,
      });
      expect(result).toEqual(mockMood);
    });
  });

  describe('update', () => {
    it('should update a mood record', async () => {
      const moodId = 1;
      const updateData = { rating: 5, notes: 'Even better now!' };

      mockApiClient.put.mockResolvedValueOnce({ data: { id: moodId, ...updateData } });

      const result = await moodService.update(moodId, updateData);

      expect(mockApiClient.put).toHaveBeenCalledWith(`/moods/${moodId}`, updateData);
      expect(result.rating).toBe(5);
    });
  });

  describe('delete', () => {
    it('should delete a mood record', async () => {
      const moodId = 1;
      mockApiClient.delete.mockResolvedValueOnce({ data: undefined });

      await moodService.delete(moodId);

      expect(mockApiClient.delete).toHaveBeenCalledWith(`/moods/${moodId}`);
    });
  });
});

// ===========================================
// sleepService Tests
// ===========================================
describe('sleepService', () => {
  const { sleepService } = require('@/services/modules/sleepService');

  describe('getAll', () => {
    it('should fetch all sleep records for a day', async () => {
      const dayId = 1;
      const mockSleep = [
        {
          id: 1,
          day_id: dayId,
          bedtime: '23:00',
          wake_time: '07:00',
          duration: 8,
          quality: 4,
          created_at: '2024-01-15T07:00:00Z',
        },
      ];

      mockApiClient.get.mockResolvedValueOnce({ data: mockSleep });

      const result = await sleepService.getAll(dayId);

      expect(mockApiClient.get).toHaveBeenCalledWith(`/days/${dayId}/sleep`);
      expect(result).toEqual(mockSleep);
    });
  });

  describe('create', () => {
    it('should create a new sleep record', async () => {
      const dayId = 1;
      const createData = {
        bedtime: '23:00',
        wake_time: '07:00',
        duration: 8,
        quality: 4,
        notes: 'Good sleep',
      };

      const mockSleep = {
        id: 1,
        day_id: dayId,
        ...createData,
        created_at: '2024-01-15T07:00:00Z',
      };

      mockApiClient.post.mockResolvedValueOnce({ data: mockSleep });

      const result = await sleepService.create(dayId, createData);

      expect(mockApiClient.post).toHaveBeenCalledWith(`/days/${dayId}/sleep`, createData);
      expect(result).toEqual(mockSleep);
    });
  });

  describe('update', () => {
    it('should update a sleep record', async () => {
      const sleepId = 1;
      const updateData = { quality: 5, notes: 'Excellent sleep!' };

      mockApiClient.put.mockResolvedValueOnce({ data: { id: sleepId, ...updateData } });

      const result = await sleepService.update(sleepId, updateData);

      expect(mockApiClient.put).toHaveBeenCalledWith(`/sleep/${sleepId}`, updateData);
      expect(result.quality).toBe(5);
    });
  });

  describe('delete', () => {
    it('should delete a sleep record', async () => {
      const sleepId = 1;
      mockApiClient.delete.mockResolvedValueOnce({ data: undefined });

      await sleepService.delete(sleepId);

      expect(mockApiClient.delete).toHaveBeenCalledWith(`/sleep/${sleepId}`);
    });
  });
});

// ===========================================
// waterService Tests
// ===========================================
describe('waterService', () => {
  const { waterService } = require('@/services/modules/waterService');

  describe('getAll', () => {
    it('should fetch all water intake records for a day', async () => {
      const dayId = 1;
      const mockWaterIntakes = [
        {
          id: 1,
          day_id: dayId,
          amount: 500,
          time: '08:00',
          created_at: '2024-01-15T08:00:00Z',
        },
        {
          id: 2,
          day_id: dayId,
          amount: 300,
          time: '12:00',
          created_at: '2024-01-15T12:00:00Z',
        },
      ];

      mockApiClient.get.mockResolvedValueOnce({ data: mockWaterIntakes });

      const result = await waterService.getAll(dayId);

      expect(mockApiClient.get).toHaveBeenCalledWith(`/days/${dayId}/water-intakes`);
      expect(result).toEqual(mockWaterIntakes);
    });
  });

  describe('create', () => {
    it('should create a new water intake record', async () => {
      const dayId = 1;
      const createData = {
        amount: 500,
        time: '08:00',
      };

      const mockWater = {
        id: 1,
        day_id: dayId,
        ...createData,
        created_at: '2024-01-15T08:00:00Z',
      };

      mockApiClient.post.mockResolvedValueOnce({ data: mockWater });

      const result = await waterService.create(dayId, createData);

      expect(mockApiClient.post).toHaveBeenCalledWith(`/days/${dayId}/water-intakes`, createData);
      expect(result).toEqual(mockWater);
    });

    it('should handle missing time field', async () => {
      const dayId = 1;
      const createData = {
        amount: 300,
      };

      const mockWater = {
        id: 1,
        day_id: dayId,
        amount: 300,
        created_at: '2024-01-15T10:00:00Z',
      };

      mockApiClient.post.mockResolvedValueOnce({ data: mockWater });

      const result = await waterService.create(dayId, createData);

      expect(result.amount).toBe(300);
    });
  });

  describe('delete', () => {
    it('should delete a water intake record', async () => {
      const waterIntakeId = 1;
      mockApiClient.delete.mockResolvedValueOnce({ data: undefined });

      await waterService.delete(waterIntakeId);

      expect(mockApiClient.delete).toHaveBeenCalledWith(`/water-intakes/${waterIntakeId}`);
    });
  });
});

// ===========================================
// notesService Tests
// ===========================================
describe('notesService', () => {
  const { notesService } = require('@/services/modules/notesService');

  describe('getAll', () => {
    it('should fetch all notes for a day', async () => {
      const dayId = 1;
      const mockNotes = [
        {
          id: 1,
          day_id: dayId,
          title: 'Morning thoughts',
          content: 'Feeling motivated today',
          created_at: '2024-01-15T08:00:00Z',
        },
      ];

      mockApiClient.get.mockResolvedValueOnce({ data: mockNotes });

      const result = await notesService.getAll(dayId);

      expect(mockApiClient.get).toHaveBeenCalledWith(`/days/${dayId}/notes`);
      expect(result).toEqual(mockNotes);
    });
  });

  describe('create', () => {
    it('should create a new note', async () => {
      const dayId = 1;
      const createData = {
        title: 'Training Plan',
        content: '# Week 1\n- Focus on cardio',
      };

      const mockNote = {
        id: 1,
        day_id: dayId,
        ...createData,
        created_at: '2024-01-15T10:00:00Z',
      };

      mockApiClient.post.mockResolvedValueOnce({ data: mockNote });

      const result = await notesService.create(dayId, createData);

      expect(mockApiClient.post).toHaveBeenCalledWith(`/days/${dayId}/notes`, createData);
      expect(result).toEqual(mockNote);
    });

    it('should create note without title', async () => {
      const dayId = 1;
      const createData = {
        content: 'Just a quick note',
      };

      const mockNote = {
        id: 1,
        day_id: dayId,
        content: 'Just a quick note',
        created_at: '2024-01-15T10:00:00Z',
      };

      mockApiClient.post.mockResolvedValueOnce({ data: mockNote });

      const result = await notesService.create(dayId, createData);

      expect(result.content).toBe('Just a quick note');
    });
  });

  describe('update', () => {
    it('should update a note', async () => {
      const noteId = 1;
      const updateData = {
        title: 'Updated Title',
        content: 'Updated content',
      };

      mockApiClient.put.mockResolvedValueOnce({ data: { id: noteId, ...updateData } });

      const result = await notesService.update(noteId, updateData);

      expect(mockApiClient.put).toHaveBeenCalledWith(`/notes/${noteId}`, updateData);
      expect(result.title).toBe('Updated Title');
    });
  });

  describe('delete', () => {
    it('should delete a note', async () => {
      const noteId = 1;
      mockApiClient.delete.mockResolvedValueOnce({ data: undefined });

      await notesService.delete(noteId);

      expect(mockApiClient.delete).toHaveBeenCalledWith(`/notes/${noteId}`);
    });
  });
});

// ===========================================
// userService Tests
// ===========================================
describe('userService', () => {
  const { userService } = require('@/services/modules/userService');

  describe('getProfile', () => {
    it('should fetch user profile', async () => {
      const mockUser = {
        id: 1,
        email: 'user@example.com',
        username: 'testuser',
        full_name: 'Test User',
        created_at: '2024-01-01T00:00:00Z',
      };

      mockApiClient.get.mockResolvedValueOnce({ data: mockUser });

      const result = await userService.getProfile();

      expect(mockApiClient.get).toHaveBeenCalledWith('/auth/me');
      expect(result).toEqual(mockUser);
    });

    it('should handle unauthorized error', async () => {
      mockApiClient.get.mockRejectedValueOnce(new Error('Unauthorized'));

      await expect(userService.getProfile()).rejects.toThrow('Unauthorized');
    });
  });

  describe('updateProfile', () => {
    it('should update user profile', async () => {
      const updateData = {
        full_name: 'Updated Name',
        username: 'newusername',
      };

      const mockUser = {
        id: 1,
        email: 'user@example.com',
        ...updateData,
        created_at: '2024-01-01T00:00:00Z',
      };

      mockApiClient.put.mockResolvedValueOnce({ data: mockUser });

      const result = await userService.updateProfile(updateData);

      expect(mockApiClient.put).toHaveBeenCalledWith('/users/me', updateData);
      expect(result).toEqual(mockUser);
      expect(result.full_name).toBe('Updated Name');
    });

    it('should handle validation errors', async () => {
      const updateData = {
        email: 'invalid-email',
      };

      mockApiClient.put.mockRejectedValueOnce(new Error('Invalid email format'));

      await expect(userService.updateProfile(updateData)).rejects.toThrow('Invalid email format');
    });
  });
});
