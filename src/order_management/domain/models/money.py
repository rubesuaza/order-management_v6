"""
Money Value Object
Immutable representation of monetary amounts with currency validation.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from ..exceptions import CurrencyMismatchException


@dataclass(frozen=True)
class Money:
    """
    Value Object representing a monetary amount.
    
    Immutable and enforces currency consistency during arithmetic operations.
    """
    
    amount: Decimal
    currency: str
    
    def __post_init__(self):
        """Validate that amount is not negative."""
        if self.amount < 0:
            raise ValueError("Money amount cannot be negative")
        if not self.currency or not isinstance(self.currency, str):
            raise ValueError("Currency must be a non-empty string")
    
    def __add__(self, other: "Money") -> "Money":
        """Add two Money objects with the same currency."""
        if not isinstance(other, Money):
            raise TypeError("Can only add Money to Money")
        if self.currency != other.currency:
            raise CurrencyMismatchException(
                f"Cannot add {self.currency} to {other.currency}"
            )
        return Money(self.amount + other.amount, self.currency)
    
    def __sub__(self, other: "Money") -> "Money":
        """Subtract two Money objects with the same currency."""
        if not isinstance(other, Money):
            raise TypeError("Can only subtract Money from Money")
        if self.currency != other.currency:
            raise CurrencyMismatchException(
                f"Cannot subtract {other.currency} from {self.currency}"
            )
        result = self.amount - other.amount
        if result < 0:
            raise ValueError("Resulting amount cannot be negative")
        return Money(result, self.currency)
    
    def __mul__(self, multiplier: Decimal) -> "Money":
        """Multiply Money by a Decimal multiplier."""
        if not isinstance(multiplier, Decimal):
            multiplier = Decimal(str(multiplier))
        result = self.amount * multiplier
        if result < 0:
            raise ValueError("Resulting amount cannot be negative")
        return Money(result, self.currency)
    
    def __rmul__(self, multiplier: Decimal) -> "Money":
        """Right multiplication for Money."""
        return self.__mul__(multiplier)
    
    def __eq__(self, other: object) -> bool:
        """Value-based equality."""
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency
    
    def __lt__(self, other: "Money") -> bool:
        """Less than comparison (same currency only)."""
        if not isinstance(other, Money):
            raise TypeError("Can only compare Money with Money")
        if self.currency != other.currency:
            raise CurrencyMismatchException(
                f"Cannot compare {self.currency} with {other.currency}"
            )
        return self.amount < other.amount
    
    def __le__(self, other: "Money") -> bool:
        """Less than or equal comparison (same currency only)."""
        if not isinstance(other, Money):
            raise TypeError("Can only compare Money with Money")
        if self.currency != other.currency:
            raise CurrencyMismatchException(
                f"Cannot compare {self.currency} with {other.currency}"
            )
        return self.amount <= other.amount
    
    def __gt__(self, other: "Money") -> bool:
        """Greater than comparison (same currency only)."""
        if not isinstance(other, Money):
            raise TypeError("Can only compare Money with Money")
        if self.currency != other.currency:
            raise CurrencyMismatchException(
                f"Cannot compare {self.currency} with {other.currency}"
            )
        return self.amount > other.amount
    
    def __ge__(self, other: "Money") -> bool:
        """Greater than or equal comparison (same currency only)."""
        if not isinstance(other, Money):
            raise TypeError("Can only compare Money with Money")
        if self.currency != other.currency:
            raise CurrencyMismatchException(
                f"Cannot compare {self.currency} with {other.currency}"
            )
        return self.amount >= other.amount
    
    @classmethod
    def zero(cls, currency: str) -> "Money":
        """Create a Money object with zero amount."""
        return cls(Decimal("0"), currency)
    
    @classmethod
    def usd(cls, amount: Decimal) -> "Money":
        """Convenience method to create USD Money."""
        return cls(amount, "USD")
