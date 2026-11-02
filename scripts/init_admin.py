#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from backend.app.core.security import hash_password
from backend.app.database.session import SessionLocal
from backend.app.models.user import User


def create_admin(email: str, password: str, full_name: str = "Admin") -> None:
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"User with email '{email}' already exists.")
            return

        user = User(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
            role="admin",
            is_active=True,
        )
        db.add(user)
        db.commit()
        print(f"Admin user '{email}' created successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed initial admin user")
    parser.add_argument("--email", required=True, help="Admin email address")
    parser.add_argument("--password", required=True, help="Admin password")
    parser.add_argument("--name", default="Admin", help="Admin full name")

    args = parser.parse_args()
    create_admin(args.email, args.password, args.name)

