import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, DateTime, String, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserRole(str, PyEnum):
    ADMIN = "admin"
    RESTAURANT = "restaurant"
    RIDER = "rider"
    CLIENT = "client"


class BaseModel(Base):
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
