from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps import get_db, get_current_user
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse, PaginatedResponse
from app.services.review_service import ReviewService
from app.models.user import User

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("/", response_model=ReviewResponse, status_code=201)
async def create_review(
    data: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ReviewService(db)
    return await service.create_review(current_user.id, data)


@router.get("/restaurant/{restaurant_id}", response_model=PaginatedResponse[ReviewResponse])
async def get_restaurant_reviews(
    restaurant_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    service = ReviewService(db)
    reviews, total = await service.get_reviews_by_restaurant(UUID(restaurant_id), page, per_page)
    return PaginatedResponse(
        items=reviews,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=(total + per_page - 1) // per_page
    )


@router.patch("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: str,
    data: ReviewUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ReviewService(db)
    return await service.update_review(UUID(review_id), data, current_user.id)
