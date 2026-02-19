"""
Base exception for all domain errors.
"""


class DomainError(Exception):
    """Base exception for domain-related errors."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
