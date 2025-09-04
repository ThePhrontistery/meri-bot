"""
cache.py
--------
Módulo para la gestión de caché de respuestas frecuentes en MeriBot.
"""


from typing import Any, Optional
import time
from collections import OrderedDict

class ResponseCache:
    """
    Caché simple en memoria para respuestas frecuentes.
    Permite almacenar, recuperar e invalidar respuestas por clave.
    """

    def __init__(self, default_ttl: int = 300, max_size: int = 1000):
        """
        :param default_ttl: Tiempo de vida por defecto en segundos.
        :param max_size: Número máximo de entradas en caché (LRU).
        """
        self._cache = OrderedDict()
        self.default_ttl = default_ttl
        self.max_size = max_size

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Almacena una respuesta en caché.
        :param key: Clave única.
        :param value: Valor a almacenar.
        :param ttl: Tiempo de vida en segundos (opcional).
        """
        expire_at = time.time() + (ttl if ttl is not None else self.default_ttl)
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = {"value": value, "expire_at": expire_at}
        if len(self._cache) > self.max_size:
            self._cache.popitem(last=False)  # Elimina el menos usado

    def get(self, key: str) -> Optional[Any]:
        """
        Recupera una respuesta de la caché si no ha expirado.
        :param key: Clave única.
        :return: Valor almacenado o None si no existe o expiró.
        """
        entry = self._cache.get(key)
        if not entry:
            return None
        if entry["expire_at"] < time.time():
            del self._cache[key]
            return None
        # Marcar como recientemente usado
        self._cache.move_to_end(key)
        return entry["value"]

    def invalidate(self, key: str):
        """
        Elimina una entrada de la caché.
        :param key: Clave única.
        """
        if key in self._cache:
            del self._cache[key]

    def clear(self):
        """
        Elimina todas las entradas de la caché.
        """
        self._cache.clear()

# Ejemplo de uso:
# cache = ResponseCache(default_ttl=600)
# cache.set("pregunta1", "respuesta frecuente")
# resp = cache.get("pregunta1")
# cache.invalidate("pregunta1")
