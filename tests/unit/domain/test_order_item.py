"""
Tests for OrderItem Entity
"""

import pytest
from decimal import Decimal
from uuid import uuid4

from order_management.domain.exceptions import InvalidItemException
from order_management.domain.models.money import Money
from order_management.domain.models.order_item import OrderItem


class TestOrderItem:
    """Test suite for OrderItem Entity."""
    
    def test_create_valid_order_item(self):
        """Test creating OrderItem with valid attributes."""
        product_id = uuid4()
        unit_price = Money.usd(Decimal("10.00"))
        item = OrderItem(
            product_id=product_id,
            product_name="Test Product",
            quantity=2,
            unit_price=unit_price
        )
        assert item.product_id == product_id
        assert item.product_name == "Test Product"
        assert item.quantity == 2
        assert item.unit_price == unit_price
        assert item.item_id is not None
    
    def test_create_order_item_negative_price_raises_exception(self):
        """Test that creating OrderItem with negative price raises ValueError from Money."""
        product_id = uuid4()
        # Money validates negative amounts before OrderItem can validate
        with pytest.raises(ValueError, match="Money amount cannot be negative"):
            OrderItem(
                product_id=product_id,
                product_name="Test Product",
                quantity=1,
                unit_price=Money.usd(Decimal("-10.00"))
            )
    
    def test_create_order_item_zero_quantity_raises_exception(self):
        """Test that creating OrderItem with zero quantity raises InvalidItemException."""
        product_id = uuid4()
        with pytest.raises(InvalidItemException, match="Quantity must be greater than 0"):
            OrderItem(
                product_id=product_id,
                product_name="Test Product",
                quantity=0,
                unit_price=Money.usd(Decimal("10.00"))
            )
    
    def test_create_order_item_negative_quantity_raises_exception(self):
        """Test that creating OrderItem with negative quantity raises InvalidItemException."""
        product_id = uuid4()
        with pytest.raises(InvalidItemException, match="Quantity must be greater than 0"):
            OrderItem(
                product_id=product_id,
                product_name="Test Product",
                quantity=-1,
                unit_price=Money.usd(Decimal("10.00"))
            )
    
    def test_create_order_item_empty_product_name_raises_exception(self):
        """Test that creating OrderItem with empty product name raises InvalidItemException."""
        product_id = uuid4()
        with pytest.raises(InvalidItemException, match="Product name must be"):
            OrderItem(
                product_id=product_id,
                product_name="",
                quantity=1,
                unit_price=Money.usd(Decimal("10.00"))
            )
    
    def test_calculate_subtotal(self):
        """Test calculating subtotal for OrderItem."""
        product_id = uuid4()
        item = OrderItem(
            product_id=product_id,
            product_name="Test Product",
            quantity=3,
            unit_price=Money.usd(Decimal("10.00"))
        )
        subtotal = item.calculate_subtotal()
        assert subtotal.amount == Decimal("30.00")
        assert subtotal.currency == "USD"
    
    def test_update_quantity_valid(self):
        """Test updating quantity with valid value."""
        product_id = uuid4()
        item = OrderItem(
            product_id=product_id,
            product_name="Test Product",
            quantity=2,
            unit_price=Money.usd(Decimal("10.00"))
        )
        item.update_quantity(5)
        assert item.quantity == 5
    
    def test_update_quantity_zero_raises_exception(self):
        """Test that updating quantity to zero raises InvalidItemException."""
        product_id = uuid4()
        item = OrderItem(
            product_id=product_id,
            product_name="Test Product",
            quantity=2,
            unit_price=Money.usd(Decimal("10.00"))
        )
        with pytest.raises(InvalidItemException, match="Quantity must be greater than 0"):
            item.update_quantity(0)
    
    def test_update_unit_price_valid(self):
        """Test updating unit price with valid value."""
        product_id = uuid4()
        item = OrderItem(
            product_id=product_id,
            product_name="Test Product",
            quantity=2,
            unit_price=Money.usd(Decimal("10.00"))
        )
        new_price = Money.usd(Decimal("15.00"))
        item.update_unit_price(new_price)
        assert item.unit_price == new_price
    
    def test_update_unit_price_negative_raises_exception(self):
        """Test that updating unit price to negative raises ValueError from Money."""
        product_id = uuid4()
        item = OrderItem(
            product_id=product_id,
            product_name="Test Product",
            quantity=2,
            unit_price=Money.usd(Decimal("10.00"))
        )
        # Money validates negative amounts before OrderItem can validate
        with pytest.raises(ValueError, match="Money amount cannot be negative"):
            item.update_unit_price(Money.usd(Decimal("-5.00")))
    
    def test_update_unit_price_different_currency_raises_exception(self):
        """Test that updating unit price with different currency raises InvalidItemException."""
        product_id = uuid4()
        item = OrderItem(
            product_id=product_id,
            product_name="Test Product",
            quantity=2,
            unit_price=Money.usd(Decimal("10.00"))
        )
        with pytest.raises(InvalidItemException, match="Cannot change currency"):
            item.update_unit_price(Money(Decimal("15.00"), "EUR"))
