import { create } from 'zustand';
import type { Day, Meal, Exercise, WaterIntake, SleepRecord, MoodRecord, Note } from '../types/models/health';
import { dayService } from '../services/api/dayService';
import { mealService } from '../services/api/mealService';
import { exerciseService } from '../services/api/exerciseService';
import { waterService } from '../services/api/waterService';
import { sleepService } from '../services/api/sleepService';
import { moodService } from '../services/api/moodService';
import { noteService } from '../services/api/noteService';

interface DayState {
  // Current day data
  currentDay: Day | null;
  meals: Meal[];
  exercises: Exercise[];
  waterIntakes: WaterIntake[];
  sleepRecords: SleepRecord[];
  moodRecords: MoodRecord[];
  notes: Note[];

  // Loading states
  isLoading: boolean;
  isMealsLoading: boolean;
  isExercisesLoading: boolean;
  isWaterLoading: boolean;
  isSleepLoading: boolean;
  isMoodLoading: boolean;
  isNotesLoading: boolean;

  // Error state
  error: string | null;

  // Actions
  loadDay: (date: string) => Promise<void>;
  updateDay: (dayId: number, data: Partial<Day>) => Promise<void>;
  clearDay: () => void;

  // Meal actions
  loadMeals: (dayId: number) => Promise<void>;
  addMeal: (dayId: number, meal: any) => Promise<void>;
  updateMeal: (mealId: number, data: any) => Promise<void>;
  deleteMeal: (mealId: number) => Promise<void>;

  // Exercise actions
  loadExercises: (dayId: number) => Promise<void>;
  addExercise: (dayId: number, exercise: any) => Promise<void>;
  updateExercise: (exerciseId: number, data: any) => Promise<void>;
  deleteExercise: (exerciseId: number) => Promise<void>;

  // Water actions
  loadWater: (dayId: number) => Promise<void>;
  addWater: (dayId: number, amount: number) => Promise<void>;
  deleteWater: (waterIntakeId: number) => Promise<void>;

  // Sleep actions
  loadSleep: (dayId: number) => Promise<void>;
  addSleep: (dayId: number, data: any) => Promise<void>;
  updateSleep: (sleepId: number, data: any) => Promise<void>;
  deleteSleep: (sleepId: number) => Promise<void>;

  // Mood actions
  loadMood: (dayId: number) => Promise<void>;
  addMood: (dayId: number, data: any) => Promise<void>;
  updateMood: (moodId: number, data: any) => Promise<void>;
  deleteMood: (moodId: number) => Promise<void>;

  // Notes actions
  loadNotes: (dayId: number) => Promise<void>;
  addNote: (dayId: number, data: any) => Promise<void>;
  updateNote: (noteId: number, data: any) => Promise<void>;
  deleteNote: (noteId: number) => Promise<void>;
}

