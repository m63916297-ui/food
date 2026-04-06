from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY_FOR_PICKUP = "ready_for_pickup"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class OrderItemCreate(BaseModel):
    menu_item_id: str
    quantity: int = Field(ge=1, le=50)
    special_instructions: str | None = None


class OrderCreate(BaseModel):
    restaurant_id: str
    items: list[OrderItemCreate] = Field(min_length=1, max_length=50)
    delivery_address_id: str | None = None
    delivery_address: str | None = None
    delivery_lat: float | None = None
    delivery_lng: float | None = None
    notes: str | None = None
    payment_method: str = "card"


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    menu_item_id: str
    menu_item_name: str | None = None
    quantity: str
    unit_price: float
    special_instructions: str | None = None


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    order_number: str
    user_id: str
    restaurant_id: str
    restaurant_name: str | None = None
    rider_id: str | None = None
    status: str
    subtotal: float
    tax_amount: float
    delivery_fee: float
    total_amount: float
    delivery_address: str
    delivery_lat: float | None = None
    delivery_lng: float | None = None
    notes: str | None = None
    estimated_delivery: datetime | None = None
    delivered_at: datetime | None = None
    created_at: datetime
    items: list[OrderItemResponse] = []


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderCancelRequest(BaseModel):
    reason: str | None = None


class TrackingResponse(BaseModel):
    order_id: str
    order_number: str
    status: str
    estimated_delivery: datetime | None = None
    rider_id: str | None = None
    rider_name: str | None = None
    rider_phone: str | None = None
    current_lat: float | None = None
    current_lng: float | None = None
