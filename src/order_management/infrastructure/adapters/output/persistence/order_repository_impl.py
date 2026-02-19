"""
SQLAlchemy implementation of OrderRepository port.
"""

from uuid import UUID

from sqlalchemy.orm import Session

from order_management.domain.ports.order_repository import OrderRepository
from order_management.domain.models import Order

from .models import OrderModel
from .mappers import order_to_domain, order_to_model, order_item_to_model


class OrderRepositoryImpl(OrderRepository):
    """Persistence adapter for Order aggregate using SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, order: Order) -> Order:
        existing = (
            self._session.query(OrderModel)
            .filter(OrderModel.id == str(order.order_id))
            .first()
        )
        total = order.calculate_total_amount()
        if existing:
            existing.customer_id = str(order.customer_id)
            existing.status = order.status.value
            existing.total_amount = total.amount
            existing.currency = total.currency
            for item in list(existing.items):
                self._session.delete(item)
            for item in order.items:
                im = order_item_to_model(item, order.order_id)
                im.order_id = str(order.order_id)
                existing.items.append(im)
            self._session.flush()
            return order
        model = order_to_model(order)
        self._session.add(model)
        self._session.flush()
        return order

    def find_by_id(self, order_id: UUID) -> Order | None:
        row = (
            self._session.query(OrderModel)
            .filter(OrderModel.id == str(order_id))
            .first()
        )
        if not row:
            return None
        return order_to_domain(row)

    def find_by_customer_id(self, customer_id: UUID) -> list[Order]:
        rows = (
            self._session.query(OrderModel)
            .filter(OrderModel.customer_id == str(customer_id))
            .all()
        )
        return [order_to_domain(r) for r in rows]

    def delete(self, order_id: UUID) -> bool:
        row = (
            self._session.query(OrderModel)
            .filter(OrderModel.id == str(order_id))
            .first()
        )
        if not row:
            return False
        self._session.delete(row)
        self._session.flush()
        return True
