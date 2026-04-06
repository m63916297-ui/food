from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.review import Review
from app.models.order import Order, OrderStatus
from app.schemas.review import ReviewCreate, ReviewUpdate
from app.repositories.restaurant_repo import RestaurantRepository
from app.repositories.order_repo import OrderRepository
from app.core.exceptions import NotFoundException, ValidationException, ForbiddenException


class ReviewService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.restaurant_repo = RestaurantRepository(session)
        self.order_repo = OrderRepository(session)

    async def create_review(self, user_id: UUID, review_data: ReviewCreate) -> Review:
        order = await self.order_repo.get_with_details(UUID(review_data.order_id))
        if not order:
            raise NotFoundException("Order not found")

        if str(order.user_id) != str(user_id):
            raise ForbiddenException("You can only review your own orders")

        if order.status != OrderStatus.DELIVERED:
            raise ValidationException("Can only review delivered orders")

        if order.review:
            raise ValidationException("Order already reviewed")

        review = Review(
            user_id=user_id,
            order_id=UUID(review_data.order_id),
            restaurant_id=UUID(review_data.restaurant_id),
            rating=review_data.rating,
            comment=review_data.comment
        )
        self.session.add(review)

        result = await self.session.execute(
            select(func.avg(Review.rating))
            .where(Review.restaurant_id == UUID(review_data.restaurant_id))
        )
        avg_rating = result.scalar_one() or review_data.rating
        restaurant = await self.restaurant_repo.get(UUID(review_data.restaurant_id))
        if restaurant:
            restaurant.rating_avg = float(avg_rating)

        await self.session.flush()
        await self.session.refresh(review)
        return review

    async def get_reviews_by_restaurant(self, restaurant_id: UUID, page: int, per_page: int) -> tuple[list[Review], int]:
        skip = (page - 1) * per_page
        result = await self.session.execute(
            select(Review)
            .where(Review.restaurant_id == restaurant_id)
            .order_by(Review.created_at.desc())
            .offset(skip)
            .limit(per_page)
        )
        reviews = list(result.scalars().all())

        count_result = await self.session.execute(
            select(func.count(Review.id)).where(Review.restaurant_id == restaurant_id)
        )
        total = count_result.scalar_one()

        return reviews, total

    async def update_review(self, review_id: UUID, review_data: ReviewUpdate, user_id: UUID) -> Review:
        result = await self.session.execute(select(Review).where(Review.id == review_id))
        review = result.scalar_one_or_none()

        if not review:
            raise NotFoundException("Review not found")

        if str(review.user_id) != str(user_id):
            raise ForbiddenException("You can only update your own reviews")

        if review_data.rating is not None:
            review.rating = review_data.rating
        if review_data.comment is not None:
            review.comment = review_data.comment

        await self.session.flush()
        await self.session.refresh(review)
        return review
