"""
test_plugin_manager.py
Tests unitarios para el módulo PluginManager de MeriBot.
Valida el registro, activación, desactivación y procesamiento de plugins.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from meribot.core.plugins.plugin_manager import PluginManager
from meribot.core.plugins.base_plugin import BasePlugin


class MockPlugin(BasePlugin):
    """Plugin de prueba para tests."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.is_active = False
        self.process_calls = []
    
    def activate(self):
        """Activar el plugin."""
        self.is_active = True
    
    def deactivate(self):
        """Desactivar el plugin."""
        self.is_active = False
    
    def process(self, query: str, context: Dict[str, Any]) -> Any:
        """Procesar query y retornar resultado."""
        self.process_calls.append((query, context))
        return f"Processed: {query}"


class FailingPlugin(BasePlugin):
    """Plugin que falla para tests de manejo de errores."""
    
    def activate(self):
        """Activación exitosa."""
        pass
    
    def deactivate(self):
        """Desactivación exitosa."""
        pass
    
    def process(self, query: str, context: Dict[str, Any]) -> Any:
        """Procesar que siempre falla."""
        raise Exception("Plugin processing failed")


class TestPluginManager:
    """Test suite para la clase PluginManager."""

    @pytest.fixture
    def manager(self):
        """Instancia de PluginManager para tests."""
        return PluginManager()

    @pytest.fixture
    def mock_plugin(self):
        """Plugin mock para tests."""
        return MockPlugin({"setting": "value"})

    @pytest.fixture
    def another_mock_plugin(self):
        """Segundo plugin mock para tests."""
        return MockPlugin({"another_setting": "another_value"})

    @pytest.fixture
    def failing_plugin(self):
        """Plugin que falla para tests."""
        return FailingPlugin()

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_plugin_manager_initialization(self, manager):
        """Test de inicialización del PluginManager."""
        assert isinstance(manager._plugins, dict)
        assert isinstance(manager._active_plugins, set)
        assert len(manager._plugins) == 0
        assert len(manager._active_plugins) == 0

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_register_plugin_success(self, manager, mock_plugin):
        """Test de registro exitoso de plugin."""
        manager.register("test_plugin", mock_plugin)
        
        assert "test_plugin" in manager._plugins
        assert manager._plugins["test_plugin"] is mock_plugin
        assert "test_plugin" not in manager._active_plugins  # No se activa automáticamente

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_register_duplicate_plugin_fails(self, manager, mock_plugin, another_mock_plugin):
        """Test que registrar plugin duplicado falla."""
        manager.register("test_plugin", mock_plugin)
        
        with pytest.raises(ValueError) as exc_info:
            manager.register("test_plugin", another_mock_plugin)
        
        assert "already registered" in str(exc_info.value)
        assert "test_plugin" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_activate_plugin_success(self, manager, mock_plugin):
        """Test de activación exitosa de plugin."""
        manager.register("test_plugin", mock_plugin)
        manager.activate("test_plugin")
        
        assert mock_plugin.is_active is True
        assert "test_plugin" in manager._active_plugins

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_activate_non_registered_plugin_fails(self, manager):
        """Test que activar plugin no registrado falla."""
        with pytest.raises(KeyError) as exc_info:
            manager.activate("non_existent_plugin")
        
        assert "not found" in str(exc_info.value)
        assert "non_existent_plugin" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_deactivate_plugin_success(self, manager, mock_plugin):
        """Test de desactivación exitosa de plugin."""
        manager.register("test_plugin", mock_plugin)
        manager.activate("test_plugin")
        
        assert "test_plugin" in manager._active_plugins
        
        manager.deactivate("test_plugin")
        
        assert mock_plugin.is_active is False
        assert "test_plugin" not in manager._active_plugins

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_deactivate_non_registered_plugin_fails(self, manager):
        """Test que desactivar plugin no registrado falla."""
        with pytest.raises(KeyError) as exc_info:
            manager.deactivate("non_existent_plugin")
        
        assert "not found" in str(exc_info.value)
        assert "non_existent_plugin" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_get_plugin_success(self, manager, mock_plugin):
        """Test de obtención exitosa de plugin."""
        manager.register("test_plugin", mock_plugin)
        
        retrieved_plugin = manager.get_plugin("test_plugin")
        
        assert retrieved_plugin is mock_plugin

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_get_plugin_non_existent_returns_none(self, manager):
        """Test que obtener plugin inexistente devuelve None."""
        result = manager.get_plugin("non_existent_plugin")
        assert result is None

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_list_plugins_empty(self, manager):
        """Test de listar plugins cuando no hay ninguno."""
        plugins = manager.list_plugins()
        assert plugins == []

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_list_plugins_with_registered_plugins(self, manager, mock_plugin, another_mock_plugin):
        """Test de listar plugins registrados."""
        manager.register("plugin1", mock_plugin)
        manager.register("plugin2", another_mock_plugin)
        
        plugins = manager.list_plugins()
        
        assert len(plugins) == 2
        assert "plugin1" in plugins
        assert "plugin2" in plugins

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_list_active_plugins_empty(self, manager):
        """Test de listar plugins activos cuando no hay ninguno."""
        active_plugins = manager.list_active_plugins()
        assert active_plugins == []

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_list_active_plugins_with_active_plugins(self, manager, mock_plugin, another_mock_plugin):
        """Test de listar plugins activos."""
        manager.register("plugin1", mock_plugin)
        manager.register("plugin2", another_mock_plugin)
        
        manager.activate("plugin1")
        
        active_plugins = manager.list_active_plugins()
        
        assert len(active_plugins) == 1
        assert "plugin1" in active_plugins
        assert "plugin2" not in active_plugins

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_process_with_active_plugins_no_active(self, manager):
        """Test de procesamiento sin plugins activos."""
        result = manager.process_with_active_plugins("test query", {"context": "test"})
        
        assert result == {}

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_process_with_active_plugins_success(self, manager, mock_plugin):
        """Test de procesamiento exitoso con plugins activos."""
        manager.register("test_plugin", mock_plugin)
        manager.activate("test_plugin")
        
        context = {"test_context": "value"}
        result = manager.process_with_active_plugins("test query", context)
        
        assert "test_plugin" in result
        assert result["test_plugin"] == "Processed: test query"
        
        # Verificar que se llamó al método process del plugin
        assert len(mock_plugin.process_calls) == 1
        assert mock_plugin.process_calls[0] == ("test query", context)

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_process_with_multiple_active_plugins(self, manager, mock_plugin, another_mock_plugin):
        """Test de procesamiento con múltiples plugins activos."""
        manager.register("plugin1", mock_plugin)
        manager.register("plugin2", another_mock_plugin)
        manager.activate("plugin1")
        manager.activate("plugin2")
        
        result = manager.process_with_active_plugins("test query", {})
        
        assert len(result) == 2
        assert "plugin1" in result
        assert "plugin2" in result
        assert result["plugin1"] == "Processed: test query"
        assert result["plugin2"] == "Processed: test query"

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_process_with_failing_plugin(self, manager, failing_plugin):
        """Test de procesamiento con plugin que falla."""
        manager.register("failing_plugin", failing_plugin)
        manager.activate("failing_plugin")
        
        result = manager.process_with_active_plugins("test query", {})
        
        assert "failing_plugin" in result
        assert "Error:" in result["failing_plugin"]
        assert "Plugin processing failed" in result["failing_plugin"]

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_process_mixed_success_and_failure(self, manager, mock_plugin, failing_plugin):
        """Test de procesamiento con plugins exitosos y fallidos."""
        manager.register("success_plugin", mock_plugin)
        manager.register("failing_plugin", failing_plugin)
        manager.activate("success_plugin")
        manager.activate("failing_plugin")
        
        result = manager.process_with_active_plugins("test query", {})
        
        assert len(result) == 2
        assert result["success_plugin"] == "Processed: test query"
        assert "Error:" in result["failing_plugin"]

    @pytest.mark.unit
    @pytest.mark.plugins
    @pytest.mark.asyncio
    async def test_run_pre_llm_plugins_returns_none(self, manager):
        """Test que run_pre_llm_plugins devuelve None por defecto."""
        result = await manager.run_pre_llm_plugins("message", {}, {})
        assert result is None

    @pytest.mark.unit
    @pytest.mark.plugins
    @pytest.mark.asyncio
    async def test_run_post_llm_plugins_returns_response(self, manager):
        """Test que run_post_llm_plugins devuelve la respuesta sin modificar."""
        original_response = "Original response"
        result = await manager.run_post_llm_plugins(original_response, {}, {})
        assert result == original_response

    @pytest.mark.unit
    @pytest.mark.plugins
    @patch('meribot.core.plugins.plugin_manager.get_logger')
    def test_logging_register_plugin(self, mock_get_logger, manager, mock_plugin):
        """Test de logging al registrar plugin."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        manager.logger = mock_logger
        
        manager.register("test_plugin", mock_plugin)
        
        mock_logger.info.assert_called()
        call_args = mock_logger.info.call_args[0][0]
        assert "Plugin registrado" in call_args
        assert "test_plugin" in call_args

    @pytest.mark.unit
    @pytest.mark.plugins
    @patch('meribot.core.plugins.plugin_manager.get_logger')
    def test_logging_register_duplicate_plugin(self, mock_get_logger, manager, mock_plugin, another_mock_plugin):
        """Test de logging al intentar registrar plugin duplicado."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        manager.logger = mock_logger
        
        manager.register("test_plugin", mock_plugin)
        
        try:
            manager.register("test_plugin", another_mock_plugin)
        except ValueError:
            pass
        
        mock_logger.warning.assert_called()
        call_args = mock_logger.warning.call_args[0][0]
        assert "plugin duplicado" in call_args

    @pytest.mark.unit
    @pytest.mark.plugins
    @patch('meribot.core.plugins.plugin_manager.get_logger')
    def test_logging_activate_plugin(self, mock_get_logger, manager, mock_plugin):
        """Test de logging al activar plugin."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        manager.logger = mock_logger
        
        manager.register("test_plugin", mock_plugin)
        manager.activate("test_plugin")
        
        # Verificar que se hizo log de activación
        info_calls = mock_logger.info.call_args_list
        assert any("Plugin activado" in str(call) for call in info_calls)

    @pytest.mark.unit
    @pytest.mark.plugins
    @patch('meribot.core.plugins.plugin_manager.get_logger')
    def test_logging_activate_non_existent_plugin(self, mock_get_logger, manager):
        """Test de logging al intentar activar plugin inexistente."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        manager.logger = mock_logger
        
        try:
            manager.activate("non_existent")
        except KeyError:
            pass
        
        mock_logger.error.assert_called()
        call_args = mock_logger.error.call_args[0][0]
        assert "plugin no registrado" in call_args

    @pytest.mark.unit
    @pytest.mark.plugins
    @patch('meribot.core.plugins.plugin_manager.get_logger')
    def test_logging_deactivate_plugin(self, mock_get_logger, manager, mock_plugin):
        """Test de logging al desactivar plugin."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        manager.logger = mock_logger
        
        manager.register("test_plugin", mock_plugin)
        manager.activate("test_plugin")
        mock_logger.reset_mock()  # Limpiar logs anteriores
        
        manager.deactivate("test_plugin")
        
        mock_logger.info.assert_called()
        call_args = mock_logger.info.call_args[0][0]
        assert "Plugin desactivado" in call_args

    @pytest.mark.unit
    @pytest.mark.plugins
    @patch('meribot.core.plugins.plugin_manager.get_logger')
    def test_logging_process_with_plugins(self, mock_get_logger, manager, mock_plugin):
        """Test de logging durante procesamiento."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        manager.logger = mock_logger
        
        manager.register("test_plugin", mock_plugin)
        manager.activate("test_plugin")
        
        manager.process_with_active_plugins("test query", {})
        
        # Verificar logs de procesamiento
        info_calls = mock_logger.info.call_args_list
        assert any("Procesando query con plugins activos" in str(call) for call in info_calls)
        assert any("procesó correctamente" in str(call) for call in info_calls)

    @pytest.mark.unit
    @pytest.mark.plugins
    @patch('meribot.core.plugins.plugin_manager.get_logger')
    def test_logging_process_with_failing_plugin(self, mock_get_logger, manager, failing_plugin):
        """Test de logging cuando falla procesamiento de plugin."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        manager.logger = mock_logger
        
        manager.register("failing_plugin", failing_plugin)
        manager.activate("failing_plugin")
        
        manager.process_with_active_plugins("test query", {})
        
        # Verificar log de error
        mock_logger.error.assert_called()
        error_call = mock_logger.error.call_args[0][0]
        assert "Error en plugin" in error_call
        assert "failing_plugin" in error_call

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_plugin_lifecycle_complete(self, manager, mock_plugin):
        """Test del ciclo de vida completo de un plugin."""
        # 1. Registrar
        manager.register("lifecycle_plugin", mock_plugin)
        assert "lifecycle_plugin" in manager.list_plugins()
        assert "lifecycle_plugin" not in manager.list_active_plugins()
        
        # 2. Activar
        manager.activate("lifecycle_plugin")
        assert mock_plugin.is_active is True
        assert "lifecycle_plugin" in manager.list_active_plugins()
        
        # 3. Procesar
        result = manager.process_with_active_plugins("test", {})
        assert "lifecycle_plugin" in result
        
        # 4. Desactivar
        manager.deactivate("lifecycle_plugin")
        assert mock_plugin.is_active is False
        assert "lifecycle_plugin" not in manager.list_active_plugins()
        assert "lifecycle_plugin" in manager.list_plugins()  # Sigue registrado

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_plugin_isolation(self, manager, mock_plugin, another_mock_plugin):
        """Test de aislamiento entre plugins."""
        manager.register("plugin1", mock_plugin)
        manager.register("plugin2", another_mock_plugin)
        
        # Activar solo uno
        manager.activate("plugin1")
        
        # Procesar
        result = manager.process_with_active_plugins("test", {})
        
        # Solo el plugin activo debería procesar
        assert "plugin1" in result
        assert "plugin2" not in result
        assert len(mock_plugin.process_calls) == 1
        assert len(another_mock_plugin.process_calls) == 0

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_deactivate_removes_from_active_set(self, manager, mock_plugin):
        """Test que desactivar remueve del conjunto de activos."""
        manager.register("test_plugin", mock_plugin)
        manager.activate("test_plugin")
        
        assert len(manager._active_plugins) == 1
        
        manager.deactivate("test_plugin")
        
        assert len(manager._active_plugins) == 0
        assert "test_plugin" not in manager._active_plugins

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_plugin_context_passing(self, manager, mock_plugin):
        """Test que el contexto se pasa correctamente a los plugins."""
        manager.register("context_plugin", mock_plugin)
        manager.activate("context_plugin")
        
        test_context = {
            "user_id": "test_user",
            "session_id": "test_session",
            "metadata": {"key": "value"}
        }
        
        manager.process_with_active_plugins("test query", test_context)
        
        # Verificar que el contexto se pasó correctamente
        assert len(mock_plugin.process_calls) == 1
        passed_query, passed_context = mock_plugin.process_calls[0]
        assert passed_query == "test query"
        assert passed_context == test_context

    @pytest.mark.unit
    @pytest.mark.plugins
    def test_empty_query_processing(self, manager, mock_plugin):
        """Test de procesamiento con query vacía."""
        manager.register("test_plugin", mock_plugin)
        manager.activate("test_plugin")
        
        result = manager.process_with_active_plugins("", {})
        
        assert "test_plugin" in result
        assert result["test_plugin"] == "Processed: "


if __name__ == "__main__":
    pytest.main([__file__, "-v"])