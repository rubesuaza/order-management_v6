"""
PaymentGatewayPort
Interface for external payment processing.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from ..models.money import Money


class PaymentGatewayPort(ABC):
    """Abstract interface for payment processing operations."""
    
    @abstractmethod
    def process_payment(
        self,
        order_id: UUID,
        amount: Money,
        payment_method: str,
    ) -> bool:
        """
        Process a payment for an order.
        
        Args:
            order_id: UUID of the order being paid
            amount: Money value object representing the payment amount
            payment_method: String identifier for the payment method
            
        Returns:
            True if payment was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def refund_payment(
        self,
        order_id: UUID,
        amount: Money,
    ) -> bool:
        """
        Process a refund for an order.
        
        Args:
            order_id: UUID of the order to refund
            amount: Money value object representing the refund amount
            
        Returns:
            True if refund was successful, False otherwise
        """
        pass
