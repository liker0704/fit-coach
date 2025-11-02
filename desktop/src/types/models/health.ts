export interface Day {
  id: number;
  user_id: number;
  date: string;
  tag?: string | null;
  feeling?: number | null;
  effort_score?: number | null;
  summary?: string | null;
  llm_advice?: string | null;
  notes: Note[];
  meals: Meal[];
  exercises: Exercise[];
  water_intakes: WaterIntake[];
  sleep_records: SleepRecord[];
  mood_records: MoodRecord[];
  created_at: string;
  updated_at: string;
}

export interface Meal {
  id: number;
  day_id: number;
  category: 'breakfast' | 'lunch' | 'dinner' | 'snack';
  time: string | null;
  calories: number | null;
  protein: number | null;
  carbs: number | null;
  fat: number | null;
  fiber: number | null;
  sugar: number | null;
  sodium: number | null;
  notes: string | null;
  photo_url: string | null;
  ai_summary: string | null;
  ai_suggestions: string | null;
  created_at: string;
}

export interface Exercise {
  id: number;
  day_id: number;
  type: string;
  name: string | null;
  start_time: string | null;
  duration: number | null;
  distance: number | null;
  calories_burned: number | null;
  heart_rate_avg: number | null;
  heart_rate_max: number | null;
  intensity: number | null;
  notes: string | null;
  created_at: string;
}

export interface WaterIntake {
  id: number;
  day_id: number;
  amount: number;
  time: string | null;
}

export interface SleepRecord {
  id: number;
  day_id: number;
  bedtime?: string | null;
  wake_time?: string | null;
  duration: number;
  quality: number | null;
  notes: string | null;
}

export interface MoodRecord {
  id: number;
  day_id: number;
  time: string;
  rating: number;
  energy_level: number | null;
  stress_level: number | null;
  anxiety_level: number | null;
  tags: string[] | null;
  notes: string | null;
  created_at: string;
}

export interface Note {
  id: number;
  day_id: number;
  content: string;
  created_at: string;
}
