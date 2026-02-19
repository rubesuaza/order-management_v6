"""
Order Aggregate Root
Responsible for the consistency of the entire order aggregate.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List
from uuid import UUID, uuid4

from .address import Address
from .money import Money
from .order_item import OrderItem
from .order_status import OrderStatus
from ..exceptions import InvalidOrderStateException, InvalidItemException


@dataclass
class Order:
    """
    Aggregate Root representing an order.
    
    Invariants:
    - Must contain at least one OrderItem
    - Must meet minimum value of 10.00 USD before transitioning to PAID status
    - State transitions: CANCELLED only from PENDING or PAID, SHIPPED only from PAID
    """
    
    order_id: UUID = field(default_factory=uuid4)
    customer_id: UUID = field(default_factory=uuid4)
    items: List[OrderItem] = field(default_factory=list)
    status: OrderStatus = field(default=OrderStatus.PENDING)
    shipping_address: Address = None
    billing_address: Address = None
    
    def __post_init__(self):
        """Validate aggregate invariants."""
        if not self.items:
            raise ValueError("Order must contain at least one item")
    
    @classmethod
    def create(
        cls,
        customer_id: UUID,
        items: List[OrderItem],
        shipping_address: Address = None,
        billing_address: Address = None,
    ) -> "Order":
        """
        Factory method to create a new Order in a valid state.
        
        Args:
            customer_id: UUID of the customer placing the order
            items: List of OrderItems (must not be empty)
            shipping_address: Optional shipping address
            billing_address: Optional billing address
            
        Returns:
            A new Order instance in PENDING status
            
        Raises:
            ValueError: If items list is empty
        """
        if not items:
            raise ValueError("Order must contain at least one item")
        
        return cls(
            customer_id=customer_id,
            items=items,
            shipping_address=shipping_address,
            billing_address=billing_address,
            status=OrderStatus.PENDING,
        )
    
    def calculate_total_amount(self) -> Money:
        """
        Calculate the total amount of the order.
        
        Returns:
            Money object representing the sum of all item subtotals
            
        Raises:
            ValueError: If items have different currencies
        """
        if not self.items:
            return Money.zero("USD")
        
        # Get currency from first item
        currency = self.items[0].unit_price.currency
        
        # Validate all items have the same currency
        for item in self.items:
            if item.unit_price.currency != currency:
                raise ValueError(
                    f"All items must have the same currency. Found {item.unit_price.currency} and {currency}"
                )
        
        total = Money.zero(currency)
        for item in self.items:
            total = total + item.calculate_subtotal()
        
        return total
    
    def mark_as_paid(self) -> None:
        """
        Transition order to PAID status.
        
        Raises:
            InvalidOrderStateException: If order is not in PENDING status
            InvalidOrderStateException: If total amount is less than 10.00 USD
        """
        if self.status != OrderStatus.PENDING:
            raise InvalidOrderStateException(
                f"Cannot mark order as PAID from {self.status.value} status. "
                "Only PENDING orders can be marked as PAID."
            )
        
        total = self.calculate_total_amount()
        minimum_amount = Money.usd(Decimal("10.00"))
        
        if total.currency != minimum_amount.currency:
            raise InvalidOrderStateException(
                f"Cannot validate minimum amount: order currency is {total.currency}, "
                f"but minimum is in {minimum_amount.currency}"
            )
        
        if total < minimum_amount:
            raise InvalidOrderStateException(
                f"Order total ({total.amount} {total.currency}) must be at least "
                f"{minimum_amount.amount} {minimum_amount.currency} to be marked as PAID"
            )
        
        self.status = OrderStatus.PAID
    
    def mark_as_shipped(self) -> None:
        """
        Transition order to SHIPPED status.
        
        Raises:
            InvalidOrderStateException: If order is not in PAID status
        """
        if self.status != OrderStatus.PAID:
            raise InvalidOrderStateException(
                f"Cannot mark order as SHIPPED from {self.status.value} status. "
                "Only PAID orders can be marked as SHIPPED."
            )
        
        self.status = OrderStatus.SHIPPED
    
    def cancel(self) -> None:
        """
        Transition order to CANCELLED status.
        
        Raises:
            InvalidOrderStateException: If order is not in PENDING or PAID status
        """
        if self.status not in (OrderStatus.PENDING, OrderStatus.PAID):
            raise InvalidOrderStateException(
                f"Cannot cancel order from {self.status.value} status. "
                "Only PENDING or PAID orders can be cancelled."
            )
        
        self.status = OrderStatus.CANCELLED
    
    def add_item(self, item: OrderItem) -> None:
        """
        Add an item to the order.
        
        Args:
            item: OrderItem to add
            
        Raises:
            InvalidOrderStateException: If order is not in PENDING status
            ValueError: If item currency doesn't match existing items
        """
        if self.status != OrderStatus.PENDING:
            raise InvalidOrderStateException(
                f"Cannot add items to order in {self.status.value} status. "
                "Only PENDING orders can be modified."
            )
        
        # Validate currency consistency if there are existing items
        if self.items:
            existing_currency = self.items[0].unit_price.currency
            if item.unit_price.currency != existing_currency:
                raise ValueError(
                    f"Cannot add item with currency {item.unit_price.currency}. "
                    f"Order items must all use {existing_currency}"
                )
        
        self.items.append(item)
    
    def remove_item(self, item_id: UUID) -> None:
        """
        Remove an item from the order.
        
        Args:
            item_id: UUID of the item to remove
            
        Raises:
            InvalidOrderStateException: If order is not in PENDING status
            ValueError: If removing the item would leave the order empty
        """
        if self.status != OrderStatus.PENDING:
            raise InvalidOrderStateException(
                f"Cannot remove items from order in {self.status.value} status. "
                "Only PENDING orders can be modified."
            )
        
        if len(self.items) <= 1:
            raise ValueError("Cannot remove item: order must contain at least one item")
        
        self.items = [item for item in self.items if item.item_id != item_id]
        
        if not self.items:
            raise ValueError("Order must contain at least one item")
