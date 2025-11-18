import { create } from 'zustand';
import { createHealthSlice, HealthSlice } from '@/store/slices/healthSlice';
import type { Day } from '@/types/models/health';

describe('healthSlice', () => {
  let useHealthStore: ReturnType<typeof create<HealthSlice>>;

  beforeEach(() => {
    // Create a fresh store for each test
    useHealthStore = create<HealthSlice>()(createHealthSlice);
  });

  describe('initial state', () => {
    it('should have correct initial values', () => {
      const state = useHealthStore.getState();

      expect(state.currentDay).toBeNull();
      expect(state.days).toEqual([]);
      expect(state.isLoading).toBe(false);
    });
  });

  describe('setCurrentDay', () => {
    it('should set current day', () => {
      const mockDay: Day = {
        id: 1,
        user_id: 1,
        date: '2024-01-15',
        tag: 'workout',
        feeling: 'energetic',
        effort_score: 8,
        created_at: '2024-01-15T00:00:00Z',
      };

      useHealthStore.getState().setCurrentDay(mockDay);

      const state = useHealthStore.getState();
      expect(state.currentDay).toEqual(mockDay);
    });

    it('should replace existing current day', () => {
      const day1: Day = {
        id: 1,
        user_id: 1,
        date: '2024-01-15',
        created_at: '2024-01-15T00:00:00Z',
      };

      const day2: Day = {
        id: 2,
        user_id: 1,
        date: '2024-01-16',
        created_at: '2024-01-16T00:00:00Z',
      };

      useHealthStore.getState().setCurrentDay(day1);
      useHealthStore.getState().setCurrentDay(day2);

      const state = useHealthStore.getState();
      expect(state.currentDay).toEqual(day2);
      expect(state.currentDay?.id).toBe(2);
    });

    it('should allow setting current day to null', () => {
      const mockDay: Day = {
        id: 1,
        user_id: 1,
        date: '2024-01-15',
        created_at: '2024-01-15T00:00:00Z',
      };

      useHealthStore.getState().setCurrentDay(mockDay);
      expect(useHealthStore.getState().currentDay).not.toBeNull();

      useHealthStore.getState().setCurrentDay(null);

      const state = useHealthStore.getState();
      expect(state.currentDay).toBeNull();
    });
  });

  describe('setDays', () => {
    it('should set days array', () => {
      const mockDays: Day[] = [
        {
          id: 1,
          user_id: 1,
          date: '2024-01-15',
          created_at: '2024-01-15T00:00:00Z',
        },
        {
          id: 2,
          user_id: 1,
          date: '2024-01-16',
          created_at: '2024-01-16T00:00:00Z',
        },
      ];

      useHealthStore.getState().setDays(mockDays);

      const state = useHealthStore.getState();
      expect(state.days).toEqual(mockDays);
      expect(state.days).toHaveLength(2);
    });

    it('should replace existing days array', () => {
      const days1: Day[] = [
        {
          id: 1,
          user_id: 1,
          date: '2024-01-15',
          created_at: '2024-01-15T00:00:00Z',
        },
      ];

      const days2: Day[] = [
        {
          id: 2,
          user_id: 1,
          date: '2024-01-16',
          created_at: '2024-01-16T00:00:00Z',
        },
        {
          id: 3,
          user_id: 1,
          date: '2024-01-17',
          created_at: '2024-01-17T00:00:00Z',
        },
      ];

      useHealthStore.getState().setDays(days1);
      useHealthStore.getState().setDays(days2);

      const state = useHealthStore.getState();
      expect(state.days).toEqual(days2);
      expect(state.days).toHaveLength(2);
    });

    it('should allow setting empty days array', () => {
      const mockDays: Day[] = [
        {
          id: 1,
          user_id: 1,
          date: '2024-01-15',
          created_at: '2024-01-15T00:00:00Z',
        },
      ];

      useHealthStore.getState().setDays(mockDays);
      expect(useHealthStore.getState().days).toHaveLength(1);

      useHealthStore.getState().setDays([]);

      const state = useHealthStore.getState();
      expect(state.days).toEqual([]);
    });
  });

  describe('setLoading', () => {
    it('should set loading to true', () => {
      useHealthStore.getState().setLoading(true);

      const state = useHealthStore.getState();
      expect(state.isLoading).toBe(true);
    });

    it('should set loading to false', () => {
      useHealthStore.getState().setLoading(true);
      expect(useHealthStore.getState().isLoading).toBe(true);

      useHealthStore.getState().setLoading(false);

      const state = useHealthStore.getState();
      expect(state.isLoading).toBe(false);
    });

    it('should toggle loading state multiple times', () => {
      useHealthStore.getState().setLoading(true);
      expect(useHealthStore.getState().isLoading).toBe(true);

      useHealthStore.getState().setLoading(false);
      expect(useHealthStore.getState().isLoading).toBe(false);

      useHealthStore.getState().setLoading(true);
      expect(useHealthStore.getState().isLoading).toBe(true);
    });
  });

  describe('combined operations', () => {
    it('should handle typical data loading flow', () => {
      const mockDays: Day[] = [
        {
          id: 1,
          user_id: 1,
          date: '2024-01-15',
          created_at: '2024-01-15T00:00:00Z',
        },
        {
          id: 2,
          user_id: 1,
          date: '2024-01-16',
          created_at: '2024-01-16T00:00:00Z',
        },
      ];

      // Start loading
      useHealthStore.getState().setLoading(true);
      expect(useHealthStore.getState().isLoading).toBe(true);

      // Load data
      useHealthStore.getState().setDays(mockDays);
      useHealthStore.getState().setCurrentDay(mockDays[0]);

      // Stop loading
      useHealthStore.getState().setLoading(false);

      const state = useHealthStore.getState();
      expect(state.isLoading).toBe(false);
      expect(state.days).toEqual(mockDays);
      expect(state.currentDay).toEqual(mockDays[0]);
    });

    it('should handle changing current day from days list', () => {
      const mockDays: Day[] = [
        {
          id: 1,
          user_id: 1,
          date: '2024-01-15',
          tag: 'workout',
          created_at: '2024-01-15T00:00:00Z',
        },
        {
          id: 2,
          user_id: 1,
          date: '2024-01-16',
          tag: 'rest',
          created_at: '2024-01-16T00:00:00Z',
        },
      ];

      useHealthStore.getState().setDays(mockDays);

      // Select first day
      useHealthStore.getState().setCurrentDay(mockDays[0]);
      expect(useHealthStore.getState().currentDay?.tag).toBe('workout');

      // Select second day
      useHealthStore.getState().setCurrentDay(mockDays[1]);
      expect(useHealthStore.getState().currentDay?.tag).toBe('rest');
    });

    it('should handle clearing all state', () => {
      const mockDays: Day[] = [
        {
          id: 1,
          user_id: 1,
          date: '2024-01-15',
          created_at: '2024-01-15T00:00:00Z',
        },
      ];

      // Set some state
      useHealthStore.getState().setDays(mockDays);
      useHealthStore.getState().setCurrentDay(mockDays[0]);
      useHealthStore.getState().setLoading(true);

      // Clear state
      useHealthStore.getState().setDays([]);
      useHealthStore.getState().setCurrentDay(null);
      useHealthStore.getState().setLoading(false);

      const state = useHealthStore.getState();
      expect(state.days).toEqual([]);
      expect(state.currentDay).toBeNull();
      expect(state.isLoading).toBe(false);
    });
  });
});
