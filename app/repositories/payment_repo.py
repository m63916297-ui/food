from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.payment import Payment, PaymentStatus
from app.repositories.base import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, session: AsyncSession):
        super().__init__(Payment, session)

    async def get_by_order(self, order_id: UUID) -> Payment | None:
        result = await self.session.execute(
            select(Payment).where(Payment.order_id == order_id)
        )
        return result.scalar_one_or_none()

    async def update_status(self, payment: Payment, status: PaymentStatus, stripe_id: str | None = None) -> Payment:
        payment.status = status
        if stripe_id:
            payment.stripe_payment_id = stripe_id
        return await self.update(payment)
