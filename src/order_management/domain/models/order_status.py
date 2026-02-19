"""
OrderStatus Enum
Represents the possible states of an Order.
"""

from enum import Enum


class OrderStatus(Enum):
    """Enumeration of order states."""
    
    PENDING = "PENDING"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"
