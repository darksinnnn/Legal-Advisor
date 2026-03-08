"""
Fact Base - Stores case facts as typed knowledge units.
"""

from dataclasses import dataclass
from typing import Union

FactValue = Union[bool, str]


@dataclass
class KnowledgeUnit:
    """A named, typed piece of knowledge."""
    name: str
    value: FactValue


class FactBase:
    """Stores and manages case facts as knowledge units."""
    
    def __init__(self):
        self._facts: dict[str, FactValue] = {}
    
    def add(self, name: str, value: FactValue) -> None:
        """
        Add or update a knowledge unit.
        
        Args:
            name: Non-empty string identifier for the fact
            value: Boolean or string value
            
        Raises:
            ValueError: If name is empty or value type is unsupported
        """
        if not name or not isinstance(name, str):
            raise ValueError("Fact name must be a non-empty string")
        
        if not isinstance(value, (bool, str)):
            raise ValueError(f"Fact value must be bool or str, got {type(value).__name__}")
        
        self._facts[name] = value
    
    def get(self, name: str) -> FactValue | None:
        """
        Get a fact value by name.
        
        Args:
            name: Fact identifier
            
        Returns:
            The fact value, or None if not present
        """
        return self._facts.get(name)
    
    def remove(self, name: str) -> bool:
        """
        Remove a fact.
        
        Args:
            name: Fact identifier
            
        Returns:
            True if the fact existed and was removed, False otherwise
        """
        if name in self._facts:
            del self._facts[name]
            return True
        return False
    
    def clear(self) -> None:
        """Remove all facts."""
        self._facts.clear()
    
    def list_all(self) -> dict[str, FactValue]:
        """Return a copy of all facts."""
        return self._facts.copy()
    
    def has(self, name: str) -> bool:
        """Check if a fact exists."""
        return name in self._facts
