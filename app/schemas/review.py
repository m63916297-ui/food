from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class ReviewCreate(BaseModel):
    order_id: str
    restaurant_id: str
    rating: int = Field(ge=1, le=5)
    comment: str | None = None


class ReviewUpdate(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = None


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    user_id: str
    user_name: str | None = None
    order_id: str
    restaurant_id: str
    rating: int
    comment: str | None = None
    created_at: datetime
