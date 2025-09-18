"""
test_base_plugin.py
Tests unitarios para el módulo BasePlugin de MeriBot.
Valida la interfaz abstracta y el comportamiento base de plugins.
"""

import pytest
from abc import ABC
from unittest.mock import Mock
from typing import Dict, Any

from meribot.core.plugins.base_plugin import BasePlugin


class ConcretePlugin(BasePlugin):
    """Implementación concreta de BasePlugin para tests."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.activated = False
        self.deactivated = False
        self.processed_queries = []
    
    def activate(self):
        """Implementación de activación."""
        self.activated = True
    
    def deactivate(self):
        """Implementación de desactivación."""
        self.deactivated = True
    
    def process(self, query: str, context: Dict[str, Any]) -> Any:
        """Implementación de procesamiento."""
        self.processed_queries.append((query, context))
        return f"Processed: {query}"


class PartialPlugin(BasePlugin):
    """Plugin parcialmente implementado para tests de abstracción."""
    
    def activate(self):
        """Solo implementa activate."""
        pass
    
    # Falta implementar deactivate y process


class TestBasePlugin:
    """Test suite para la clase BasePlugin."""

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_base_plugin_is_abstract(self):
        """Test que BasePlugin es una clase abstracta."""
        assert issubclass(BasePlugin, ABC)
        
        # Verificar que no se puede instanciar directamente
        with pytest.raises(TypeError):
            BasePlugin()

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_partial_implementation_fails(self):
        """Test que implementación parcial falla."""
        with pytest.raises(TypeError):
            PartialPlugin()

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_concrete_plugin_initialization_default(self):
        """Test de inicialización con configuración por defecto."""
        plugin = ConcretePlugin()
        
        assert plugin.config == {}
        assert plugin.activated is False
        assert plugin.deactivated is False
        assert plugin.processed_queries == []

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_concrete_plugin_initialization_with_config(self):
        """Test de inicialización con configuración personalizada."""
        config = {
            "setting1": "value1",
            "setting2": 42,
            "setting3": True
        }
        
        plugin = ConcretePlugin(config)
        
        assert plugin.config == config
        assert plugin.config["setting1"] == "value1"
        assert plugin.config["setting2"] == 42
        assert plugin.config["setting3"] is True

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_concrete_plugin_initialization_with_none_config(self):
        """Test de inicialización con configuración None."""
        plugin = ConcretePlugin(None)
        
        assert plugin.config == {}

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_activate_method_implementation(self):
        """Test de implementación del método activate."""
        plugin = ConcretePlugin()
        
        assert plugin.activated is False
        
        plugin.activate()
        
        assert plugin.activated is True

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_deactivate_method_implementation(self):
        """Test de implementación del método deactivate."""
        plugin = ConcretePlugin()
        
        assert plugin.deactivated is False
        
        plugin.deactivate()
        
        assert plugin.deactivated is True

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_process_method_implementation(self):
        """Test de implementación del método process."""
        plugin = ConcretePlugin()
        context = {"user_id": "test_user"}
        
        result = plugin.process("test query", context)
        
        assert result == "Processed: test query"
        assert len(plugin.processed_queries) == 1
        assert plugin.processed_queries[0] == ("test query", context)

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_process_method_multiple_calls(self):
        """Test de múltiples llamadas al método process."""
        plugin = ConcretePlugin()
        
        contexts = [
            {"user_id": "user1"},
            {"user_id": "user2"},
            {"session_id": "session1"}
        ]
        
        queries = ["query1", "query2", "query3"]
        
        results = []
        for i, (query, context) in enumerate(zip(queries, contexts)):
            result = plugin.process(query, context)
            results.append(result)
        
        assert len(results) == 3
        assert results[0] == "Processed: query1"
        assert results[1] == "Processed: query2"
        assert results[2] == "Processed: query3"
        
        assert len(plugin.processed_queries) == 3
        assert plugin.processed_queries[0] == ("query1", contexts[0])
        assert plugin.processed_queries[1] == ("query2", contexts[1])
        assert plugin.processed_queries[2] == ("query3", contexts[2])

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_abstract_methods_are_required(self):
        """Test que los métodos abstractos son requeridos."""
        # Verificar que BasePlugin tiene los métodos abstractos esperados
        abstract_methods = BasePlugin.__abstractmethods__
        
        expected_methods = {'activate', 'deactivate', 'process'}
        assert abstract_methods == expected_methods

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_config_immutability_not_enforced(self):
        """Test que la configuración no está protegida contra modificaciones."""
        config = {"mutable": "value"}
        plugin = ConcretePlugin(config)
        
        # La configuración debería ser modificable (no hay protección en BasePlugin)
        plugin.config["mutable"] = "changed"
        plugin.config["new_key"] = "new_value"
        
        assert plugin.config["mutable"] == "changed"
        assert plugin.config["new_key"] == "new_value"

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_config_reference_sharing(self):
        """Test que la configuración se comparte por referencia."""
        original_config = {"shared": "value"}
        plugin = ConcretePlugin(original_config)
        
        # Modificar la configuración original debería afectar el plugin
        original_config["shared"] = "modified"
        
        assert plugin.config["shared"] == "modified"

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_empty_config_handling(self):
        """Test de manejo de configuración vacía."""
        plugin = ConcretePlugin({})
        
        assert plugin.config == {}
        assert len(plugin.config) == 0

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_complex_config_handling(self):
        """Test de manejo de configuración compleja."""
        complex_config = {
            "string_setting": "value",
            "number_setting": 42,
            "boolean_setting": True,
            "list_setting": [1, 2, 3],
            "dict_setting": {"nested": "value"},
            "none_setting": None
        }
        
        plugin = ConcretePlugin(complex_config)
        
        assert plugin.config == complex_config
        assert plugin.config["string_setting"] == "value"
        assert plugin.config["number_setting"] == 42
        assert plugin.config["boolean_setting"] is True
        assert plugin.config["list_setting"] == [1, 2, 3]
        assert plugin.config["dict_setting"]["nested"] == "value"
        assert plugin.config["none_setting"] is None

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_plugin_state_independence(self):
        """Test que instancias de plugin son independientes."""
        config1 = {"instance": "1"}
        config2 = {"instance": "2"}
        
        plugin1 = ConcretePlugin(config1)
        plugin2 = ConcretePlugin(config2)
        
        # Activar solo uno
        plugin1.activate()
        
        assert plugin1.activated is True
        assert plugin2.activated is False
        
        # Procesar con cada uno
        plugin1.process("query1", {})
        plugin2.process("query2", {})
        
        assert len(plugin1.processed_queries) == 1
        assert len(plugin2.processed_queries) == 1
        assert plugin1.processed_queries[0][0] == "query1"
        assert plugin2.processed_queries[0][0] == "query2"

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_process_with_empty_query(self):
        """Test de procesamiento con query vacía."""
        plugin = ConcretePlugin()
        
        result = plugin.process("", {})
        
        assert result == "Processed: "
        assert plugin.processed_queries[0][0] == ""

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_process_with_empty_context(self):
        """Test de procesamiento con contexto vacío."""
        plugin = ConcretePlugin()
        
        result = plugin.process("test query", {})
        
        assert result == "Processed: test query"
        assert plugin.processed_queries[0][1] == {}

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_activate_deactivate_sequence(self):
        """Test de secuencia de activación y desactivación."""
        plugin = ConcretePlugin()
        
        # Estado inicial
        assert plugin.activated is False
        assert plugin.deactivated is False
        
        # Activar
        plugin.activate()
        assert plugin.activated is True
        assert plugin.deactivated is False
        
        # Desactivar
        plugin.deactivate()
        assert plugin.activated is True  # Permanece True (no se resetea)
        assert plugin.deactivated is True

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_multiple_activations(self):
        """Test de múltiples activaciones."""
        plugin = ConcretePlugin()
        
        # Múltiples activaciones no deberían causar problemas
        plugin.activate()
        plugin.activate()
        plugin.activate()
        
        assert plugin.activated is True

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_multiple_deactivations(self):
        """Test de múltiples desactivaciones."""
        plugin = ConcretePlugin()
        
        # Múltiples desactivaciones no deberían causar problemas
        plugin.deactivate()
        plugin.deactivate()
        plugin.deactivate()
        
        assert plugin.deactivated is True

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_base_plugin_inheritance_structure(self):
        """Test de estructura de herencia."""
        plugin = ConcretePlugin()
        
        # Verificar que hereda correctamente de BasePlugin
        assert isinstance(plugin, BasePlugin)
        assert isinstance(plugin, ABC)
        
        # Verificar que tiene los métodos requeridos
        assert hasattr(plugin, 'activate')
        assert hasattr(plugin, 'deactivate')
        assert hasattr(plugin, 'process')
        assert hasattr(plugin, 'config')
        
        # Verificar que los métodos son callable
        assert callable(plugin.activate)
        assert callable(plugin.deactivate)
        assert callable(plugin.process)


class AnotherConcretePlugin(BasePlugin):
    """Otra implementación de BasePlugin para tests adicionales."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.operations = []
    
    def activate(self):
        """Implementación alternativa de activación."""
        self.operations.append("activated")
    
    def deactivate(self):
        """Implementación alternativa de desactivación."""
        self.operations.append("deactivated")
    
    def process(self, query: str, context: Dict[str, Any]) -> Any:
        """Implementación alternativa de procesamiento."""
        self.operations.append(f"processed: {query}")
        return {"query": query, "context": context}


class TestBasePluginWithAlternativeImplementation:
    """Tests adicionales con implementación alternativa."""

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_alternative_implementation(self):
        """Test de implementación alternativa de BasePlugin."""
        plugin = AnotherConcretePlugin({"setting": "test"})
        
        assert plugin.config == {"setting": "test"}
        assert plugin.operations == []
        
        plugin.activate()
        assert "activated" in plugin.operations
        
        result = plugin.process("test", {"key": "value"})
        assert isinstance(result, dict)
        assert result["query"] == "test"
        assert result["context"] == {"key": "value"}
        assert "processed: test" in plugin.operations
        
        plugin.deactivate()
        assert "deactivated" in plugin.operations

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_different_implementations_isolation(self):
        """Test de aislamiento entre diferentes implementaciones."""
        plugin1 = ConcretePlugin()
        plugin2 = AnotherConcretePlugin()
        
        plugin1.activate()
        plugin2.activate()
        
        # Diferentes comportamientos
        result1 = plugin1.process("test", {})
        result2 = plugin2.process("test", {})
        
        assert isinstance(result1, str)
        assert isinstance(result2, dict)
        assert result1 == "Processed: test"
        assert result2["query"] == "test"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])