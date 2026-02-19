"""
Exception raised when an OrderItem has invalid attributes.
"""

from .domain_error import DomainError


class InvalidItemException(DomainError):
    """Raised when an OrderItem violates business rules (e.g., negative price or quantity)."""
    
    def __init__(self, message: str):
        super().__init__(message)
