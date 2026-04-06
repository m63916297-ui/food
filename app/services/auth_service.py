from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.models.address import Address
from app.schemas.auth import UserCreate, UserUpdate, TokenResponse
from app.schemas.address import AddressCreate, AddressUpdate
from app.repositories.user_repo import UserRepository, AddressRepository
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.exceptions import NotFoundException, ConflictException, UnauthorizedException, ForbiddenException
from app.core.config import settings
from datetime import timedelta


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def register(self, user_data: UserCreate) -> User:
        if await self.user_repo.get_by_email(user_data.email):
            raise ConflictException("Email already registered")
        if await self.user_repo.get_by_phone(user_data.phone):
            raise ConflictException("Phone already registered")

        user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            phone=user_data.phone,
            hashed_password=get_password_hash(user_data.password),
            role=UserRole(user_data.role)
        )
        return await self.user_repo.create(user)

    async def login(self, email: str, password: str) -> TokenResponse:
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password")
        if not user.is_active:
            raise ForbiddenException("User account is inactive")

        access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise UnauthorizedException("Invalid token type")
        except Exception:
            raise UnauthorizedException("Invalid refresh token")

        user = await self.user_repo.get(UUID(payload["sub"]))
        if not user or not user.is_active:
            raise UnauthorizedException("User not found or inactive")

        access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
        new_refresh_token = create_refresh_token(data={"sub": str(user.id)})

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    async def get_current_user(self, user_id: UUID) -> User:
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundException("User not found")
        return user


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.address_repo = AddressRepository(session)

    async def get_user(self, user_id: UUID) -> User:
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundException("User not found")
        return user

    async def update_user(self, user_id: UUID, user_data: UserUpdate, current_user_id: UUID) -> User:
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundException("User not found")
        if str(user.id) != str(current_user_id):
            raise ForbiddenException("Cannot update another user's profile")

        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        if user_data.phone is not None:
            existing = await self.user_repo.get_by_phone(user_data.phone)
            if existing and str(existing.id) != str(user_id):
                raise ConflictException("Phone already in use")
            user.phone = user_data.phone
        if user_data.avatar_url is not None:
            user.avatar_url = user_data.avatar_url

        return await self.user_repo.update(user)

    async def list_users(self, skip: int, limit: int) -> tuple[list[User], int]:
        users = await self.user_repo.get_with_pagination(skip, limit)
        total = await self.user_repo.count()
        return users, total

    async def delete_user(self, user_id: UUID) -> None:
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundException("User not found")
        user.is_active = False
        await self.user_repo.update(user)

    async def get_addresses(self, user_id: UUID) -> list[Address]:
        return await self.address_repo.get_by_user(user_id)

    async def create_address(self, user_id: UUID, address_data: AddressCreate) -> Address:
        if address_data.is_default:
            await self.address_repo.clear_defaults(user_id)

        address = Address(
            user_id=user_id,
            **address_data.model_dump()
        )
        return await self.address_repo.create(address)

    async def update_address(self, user_id: UUID, address_id: UUID, address_data: AddressUpdate) -> Address:
        address = await self.address_repo.get(address_id)
        if not address or str(address.user_id) != str(user_id):
            raise NotFoundException("Address not found")

        if address_data.is_default:
            await self.address_repo.clear_defaults(user_id)

        for key, value in address_data.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(address, key, value)

        return await self.address_repo.update(address)

    async def delete_address(self, user_id: UUID, address_id: UUID) -> None:
        address = await self.address_repo.get(address_id)
        if not address or str(address.user_id) != str(user_id):
            raise NotFoundException("Address not found")
        await self.address_repo.delete(address)
