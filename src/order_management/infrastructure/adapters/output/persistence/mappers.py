"""
Mappers: Domain entities <-> Persistence models.
"""

from decimal import Decimal
from uuid import UUID

from order_management.domain.models import (
    Money,
    Order,
    OrderItem,
    OrderStatus,
)
from .models import OrderItemModel, OrderModel


def _uuid_s(s: str | UUID) -> str:
    """Normalize to string for DB."""
    return str(s) if s is not None else None


def _uuid_u(s: str | UUID) -> UUID:
    """Normalize to UUID for domain."""
    return s if isinstance(s, UUID) else UUID(s) if s else None


def order_item_to_domain(row: OrderItemModel) -> OrderItem:
    """Map OrderItemModel -> OrderItem (domain)."""
    return OrderItem(
        item_id=_uuid_u(row.id),
        product_id=_uuid_u(row.product_id),
        product_name=row.product_name or "",
        quantity=row.quantity,
        unit_price=Money(amount=Decimal(str(row.unit_price)), currency=row.currency),
    )


def order_item_to_model(item: OrderItem, order_id: UUID) -> OrderItemModel:
    """Map OrderItem (domain) -> OrderItemModel."""
    return OrderItemModel(
        id=_uuid_s(item.item_id),
        order_id=_uuid_s(order_id),
        product_id=_uuid_s(item.product_id),
        product_name=item.product_name,
        quantity=item.quantity,
        unit_price=item.unit_price.amount,
        currency=item.unit_price.currency,
    )


def order_to_domain(row: OrderModel) -> Order:
    """Map OrderModel (and its items) -> Order (domain)."""
    items = [order_item_to_domain(i) for i in row.items]
    total = Money(
        amount=Decimal(str(row.total_amount)),
        currency=row.currency,
    )
    order = Order(
        order_id=_uuid_u(row.id),
        customer_id=_uuid_u(row.customer_id),
        items=items,
        status=OrderStatus(row.status),
    )
    # Recompute total from items to satisfy invariants; we don't persist shipping_address/billing_address
    return order


def order_to_model(order: Order) -> OrderModel:
    """Map Order (domain) -> OrderModel. Caller must set total_amount from order.calculate_total_amount()."""
    total = order.calculate_total_amount()
    model = OrderModel(
        id=_uuid_s(order.order_id),
        customer_id=_uuid_s(order.customer_id),
        status=order.status.value,
        total_amount=total.amount,
        currency=total.currency,
    )
    model.items = [
        order_item_to_model(item, order.order_id) for item in order.items
    ]
    return model