export const useDayStore = create<DayState>((set, get) => ({
  // Initial state
  currentDay: null,
  meals: [],
  exercises: [],
  waterIntakes: [],
  sleepRecords: [],
  moodRecords: [],
  notes: [],

  isLoading: false,
  isMealsLoading: false,
  isExercisesLoading: false,
  isWaterLoading: false,
  isSleepLoading: false,
  isMoodLoading: false,
  isNotesLoading: false,

  error: null,

  // Load day and all its data
  loadDay: async (date: string) => {
    set({ isLoading: true, error: null });
    try {
      // Get or create day
      let day = await dayService.getDayByDate(date);
      if (!day) {
        day = await dayService.createDay(date);
      }

      set({ currentDay: day, isLoading: false });

      // Load all related data in parallel
      if (day.id) {
        const { loadMeals, loadExercises, loadWater, loadSleep, loadMood, loadNotes } = get();
        await Promise.all([
          loadMeals(day.id),
          loadExercises(day.id),
          loadWater(day.id),
          loadSleep(day.id),
          loadMood(day.id),
          loadNotes(day.id),
        ]);
      }
    } catch (error) {
      console.error('Failed to load day:', error);
      set({ error: error instanceof Error ? error.message : 'Failed to load day', isLoading: false });
    }
  },

  updateDay: async (dayId: number, data: Partial<Day>) => {
    try {
      const updatedDay = await dayService.updateDay(dayId, data);
      set({ currentDay: updatedDay });
    } catch (error) {
      console.error('Failed to update day:', error);
      throw error;
    }
  },

  clearDay: () => {
    set({
      currentDay: null,
      meals: [],
      exercises: [],
      waterIntakes: [],
      sleepRecords: [],
      moodRecords: [],
      notes: [],
      error: null,
    });
  },

  // Meals
  loadMeals: async (dayId: number) => {
    set({ isMealsLoading: true });
    try {
      const meals = await mealService.getAll(dayId);
      set({ meals, isMealsLoading: false });
    } catch (error) {
      console.error('Failed to load meals:', error);
      set({ isMealsLoading: false });
    }
  },

  addMeal: async (dayId: number, mealData: any) => {
    try {
      const newMeal = await mealService.create(dayId, mealData);
      set((state) => ({ meals: [...state.meals, newMeal] }));
    } catch (error) {
      console.error('Failed to add meal:', error);
      throw error;
    }
  },

  updateMeal: async (mealId: number, data: any) => {
    try {
      const updatedMeal = await mealService.update(mealId, data);
      set((state) => ({
        meals: state.meals.map((m) => (m.id === mealId ? updatedMeal : m)),
      }));
    } catch (error) {
      console.error('Failed to update meal:', error);
      throw error;
    }
  },

  deleteMeal: async (mealId: number) => {
    try {
      await mealService.delete(mealId);
      set((state) => ({
        meals: state.meals.filter((m) => m.id !== mealId),
      }));
    } catch (error) {
      console.error('Failed to delete meal:', error);
      throw error;
    }
  },

  // Exercises
  loadExercises: async (dayId: number) => {
    set({ isExercisesLoading: true });
    try {
      const exercises = await exerciseService.getAll(dayId);
      set({ exercises, isExercisesLoading: false });
    } catch (error) {
      console.error('Failed to load exercises:', error);
      set({ isExercisesLoading: false });
    }
  },

  addExercise: async (dayId: number, exerciseData: any) => {
    try {
      const newExercise = await exerciseService.create(dayId, exerciseData);
      set((state) => ({ exercises: [...state.exercises, newExercise] }));
    } catch (error) {
      console.error('Failed to add exercise:', error);
      throw error;
    }
  },

  updateExercise: async (exerciseId: number, data: any) => {
    try {
      const updatedExercise = await exerciseService.update(exerciseId, data);
      set((state) => ({
        exercises: state.exercises.map((e) => (e.id === exerciseId ? updatedExercise : e)),
      }));
    } catch (error) {
      console.error('Failed to update exercise:', error);
      throw error;
    }
  },

  deleteExercise: async (exerciseId: number) => {
    try {
      await exerciseService.delete(exerciseId);
      set((state) => ({
        exercises: state.exercises.filter((e) => e.id !== exerciseId),
      }));
    } catch (error) {
      console.error('Failed to delete exercise:', error);
      throw error;
    }
  },

  // Water
  loadWater: async (dayId: number) => {
    set({ isWaterLoading: true });
    try {
      const waterIntakes = await waterService.getAll(dayId);
      set({ waterIntakes, isWaterLoading: false });
    } catch (error) {
      console.error('Failed to load water intakes:', error);
      set({ isWaterLoading: false });
    }
  },

  addWater: async (dayId: number, amount: number) => {
    try {
      const newIntake = await waterService.create(dayId, { amount });
      set((state) => ({ waterIntakes: [...state.waterIntakes, newIntake] }));
    } catch (error) {
      console.error('Failed to add water:', error);
      throw error;
    }
  },

  deleteWater: async (waterIntakeId: number) => {
    try {
      await waterService.delete(waterIntakeId);
      set((state) => ({
        waterIntakes: state.waterIntakes.filter((w) => w.id !== waterIntakeId),
      }));
    } catch (error) {
      console.error('Failed to delete water intake:', error);
      throw error;
    }
  },

  // Sleep
  loadSleep: async (dayId: number) => {
    set({ isSleepLoading: true });
    try {
      const sleepRecords = await sleepService.getAll(dayId);
      set({ sleepRecords, isSleepLoading: false });
    } catch (error) {
      console.error('Failed to load sleep records:', error);
      set({ isSleepLoading: false });
    }
  },

  addSleep: async (dayId: number, data: any) => {
    try {
      const newSleep = await sleepService.create(dayId, data);
      set((state) => ({ sleepRecords: [...state.sleepRecords, newSleep] }));
    } catch (error) {
      console.error('Failed to add sleep:', error);
      throw error;
    }
  },

  updateSleep: async (sleepId: number, data: any) => {
    try {
      const updatedSleep = await sleepService.update(sleepId, data);
      set((state) => ({
        sleepRecords: state.sleepRecords.map((s) => (s.id === sleepId ? updatedSleep : s)),
      }));
    } catch (error) {
      console.error('Failed to update sleep:', error);
      throw error;
    }
  },

  deleteSleep: async (sleepId: number) => {
    try {
      await sleepService.delete(sleepId);
      set((state) => ({
        sleepRecords: state.sleepRecords.filter((s) => s.id !== sleepId),
      }));
    } catch (error) {
      console.error('Failed to delete sleep:', error);
      throw error;
    }
  },

  // Mood
  loadMood: async (dayId: number) => {
    set({ isMoodLoading: true });
    try {
      const moodRecords = await moodService.getAll(dayId);
      set({ moodRecords, isMoodLoading: false });
    } catch (error) {
      console.error('Failed to load mood records:', error);
      set({ isMoodLoading: false });
    }
  },

  addMood: async (dayId: number, data: any) => {
    try {
      const newMood = await moodService.create(dayId, data);
      set((state) => ({ moodRecords: [...state.moodRecords, newMood] }));
    } catch (error) {
      console.error('Failed to add mood:', error);
      throw error;
    }
  },

  updateMood: async (moodId: number, data: any) => {
    try {
      const updatedMood = await moodService.update(moodId, data);
      set((state) => ({
        moodRecords: state.moodRecords.map((m) => (m.id === moodId ? updatedMood : m)),
      }));
    } catch (error) {
      console.error('Failed to update mood:', error);
      throw error;
    }
  },

  deleteMood: async (moodId: number) => {
    try {
      await moodService.delete(moodId);
      set((state) => ({
        moodRecords: state.moodRecords.filter((m) => m.id !== moodId),
      }));
    } catch (error) {
      console.error('Failed to delete mood:', error);
      throw error;
    }
  },

  // Notes
  loadNotes: async (dayId: number) => {
    set({ isNotesLoading: true });
    try {
      const notes = await noteService.getAll(dayId);
      set({ notes, isNotesLoading: false });
    } catch (error) {
      console.error('Failed to load notes:', error);
      set({ isNotesLoading: false });
    }
  },

  addNote: async (dayId: number, data: any) => {
    try {
      const newNote = await noteService.create(dayId, data);
      set((state) => ({ notes: [...state.notes, newNote] }));
    } catch (error) {
      console.error('Failed to add note:', error);
      throw error;
    }
  },

  updateNote: async (noteId: number, data: any) => {
    try {
      const updatedNote = await noteService.update(noteId, data);
      set((state) => ({
        notes: state.notes.map((n) => (n.id === noteId ? updatedNote : n)),
      }));
    } catch (error) {
      console.error('Failed to update note:', error);
      throw error;
    }
  },

  deleteNote: async (noteId: number) => {
    try {
      await noteService.delete(noteId);
      set((state) => ({
        notes: state.notes.filter((n) => n.id !== noteId),
      }));
    } catch (error) {
      console.error('Failed to delete note:', error);
      throw error;
    }
  },
}));
