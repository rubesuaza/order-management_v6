"""
Tests for Money Value Object
"""

import pytest
from decimal import Decimal

from order_management.domain.exceptions import CurrencyMismatchException
from order_management.domain.models.money import Money


class TestMoney:
    """Test suite for Money Value Object."""
    
    def test_create_money_with_valid_amount(self):
        """Test creating Money with valid amount and currency."""
        money = Money(Decimal("100.50"), "USD")
        assert money.amount == Decimal("100.50")
        assert money.currency == "USD"
    
    def test_create_money_zero(self):
        """Test creating Money with zero amount."""
        money = Money(Decimal("0"), "USD")
        assert money.amount == Decimal("0")
    
    def test_create_money_negative_raises_error(self):
        """Test that creating Money with negative amount raises ValueError."""
        with pytest.raises(ValueError, match="cannot be negative"):
            Money(Decimal("-10"), "USD")
    
    def test_create_money_empty_currency_raises_error(self):
        """Test that creating Money with empty currency raises ValueError."""
        with pytest.raises(ValueError, match="Currency must be"):
            Money(Decimal("10"), "")
    
    def test_add_money_same_currency(self):
        """Test adding Money objects with same currency."""
        money1 = Money(Decimal("100"), "USD")
        money2 = Money(Decimal("50"), "USD")
        result = money1 + money2
        assert result.amount == Decimal("150")
        assert result.currency == "USD"
    
    def test_add_money_different_currency_raises_exception(self):
        """Test that adding Money with different currencies raises CurrencyMismatchException."""
        money1 = Money(Decimal("100"), "USD")
        money2 = Money(Decimal("50"), "EUR")
        with pytest.raises(CurrencyMismatchException):
            money1 + money2
    
    def test_subtract_money_same_currency(self):
        """Test subtracting Money objects with same currency."""
        money1 = Money(Decimal("100"), "USD")
        money2 = Money(Decimal("30"), "USD")
        result = money1 - money2
        assert result.amount == Decimal("70")
        assert result.currency == "USD"
    
    def test_subtract_money_result_negative_raises_error(self):
        """Test that subtracting Money resulting in negative raises ValueError."""
        money1 = Money(Decimal("50"), "USD")
        money2 = Money(Decimal("100"), "USD")
        with pytest.raises(ValueError, match="cannot be negative"):
            money1 - money2
    
    def test_multiply_money_by_decimal(self):
        """Test multiplying Money by Decimal."""
        money = Money(Decimal("100"), "USD")
        result = money * Decimal("2.5")
        assert result.amount == Decimal("250")
        assert result.currency == "USD"
    
    def test_multiply_money_by_int(self):
        """Test multiplying Money by int (converted to Decimal)."""
        money = Money(Decimal("100"), "USD")
        result = money * 3
        assert result.amount == Decimal("300")
    
    def test_rmul_money(self):
        """Test right multiplication of Money."""
        money = Money(Decimal("100"), "USD")
        result = Decimal("2") * money
        assert result.amount == Decimal("200")
    
    def test_equality_same_amount_and_currency(self):
        """Test Money equality with same amount and currency."""
        money1 = Money(Decimal("100"), "USD")
        money2 = Money(Decimal("100"), "USD")
        assert money1 == money2
    
    def test_equality_different_amount(self):
        """Test Money inequality with different amount."""
        money1 = Money(Decimal("100"), "USD")
        money2 = Money(Decimal("200"), "USD")
        assert money1 != money2
    
    def test_equality_different_currency(self):
        """Test Money inequality with different currency."""
        money1 = Money(Decimal("100"), "USD")
        money2 = Money(Decimal("100"), "EUR")
        assert money1 != money2
    
    def test_comparison_lt(self):
        """Test less than comparison."""
        money1 = Money(Decimal("50"), "USD")
        money2 = Money(Decimal("100"), "USD")
        assert money1 < money2
    
    def test_comparison_different_currency_raises_exception(self):
        """Test that comparing Money with different currencies raises exception."""
        money1 = Money(Decimal("50"), "USD")
        money2 = Money(Decimal("100"), "EUR")
        with pytest.raises(CurrencyMismatchException):
            money1 < money2
    
    def test_zero_class_method(self):
        """Test Money.zero() class method."""
        money = Money.zero("USD")
        assert money.amount == Decimal("0")
        assert money.currency == "USD"
    
    def test_usd_class_method(self):
        """Test Money.usd() convenience method."""
        money = Money.usd(Decimal("100"))
        assert money.amount == Decimal("100")
        assert money.currency == "USD"
