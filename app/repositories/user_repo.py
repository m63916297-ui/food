from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.address import Address
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_phone(self, phone: str) -> User | None:
        result = await self.session.execute(select(User).where(User.phone == phone))
        return result.scalar_one_or_none()

    async def get_with_pagination(self, skip: int, limit: int):
        result = await self.session.execute(
            select(User).order_by(User.created_at.desc()).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def update_password(self, user: User, hashed_password: str) -> User:
        user.hashed_password = hashed_password
        return await self.update(user)


class AddressRepository(BaseRepository[Address]):
    def __init__(self, session: AsyncSession):
        super().__init__(Address, session)

    async def get_by_user(self, user_id: UUID) -> list[Address]:
        result = await self.session.execute(
            select(Address).where(Address.user_id == user_id).order_by(Address.is_default.desc())
        )
        return list(result.scalars().all())

    async def get_default(self, user_id: UUID) -> Address | None:
        result = await self.session.execute(
            select(Address).where(and_(Address.user_id == user_id, Address.is_default == True))
        )
        return result.scalar_one_or_none()

    async def clear_defaults(self, user_id: UUID) -> None:
        addresses = await self.get_by_user(user_id)
        for addr in addresses:
            if addr.is_default:
                addr.is_default = False
        await self.session.flush()
