"""User management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.user import ChangePasswordRequest, UserResponse, UserUpdate
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter()


@router.put("/me", response_model=UserResponse)
def update_profile(
    profile_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user's profile.

    This endpoint allows updating profile information such as:
    - Personal info: full_name, age, height, weight, target_weight
    - Settings: language, timezone, water_goal, calorie_goal, sleep_goal

    Only profile fields can be updated. Auth fields (email, password, etc.)
    are managed through separate endpoints.

    Args:
        profile_data: Profile data to update
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated user profile

    Raises:
        HTTPException: If validation fails or update error occurs
    """
    # Get only the fields that were actually provided
    update_data = profile_data.model_dump(exclude_unset=True)

    # If no fields provided, return current user
    if not update_data:
        return current_user

    try:
        updated_user = UserService.update_profile(db, current_user.id, **update_data)
        return updated_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/me/password", status_code=status.HTTP_200_OK)
def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change current user's password.

    Args:
        request: Password change request with current and new passwords
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If current password is incorrect
    """
    try:
        AuthService.change_password(
            db, current_user, request.current_password, request.new_password
        )
        return {"message": "Password changed successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete current user account.

    This will permanently delete the user account and all associated data
    (days, goals, refresh tokens, notifications). This action cannot be undone.

    All refresh tokens for the user will be revoked, effectively logging them out
    from all devices.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        204 No Content on success

    Raises:
        HTTPException: If deletion fails
    """
    success = UserService.delete_account(db, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account",
        )

    # Return 204 No Content (no body needed)
    return None
