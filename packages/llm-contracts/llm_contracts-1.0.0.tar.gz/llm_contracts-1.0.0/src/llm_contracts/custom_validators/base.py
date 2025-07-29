"""Base class for custom validators."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseValidator(ABC):
    """Base class for custom validators."""
    
    @abstractmethod
    def validate(self, content: Any, **kwargs) -> List[str]:
        """
        Validate content and return list of error messages.
        
        Args:
            content: Content to validate
            **kwargs: Additional validation parameters
            
        Returns:
            List of error messages (empty if validation passes)
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this validator."""
        pass 