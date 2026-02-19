"""
Tests for Order Aggregate Root
"""

import pytest
from decimal import Decimal
from uuid import uuid4

from order_management.domain.exceptions import InvalidOrderStateException
from order_management.domain.models.address import Address
from order_management.domain.models.money import Money
from order_management.domain.models.order import Order
from order_management.domain.models.order_item import OrderItem
from order_management.domain.models.order_status import OrderStatus


class TestOrder:
    """Test suite for Order Aggregate Root."""
    
    @pytest.fixture
    def customer_id(self):
        """Fixture for customer ID."""
        return uuid4()
    
    @pytest.fixture
    def product_id(self):
        """Fixture for product ID."""
        return uuid4()
    
    @pytest.fixture
    def sample_item(self, product_id):
        """Fixture for a sample OrderItem."""
        return OrderItem(
            product_id=product_id,
            product_name="Test Product",
            quantity=2,
            unit_price=Money.usd(Decimal("10.00"))
        )
    
    @pytest.fixture
    def sample_address(self):
        """Fixture for a sample Address."""
        return Address(
            street="123 Main St",
            city="New York",
            state="NY",
            zip_code="10001",
            country="USA"
        )
    
    def test_create_order_with_factory_method(self, customer_id, sample_item):
        """Test creating Order using factory method."""
        order = Order.create(
            customer_id=customer_id,
            items=[sample_item]
        )
        assert order.customer_id == customer_id
        assert len(order.items) == 1
        assert order.status == OrderStatus.PENDING
        assert order.order_id is not None
    
    def test_create_order_empty_items_raises_error(self, customer_id):
        """Test that creating Order with empty items raises ValueError."""
        with pytest.raises(ValueError, match="must contain at least one item"):
            Order.create(customer_id=customer_id, items=[])
    
    def test_calculate_total_amount_single_item(self, customer_id, sample_item):
        """Test calculating total amount for order with single item."""
        order = Order.create(customer_id=customer_id, items=[sample_item])
        total = order.calculate_total_amount()
        assert total.amount == Decimal("20.00")  # 2 * 10.00
        assert total.currency == "USD"
    
    def test_calculate_total_amount_multiple_items(self, customer_id, product_id):
        """Test calculating total amount for order with multiple items."""
        item1 = OrderItem(
            product_id=product_id,
            product_name="Product 1",
            quantity=2,
            unit_price=Money.usd(Decimal("10.00"))
        )
        item2 = OrderItem(
            product_id=uuid4(),
            product_name="Product 2",
            quantity=3,
            unit_price=Money.usd(Decimal("5.00"))
        )
        order = Order.create(customer_id=customer_id, items=[item1, item2])
        total = order.calculate_total_amount()
        assert total.amount == Decimal("35.00")  # (2 * 10.00) + (3 * 5.00)
        assert total.currency == "USD"
    
    def test_calculate_total_amount_different_currencies_raises_error(self, customer_id, product_id):
        """Test that calculating total with different currencies raises ValueError."""
        item1 = OrderItem(
            product_id=product_id,
            product_name="Product 1",
            quantity=1,
            unit_price=Money.usd(Decimal("10.00"))
        )
        item2 = OrderItem(
            product_id=uuid4(),
            product_name="Product 2",
            quantity=1,
            unit_price=Money(Decimal("5.00"), "EUR")
        )
        order = Order.create(customer_id=customer_id, items=[item1, item2])
        with pytest.raises(ValueError, match="same currency"):
            order.calculate_total_amount()
    
    def test_mark_as_paid_from_pending_success(self, customer_id, product_id):
        """Test marking order as PAID from PENDING status with valid amount."""
        item = OrderItem(
            product_id=product_id,
            product_name="Test Product",
            quantity=2,
            unit_price=Money.usd(Decimal("10.00"))  # Total: 20.00 >= 10.00
        )
        order = Order.create(customer_id=customer_id, items=[item])
        order.mark_as_paid()
        assert order.status == OrderStatus.PAID
    
    def test_mark_as_paid_amount_below_minimum_raises_exception(self, customer_id, product_id):
        """Test that marking order as PAID with amount below 10.00 USD raises exception."""
        item = OrderItem(
            product_id=product_id,
            product_name="Test Product",
            quantity=1,
            unit_price=Money.usd(Decimal("5.00"))  # Total: 5.00 < 10.00
        )
        order = Order.create(customer_id=customer_id, items=[item])
        with pytest.raises(InvalidOrderStateException, match="must be at least"):
            order.mark_as_paid()
    
    def test_mark_as_paid_from_non_pending_raises_exception(self, customer_id, product_id):
        """Test that marking non-PENDING order as PAID raises exception."""
        item = OrderItem(
            product_id=product_id,
            product_name="Test Product",
            quantity=2,
            unit_price=Money.usd(Decimal("10.00"))
        )
        order = Order.create(customer_id=customer_id, items=[item])
        order.mark_as_paid()
        # Try to mark as PAID again
        with pytest.raises(InvalidOrderStateException, match="Only PENDING orders"):
            order.mark_as_paid()
    
    def test_mark_as_shipped_from_paid_success(self, customer_id, product_id):
        """Test marking order as SHIPPED from PAID status."""
        item = OrderItem(
            product_id=product_id,
            product_name="Test Product",
            quantity=2,
            unit_price=Money.usd(Decimal("10.00"))
        )
        order = Order.create(customer_id=customer_id, items=[item])
        order.mark_as_paid()
        order.mark_as_shipped()
        assert order.status == OrderStatus.SHIPPED
    
    def test_mark_as_shipped_from_non_paid_raises_exception(self, customer_id, product_id):
        """Test that marking non-PAID order as SHIPPED raises exception."""
        item = OrderItem(
            product_id=product_id,
            product_name="Test Product",
            quantity=2,
            unit_price=Money.usd(Decimal("10.00"))
        )
        order = Order.create(customer_id=customer_id, items=[item])
        # Try to mark as SHIPPED without being PAID
        with pytest.raises(InvalidOrderStateException, match="Only PAID orders"):
            order.mark_as_shipped()
    
    def test_cancel_from_pending_success(self, customer_id, product_id):
        """Test cancelling order from PENDING status."""
        item = OrderItem(
            product_id=product_id,
            product_name="Test Product",
            quantity=2,
            unit_price=Money.usd(Decimal("10.00"))
        )
        order = Order.create(customer_id=customer_id, items=[item])
        order.cancel()
        assert order.status == OrderStatus.CANCELLED
    
    def test_cancel_from_paid_success(self, customer_id, product_id):
        """Test cancelling order from PAID status."""
        item = OrderItem(
            product_id=product_id,
            product_name="Test Product",
            quantity=2,
            unit_price=Money.usd(Decimal("10.00"))
        )
        order = Order.create(customer_id=customer_id, items=[item])
        order.mark_as_paid()
        order.cancel()
        assert order.status == OrderStatus.CANCELLED
    
    def test_cancel_from_shipped_raises_exception(self, customer_id, product_id):
        """Test that cancelling SHIPPED order raises exception."""
        item = OrderItem(
            product_id=product_id,
            product_name="Test Product",
            quantity=2,
            unit_price=Money.usd(Decimal("10.00"))
        )
        order = Order.create(customer_id=customer_id, items=[item])
        order.mark_as_paid()
        order.mark_as_shipped()
        # Try to cancel SHIPPED order
        with pytest.raises(InvalidOrderStateException, match="Only PENDING or PAID orders"):
            order.cancel()
    
    def test_add_item_to_pending_order(self, customer_id, product_id):
        """Test adding item to PENDING order."""
        item1 = OrderItem(
            product_id=product_id,
            product_name="Product 1",
            quantity=1,
            unit_price=Money.usd(Decimal("10.00"))
        )
        order = Order.create(customer_id=customer_id, items=[item1])
        item2 = OrderItem(
            product_id=uuid4(),
            product_name="Product 2",
            quantity=1,
            unit_price=Money.usd(Decimal("5.00"))
        )
        order.add_item(item2)
        assert len(order.items) == 2
    
    def test_add_item_to_non_pending_raises_exception(self, customer_id, product_id):
        """Test that adding item to non-PENDING order raises exception."""
        item1 = OrderItem(
            product_id=product_id,
            product_name="Product 1",
            quantity=2,
            unit_price=Money.usd(Decimal("10.00"))
        )
        order = Order.create(customer_id=customer_id, items=[item1])
        order.mark_as_paid()
        item2 = OrderItem(
            product_id=uuid4(),
            product_name="Product 2",
            quantity=1,
            unit_price=Money.usd(Decimal("5.00"))
        )
        with pytest.raises(InvalidOrderStateException, match="Only PENDING orders"):
            order.add_item(item2)
    
    def test_add_item_different_currency_raises_error(self, customer_id, product_id):
        """Test that adding item with different currency raises ValueError."""
        item1 = OrderItem(
            product_id=product_id,
            product_name="Product 1",
            quantity=1,
            unit_price=Money.usd(Decimal("10.00"))
        )
        order = Order.create(customer_id=customer_id, items=[item1])
        item2 = OrderItem(
            product_id=uuid4(),
            product_name="Product 2",
            quantity=1,
            unit_price=Money(Decimal("5.00"), "EUR")
        )
        with pytest.raises(ValueError, match="must all use"):
            order.add_item(item2)
    
    def test_remove_item_from_pending_order(self, customer_id, product_id):
        """Test removing item from PENDING order."""
        item1 = OrderItem(
            product_id=product_id,
            product_name="Product 1",
            quantity=1,
            unit_price=Money.usd(Decimal("10.00"))
        )
        item2 = OrderItem(
            product_id=uuid4(),
            product_name="Product 2",
            quantity=1,
            unit_price=Money.usd(Decimal("5.00"))
        )
        order = Order.create(customer_id=customer_id, items=[item1, item2])
        item2_id = item2.item_id
        order.remove_item(item2_id)
        assert len(order.items) == 1
        assert order.items[0].item_id == item1.item_id
    
    def test_remove_item_would_empty_order_raises_error(self, customer_id, product_id):
        """Test that removing item that would leave order empty raises ValueError."""
        item = OrderItem(
            product_id=product_id,
            product_name="Product 1",
            quantity=1,
            unit_price=Money.usd(Decimal("10.00"))
        )
        order = Order.create(customer_id=customer_id, items=[item])
        with pytest.raises(ValueError, match="must contain at least one item"):
            order.remove_item(item.item_id)
    
    def test_remove_item_from_non_pending_raises_exception(self, customer_id, product_id):
        """Test that removing item from non-PENDING order raises exception."""
        item1 = OrderItem(
            product_id=product_id,
            product_name="Product 1",
            quantity=1,
            unit_price=Money.usd(Decimal("10.00"))
        )
        item2 = OrderItem(
            product_id=uuid4(),
            product_name="Product 2",
            quantity=1,
            unit_price=Money.usd(Decimal("5.00"))
        )
        order = Order.create(customer_id=customer_id, items=[item1, item2])
        order.mark_as_paid()
        with pytest.raises(InvalidOrderStateException, match="Only PENDING orders"):
            order.remove_item(item2.item_id)
    
    def test_order_with_addresses(self, customer_id, product_id, sample_address):
        """Test creating order with shipping and billing addresses."""
        item = OrderItem(
            product_id=product_id,
            product_name="Test Product",
            quantity=1,
            unit_price=Money.usd(Decimal("10.00"))
        )
        order = Order.create(
            customer_id=customer_id,
            items=[item],
            shipping_address=sample_address,
            billing_address=sample_address
        )
        assert order.shipping_address == sample_address
        assert order.billing_address == sample_address
