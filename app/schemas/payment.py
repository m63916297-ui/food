from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from enum import Enum


class PaymentMethod(str, Enum):
    CARD = "card"
    CASH = "cash"
    WALLET = "wallet"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentCreate(BaseModel):
    order_id: str
    method: PaymentMethod = PaymentMethod.CARD


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    order_id: str
    amount: float
    method: str
    status: str
    stripe_payment_id: str | None = None
    transaction_date: str | None = None
    failure_reason: str | None = None
    created_at: datetime


class PaymentIntentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str
