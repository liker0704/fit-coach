"""Schemas package."""

from app.schemas.auth import (
    PasswordChange,
    PasswordReset,
    PasswordResetConfirm,
    RefreshTokenRequest,
    Token,
    TokenData,
    UserLogin,
)
from app.schemas.day import DayCreate, DayResponse, DayUpdate
from app.schemas.exercise import ExerciseCreate, ExerciseResponse, ExerciseUpdate
from app.schemas.meal import MealCreate, MealResponse, MealUpdate
from app.schemas.user import UserCreate, UserInDB, UserResponse, UserUpdate
from app.schemas.water import WaterCreate, WaterResponse, WaterUpdate

__all__ = [
    # User schemas
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserInDB",
    # Auth schemas
    "UserLogin",
    "Token",
    "TokenData",
    "RefreshTokenRequest",
    "PasswordChange",
    "PasswordReset",
    "PasswordResetConfirm",
    # Day schemas
    "DayCreate",
    "DayUpdate",
    "DayResponse",
    # Exercise schemas
    "ExerciseCreate",
    "ExerciseUpdate",
    "ExerciseResponse",
    # Meal schemas
    "MealCreate",
    "MealUpdate",
    "MealResponse",
    # Water schemas
    "WaterCreate",
    "WaterUpdate",
    "WaterResponse",
]
