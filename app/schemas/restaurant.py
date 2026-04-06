from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, time
from typing import Optional


class RestaurantCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    cuisine_type: str = Field(min_length=1, max_length=100)
    address: str = Field(min_length=1, max_length=300)
    latitude: float
    longitude: float
    phone: str = Field(min_length=1, max_length=20)
    email: str = Field(min_length=1, max_length=255)
    logo_url: str | None = None
    cover_image_url: str | None = None
    opening_time: time
    closing_time: time
    min_order_amount: float = 0.0
    delivery_fee: float = 0.0
    delivery_radius_km: float = 5.0


class RestaurantUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    cuisine_type: str | None = Field(default=None, min_length=1, max_length=100)
    address: str | None = Field(default=None, min_length=1, max_length=300)
    latitude: float | None = None
    longitude: float | None = None
    phone: str | None = Field(default=None, min_length=1, max_length=20)
    email: str | None = Field(default=None, min_length=1, max_length=255)
    logo_url: str | None = None
    cover_image_url: str | None = None
    opening_time: time | None = None
    closing_time: time | None = None
    min_order_amount: float | None = None
    delivery_fee: float | None = None
    delivery_radius_km: float | None = None
    is_active: bool | None = None


class RestaurantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    owner_id: str
    name: str
    description: str | None = None
    cuisine_type: str
    address: str
    latitude: float
    longitude: float
    phone: str
    email: str
    logo_url: str | None = None
    cover_image_url: str | None = None
    opening_time: time
    closing_time: time
    min_order_amount: float
    delivery_fee: float
    delivery_radius_km: float
    rating_avg: float
    is_active: bool
    created_at: datetime


class RestaurantListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    cuisine_type: str
    address: str
    logo_url: str | None = None
    rating_avg: float
    delivery_fee: float
    is_active: bool


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    sort_order: str = "0"
    image_url: str | None = None


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    sort_order: str | None = None
    image_url: str | None = None
    is_active: bool | None = None


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    restaurant_id: str
    name: str
    description: str | None = None
    sort_order: str
    image_url: str | None = None
    is_active: bool
    created_at: datetime


class MenuItemCreate(BaseModel):
    category_id: str
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    price: float = Field(gt=0)
    image_url: str | None = None
    is_available: bool = True
    preparation_time_min: str = "15"
    calories: str | None = None
    is_vegan: bool = False
    is_gluten_free: bool = False


class MenuItemUpdate(BaseModel):
    category_id: str | None = None
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    price: float | None = Field(default=None, gt=0)
    image_url: str | None = None
    is_available: bool | None = None
    preparation_time_min: str | None = None
    calories: str | None = None
    is_vegan: bool | None = None
    is_gluten_free: bool | None = None


class MenuItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    restaurant_id: str
    category_id: str
    name: str
    description: str | None = None
    price: float
    image_url: str | None = None
    is_available: bool
    preparation_time_min: str
    calories: str | None = None
    is_vegan: bool
    is_gluten_free: bool
    created_at: datetime


class CategoryWithItemsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    description: str | None = None
    sort_order: str
    items: list[MenuItemResponse]
