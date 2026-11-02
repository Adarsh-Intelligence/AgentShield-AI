from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.app.api.deps import get_current_user, security_scheme
from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.auth import (
    RefreshTokenRequest,
    Token,
    UserCreate,
    UserLogin,
    UserResponse,
)
from backend.app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Register a new user (Developer or Admin)."""
    return AuthService.register_user(db, user_in)


@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate with email and password, returning JWT access and refresh tokens."""
    return AuthService.authenticate_user(db, login_data)


@router.post("/refresh", response_model=Token)
def refresh_token(token_req: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Rotate refresh token and issue a fresh access token."""
    return AuthService.refresh_access_token(db, token_req.refresh_token)


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(credentials=Depends(security_scheme)):
    """Revoke the current authentication token."""
    if credentials:
        AuthService.logout(credentials.credentials)
    return {"message": "Successfully logged out."}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Retrieve details of the currently authenticated user."""
    return current_user

