"""
Exception raised when attempting arithmetic operations with mismatched currencies.
"""

from .domain_error import DomainError


class CurrencyMismatchException(DomainError):
    """Raised when attempting Money arithmetic with different currencies."""
    
    def __init__(self, message: str):
        super().__init__(message)
