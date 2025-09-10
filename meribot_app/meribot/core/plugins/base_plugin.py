from abc import ABC, abstractmethod
from typing import Any, Dict

class BasePlugin(ABC):
    """
    Abstract base class for MeriBot plugins. Implement activate, deactivate, and process methods.
    """
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

    @abstractmethod
    def activate(self) -> None:
        pass

    @abstractmethod
    def deactivate(self) -> None:
        pass

    @abstractmethod
    def process(self, query: str, context: Dict[str, Any]) -> Any:
        pass
