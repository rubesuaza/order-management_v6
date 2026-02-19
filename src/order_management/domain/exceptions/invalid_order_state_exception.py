"""
Exception raised when an invalid order state transition is attempted.
"""

from .domain_error import DomainError


class InvalidOrderStateException(DomainError):
    """Raised when attempting an invalid state transition on an Order."""
    
    def __init__(self, message: str):
        super().__init__(message)
