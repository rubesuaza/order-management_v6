"""
OrderItem Entity
Represents an item within an Order aggregate.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID, uuid4

from .money import Money
from ..exceptions import InvalidItemException


@dataclass
class OrderItem:
    """
    Entity representing an item in an order.
    
    Invariants:
    - quantity must be > 0
    - unit_price cannot be negative
    """
    
    product_id: UUID
    product_name: str
    quantity: int
    unit_price: Money
    item_id: UUID = field(default_factory=uuid4)
    
    def __post_init__(self):
        """Validate business invariants."""
        if self.quantity <= 0:
            raise InvalidItemException("Quantity must be greater than 0")
        if self.unit_price.amount < 0:
            raise InvalidItemException("Unit price cannot be negative")
        if not self.product_name or not isinstance(self.product_name, str):
            raise InvalidItemException("Product name must be a non-empty string")
    
    def calculate_subtotal(self) -> Money:
        """Calculate the subtotal for this item (quantity * unit_price)."""
        return self.unit_price * Decimal(self.quantity)
    
    def update_quantity(self, new_quantity: int) -> None:
        """Update the quantity of this item."""
        if new_quantity <= 0:
            raise InvalidItemException("Quantity must be greater than 0")
        object.__setattr__(self, "quantity", new_quantity)
    
    def update_unit_price(self, new_price: Money) -> None:
        """Update the unit price of this item."""
        if new_price.amount < 0:
            raise InvalidItemException("Unit price cannot be negative")
        if self.unit_price.currency != new_price.currency:
            raise InvalidItemException(
                f"Cannot change currency from {self.unit_price.currency} to {new_price.currency}"
            )
        object.__setattr__(self, "unit_price", new_price)
