"""
Authentication endpoints
"""
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from app.core.config import settings
from app.core.database import get_db
from app.core.redis import get_redis
from app.models.user import User
from app.schemas.user import AuthRequest, AuthResponse, MagicLinkRequest, MagicLinkResponse
from app.services.auth_service import AuthService

router = APIRouter()
security = HTTPBearer()


async def get_current_user(
    token: str = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token.credentials, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_email(email)
    if user is None:
        raise credentials_exception
    
    return user


@router.post("/magic-link", response_model=MagicLinkResponse)
async def send_magic_link(
    request: MagicLinkRequest,
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis)
):
    """Send magic link for passwordless authentication"""
    auth_service = AuthService(db)
    
    # Generate magic link token
    token = secrets.token_urlsafe(32)
    expires_in = 300  # 5 minutes
    
    # Store token in Redis with expiration
    await redis.setex(
        f"magic_link:{token}",
        expires_in,
        request.email
    )
    
    # TODO: Send email with magic link
    # For now, just return the token for testing
    magic_link = f"http://localhost:3000/auth/verify?token={token}"
    
    return MagicLinkResponse(
        message=f"Magic link sent to {request.email}. Link: {magic_link}",
        expires_in=expires_in
    )


@router.post("/verify", response_model=AuthResponse)
async def verify_magic_link(
    token: str,
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis)
):
    """Verify magic link token and authenticate user"""
    # Check if token exists in Redis
    email = await redis.get(f"magic_link:{token}")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired magic link"
        )
    
    # Remove token from Redis (one-time use)
    await redis.delete(f"magic_link:{token}")
    
    # Get or create user
    auth_service = AuthService(db)
    user = await auth_service.get_or_create_user(email)
    
    # Generate JWT token
    access_token = auth_service.create_access_token(user.email)
    
    return AuthResponse(
        message="Authentication successful",
        token=access_token
    )


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "auth_provider": current_user.auth_provider,
        "is_verified": current_user.is_verified,
        "auto_delete_enabled": current_user.auto_delete_enabled,
        "retention_hours": current_user.retention_hours,
        "created_at": current_user.created_at
    }


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    redis = Depends(get_redis)
):
    """Logout user (invalidate token)"""
    # In a real implementation, you would add the token to a blacklist
    # For now, just return success
    return {"message": "Logged out successfully"}
