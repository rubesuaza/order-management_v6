"""
Domain Exceptions
Domain-specific exceptions for business rule violations.
"""

from .domain_error import DomainError
from .entity_not_found_exception import EntityNotFoundException
from .invalid_order_state_exception import InvalidOrderStateException
from .invalid_item_exception import InvalidItemException
from .currency_mismatch_exception import CurrencyMismatchException

__all__ = [
    "DomainError",
    "EntityNotFoundException",
    "InvalidOrderStateException",
    "InvalidItemException",
    "CurrencyMismatchException",
]
