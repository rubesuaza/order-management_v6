"""
OrderRepository Port
Interface for persisting and retrieving Order aggregates.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..models.order import Order


class OrderRepository(ABC):
    """Abstract interface for Order persistence operations."""
    
    @abstractmethod
    def save(self, order: Order) -> Order:
        """
        Save or update an Order aggregate.
        
        Args:
            order: Order instance to persist
            
        Returns:
            The persisted Order instance
        """
        pass
    
    @abstractmethod
    def find_by_id(self, order_id: UUID) -> Optional[Order]:
        """
        Find an Order by its ID.
        
        Args:
            order_id: UUID of the order to retrieve
            
        Returns:
            Order instance if found, None otherwise
        """
        pass
    
    @abstractmethod
    def find_by_customer_id(self, customer_id: UUID) -> List[Order]:
        """
        Find all Orders for a given customer.
        
        Args:
            customer_id: UUID of the customer
            
        Returns:
            List of Order instances for the customer
        """
        pass
    
    @abstractmethod
    def delete(self, order_id: UUID) -> bool:
        """
        Delete an Order by its ID.
        
        Args:
            order_id: UUID of the order to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        pass
