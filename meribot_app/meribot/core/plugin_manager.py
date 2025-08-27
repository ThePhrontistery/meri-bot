# =============================================================
# Guía rápida: Cómo crear un nuevo plugin para MeriBot
# =============================================================
# 1. Hereda de BasePlugin e implementa los métodos abstractos:
#
# class MyPlugin(BasePlugin):
#     def activate(self):
#         # Inicialización
#         pass
#     def deactivate(self):
#         # Limpieza
#         pass
#     def process(self, query, context):
#         # Lógica principal
#         return f"Echo: {query}"
#
# 2. Registra el plugin en el PluginManager:
#
# manager = PluginManager()
# my_plugin = MyPlugin()
# manager.register('mi_plugin', my_plugin)
# manager.activate('mi_plugin')
#
# 3. Procesa consultas:
#
# respuestas = manager.process_with_active_plugins('Hola', {'user_id': 123})
# print(respuestas)
#
# Nota: Consulta la documentación oficial para detalles avanzados.



from abc import ABC, abstractmethod
from typing import Any, Dict

class BasePlugin(ABC):
    """
    Clase base abstracta para todos los plugins de MeriBot.
    Los plugins deben heredar de esta clase e implementar los métodos requeridos.

    Métodos principales:
        - activate: Lógica de inicialización o activación del plugin.
        - deactivate: Lógica de limpieza o desactivación del plugin.
        - process: Procesa una consulta usando el contexto y metadatos.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Inicializa el plugin con una configuración opcional.
        :param config: Diccionario de configuración específico del plugin.
        """
        self.config = config or {}

    @abstractmethod
    def activate(self) -> None:
        """Activa o inicializa el plugin."""
        pass

    @abstractmethod
    def deactivate(self) -> None:
        """Desactiva o limpia el plugin."""
        pass

    @abstractmethod
    def process(self, query: str, context: Dict[str, Any]) -> Any:
        """
        Procesa una consulta usando el contexto y metadatos.
        :param query: Consulta del usuario.
        :param context: Contexto conversacional y metadatos.
        :return: Respuesta generada por el plugin.
        """
        pass



class PluginManager:

    def process_with_active_plugins(self, query: str, context: dict) -> dict:
        """
        Procesa una consulta con todos los plugins activos, pasando contexto y metadatos.
        :param query: Consulta del usuario.
        :param context: Contexto conversacional y metadatos.
        :return: Diccionario con respuestas de cada plugin activo.
        """
        results = {}
        for name in self._active_plugins:
            plugin = self._plugins[name]
            try:
                results[name] = plugin.process(query, context)
            except Exception as e:
                results[name] = f"Error: {e}"
        return results
    """
    Gestor de plugins para MeriBot.
    Permite registrar, activar, desactivar y obtener plugins.
    """
    def __init__(self):
        self._plugins = {}
        self._active_plugins = set()

    def register(self, name: str, plugin: BasePlugin) -> None:
        """
        Registra un plugin bajo un nombre único.
        :param name: Nombre identificador del plugin.
        :param plugin: Instancia del plugin (debe heredar de BasePlugin).
        """
        if name in self._plugins:
            raise ValueError(f"El plugin '{name}' ya está registrado.")
        self._plugins[name] = plugin

    def activate(self, name: str) -> None:
        """
        Activa un plugin registrado.
        :param name: Nombre del plugin a activar.
        """
        plugin = self._plugins.get(name)
        if not plugin:
            raise KeyError(f"Plugin '{name}' no encontrado.")
        plugin.activate()
        self._active_plugins.add(name)

    def deactivate(self, name: str) -> None:
        """
        Desactiva un plugin activo.
        :param name: Nombre del plugin a desactivar.
        """
        plugin = self._plugins.get(name)
        if not plugin:
            raise KeyError(f"Plugin '{name}' no encontrado.")
        plugin.deactivate()
        self._active_plugins.discard(name)

    def get_plugin(self, name: str) -> BasePlugin:
        """
        Obtiene una instancia de plugin por nombre.
        :param name: Nombre del plugin.
        :return: Instancia del plugin.
        """
        return self._plugins.get(name)

    def list_plugins(self) -> list:
        """Devuelve la lista de nombres de plugins registrados."""
        return list(self._plugins.keys())

    def list_active_plugins(self) -> list:
        """Devuelve la lista de nombres de plugins activos."""
        return list(self._active_plugins)
