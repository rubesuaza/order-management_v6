"""
Tests for Address Value Object
"""

import pytest

from order_management.domain.models.address import Address


class TestAddress:
    """Test suite for Address Value Object."""
    
    def test_create_valid_address(self):
        """Test creating Address with all required fields."""
        address = Address(
            street="123 Main St",
            city="New York",
            state="NY",
            zip_code="10001",
            country="USA"
        )
        assert address.street == "123 Main St"
        assert address.city == "New York"
        assert address.state == "NY"
        assert address.zip_code == "10001"
        assert address.country == "USA"
    
    def test_address_is_immutable(self):
        """Test that Address is immutable (frozen dataclass)."""
        address = Address(
            street="123 Main St",
            city="New York",
            state="NY",
            zip_code="10001",
            country="USA"
        )
        with pytest.raises(Exception):  # dataclass frozen raises FrozenInstanceError
            address.street = "456 Other St"
    
    def test_empty_street_raises_error(self):
        """Test that empty street raises ValueError."""
        with pytest.raises(ValueError, match="Street must be"):
            Address(
                street="",
                city="New York",
                state="NY",
                zip_code="10001",
                country="USA"
            )
    
    def test_empty_city_raises_error(self):
        """Test that empty city raises ValueError."""
        with pytest.raises(ValueError, match="City must be"):
            Address(
                street="123 Main St",
                city="",
                state="NY",
                zip_code="10001",
                country="USA"
            )
    
    def test_empty_state_raises_error(self):
        """Test that empty state raises ValueError."""
        with pytest.raises(ValueError, match="State must be"):
            Address(
                street="123 Main St",
                city="New York",
                state="",
                zip_code="10001",
                country="USA"
            )
    
    def test_empty_zip_code_raises_error(self):
        """Test that empty zip_code raises ValueError."""
        with pytest.raises(ValueError, match="Zip code must be"):
            Address(
                street="123 Main St",
                city="New York",
                state="NY",
                zip_code="",
                country="USA"
            )
    
    def test_empty_country_raises_error(self):
        """Test that empty country raises ValueError."""
        with pytest.raises(ValueError, match="Country must be"):
            Address(
                street="123 Main St",
                city="New York",
                state="NY",
                zip_code="10001",
                country=""
            )
