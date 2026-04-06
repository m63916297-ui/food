from uuid import UUID
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.repositories.user_repo import UserRepository
from app.models.user import User, UserRole

security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: AsyncSession = Depends(get_db)
) -> User:
    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            raise UnauthorizedException("Invalid token type")
        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedException("Invalid token payload")
    except Exception:
        raise UnauthorizedException("Could not validate credentials")

    user_repo = UserRepository(db)
    user = await user_repo.get(UUID(user_id))

    if not user:
        raise UnauthorizedException("User not found")

    if not user.is_active:
        raise UnauthorizedException("User account is inactive")

    return user


async def require_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_user.role != UserRole.ADMIN:
        raise ForbiddenException("Admin access required")
    return current_user


async def require_restaurant_owner(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_user.role not in [UserRole.ADMIN, UserRole.RESTAURANT]:
        raise ForbiddenException("Restaurant owner access required")
    return current_user


async def require_rider(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_user.role not in [UserRole.ADMIN, UserRole.RIDER]:
        raise ForbiddenException("Rider access required")
    return current_user


async def require_admin_or_restaurant(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_user.role not in [UserRole.ADMIN, UserRole.RESTAURANT]:
        raise ForbiddenException("Admin or restaurant access required")
    return current_user


CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(require_admin)]
RestaurantUser = Annotated[User, Depends(require_restaurant_owner)]
RiderUser = Annotated[User, Depends(require_rider)]
