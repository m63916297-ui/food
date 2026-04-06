from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class AddressCreate(BaseModel):
    street: str = Field(min_length=1, max_length=300)
    city: str = Field(min_length=1, max_length=100)
    state: str = Field(min_length=1, max_length=100)
    zip_code: str = Field(min_length=1, max_length=20)
    latitude: float | None = None
    longitude: float | None = None
    is_default: bool = False
    label: str | None = Field(default=None, max_length=50)


class AddressUpdate(BaseModel):
    street: str | None = Field(default=None, min_length=1, max_length=300)
    city: str | None = Field(default=None, min_length=1, max_length=100)
    state: str | None = Field(default=None, min_length=1, max_length=100)
    zip_code: str | None = Field(default=None, min_length=1, max_length=20)
    latitude: float | None = None
    longitude: float | None = None
    is_default: bool | None = None
    label: str | None = Field(default=None, max_length=50)


class AddressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    user_id: str
    street: str
    city: str
    state: str
    zip_code: str
    latitude: float | None = None
    longitude: float | None = None
    is_default: bool
    label: str | None = None
    created_at: datetime
