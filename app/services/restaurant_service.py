from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.restaurant import Restaurant, Category, MenuItem
from app.schemas.restaurant import RestaurantCreate, RestaurantUpdate, CategoryCreate, CategoryUpdate, MenuItemCreate, MenuItemUpdate
from app.repositories.restaurant_repo import RestaurantRepository, CategoryRepository, MenuItemRepository
from app.core.exceptions import NotFoundException, ForbiddenException


class RestaurantService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.restaurant_repo = RestaurantRepository(session)
        self.category_repo = CategoryRepository(session)
        self.menu_item_repo = MenuItemRepository(session)

    async def create_restaurant(self, owner_id: UUID, data: RestaurantCreate) -> Restaurant:
        restaurant = Restaurant(owner_id=owner_id, **data.model_dump())
        return await self.restaurant_repo.create(restaurant)

    async def get_restaurant(self, restaurant_id: UUID) -> Restaurant:
        restaurant = await self.restaurant_repo.get_with_details(restaurant_id)
        if not restaurant:
            raise NotFoundException("Restaurant not found")
        return restaurant

    async def update_restaurant(self, restaurant_id: UUID, data: RestaurantUpdate, current_user_id: UUID) -> Restaurant:
        restaurant = await self.restaurant_repo.get(restaurant_id)
        if not restaurant:
            raise NotFoundException("Restaurant not found")
        if str(restaurant.owner_id) != str(current_user_id):
            raise ForbiddenException("You can only update your own restaurant")

        for key, value in data.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(restaurant, key, value)

        return await self.restaurant_repo.update(restaurant)

    async def list_restaurants(self, page: int, per_page: int, cuisine_type: str | None = None) -> tuple[list[Restaurant], int]:
        skip = (page - 1) * per_page
        restaurants = await self.restaurant_repo.get_active_restaurants(skip, per_page, cuisine_type)
        total = await self.restaurant_repo.count_active(cuisine_type)
        return restaurants, total

    async def delete_restaurant(self, restaurant_id: UUID, current_user_id: UUID) -> None:
        restaurant = await self.restaurant_repo.get(restaurant_id)
        if not restaurant:
            raise NotFoundException("Restaurant not found")
        if str(restaurant.owner_id) != str(current_user_id):
            raise ForbiddenException("You can only delete your own restaurant")
        restaurant.is_active = False
        await self.restaurant_repo.update(restaurant)

    async def create_category(self, restaurant_id: UUID, data: CategoryCreate, current_user_id: UUID) -> Category:
        restaurant = await self.restaurant_repo.get(restaurant_id)
        if not restaurant:
            raise NotFoundException("Restaurant not found")
        if str(restaurant.owner_id) != str(current_user_id):
            raise ForbiddenException("You can only add categories to your own restaurant")

        category = Category(restaurant_id=restaurant_id, **data.model_dump())
        return await self.category_repo.create(category)

    async def update_category(self, category_id: UUID, data: CategoryUpdate, current_user_id: UUID) -> Category:
        category = await self.category_repo.get(category_id)
        if not category:
            raise NotFoundException("Category not found")

        restaurant = await self.restaurant_repo.get(category.restaurant_id)
        if str(restaurant.owner_id) != str(current_user_id):
            raise ForbiddenException("You can only update categories of your own restaurant")

        for key, value in data.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(category, key, value)

        return await self.category_repo.update(category)

    async def delete_category(self, category_id: UUID, current_user_id: UUID) -> None:
        category = await self.category_repo.get(category_id)
        if not category:
            raise NotFoundException("Category not found")

        restaurant = await self.restaurant_repo.get(category.restaurant_id)
        if str(restaurant.owner_id) != str(current_user_id):
            raise ForbiddenException("You can only delete categories of your own restaurant")

        category.is_active = False
        await self.category_repo.update(category)

    async def create_menu_item(self, restaurant_id: UUID, data: MenuItemCreate, current_user_id: UUID) -> MenuItem:
        restaurant = await self.restaurant_repo.get(restaurant_id)
        if not restaurant:
            raise NotFoundException("Restaurant not found")
        if str(restaurant.owner_id) != str(current_user_id):
            raise ForbiddenException("You can only add items to your own restaurant")

        category = await self.category_repo.get(UUID(data.category_id))
        if not category or str(category.restaurant_id) != str(restaurant_id):
            raise NotFoundException("Category not found in this restaurant")

        menu_item = MenuItem(restaurant_id=restaurant_id, **data.model_dump())
        return await self.menu_item_repo.create(menu_item)

    async def update_menu_item(self, item_id: UUID, data: MenuItemUpdate, current_user_id: UUID) -> MenuItem:
        menu_item = await self.menu_item_repo.get(item_id)
        if not menu_item:
            raise NotFoundException("Menu item not found")

        restaurant = await self.restaurant_repo.get(menu_item.restaurant_id)
        if str(restaurant.owner_id) != str(current_user_id):
            raise ForbiddenException("You can only update items of your own restaurant")

        for key, value in data.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(menu_item, key, value)

        return await self.menu_item_repo.update(menu_item)

    async def delete_menu_item(self, item_id: UUID, current_user_id: UUID) -> None:
        menu_item = await self.menu_item_repo.get(item_id)
        if not menu_item:
            raise NotFoundException("Menu item not found")

        restaurant = await self.restaurant_repo.get(menu_item.restaurant_id)
        if str(restaurant.owner_id) != str(current_user_id):
            raise ForbiddenException("You can only delete items of your own restaurant")

        await self.menu_item_repo.delete(menu_item)

    async def get_menu(self, restaurant_id: UUID) -> list[Category]:
        return await self.category_repo.get_by_restaurant(restaurant_id)
