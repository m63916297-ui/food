from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.payment import Payment, PaymentStatus
from app.schemas.payment import PaymentCreate, PaymentMethod
from app.repositories.payment_repo import PaymentRepository
from app.repositories.order_repo import OrderRepository
from app.core.exceptions import NotFoundException, ValidationException
from app.core.config import settings


class PaymentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.payment_repo = PaymentRepository(session)
        self.order_repo = OrderRepository(session)

    async def get_payment_by_order(self, order_id: UUID) -> Payment:
        payment = await self.payment_repo.get_by_order(order_id)
        if not payment:
            raise NotFoundException("Payment not found")
        return payment

    async def process_payment(self, order_id: UUID) -> Payment:
        order = await self.order_repo.get(order_id)
        if not order:
            raise NotFoundException("Order not found")

        payment = await self.payment_repo.get_by_order(order_id)
        if not payment:
            raise ValidationException("Payment not found for this order")

        if payment.status == PaymentStatus.COMPLETED:
            raise ValidationException("Payment already completed")

        if payment.method == PaymentMethod.CARD and settings.STRIPE_SECRET_KEY:
            try:
                import stripe
                stripe.api_key = settings.STRIPE_SECRET_KEY
                intent = stripe.PaymentIntent.create(
                    amount=int(float(payment.amount) * 100),
                    currency="usd",
                    metadata={"order_id": str(order_id)}
                )
                payment = await self.payment_repo.update_status(payment, PaymentStatus.COMPLETED, intent.id)
            except Exception as e:
                payment = await self.payment_repo.update_status(payment, PaymentStatus.FAILED)
                payment.failure_reason = str(e)
                await self.session.flush()
                raise ValidationException(f"Payment failed: {str(e)}")
        else:
            payment = await self.payment_repo.update_status(payment, PaymentStatus.COMPLETED)

        await self.session.commit()
        return payment

    async def refund_payment(self, order_id: UUID) -> Payment:
        order = await self.order_repo.get(order_id)
        if not order:
            raise NotFoundException("Order not found")

        payment = await self.payment_repo.get_by_order(order_id)
        if not payment:
            raise NotFoundException("Payment not found")

        if payment.status != PaymentStatus.COMPLETED:
            raise ValidationException("Can only refund completed payments")

        if settings.STRIPE_SECRET_KEY and payment.stripe_payment_id:
            try:
                import stripe
                stripe.api_key = settings.STRIPE_SECRET_KEY
                stripe.Refund.create(payment_intent=payment.stripe_payment_id)
            except Exception:
                pass

        payment = await self.payment_repo.update_status(payment, PaymentStatus.REFUNDED)
        await self.session.commit()
        return payment
