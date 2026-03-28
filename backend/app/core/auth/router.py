"""Authentication API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.dependencies import get_current_user
from app.core.auth.models import User
from app.core.auth.schemas import TokenResponse, UserCreate, UserLogin, UserResponse
from app.core.auth.service import authenticate_user, create_access_token, register_user
from app.database import get_db

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    """Register a new user account."""
    return await register_user(db, data)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """Authenticate and receive a JWT access token."""
    user = await authenticate_user(db, data.email, data.password)
    return create_access_token(user)


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)) -> User:
    """Get the current authenticated user's profile."""
    return user
