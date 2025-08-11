#!/usr/bin/env python3
"""
Authentication Service for JWT tokens and API keys
Handles user authentication and authorization
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from models.database import User
from models.schemas import UserCreate, UserResponse

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """Authentication and authorization service"""
    
    def __init__(self):
        self.secret_key = "your-super-secret-jwt-key-change-in-production"
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
        
    def get_password_hash(self, password: str) -> str:
        """Hash password"""
        return pwd_context.hash(password)
        
    def generate_api_key(self) -> str:
        """Generate secure API key"""
        return secrets.token_urlsafe(32)
        
    async def create_user(self, user: UserCreate, db: Session) -> UserResponse:
        """Create new user account"""
        # Check if user exists
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise ValueError("User already exists")
            
        # Create new user
        hashed_password = self.get_password_hash(user.password)
        api_key = self.generate_api_key()
        
        db_user = User(
            email=user.email,
            hashed_password=hashed_password,
            api_key=api_key,
            plan=user.plan,
            rate_limit=100 if user.plan == "free" else 1000,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return UserResponse(
            id=db_user.id,
            email=db_user.email,
            plan=db_user.plan,
            is_active=db_user.is_active,
            created_at=db_user.created_at,
            api_key=db_user.api_key
        )
        
    async def verify_api_key(self, api_key: str, db: Session) -> Optional[User]:
        """Verify API key and return user"""
        if not api_key:
            return None
            
        user = db.query(User).filter(
            User.api_key == api_key,
            User.is_active == True
        ).first()
        
        if user:
            # Update last login
            user.last_login = datetime.utcnow()
            db.commit()
            
        return user
        
    async def refresh_api_key(self, user_id: int, db: Session) -> str:
        """Generate new API key for user"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
            
        new_api_key = self.generate_api_key()
        user.api_key = new_api_key
        db.commit()
        
        return new_api_key
        
    async def get_api_usage(self, user_id: int) -> int:
        """Get API usage count for user (today)"""
        # This would typically query the APIUsage table
        # For now, return mock data
        return 42
        
    async def get_usage_stats(self, user_id: int, days_back: int = 30) -> dict:
        """Get usage statistics for user"""
        # Mock usage stats
        return {
            "total_api_calls": 1250,
            "api_calls_today": 42,
            "average_daily_calls": 41.7,
            "peak_day": "2025-01-08",
            "peak_day_calls": 156
        }