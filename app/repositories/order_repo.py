from uuid import UUID
from datetime import datetime
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.order import Order, OrderItem, OrderStatus
from app.repositories.base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    def __init__(self, session: AsyncSession):
        super().__init__(Order, session)

    async def get_by_user(self, user_id: UUID, skip: int, limit: int) -> list[Order]:
        result = await self.session.execute(
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_restaurant(self, restaurant_id: UUID, skip: int, limit: int) -> list[Order]:
        result = await self.session.execute(
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.restaurant_id == restaurant_id)
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_rider(self, rider_id: UUID, skip: int, limit: int) -> list[Order]:
        result = await self.session.execute(
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.rider_id == rider_id)
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_with_details(self, order_id: UUID) -> Order | None:
        result = await self.session.execute(
            select(Order)
            .options(
                selectinload(Order.items).selectinload(OrderItem.menu_item),
                selectinload(Order.restaurant),
                selectinload(Order.user),
                selectinload(Order.rider)
            )
            .where(Order.id == order_id)
        )
        return result.scalar_one_or_none()

    async def count_by_user(self, user_id: UUID) -> int:
        result = await self.session.execute(
            select(func.count(Order.id)).where(Order.user_id == user_id)
        )
        return result.scalar_one()

    async def count_by_restaurant(self, restaurant_id: UUID) -> int:
        result = await self.session.execute(
            select(func.count(Order.id)).where(Order.restaurant_id == restaurant_id)
        )
        return result.scalar_one()

    async def get_next_order_number(self) -> str:
        today = datetime.utcnow().strftime("%Y%m%d")
        result = await self.session.execute(
            select(func.count(Order.id)).where(
                Order.order_number.like(f"ORD-{today}-%")
            )
        )
        count = result.scalar_one()
        return f"ORD-{today}-{str(count + 1).zfill(4)}"

    async def update_status(self, order: Order, status: OrderStatus) -> Order:
        order.status = status
        if status == OrderStatus.DELIVERED:
            order.delivered_at = datetime.utcnow()
        return await self.update(order)

    async def assign_rider(self, order: Order, rider_id: UUID) -> Order:
        order.rider_id = rider_id
        return await self.update(order)


class OrderItemRepository(BaseRepository[OrderItem]):
    def __init__(self, session: AsyncSession):
        super().__init__(OrderItem, session)

    async def get_by_order(self, order_id: UUID) -> list[OrderItem]:
        result = await self.session.execute(
            select(OrderItem)
            .options(selectinload(OrderItem.menu_item))
            .where(OrderItem.order_id == order_id)
        )
        return list(result.scalars().all())
