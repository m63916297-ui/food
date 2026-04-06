from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps import get_db, get_current_user
from app.schemas.restaurant import (
    RestaurantCreate, RestaurantUpdate, RestaurantResponse, RestaurantListResponse,
    CategoryCreate, CategoryUpdate, CategoryResponse,
    MenuItemCreate, MenuItemUpdate, MenuItemResponse, CategoryWithItemsResponse,
    PaginatedResponse
)
from app.schemas.auth import MessageResponse
from app.services.restaurant_service import RestaurantService
from app.models.user import User

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


@router.get("/", response_model=PaginatedResponse[RestaurantListResponse])
async def list_restaurants(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    cuisine_type: str | None = Query(None),
    db: AsyncSession = Depends(get_db)
):
    service = RestaurantService(db)
    restaurants, total = await service.list_restaurants(page, per_page, cuisine_type)
    return PaginatedResponse(
        items=restaurants,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=(total + per_page - 1) // per_page
    )


@router.get("/{restaurant_id}", response_model=RestaurantResponse)
async def get_restaurant(restaurant_id: str, db: AsyncSession = Depends(get_db)):
    service = RestaurantService(db)
    return await service.get_restaurant(UUID(restaurant_id))


@router.post("/", response_model=RestaurantResponse, status_code=201)
async def create_restaurant(
    data: RestaurantCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = RestaurantService(db)
    return await service.create_restaurant(current_user.id, data)


@router.patch("/{restaurant_id}", response_model=RestaurantResponse)
async def update_restaurant(
    restaurant_id: str,
    data: RestaurantUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = RestaurantService(db)
    return await service.update_restaurant(UUID(restaurant_id), data, current_user.id)


@router.delete("/{restaurant_id}", status_code=204)
async def delete_restaurant(
    restaurant_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = RestaurantService(db)
    await service.delete_restaurant(UUID(restaurant_id), current_user.id)


@router.get("/{restaurant_id}/menu", response_model=list[CategoryWithItemsResponse])
async def get_menu(restaurant_id: str, db: AsyncSession = Depends(get_db)):
    service = RestaurantService(db)
    categories = await service.get_menu(UUID(restaurant_id))
    return categories


@router.post("/{restaurant_id}/categories", response_model=CategoryResponse, status_code=201)
async def create_category(
    restaurant_id: str,
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = RestaurantService(db)
    return await service.create_category(UUID(restaurant_id), data, current_user.id)


@router.patch("/{restaurant_id}/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    restaurant_id: str,
    category_id: str,
    data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = RestaurantService(db)
    return await service.update_category(UUID(category_id), data, current_user.id)


@router.delete("/{restaurant_id}/categories/{category_id}", status_code=204)
async def delete_category(
    restaurant_id: str,
    category_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = RestaurantService(db)
    await service.delete_category(UUID(category_id), current_user.id)


@router.post("/{restaurant_id}/items", response_model=MenuItemResponse, status_code=201)
async def create_menu_item(
    restaurant_id: str,
    data: MenuItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = RestaurantService(db)
    return await service.create_menu_item(UUID(restaurant_id), data, current_user.id)


@router.patch("/{restaurant_id}/items/{item_id}", response_model=MenuItemResponse)
async def update_menu_item(
    restaurant_id: str,
    item_id: str,
    data: MenuItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = RestaurantService(db)
    return await service.update_menu_item(UUID(item_id), data, current_user.id)


@router.delete("/{restaurant_id}/items/{item_id}", status_code=204)
async def delete_menu_item(
    restaurant_id: str,
    item_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = RestaurantService(db)
    await service.delete_menu_item(UUID(item_id), current_user.id)
