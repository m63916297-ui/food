from sqlalchemy import Column, String, Numeric, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from enum import Enum as PyEnum


class PaymentMethod(str, PyEnum):
    CARD = "card"
    CASH = "cash"
    WALLET = "wallet"


class PaymentStatus(str, PyEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class Payment(BaseModel):
    __tablename__ = "payments"

    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), unique=True, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    method = Column(Enum(PaymentMethod), nullable=False)
    status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    stripe_payment_id = Column(String(255), nullable=True)
    transaction_date = Column(String(30), nullable=True)
    failure_reason = Column(String(500), nullable=True)

    order = relationship("Order", back_populates="payment")
