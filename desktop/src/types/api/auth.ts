export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  full_name: string;
}

export interface User {
  id: number;
  email: string;
  username: string | null;
  full_name: string | null;
  age: number | null;
  weight: number | null;
  height: number | null;
  target_weight: number | null;
  water_goal: number | null;
  calorie_goal: number | null;
  sleep_goal: number | null;
  is_active: boolean;
  is_email_verified: boolean;
  created_at: string;
  updated_at: string;
}
