"""Training program schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TrainingProgramGenerateRequest(BaseModel):
    """Request schema for generating a new training program."""

    name: Optional[str] = Field(default="My Training Program", description="Name for the program")
    description: Optional[str] = Field(default=None, description="Optional description")
    goal: str = Field(..., description="Training goal (e.g., 'muscle_gain', 'weight_loss', 'strength', 'endurance')")
    experience_level: str = Field(default="beginner", description="Fitness level: beginner/intermediate/advanced")
    days_per_week: int = Field(default=3, description="Training days per week (2-7)", ge=2, le=7)
    equipment: Optional[List[str]] = Field(default=None, description="Available equipment (e.g., ['dumbbells', 'barbell'])")


class TrainingProgramResponse(BaseModel):
    """Response schema for training program."""

    id: int
    user_id: int
    name: str
    description: Optional[str] = None
    goal: str
    experience_level: str
    days_per_week: int
    equipment: Optional[List[str]] = None
    program_data: Dict[str, Any]  # 12-week program data
    summary: Optional[Dict[str, Any]] = None
    is_active: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TrainingProgramListResponse(BaseModel):
    """Response schema for list of training programs."""

    programs: List[TrainingProgramResponse]
    total: int


class TrainingProgramCreateResponse(BaseModel):
    """Response schema after creating a training program."""

    success: bool
    program: Optional[TrainingProgramResponse] = None
    error: Optional[str] = None
