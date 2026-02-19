"""
Unit tests for persistence mappers (domain <-> model).
"""

import pytest
from decimal import Decimal
from uuid import uuid4

from order_management.domain.models import (
    Money,
    Order,
    OrderItem,
    OrderStatus,
)
from order_management.infrastructure.adapters.output.persistence.mappers import (
    order_item_to_domain,
    order_item_to_model,
    order_to_domain,
    order_to_model,
)
from order_management.infrastructure.adapters.output.persistence.models import (
    OrderItemModel,
    OrderModel,
)


class TestOrderItemMapper:
    """Tests for OrderItem <-> OrderItemModel mapping."""

    def test_order_item_to_domain_maps_all_fields(self):
        # Arrange
        item_id = uuid4()
        product_id = uuid4()
        order_id = uuid4()
        row = OrderItemModel(
            id=str(item_id),
            order_id=str(order_id),
            product_id=str(product_id),
            product_name="Test Product",
            quantity=2,
            unit_price=Decimal("10.50"),
            currency="USD",
        )
        # Act
        domain_item = order_item_to_domain(row)
        # Assert
        assert domain_item.item_id == item_id
        assert domain_item.product_id == product_id
        assert domain_item.product_name == "Test Product"
        assert domain_item.quantity == 2
        assert domain_item.unit_price.amount == Decimal("10.50")
        assert domain_item.unit_price.currency == "USD"

    def test_order_item_to_model_maps_all_fields(self):
        # Arrange
        item_id = uuid4()
        product_id = uuid4()
        order_id = uuid4()
        domain_item = OrderItem(
            item_id=item_id,
            product_id=product_id,
            product_name="Mapped Product",
            quantity=3,
            unit_price=Money.usd(Decimal("15.00")),
        )
        # Act
        model = order_item_to_model(domain_item, order_id)
        # Assert
        assert model.id == str(item_id)
        assert model.order_id == str(order_id)
        assert model.product_id == str(product_id)
        assert model.product_name == "Mapped Product"
        assert model.quantity == 3
        assert model.unit_price == Decimal("15.00")
        assert model.currency == "USD"


class TestOrderMapper:
    """Tests for Order <-> OrderModel mapping."""

    @pytest.fixture
    def order_id(self):
        return uuid4()

    @pytest.fixture
    def customer_id(self):
        return uuid4()

    @pytest.fixture
    def product_id(self):
        return uuid4()

    @pytest.fixture
    def domain_order(self, order_id, customer_id, product_id):
        item = OrderItem(
            product_id=product_id,
            product_name="Product A",
            quantity=2,
            unit_price=Money.usd(Decimal("10.00")),
        )
        return Order(
            order_id=order_id,
            customer_id=customer_id,
            items=[item],
            status=OrderStatus.PENDING,
        )

    def test_order_to_model_maps_all_fields(self, domain_order):
        # Act
        model = order_to_model(domain_order)
        # Assert
        assert model.id == str(domain_order.order_id)
        assert model.customer_id == str(domain_order.customer_id)
        assert model.status == OrderStatus.PENDING.value
        assert model.total_amount == Decimal("20.00")
        assert model.currency == "USD"
        assert len(model.items) == 1
        assert model.items[0].product_name == "Product A"
        assert model.items[0].quantity == 2

    def test_order_to_domain_maps_all_fields(self, order_id, customer_id, product_id):
        # Arrange: build model-like structure (OrderModel with items)
        item_row = OrderItemModel(
            id=str(uuid4()),
            order_id=str(order_id),
            product_id=str(product_id),
            product_name="DB Product",
            quantity=1,
            unit_price=Decimal("25.00"),
            currency="USD",
        )
        order_row = OrderModel(
            id=str(order_id),
            customer_id=str(customer_id),
            status=OrderStatus.PAID.value,
            total_amount=Decimal("25.00"),
            currency="USD",
        )
        order_row.items = [item_row]
        # Act
        domain_order = order_to_domain(order_row)
        # Assert
        assert domain_order.order_id == order_id
        assert domain_order.customer_id == customer_id
        assert domain_order.status == OrderStatus.PAID
        assert len(domain_order.items) == 1
        assert domain_order.items[0].product_name == "DB Product"
        assert domain_order.items[0].quantity == 1
        assert domain_order.items[0].unit_price.amount == Decimal("25.00")

    def test_order_to_domain_roundtrip_preserves_data(self, domain_order):
        # Act: domain -> model -> domain
        model = order_to_model(domain_order)
        model.items = [order_item_to_model(item, domain_order.order_id) for item in domain_order.items]
        restored = order_to_domain(model)
        # Assert
        assert restored.order_id == domain_order.order_id
        assert restored.customer_id == domain_order.customer_id
        assert restored.status == domain_order.status
        assert len(restored.items) == len(domain_order.items)
        assert restored.items[0].product_name == domain_order.items[0].product_name
        assert restored.items[0].quantity == domain_order.items[0].quantity
        assert restored.calculate_total_amount().amount == domain_order.calculate_total_amount().amount
