from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseTool(ABC):
    """Base class for all tools."""
    
    @abstractmethod
    async def run(self, **kwargs: Any) -> Dict[str, Any]:
        """Execute the tool."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description."""
        pass