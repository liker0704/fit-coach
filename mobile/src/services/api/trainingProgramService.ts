import { apiClient } from './apiClient';

export interface Exercise {
  name: string;
  sets: number;
  reps: string;
  rest_seconds: number;
  intensity?: string;
  notes?: string;
}

export interface WorkoutDay {
  day_name: string;
  focus: string;
  exercises: Exercise[];
  estimated_duration_minutes?: number;
  warm_up?: string;
  cool_down?: string;
}

export interface TrainingWeek {
  week_number: number;
  focus: string;
  workouts: WorkoutDay[];
  notes?: string;
}

export interface ProgramSummary {
  goal?: string;
  experience_level?: string;
  equipment_needed?: string[];
  progression_strategy?: string;
  notes?: string;
}

export interface TrainingProgram {
  id: number;
  user_id: number;
  name: string;
  goal: string;
  experience_level: string;
  days_per_week: number;
  duration_weeks: number;
  equipment?: string[];
  program_data: TrainingWeek[];
  summary?: ProgramSummary;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface GenerateTrainingProgramRequest {
  goal: string;
  experience_level?: string;
  days_per_week?: number;
  equipment?: string[];
}

export interface GenerateTrainingProgramResponse {
  success: boolean;
  program_id?: number;
  program?: TrainingProgram;
  message?: string;
}

export const trainingProgramService = {
  /**
   * Generate a new 12-week training program
   */
  generate: async (
    request: GenerateTrainingProgramRequest
  ): Promise<GenerateTrainingProgramResponse> => {
    const response = await apiClient.post('/training-programs/generate', request);
    return response.data;
  },

  /**
   * Get all training programs for current user
   */
  getAll: async (): Promise<TrainingProgram[]> => {
    const response = await apiClient.get('/training-programs');
    return response.data;
  },

  /**
   * Get a specific training program by ID
   */
  get: async (programId: number): Promise<TrainingProgram> => {
    const response = await apiClient.get(`/training-programs/${programId}`);
    return response.data;
  },

  /**
   * Delete a training program
   */
  delete: async (programId: number): Promise<void> => {
    await apiClient.delete(`/training-programs/${programId}`);
  },

  /**
   * Activate a training program (deactivates others)
   */
  activate: async (programId: number): Promise<TrainingProgram> => {
    const response = await apiClient.patch(
      `/training-programs/${programId}/activate`
    );
    return response.data;
  },
};
