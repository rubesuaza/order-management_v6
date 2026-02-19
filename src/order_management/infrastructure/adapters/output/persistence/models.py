"""
SQLAlchemy persistence models for orders and order_items.
Decoupled from domain entities; use mappers for conversion.
No ON DELETE CASCADE to preserve audit trail.
"""

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import declarative_base, relationship

# String(36) works with SQLite and PostgreSQL; mappers handle UUID conversion
UUID_COLUMN = String(36)

Base = declarative_base()


def _uuid_default():
    return str(uuid4())


class OrderModel(Base):
    """Persistence model for Order aggregate (master table)."""

    __tablename__ = "orders"

    id = Column(UUID_COLUMN, primary_key=True, default=_uuid_default, nullable=False)
    customer_id = Column(UUID_COLUMN, nullable=False, index=True)
    status = Column(String(20), nullable=False, index=True)
    total_amount = Column(Numeric(19, 2), nullable=False)
    currency = Column(String(3), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    items = relationship(
        "OrderItemModel",
        back_populates="order",
        cascade="all, delete-orphan",
        passive_deletes=False,
    )

    __table_args__ = (
        Index("ix_orders_customer_id", "customer_id"),
        Index("ix_orders_status", "status"),
    )


class OrderItemModel(Base):
    """Persistence model for OrderItem (detail table). No ON DELETE CASCADE on order_id."""

    __tablename__ = "order_items"

    id = Column(UUID_COLUMN, primary_key=True, default=_uuid_default, nullable=False)
    order_id = Column(
        UUID_COLUMN,
        ForeignKey("orders.id", ondelete="RESTRICT"),
        nullable=False,
    )
    product_id = Column(UUID_COLUMN, nullable=False)
    product_name = Column(String(255), nullable=True)  # optional in DB for flexibility
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(19, 2), nullable=False)
    currency = Column(String(3), nullable=False)

    order = relationship("OrderModel", back_populates="items")
