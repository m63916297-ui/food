from sqlalchemy import Column, String, Text, Float, Boolean, Time, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Restaurant(BaseModel):
    __tablename__ = "restaurants"

    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    cuisine_type = Column(String(100), nullable=False, index=True)
    address = Column(String(300), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(255), nullable=False)
    logo_url = Column(String(500), nullable=True)
    cover_image_url = Column(String(500), nullable=True)
    opening_time = Column(Time, nullable=False)
    closing_time = Column(Time, nullable=False)
    min_order_amount = Column(Numeric(10, 2), default=0.00)
    delivery_fee = Column(Numeric(10, 2), default=0.00)
    delivery_radius_km = Column(Float, default=5.0)
    rating_avg = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)

    owner = relationship("User", back_populates="restaurants")
    categories = relationship("Category", back_populates="restaurant", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="restaurant")
    reviews = relationship("Review", back_populates="restaurant")


class Category(BaseModel):
    __tablename__ = "categories"

    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    sort_order = Column(String(10), default="0")
    image_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)

    restaurant = relationship("Restaurant", back_populates="categories")
    items = relationship("MenuItem", back_populates="category", cascade="all, delete-orphan")


class MenuItem(BaseModel):
    __tablename__ = "menu_items"

    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    image_url = Column(String(500), nullable=True)
    is_available = Column(Boolean, default=True)
    preparation_time_min = Column(String(10), default="15")
    calories = Column(String(10), nullable=True)
    is_vegan = Column(Boolean, default=False)
    is_gluten_free = Column(Boolean, default=False)

    restaurant = relationship("Restaurant")
    category = relationship("Category", back_populates="items")
    order_items = relationship("OrderItem", back_populates="menu_item")
