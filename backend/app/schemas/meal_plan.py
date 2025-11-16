"""Meal plan schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MealPlanGenerateRequest(BaseModel):
    """Request schema for generating a new meal plan."""

    name: Optional[str] = Field(default="My Meal Plan", description="Name for the meal plan")
    description: Optional[str] = Field(default=None, description="Optional description")
    calorie_target: Optional[int] = Field(default=None, description="Daily calorie target (auto-calculated if not provided)")
    dietary_preferences: Optional[List[str]] = Field(default=None, description="Dietary preferences (e.g., ['vegetarian', 'low-carb'])")
    allergies: Optional[List[str]] = Field(default=None, description="Food allergies (e.g., ['peanuts', 'dairy'])")


class MealPlanResponse(BaseModel):
    """Response schema for meal plan."""

    id: int
    user_id: int
    name: str
    description: Optional[str] = None
    calorie_target: int
    dietary_preferences: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    plan_data: Dict[str, Any]  # 7-day meal plan data
    summary: Optional[Dict[str, Any]] = None
    is_active: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MealPlanListResponse(BaseModel):
    """Response schema for list of meal plans."""

    meal_plans: List[MealPlanResponse]
    total: int


class MealPlanCreateResponse(BaseModel):
    """Response schema after creating a meal plan."""

    success: bool
    meal_plan: Optional[MealPlanResponse] = None
    error: Optional[str] = None
