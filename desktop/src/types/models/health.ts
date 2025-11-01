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
  name: string;
  category?: string | null;
  calories: number | null;
  protein: number | null;
  carbs: number | null;
  fats: number | null;
  meal_time: string | null;
  notes: string | null;
}

export interface Exercise {
  id: number;
  day_id: number;
  name: string;
  exercise_type: string | null;
  start_time?: string | null;
  duration: number | null;
  distance?: number | null;
  intensity?: number | null;
  calories_burned: number | null;
  heart_rate?: number | null;
  notes: string | null;
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
  mood_level: number;
  notes: string | null;
  time: string | null;
}

export interface Note {
  id: number;
  day_id: number;
  content: string;
  created_at: string;
}
