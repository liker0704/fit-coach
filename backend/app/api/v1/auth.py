"""Authentication endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import (
    EmailVerificationRequest,
    EmailVerificationResponse,
    PasswordReset,
    PasswordResetConfirm,
    RefreshTokenRequest,
    Token,
    UserLogin,
)
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    """Register a new user.

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        Created user

    Raises:
        HTTPException: If user already exists
    """
    try:
        user = AuthService.create_user(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login", response_model=Token)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
):
    """Authenticate user and return tokens.

    Args:
        credentials: User login credentials
        db: Database session

    Returns:
        Access and refresh tokens

    Raises:
        HTTPException: If credentials are invalid
    """
    user = AuthService.authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    tokens = AuthService.create_tokens(db, user)
    return tokens


@router.post("/refresh", response_model=dict)
def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """Refresh access token using refresh token.

    Args:
        request: Refresh token request
        db: Database session

    Returns:
        New access token

    Raises:
        HTTPException: If refresh token is invalid
    """
    access_token = AuthService.refresh_access_token(db, request.refresh_token)
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
def logout(
    request: RefreshTokenRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Logout user by revoking refresh token.

    Args:
        request: Refresh token request
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success message
    """
    AuthService.revoke_refresh_token(db, request.refresh_token)
    return {"message": "Successfully logged out"}


@router.post("/logout-all")
def logout_all(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Logout user from all devices by revoking all refresh tokens.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success message with count of revoked tokens
    """
    count = AuthService.revoke_all_user_tokens(db, current_user.id)
    return {"message": f"Successfully revoked {count} tokens"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """Get current user information.

    Args:
        current_user: Current authenticated user

    Returns:
        Current user data
    """
    return current_user


@router.post("/forgot-password")
def forgot_password(
    request: PasswordReset,
    db: Session = Depends(get_db),
):
    """Request a password reset token.

    Args:
        request: Password reset request with email
        db: Database session

    Returns:
        Success message (always returns success for security)
    """
    token = AuthService.create_password_reset_token(db, request.email)

    # Always return success message to avoid revealing if email exists
    # TODO: In production, send token via email instead of returning it
    return {
        "message": "If the email exists, a password reset link has been sent",
        "token": token  # TODO: Remove in production, send via email instead
    }


@router.post("/reset-password")
def reset_password(
    request: PasswordResetConfirm,
    db: Session = Depends(get_db),
):
    """Reset password using a reset token.

    Args:
        request: Password reset confirmation with token and new password
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If token is invalid or expired
    """
    success = AuthService.reset_password_with_token(
        db, request.token, request.new_password
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    return {"message": "Password has been reset successfully"}


@router.post("/verify-email", response_model=EmailVerificationResponse)
def verify_email(
    request: EmailVerificationRequest,
    db: Session = Depends(get_db),
):
    """Verify user email using a verification token.

    Args:
        request: Email verification request with token
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If token is invalid, expired, or email already verified
    """
    success = AuthService.verify_email_with_token(db, request.token)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid, expired, or already used verification token"
        )

    return EmailVerificationResponse(
        message="Email verified successfully"
    )


@router.post("/resend-verification", response_model=EmailVerificationResponse)
def resend_verification(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Resend email verification token to the current user.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success message with token (MVP only)

    Raises:
        HTTPException: If email is already verified
    """
    token = AuthService.resend_verification_email(db, current_user.id)

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified or user not found"
        )

    # TODO: In production, send token via email instead of returning it
    return EmailVerificationResponse(
        message="Verification email sent successfully",
        token=token  # MVP only - remove in production
    )
