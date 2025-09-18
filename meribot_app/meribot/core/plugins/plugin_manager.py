import os

from typing import Any, Dict
from .base_plugin import BasePlugin
from meribot.core.logger import get_logger

class PluginManager:
    """
    Manages MeriBot plugins: register, activate, deactivate, and process queries with active plugins.
    """
    def __init__(self):
        self.logger = get_logger("meribot.plugins.manager", log_file=os.getenv("MERIBOT_LOG_FILE"))
        self._plugins: Dict[str, BasePlugin] = {}
        self._active_plugins: set = set()

    async def run_pre_llm_plugins(self, message: str, context: Dict[str, Any], metadata: Dict[str, Any]) -> Any:
        """Hook for pre-LLM plugins. Returns first non-empty response or None."""
        return None

    async def run_post_llm_plugins(self, response: Any, context: Dict[str, Any], metadata: Dict[str, Any]) -> Any:
        """Hook for post-LLM plugins. Allows modifying the response before returning."""
        return response

    def process_with_active_plugins(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes a query with all active plugins, passing context and metadata.
        Returns a dict with each plugin's response or error.
        """
        results: Dict[str, Any] = {}
        self.logger.info(f"Procesando query con plugins activos: {self._active_plugins}")
        for name in self._active_plugins:
            plugin = self._plugins[name]
            try:
                results[name] = plugin.process(query, context)
                self.logger.info(f"Plugin '{name}' procesó correctamente.")
            except Exception as e:
                results[name] = f"Error: {e}"
                self.logger.error(f"Error en plugin '{name}': {e}")
        return results

    def register(self, name: str, plugin: BasePlugin) -> None:
        """Register a plugin under a unique name."""
        if name in self._plugins:
            self.logger.warning(f"Intento de registrar plugin duplicado: {name}")
            raise ValueError(f"Plugin '{name}' is already registered.")
        self._plugins[name] = plugin
        self.logger.info(f"Plugin registrado: {name}")

    def activate(self, name: str) -> None:
        """Activate a registered plugin."""
        plugin = self._plugins.get(name)
        if not plugin:
            self.logger.error(f"Intento de activar plugin no registrado: {name}")
            raise KeyError(f"Plugin '{name}' not found.")
        plugin.activate()
        self._active_plugins.add(name)
        self.logger.info(f"Plugin activado: {name}")

    def deactivate(self, name: str) -> None:
        """Deactivate an active plugin."""
        plugin = self._plugins.get(name)
        if not plugin:
            self.logger.error(f"Intento de desactivar plugin no registrado: {name}")
            raise KeyError(f"Plugin '{name}' not found.")
        plugin.deactivate()
        self._active_plugins.discard(name)
        self.logger.info(f"Plugin desactivado: {name}")

    def get_plugin(self, name: str) -> BasePlugin:
        """Get a plugin instance by name."""
        return self._plugins.get(name)

    def list_plugins(self) -> list:
        """List names of registered plugins."""
        return list(self._plugins.keys())

    def list_active_plugins(self) -> list:
        """List names of active plugins."""
        return list(self._active_plugins)
