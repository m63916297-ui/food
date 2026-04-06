from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.restaurant import Restaurant, Category, MenuItem
from app.repositories.base import BaseRepository


class RestaurantRepository(BaseRepository[Restaurant]):
    def __init__(self, session: AsyncSession):
        super().__init__(Restaurant, session)

    async def get_by_owner(self, owner_id: UUID) -> list[Restaurant]:
        result = await self.session.execute(
            select(Restaurant).where(Restaurant.owner_id == owner_id)
        )
        return list(result.scalars().all())

    async def get_active_restaurants(self, skip: int, limit: int, cuisine_type: str | None = None):
        query = select(Restaurant).where(Restaurant.is_active == True)
        if cuisine_type:
            query = query.where(Restaurant.cuisine_type.ilike(f"%{cuisine_type}%"))
        query = query.order_by(Restaurant.rating_avg.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_active(self, cuisine_type: str | None = None) -> int:
        from sqlalchemy import func, select
        query = select(func.count(Restaurant.id)).where(Restaurant.is_active == True)
        if cuisine_type:
            query = query.where(Restaurant.cuisine_type.ilike(f"%{cuisine_type}%"))
        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_with_details(self, restaurant_id: UUID) -> Restaurant | None:
        result = await self.session.execute(
            select(Restaurant)
            .options(selectinload(Restaurant.categories).selectinload(Category.items))
            .where(Restaurant.id == restaurant_id)
        )
        return result.scalar_one_or_none()


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, session: AsyncSession):
        super().__init__(Category, session)

    async def get_by_restaurant(self, restaurant_id: UUID) -> list[Category]:
        result = await self.session.execute(
            select(Category)
            .where(Category.restaurant_id == restaurant_id, Category.is_active == True)
            .order_by(Category.sort_order)
        )
        return list(result.scalars().all())

    async def get_with_items(self, category_id: UUID) -> Category | None:
        result = await self.session.execute(
            select(Category)
            .options(selectinload(Category.items))
            .where(Category.id == category_id)
        )
        return result.scalar_one_or_none()


class MenuItemRepository(BaseRepository[MenuItem]):
    def __init__(self, session: AsyncSession):
        super().__init__(MenuItem, session)

    async def get_by_category(self, category_id: UUID) -> list[MenuItem]:
        result = await self.session.execute(
            select(MenuItem)
            .where(MenuItem.category_id == category_id)
            .order_by(MenuItem.name)
        )
        return list(result.scalars().all())

    async def get_available_items(self, restaurant_id: UUID) -> list[MenuItem]:
        result = await self.session.execute(
            select(MenuItem)
            .where(MenuItem.restaurant_id == restaurant_id, MenuItem.is_available == True)
            .order_by(MenuItem.name)
        )
        return list(result.scalars().all())
