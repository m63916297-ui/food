from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps import get_db, get_current_user, require_admin
from app.schemas.auth import UserResponse
from app.schemas.address import AddressCreate, AddressUpdate, AddressResponse
from app.schemas.auth import PaginatedResponse
from app.services.auth_service import UserService
from app.models.user import User, UserRole

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=PaginatedResponse[UserResponse])
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin)
):
    service = UserService(db)
    users, total = await service.list_users((page - 1) * per_page, per_page)
    return PaginatedResponse(
        items=users,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=(total + per_page - 1) // per_page
    )


@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/me/addresses", response_model=list[AddressResponse])
async def get_addresses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = UserService(db)
    return await service.get_addresses(current_user.id)


@router.post("/me/addresses", response_model=AddressResponse, status_code=201)
async def create_address(
    address_data: AddressCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = UserService(db)
    return await service.create_address(current_user.id, address_data)


@router.patch("/me/addresses/{address_id}", response_model=AddressResponse)
async def update_address(
    address_id: str,
    address_data: AddressUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = UserService(db)
    return await service.update_address(current_user.id, UUID(address_id), address_data)


@router.delete("/me/addresses/{address_id}", status_code=204)
async def delete_address(
    address_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = UserService(db)
    await service.delete_address(current_user.id, UUID(address_id))


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = UserService(db)
    return await service.get_user(UUID(user_id))


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserResponse,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = UserService(db)
    from app.schemas.auth import UserUpdate
    update_data = UserUpdate(
        full_name=user_data.full_name,
        phone=user_data.phone,
        avatar_url=user_data.avatar_url
    )
    return await service.update_user(UUID(user_id), update_data, current_user.id)


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin)
):
    service = UserService(db)
    await service.delete_user(UUID(user_id))
