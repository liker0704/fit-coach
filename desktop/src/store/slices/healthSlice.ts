import { StateCreator } from 'zustand';
import type { Day } from '@/types/models/health';

export interface HealthSlice {
  currentDay: Day | null;
  days: Day[];
  isLoading: boolean;
  setCurrentDay: (day: Day | null) => void;
  setDays: (days: Day[]) => void;
  setLoading: (isLoading: boolean) => void;
}

export const createHealthSlice: StateCreator<HealthSlice> = (set) => ({
  currentDay: null,
  days: [],
  isLoading: false,
  setCurrentDay: (currentDay) => set({ currentDay }),
  setDays: (days) => set({ days }),
  setLoading: (isLoading) => set({ isLoading }),
});
