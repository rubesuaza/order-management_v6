"""
Exception raised when an entity is not found by ID.
"""

from .domain_error import DomainError


class EntityNotFoundException(DomainError):
    """Raised when an entity (e.g. Order) does not exist for the given identifier."""

    def __init__(self, message: str):
        super().__init__(message)
