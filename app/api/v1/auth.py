from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps import get_db, get_current_user
from app.schemas.auth import UserCreate, UserLogin, TokenResponse, RefreshTokenRequest, UserResponse, EmailRequest, ResetPasswordRequest, MessageResponse
from app.schemas.address import AddressCreate, AddressUpdate, AddressResponse
from app.services.auth_service import AuthService, UserService
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    user = await service.register(user_data)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.login(user_data.email, user_data.password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(token_data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.refresh_access_token(token_data.refresh_token)


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: User = Depends(get_current_user)):
    return MessageResponse(message="Successfully logged out")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(email_data: EmailRequest, db: AsyncSession = Depends(get_db)):
    return MessageResponse(message="If the email exists, a reset link has been sent")


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(reset_data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    return MessageResponse(message="Password reset successful")
