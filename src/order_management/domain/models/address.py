"""
Address Value Object
Immutable representation of shipping or billing locations.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Address:
    """
    Value Object representing a physical address.
    
    Immutable and value-based equality.
    """
    
    street: str
    city: str
    state: str
    zip_code: str
    country: str
    
    def __post_init__(self):
        """Validate required fields."""
        if not self.street or not isinstance(self.street, str):
            raise ValueError("Street must be a non-empty string")
        if not self.city or not isinstance(self.city, str):
            raise ValueError("City must be a non-empty string")
        if not self.state or not isinstance(self.state, str):
            raise ValueError("State must be a non-empty string")
        if not self.zip_code or not isinstance(self.zip_code, str):
            raise ValueError("Zip code must be a non-empty string")
        if not self.country or not isinstance(self.country, str):
            raise ValueError("Country must be a non-empty string")
