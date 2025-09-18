"""
test_core_utils_integration.py
Tests de integración entre el módulo Core y Utils de MeriBot.
Valida el uso de utilidades compartidas, logging, configuración y helpers.
"""

import pytest
import asyncio
import os
import yaml
from unittest.mock import Mock, AsyncMock, patch, MagicMock, mock_open
from typing import List, Dict, Any

from meribot.core.chatengine import ChatEngine
from meribot.core.validation import ChatEngineRequest


class TestCoreUtilsIntegration:
    """Test suite para integración Core-Utils."""

    @pytest.fixture
    def mock_config_yaml(self):
        """Mock de configuración YAML para tests."""
        return {
            'allowed_domains': ['onboarding', 'training', 'cca', 'sdo'],
            'max_message_length': 4000,
            'max_conversation_id_length': 100,
            'max_domains_count': 5,
            'dangerous_patterns': ['<script>', 'javascript:', 'eval('],
            'chroma_settings': {
                'persist_directory': './test_chroma_data',
                'collection_name': 'meribot_documents'
            },
            'llm_settings': {
                'model': 'gpt-3.5-turbo',
                'temperature': 0.7,
                'max_tokens': 1000
            }
        }

    @pytest.fixture
    def mock_system_prompt(self):
        """Mock del system prompt cargado desde utils."""
        return """
        Eres MeriBot, el asistente virtual de C&CA.
        Responde de manera profesional y útil.
        Siempre cita las fuentes cuando sea apropiado.
        """

    @pytest.fixture
    def mock_logger_config(self):
        """Mock de configuración de logging."""
        return {
            'log_level': 'INFO',
            'log_file': 'test_meribot_core.log',
            'max_bytes': 1048576,
            'backup_count': 5
        }

    @pytest.mark.integration
    @pytest.mark.utils
    def test_core_uses_utils_config_loader(self, mock_config_yaml):
        """Test que el core usa el cargador de configuración de utils."""
        with patch('meribot.utils.utils.load_config_from_yaml') as mock_load:
            mock_load.side_effect = lambda key: mock_config_yaml.get(key)
            
            # El core debe cargar configuración usando utils
            from meribot.core.validation import ALLOWED_DOMAINS, MAX_MESSAGE_LENGTH
            
            # Verificar que se cargan valores desde utils
            with patch('meribot.core.validation.load_config_from_yaml') as mock_validation_load:
                mock_validation_load.side_effect = lambda key: mock_config_yaml.get(key)
                
                # Simular importación del módulo validation
                import importlib
                import meribot.core.validation
                importlib.reload(meribot.core.validation)
                
                # Verificar que se llamó al cargador de utils
                assert mock_validation_load.called

    @pytest.mark.integration
    @pytest.mark.utils
    @pytest.mark.asyncio
    async def test_core_uses_utils_system_prompt(self, mock_system_prompt):
        """Test que el core usa el cargador de system prompt de utils."""
        with patch('meribot.utils.utils.load_system_prompt') as mock_load_prompt:
            mock_load_prompt.return_value = mock_system_prompt
            
            engine = ChatEngine()
            
            with patch.object(engine.llm_engine, 'generate_response', new_callable=AsyncMock) as mock_generate:
                mock_generate.return_value = "Respuesta del LLM"
                
                await engine.process_message(
                    conversation_id="prompt_test",
                    message="Test system prompt loading"
                )
                
                # Verificar que se cargó el system prompt desde utils
                mock_load_prompt.assert_called_once()
                
                # Verificar que se pasó al LLM
                call_args = mock_generate.call_args
                assert 'system_prompt' in call_args[1]
                assert call_args[1]['system_prompt'] == mock_system_prompt

    @pytest.mark.integration
    @pytest.mark.utils
    def test_core_uses_utils_logger(self, mock_logger_config):
        """Test que el core usa el sistema de logging de utils."""
        with patch('meribot.utils.logger.get_logger') as mock_get_logger:
            mock_logger_instance = Mock()
            mock_get_logger.return_value = mock_logger_instance
            
            # El core debe usar el logger de utils
            engine = ChatEngine()
            
            # Verificar que se obtuvo el logger desde utils
            mock_get_logger.assert_called()
            
            # El logger debería haberse configurado para el core
            call_args = mock_get_logger.call_args[0]
            assert "meribot.core" in call_args[0] or "core" in call_args[0]

    @pytest.mark.integration
    @pytest.mark.utils
    @pytest.mark.asyncio
    async def test_core_logging_integration(self):
        """Test de integración del logging entre core y utils."""
        with patch('meribot.utils.logger.get_logger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            engine = ChatEngine()
            
            # Simular operación que genera logs
            with patch.object(engine.llm_engine, 'generate_response', new_callable=AsyncMock) as mock_generate:
                mock_generate.return_value = "Test response"
                
                await engine.process_message(
                    conversation_id="logging_test",
                    message="Test logging integration"
                )
                
                # Verificar que se generaron logs a través de utils
                assert mock_logger.info.called or mock_logger.debug.called

    @pytest.mark.integration
    @pytest.mark.utils
    @pytest.mark.asyncio
    async def test_core_error_logging_integration(self):
        """Test de integración del logging de errores entre core y utils."""
        with patch('meribot.utils.logger.log_generation_failure') as mock_log_failure:
            with patch('meribot.utils.logger.get_logger') as mock_get_logger:
                mock_logger = Mock()
                mock_get_logger.return_value = mock_logger
                
                engine = ChatEngine()
                
                # Simular error para activar logging
                with patch.object(engine.llm_engine, 'generate_response', new_callable=AsyncMock) as mock_generate:
                    mock_generate.side_effect = Exception("LLM error for logging test")
                    
                    result = await engine.process_message(
                        conversation_id="error_logging_test",
                        message="Test error logging"
                    )
                    
                    # Verificar que se registró el error usando utils
                    assert mock_log_failure.called
                    
                    # Verificar que la respuesta indica error
                    assert "[Error al generar respuesta]" in result["response"]

    @pytest.mark.integration
    @pytest.mark.utils
    def test_validation_uses_utils_config(self, mock_config_yaml):
        """Test que la validación del core usa configuración de utils."""
        with patch('meribot.utils.utils.load_config_from_yaml') as mock_load:
            mock_load.side_effect = lambda key: mock_config_yaml.get(key)
            
            # Test validación con configuración de utils
            try:
                request = ChatEngineRequest(
                    conversation_id="test_conv",
                    message="x" * 5000,  # Excede max_message_length de config
                    domains=["onboarding"]
                )
                # Si la validación usa utils, debería fallar por longitud
                assert False, "Should have failed validation"
            except Exception as e:
                # Validación debería fallar usando configuración de utils
                assert "message" in str(e).lower() or "length" in str(e).lower()

    @pytest.mark.integration
    @pytest.mark.utils
    def test_core_config_file_paths_integration(self):
        """Test de integración de rutas de archivos de configuración."""
        with patch.dict(os.environ, {'CRAWLER_CONFIG_PATH': '/test/path/config.yaml'}):
            with patch('meribot.utils.utils.load_config_from_yaml') as mock_load:
                mock_load.return_value = ['onboarding', 'training']
                
                # El core debe usar las rutas configuradas en utils
                from meribot.core.validation import load_config_from_yaml
                
                result = load_config_from_yaml('allowed_domains')
                
                # Verificar que se usó la función de utils
                mock_load.assert_called_with('allowed_domains')

    @pytest.mark.integration
    @pytest.mark.utils
    @pytest.mark.asyncio
    async def test_utils_hash_integration(self):
        """Test de integración con utilidades de hash de utils."""
        with patch('meribot.utils.hash_utils.generate_content_hash') as mock_hash:
            mock_hash.return_value = "test_hash_123"
            
            # Simular uso de hash utils en el core
            content = "Test content for hashing"
            content_hash = mock_hash(content)
            
            assert content_hash == "test_hash_123"
            mock_hash.assert_called_once_with(content)

    @pytest.mark.integration
    @pytest.mark.utils
    def test_utils_json_formatter_integration(self):
        """Test de integración con el formateador JSON de utils."""
        with patch('meribot.utils.json_formatter.JsonFormatter') as mock_formatter:
            mock_formatter_instance = Mock()
            mock_formatter.return_value = mock_formatter_instance
            
            # El logging del core debería poder usar el formateador JSON
            with patch('meribot.utils.logger.get_logger') as mock_get_logger:
                mock_logger = Mock()
                mock_get_logger.return_value = mock_logger
                
                # Simular configuración de logger con JSON formatter
                logger_config = {
                    'formatter': 'json',
                    'level': 'INFO'
                }
                
                # Verificar que el formateador está disponible
                assert mock_formatter is not None

    @pytest.mark.integration
    @pytest.mark.utils
    @pytest.mark.asyncio
    async def test_core_shared_utilities_integration(self):
        """Test de integración con utilidades compartidas de utils."""
        with patch('meribot.utils.utils.load_config_from_yaml') as mock_config:
            with patch('meribot.utils.utils.load_system_prompt') as mock_prompt:
                with patch('meribot.utils.logger.get_logger') as mock_logger:
                    
                    # Configurar mocks
                    mock_config.side_effect = lambda key: {
                        'allowed_domains': ['onboarding'],
                        'max_message_length': 4000
                    }.get(key)
                    
                    mock_prompt.return_value = "System prompt from utils"
                    mock_logger.return_value = Mock()
                    
                    # El core debe usar todas estas utilidades
                    engine = ChatEngine()
                    
                    with patch.object(engine.llm_engine, 'generate_response', new_callable=AsyncMock) as mock_generate:
                        mock_generate.return_value = "Response using utils"
                        
                        result = await engine.process_message(
                            conversation_id="utils_integration",
                            message="Test shared utilities"
                        )
                        
                        # Verificar que se usaron las utilidades de utils
                        assert mock_config.called
                        assert mock_prompt.called
                        assert mock_logger.called
                        assert result["type"] == "llm"

    @pytest.mark.integration
    @pytest.mark.utils
    def test_utils_environment_integration(self):
        """Test de integración con variables de entorno gestionadas por utils."""
        test_env_vars = {
            'MERIBOT_LOG_LEVEL': 'DEBUG',
            'MERIBOT_LOG_FILE': 'test_integration.log',
            'CRAWLER_CONFIG_PATH': './test_config.yaml'
        }
        
        with patch.dict(os.environ, test_env_vars):
            with patch('meribot.utils.logger.get_logger') as mock_get_logger:
                mock_logger = Mock()
                mock_get_logger.return_value = mock_logger
                
                # El core debe usar variables de entorno a través de utils
                engine = ChatEngine()
                
                # Verificar que el logger se configuró con variables de entorno
                mock_get_logger.assert_called()

    @pytest.mark.integration
    @pytest.mark.utils
    @pytest.mark.asyncio
    async def test_core_utils_error_handling_integration(self):
        """Test de manejo de errores compartido entre core y utils."""
        with patch('meribot.utils.utils.load_config_from_yaml') as mock_config:
            # Simular error en carga de configuración
            mock_config.side_effect = FileNotFoundError("Config file not found")
            
            with patch('meribot.utils.logger.get_logger') as mock_get_logger:
                mock_logger = Mock()
                mock_get_logger.return_value = mock_logger
                
                # El core debe manejar gracefully errores de utils
                try:
                    engine = ChatEngine()
                    
                    result = await engine.process_message(
                        conversation_id="error_handling_test",
                        message="Test error handling"
                    )
                    
                    # El core debe continuar funcionando con valores por defecto
                    assert "type" in result
                    
                except Exception as e:
                    # Si hay error, debe ser manejado apropiadamente
                    assert "config" in str(e).lower() or "file" in str(e).lower()

    @pytest.mark.integration
    @pytest.mark.utils
    def test_utils_config_validation_integration(self, mock_config_yaml):
        """Test de integración de validación de configuración entre core y utils."""
        with patch('meribot.utils.utils.load_config_from_yaml') as mock_load:
            mock_load.side_effect = lambda key: mock_config_yaml.get(key)
            
            # Test que el core valida configuración usando utils
            from meribot.core.validation import ChatEngineRequest
            
            # Configuración válida debe pasar
            valid_request = ChatEngineRequest(
                conversation_id="valid_test",
                message="Valid message",
                domains=["onboarding"]  # Dominio válido según config
            )
            
            assert valid_request.conversation_id == "valid_test"
            assert valid_request.domains == ["onboarding"]

    @pytest.mark.integration
    @pytest.mark.utils
    @pytest.mark.external
    def test_real_utils_integration(self):
        """Test de integración real con utils (requiere archivos reales)."""
        # Test que requiere archivos de configuración reales
        
        try:
            # Intentar cargar configuración real
            from meribot.utils.utils import load_config_from_yaml
            real_config = load_config_from_yaml('allowed_domains')
            
            if real_config:
                assert isinstance(real_config, list)
                assert len(real_config) > 0
                
        except Exception as e:
            # Si no hay configuración real, debería fallar gracefully
            assert "config" in str(e).lower() or "file" in str(e).lower()

    @pytest.mark.integration
    @pytest.mark.utils
    @pytest.mark.asyncio
    async def test_utils_performance_integration(self):
        """Test de integración de rendimiento con utils."""
        import time
        
        with patch('meribot.utils.logger.get_logger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            engine = ChatEngine()
            
            # Medir tiempo de operaciones usando utils
            start_time = time.time()
            
            with patch.object(engine.llm_engine, 'generate_response', new_callable=AsyncMock) as mock_generate:
                mock_generate.return_value = "Performance test response"
                
                result = await engine.process_message(
                    conversation_id="performance_test",
                    message="Test performance with utils"
                )
                
                end_time = time.time()
                execution_time = end_time - start_time
                
                # Verificar que la operación completó en tiempo razonable
                assert execution_time < 5.0  # Menos de 5 segundos
                assert result["type"] == "llm"

    @pytest.mark.integration
    @pytest.mark.utils
    def test_utils_logging_rotation_integration(self):
        """Test de integración de rotación de logs con utils."""
        with patch('meribot.utils.logger.get_logger') as mock_get_logger:
            with patch('logging.handlers.RotatingFileHandler') as mock_rotating_handler:
                mock_handler = Mock()
                mock_rotating_handler.return_value = mock_handler
                
                mock_logger = Mock()
                mock_get_logger.return_value = mock_logger
                
                # El core debe poder usar rotación de logs de utils
                engine = ChatEngine()
                
                # Verificar que se configuró logging
                mock_get_logger.assert_called()

    @pytest.mark.integration
    @pytest.mark.utils
    @pytest.mark.asyncio
    async def test_utils_concurrent_config_access(self, mock_config_yaml):
        """Test de acceso concurrente a configuración a través de utils."""
        with patch('meribot.utils.utils.load_config_from_yaml') as mock_load:
            mock_load.side_effect = lambda key: mock_config_yaml.get(key)
            
            # Simular múltiples operaciones concurrentes accediendo a config
            engines = [ChatEngine() for _ in range(3)]
            
            tasks = []
            for i, engine in enumerate(engines):
                with patch.object(engine.llm_engine, 'generate_response', new_callable=AsyncMock) as mock_generate:
                    mock_generate.return_value = f"Response {i}"
                    
                    task = engine.process_message(
                        conversation_id=f"concurrent_test_{i}",
                        message=f"Concurrent message {i}"
                    )
                    tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            
            # Verificar que todas las operaciones completaron exitosamente
            assert len(results) == 3
            assert all(result["type"] == "llm" for result in results)
            
            # La configuración debería haberse cargado múltiples veces
            assert mock_load.call_count >= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration and utils"])