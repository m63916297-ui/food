from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps import get_db, get_current_user
from app.schemas.payment import PaymentResponse, PaymentCreate
from app.services.payment_service import PaymentService
from app.models.user import User
from app.core.exceptions import require_admin_or_restaurant

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/", response_model=PaymentResponse, status_code=201)
async def create_payment(
    data: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = PaymentService(db)
    payment = await service.process_payment(UUID(data.order_id))
    return payment


@router.get("/order/{order_id}", response_model=PaymentResponse)
async def get_payment_by_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = PaymentService(db)
    return await service.get_payment_by_order(UUID(order_id))


@router.post("/order/{order_id}/refund", response_model=PaymentResponse)
async def refund_payment(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin_or_restaurant)
):
    service = PaymentService(db)
    return await service.refund_payment(UUID(order_id))
