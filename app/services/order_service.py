from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.order import Order, OrderItem, OrderStatus
from app.models.restaurant import MenuItem
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.schemas.order import OrderCreate, OrderStatusUpdate
from app.repositories.order_repo import OrderRepository, OrderItemRepository
from app.repositories.restaurant_repo import MenuItemRepository, RestaurantRepository
from app.repositories.payment_repo import PaymentRepository
from app.repositories.user_repo import AddressRepository
from app.core.exceptions import NotFoundException, ValidationException, ForbiddenException
from app.models.user import UserRole


class OrderService:
    TAX_RATE = Decimal("0.10")

    def __init__(self, session: AsyncSession):
        self.session = session
        self.order_repo = OrderRepository(session)
        self.order_item_repo = OrderItemRepository(session)
        self.menu_item_repo = MenuItemRepository(session)
        self.restaurant_repo = RestaurantRepository(session)
        self.payment_repo = PaymentRepository(session)
        self.address_repo = AddressRepository(session)

    async def create_order(self, user_id: UUID, order_data: OrderCreate) -> Order:
        restaurant = await self.restaurant_repo.get(UUID(order_data.restaurant_id))
        if not restaurant or not restaurant.is_active:
            raise ValidationException("Restaurant not available")

        items_data = []
        subtotal = Decimal("0")

        for item in order_data.items:
            menu_item = await self.menu_item_repo.get(UUID(item.menu_item_id))
            if not menu_item or not menu_item.is_available:
                raise ValidationException(f"Item {item.menu_item_id} not available")
            if str(menu_item.restaurant_id) != str(order_data.restaurant_id):
                raise ValidationException("All items must be from the same restaurant")

            item_total = Decimal(str(menu_item.price)) * item.quantity
            subtotal += item_total
            items_data.append({
                "menu_item": menu_item,
                "quantity": str(item.quantity),
                "unit_price": float(menu_item.price),
                "special_instructions": item.special_instructions
            })

        if float(restaurant.min_order_amount) > float(subtotal):
            raise ValidationException(f"Minimum order amount is ${restaurant.min_order_amount}")

        tax_amount = subtotal * self.TAX_RATE
        delivery_fee = Decimal(str(restaurant.delivery_fee))
        total_amount = subtotal + tax_amount + delivery_fee

        delivery_address = order_data.delivery_address
        delivery_lat = order_data.delivery_lat
        delivery_lng = order_data.delivery_lng

        if order_data.delivery_address_id:
            address = await self.address_repo.get(UUID(order_data.delivery_address_id))
            if address:
                delivery_address = f"{address.street}, {address.city}, {address.state} {address.zip_code}"
                delivery_lat = address.latitude
                delivery_lng = address.longitude

        order_number = await self.order_repo.get_next_order_number()
        max_prep_time = max(int(item["menu_item"].preparation_time_min or "15") for item in items_data)

        order = Order(
            order_number=order_number,
            user_id=user_id,
            restaurant_id=UUID(order_data.restaurant_id),
            status=OrderStatus.PENDING,
            subtotal=float(subtotal),
            tax_amount=float(tax_amount),
            delivery_fee=float(delivery_fee),
            total_amount=float(total_amount),
            delivery_address=delivery_address or "No address provided",
            delivery_lat=delivery_lat,
            delivery_lng=delivery_lng,
            notes=order_data.notes,
            estimated_delivery=datetime.utcnow() + timedelta(minutes=max_prep_time + 30)
        )
        order = await self.order_repo.create(order)

        for item_data in items_data:
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=item_data["menu_item"].id,
                quantity=item_data["quantity"],
                unit_price=item_data["unit_price"],
                special_instructions=item_data["special_instructions"]
            )
            await self.order_item_repo.create(order_item)

        payment = Payment(
            order_id=order.id,
            amount=float(total_amount),
            method=PaymentMethod(order_data.payment_method),
            status=PaymentStatus.PENDING
        )
        await self.payment_repo.create(payment)

        await self.session.commit()
        return await self.order_repo.get_with_details(order.id)

    async def get_order(self, order_id: UUID, current_user_id: UUID, user_role: UserRole) -> Order:
        order = await self.order_repo.get_with_details(order_id)
        if not order:
            raise NotFoundException("Order not found")

        if user_role != UserRole.ADMIN:
            if str(order.user_id) != str(current_user_id):
                if str(order.restaurant.owner_id) != str(current_user_id):
                    if str(order.rider_id) != str(current_user_id):
                        raise ForbiddenException("You don't have access to this order")

        return order

    async def list_orders(self, current_user_id: UUID, user_role: UserRole, page: int, per_page: int) -> tuple[list[Order], int]:
        skip = (page - 1) * per_page

        if user_role == UserRole.ADMIN:
            orders = await self.order_repo.get_all(skip, per_page)
            total = await self.order_repo.count()
        elif user_role == UserRole.RESTAURANT:
            restaurants = await self.restaurant_repo.get_by_owner(current_user_id)
            restaurant_ids = [r.id for r in restaurants]
            orders = []
            total = 0
            for rid in restaurant_ids:
                ords = await self.order_repo.get_by_restaurant(rid, skip, per_page)
                orders.extend(ords)
                total += await self.order_repo.count_by_restaurant(rid)
        elif user_role == UserRole.RIDER:
            orders = await self.order_repo.get_by_rider(current_user_id, skip, per_page)
            total = len(orders)
        else:
            orders = await self.order_repo.get_by_user(current_user_id, skip, per_page)
            total = await self.order_repo.count_by_user(current_user_id)

        return orders, total

    async def update_status(self, order_id: UUID, status_data: OrderStatusUpdate, current_user_id: UUID, user_role: UserRole) -> Order:
        order = await self.order_repo.get_with_details(order_id)
        if not order:
            raise NotFoundException("Order not found")

        new_status = OrderStatus(status_data.status.value)

        if user_role == UserRole.CLIENT:
            if new_status not in [OrderStatus.CANCELLED]:
                raise ForbiddenException("Clients can only cancel orders")
            if order.status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
                raise ValidationException("Order cannot be cancelled at this stage")

        elif user_role == UserRole.RESTAURANT:
            if str(order.restaurant.owner_id) != str(current_user_id):
                raise ForbiddenException("You can only update your restaurant's orders")
            allowed_transitions = {
                OrderStatus.PENDING: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
                OrderStatus.CONFIRMED: [OrderStatus.PREPARING, OrderStatus.CANCELLED],
                OrderStatus.PREPARING: [OrderStatus.READY_FOR_PICKUP],
            }
            if order.status in allowed_transitions and new_status not in allowed_transitions[order.status]:
                raise ValidationException(f"Cannot transition from {order.status} to {new_status}")

        elif user_role == UserRole.RIDER:
            if str(order.rider_id) != str(current_user_id):
                raise ForbiddenException("This order is not assigned to you")
            allowed_transitions = {
                OrderStatus.READY_FOR_PICKUP: [OrderStatus.IN_TRANSIT],
                OrderStatus.IN_TRANSIT: [OrderStatus.DELIVERED],
            }
            if order.status in allowed_transitions and new_status not in allowed_transitions[order.status]:
                raise ValidationException(f"Cannot transition from {order.status} to {new_status}")

        return await self.order_repo.update_status(order, new_status)

    async def assign_rider(self, order_id: UUID, rider_id: UUID, current_user_id: UUID) -> Order:
        order = await self.order_repo.get_with_details(order_id)
        if not order:
            raise NotFoundException("Order not found")

        if order.status not in [OrderStatus.CONFIRMED, OrderStatus.PREPARING]:
            raise ValidationException("Order must be confirmed or preparing to assign a rider")

        return await self.order_repo.assign_rider(order, rider_id)

    async def get_tracking(self, order_id: UUID, current_user_id: UUID) -> dict:
        order = await self.order_repo.get_with_details(order_id)
        if not order:
            raise NotFoundException("Order not found")

        if str(order.user_id) != str(current_user_id):
            raise ForbiddenException("You can only track your own orders")

        return {
            "order_id": str(order.id),
            "order_number": order.order_number,
            "status": order.status.value,
            "estimated_delivery": order.estimated_delivery,
            "rider_id": str(order.rider_id) if order.rider_id else None,
            "rider_name": order.rider.full_name if order.rider else None,
            "rider_phone": order.rider.phone if order.rider else None,
            "current_lat": None,
            "current_lng": None
        }
