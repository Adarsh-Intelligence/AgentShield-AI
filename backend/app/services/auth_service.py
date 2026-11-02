from __future__ import annotations

from typing import Optional
from sqlalchemy.orm import Session
from backend.app.core.exceptions import (
    BadRequestException,
    ConflictException,
    UnauthorizedException,
)
from backend.app.core.security import (
    create_jwt_token,
    decode_jwt_token,
    hash_password,
    revoke_token,
    verify_password,
)
from backend.app.models.user import User
from backend.app.schemas.auth import Token, UserCreate, UserLogin


class AuthService:
    @staticmethod
    def register_user(db: Session, user_in: UserCreate) -> User:
        existing = db.query(User).filter(User.email == user_in.email).first()
        if existing:
            raise ConflictException(f"User with email '{user_in.email}' already exists.")

        hashed_pw = hash_password(user_in.password)
        user = User(
            email=user_in.email,
            hashed_password=hashed_pw,
            full_name=user_in.full_name,
            role=user_in.role or "developer",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def authenticate_user(db: Session, login_data: UserLogin) -> Token:
        user = db.query(User).filter(User.email == login_data.email).first()
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password.")

        if not user.is_active:
            raise UnauthorizedException("User account is inactive.")

        token_payload = {"sub": user.id, "email": user.email, "role": user.role}
        access_token = create_jwt_token(token_payload, token_type="access")
        refresh_token = create_jwt_token(token_payload, token_type="refresh")

        from backend.app.config import settings
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> Token:
        payload = decode_jwt_token(refresh_token, expected_type="refresh")
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise UnauthorizedException("User account invalid or inactive.")

        # Rotate refresh token: revoke old one
        revoke_token(refresh_token)

        new_payload = {"sub": user.id, "email": user.email, "role": user.role}
        new_access_token = create_jwt_token(new_payload, token_type="access")
        new_refresh_token = create_jwt_token(new_payload, token_type="refresh")

        from backend.app.config import settings
        return Token(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    @staticmethod
    def logout(token: str) -> None:
        revoke_token(token)

    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

