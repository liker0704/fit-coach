import { apiClient } from './apiClient';

export interface MealItem {
  name: string;
  portion_size: string;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  recipe_tips?: string;
}

export interface DayMeals {
  breakfast: MealItem[];
  lunch: MealItem[];
  dinner: MealItem[];
  snacks: MealItem[];
}

export interface MealPlanWeek {
  monday?: DayMeals;
  tuesday?: DayMeals;
  wednesday?: DayMeals;
  thursday?: DayMeals;
  friday?: DayMeals;
  saturday?: DayMeals;
  sunday?: DayMeals;
}

export interface MealPlanSummary {
  total_calories_per_day?: number;
  protein_target?: string;
  carbs_target?: string;
  fat_target?: string;
  notes?: string;
}

export interface MealPlan {
  id: number;
  user_id: number;
  name: string;
  calorie_target: number;
  dietary_preferences?: string[];
  allergies?: string[];
  plan_data: MealPlanWeek;
  summary?: MealPlanSummary;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface GenerateMealPlanRequest {
  dietary_preferences?: string[];
  calorie_target?: number;
  allergies?: string[];
}

export interface GenerateMealPlanResponse {
  success: boolean;
  meal_plan_id?: number;
  meal_plan?: MealPlan;
  message?: string;
}

export const mealPlanService = {
  /**
   * Generate a new 7-day meal plan
   */
  generate: async (
    request: GenerateMealPlanRequest
  ): Promise<GenerateMealPlanResponse> => {
    const response = await apiClient.post('/meal-plans/generate', request);
    return response.data;
  },

  /**
   * Get all meal plans for current user
   */
  getAll: async (): Promise<MealPlan[]> => {
    const response = await apiClient.get('/meal-plans');
    return response.data;
  },

  /**
   * Get a specific meal plan by ID
   */
  get: async (planId: number): Promise<MealPlan> => {
    const response = await apiClient.get(`/meal-plans/${planId}`);
    return response.data;
  },

  /**
   * Delete a meal plan
   */
  delete: async (planId: number): Promise<void> => {
    await apiClient.delete(`/meal-plans/${planId}`);
  },

  /**
   * Activate a meal plan (deactivates others)
   */
  activate: async (planId: number): Promise<MealPlan> => {
    const response = await apiClient.patch(`/meal-plans/${planId}/activate`);
    return response.data;
  },
};
