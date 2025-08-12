from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta

from app.database import get_database
from app.models import User, AuditLog
from app.schemas import UserCreate, UserLogin, Token, UserProfile
from app.auth import (
    authenticate_user, 
    create_access_token, 
    get_password_hash,
    get_current_user
)
from app.rate_limiter import limiter

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserProfile, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")  # Prevent spam registrations
async def register_user(
    request: Request,
    user_data: UserCreate,
    db: AsyncSession = Depends(get_database)
):
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(email=user_data.email, password_hash=hashed_password)
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return UserProfile.from_orm(new_user)


@router.post("/token", response_model=Token)
@limiter.limit("5/minute")  # Prevent brute force attacks
async def login_user(
    request: Request,
    user_credentials: UserLogin,
    db: AsyncSession = Depends(get_database)
):
    user = await authenticate_user(user_credentials.email, user_credentials.password, db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token)


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    return UserProfile.from_orm(current_user)
