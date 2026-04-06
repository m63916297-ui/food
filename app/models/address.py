from sqlalchemy import Column, String, Float, Boolean, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Address(BaseModel):
    __tablename__ = "addresses"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    street = Column(String(300), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    zip_code = Column(String(20), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    is_default = Column(Boolean, default=False)
    label = Column(String(50), nullable=True)

    user = relationship("User", back_populates="addresses")
