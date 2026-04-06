from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps import get_db, get_current_user
from app.schemas.order import (
    OrderCreate, OrderResponse, OrderStatusUpdate, OrderCancelRequest,
    TrackingResponse, PaginatedResponse
)
from app.schemas.auth import MessageResponse
from app.services.order_service import OrderService
from app.models.user import User

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("/", response_model=PaginatedResponse[OrderResponse])
async def list_orders(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = OrderService(db)
    orders, total = await service.list_orders(current_user.id, current_user.role, page, per_page)
    return PaginatedResponse(
        items=orders,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=(total + per_page - 1) // per_page
    )


@router.post("/", response_model=OrderResponse, status_code=201)
async def create_order(
    data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = OrderService(db)
    return await service.create_order(current_user.id, data)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = OrderService(db)
    return await service.get_order(UUID(order_id), current_user.id, current_user.role)


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: str,
    data: OrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = OrderService(db)
    return await service.update_status(UUID(order_id), data, current_user.id, current_user.role)


@router.patch("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: str,
    data: OrderCancelRequest | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = OrderService(db)
    from app.schemas.order import OrderStatus
    return await service.update_status(
        UUID(order_id),
        OrderStatusUpdate(status=OrderStatus.CANCELLED),
        current_user.id,
        current_user.role
    )


@router.post("/{order_id}/assign/{rider_id}", response_model=OrderResponse)
async def assign_rider(
    order_id: str,
    rider_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = OrderService(db)
    return await service.assign_rider(UUID(order_id), UUID(rider_id), current_user.id)


@router.get("/{order_id}/tracking", response_model=TrackingResponse)
async def track_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = OrderService(db)
    return await service.get_tracking(UUID(order_id), current_user.id)
