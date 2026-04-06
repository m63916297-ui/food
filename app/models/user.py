from sqlalchemy import Column, String, Enum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel, UserRole


class User(BaseModel):
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(150), nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.CLIENT)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    avatar_url = Column(String(500), nullable=True)

    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", foreign_keys="Order.user_id")
    delivered_orders = relationship("Order", back_populates="rider", foreign_keys="Order.rider_id")
    reviews = relationship("Review", back_populates="user")
    restaurants = relationship("Restaurant", back_populates="owner")
