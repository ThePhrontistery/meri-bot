"""
Tests unitarios para el módulo config.py del crawler.
Valida carga de configuración YAML, validación, variables de entorno y manejo de errores.
"""

import pytest
import os
import tempfile
import yaml
from unittest.mock import patch, mock_open
from pydantic import ValidationError

from meribot.crawler.config import (
    CrawlerConfig,
    ConfigError,
    load_yaml_config,
    override_with_env,
    validate_config,
    get_config
)


class TestCrawlerConfig:
    """Tests para el modelo Pydantic CrawlerConfig."""
    
    def test_crawler_config_valid_data(self):
        """Test que CrawlerConfig acepta datos válidos."""
        valid_config = {
            "seeds": ["https://example.com"],
            "allowed_domains": ["example.com"],
            "user_agent": "TestBot/1.0",
            "delay": 1.0,
            "output_dir": "./data",
            "log_level": "INFO",
            "chroma_path": "./chroma",
            "embedding_model": "text-embedding-ada-002"
        }
        
        config = CrawlerConfig(**valid_config)
        assert config.seeds == ["https://example.com"]
        assert config.allowed_domains == ["example.com"]
        assert config.user_agent == "TestBot/1.0"
        assert config.delay == 1.0
        assert config.max_depth == 3  # Default value
        assert config.file_types == ["html", "pdf", "docx", "xlsx"]  # Default value
    
    def test_crawler_config_with_optional_fields(self):
        """Test que CrawlerConfig maneja campos opcionales correctamente."""
        config_data = {
            "seeds": ["https://example.com"],
            "allowed_domains": ["example.com"],
            "user_agent": "TestBot/1.0",
            "delay": 1.0,
            "output_dir": "./data",
            "log_level": "INFO",
            "chroma_path": "./chroma",
            "embedding_model": "text-embedding-ada-002",
            "max_depth": 5,
            "file_types": ["html", "pdf"]
        }
        
        config = CrawlerConfig(**config_data)
        assert config.max_depth == 5
        assert config.file_types == ["html", "pdf"]
    
    def test_crawler_config_missing_required_fields(self):
        """Test que CrawlerConfig falla con campos requeridos faltantes."""
        incomplete_config = {
            "seeds": ["https://example.com"],
            "allowed_domains": ["example.com"],
            # Faltan campos requeridos
        }
        
        with pytest.raises(ValidationError) as exc_info:
            CrawlerConfig(**incomplete_config)
        
        error = exc_info.value
        assert "user_agent" in str(error)
        assert "delay" in str(error)
        assert "output_dir" in str(error)
    
    def test_crawler_config_invalid_types(self):
        """Test que CrawlerConfig falla con tipos de datos incorrectos."""
        invalid_config = {
            "seeds": "not_a_list",  # Debería ser lista
            "allowed_domains": ["example.com"],
            "user_agent": "TestBot/1.0",
            "delay": "not_a_number",  # Debería ser float
            "output_dir": "./data",
            "log_level": "INFO",
            "chroma_path": "./chroma",
            "embedding_model": "text-embedding-ada-002"
        }
        
        with pytest.raises(ValidationError):
            CrawlerConfig(**invalid_config)
    
    def test_crawler_config_forbids_extra_fields(self):
        """Test que CrawlerConfig rechaza campos extra."""
        config_with_extra = {
            "seeds": ["https://example.com"],
            "allowed_domains": ["example.com"],
            "user_agent": "TestBot/1.0",
            "delay": 1.0,
            "output_dir": "./data",
            "log_level": "INFO",
            "chroma_path": "./chroma",
            "embedding_model": "text-embedding-ada-002",
            "extra_field": "not_allowed"  # Campo extra no permitido
        }
        
        with pytest.raises(ValidationError) as exc_info:
            CrawlerConfig(**config_with_extra)
        
        assert "extra_field" in str(exc_info.value)


class TestLoadYamlConfig:
    """Tests para la función load_yaml_config."""
    
    def test_load_yaml_config_valid_file(self):
        """Test carga exitosa de archivo YAML válido."""
        yaml_content = """
        seeds:
          - https://example.com
        allowed_domains:
          - example.com
        user_agent: TestBot/1.0
        delay: 1.0
        output_dir: ./data
        log_level: INFO
        chroma_path: ./chroma
        embedding_model: text-embedding-ada-002
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_path = f.name
        
        try:
            config = load_yaml_config(temp_path)
            assert config["seeds"] == ["https://example.com"]
            assert config["allowed_domains"] == ["example.com"]
            assert config["user_agent"] == "TestBot/1.0"
            assert config["delay"] == 1.0
        finally:
            os.unlink(temp_path)
    
    def test_load_yaml_config_file_not_found(self):
        """Test error cuando el archivo YAML no existe."""
        with pytest.raises(FileNotFoundError):
            load_yaml_config("nonexistent_file.yaml")
    
    def test_load_yaml_config_invalid_yaml(self):
        """Test error con YAML inválido."""
        invalid_yaml = """
        seeds:
          - https://example.com
        invalid_yaml: [unclosed_bracket
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(invalid_yaml)
            temp_path = f.name
        
        try:
            with pytest.raises(yaml.YAMLError):
                load_yaml_config(temp_path)
        finally:
            os.unlink(temp_path)
    
    @patch("builtins.open", mock_open(read_data=""))
    def test_load_yaml_config_empty_file(self):
        """Test manejo de archivo YAML vacío."""
        config = load_yaml_config("empty.yaml")
        assert config is None


class TestOverrideWithEnv:
    """Tests para la función override_with_env."""
    
    def test_override_with_env_no_overrides(self):
        """Test que la configuración permanece igual sin variables de entorno."""
        original_config = {
            "delay": 1.0,
            "user_agent": "TestBot/1.0",
            "log_level": "INFO"
        }
        
        result = override_with_env(original_config.copy())
        assert result == original_config
    
    @patch.dict(os.environ, {"CRAWLER_DELAY": "2.5"})
    def test_override_with_env_float_conversion(self):
        """Test conversión de variable de entorno a float."""
        config = {"delay": 1.0}
        result = override_with_env(config)
        assert result["delay"] == 2.5
        assert isinstance(result["delay"], float)
    
    @patch.dict(os.environ, {"CRAWLER_MAX_DEPTH": "5"})
    def test_override_with_env_int_conversion(self):
        """Test conversión de variable de entorno a int."""
        config = {"max_depth": 3}
        result = override_with_env(config)
        assert result["max_depth"] == 5
        assert isinstance(result["max_depth"], int)
    
    @patch.dict(os.environ, {"CRAWLER_ALLOWED_DOMAINS": "example.com,test.com"})
    def test_override_with_env_list_conversion(self):
        """Test conversión de variable de entorno a lista."""
        config = {"allowed_domains": ["original.com"]}
        result = override_with_env(config)
        assert result["allowed_domains"] == ["example.com", "test.com"]
        assert isinstance(result["allowed_domains"], list)
    
    @patch.dict(os.environ, {"CRAWLER_USER_AGENT": "EnvBot/2.0"})
    def test_override_with_env_string_override(self):
        """Test override de string desde variable de entorno."""
        config = {"user_agent": "OriginalBot/1.0"}
        result = override_with_env(config)
        assert result["user_agent"] == "EnvBot/2.0"
    
    @patch.dict(os.environ, {
        "CRAWLER_DELAY": "3.0",
        "CRAWLER_LOG_LEVEL": "DEBUG",
        "CRAWLER_MAX_DEPTH": "10"
    })
    def test_override_with_env_multiple_overrides(self):
        """Test múltiples overrides desde variables de entorno."""
        config = {
            "delay": 1.0,
            "log_level": "INFO",
            "max_depth": 3,
            "user_agent": "TestBot/1.0"  # No override
        }
        
        result = override_with_env(config)
        assert result["delay"] == 3.0
        assert result["log_level"] == "DEBUG"
        assert result["max_depth"] == 10
        assert result["user_agent"] == "TestBot/1.0"  # Sin cambios


class TestValidateConfig:
    """Tests para la función validate_config."""
    
    def test_validate_config_valid_configuration(self):
        """Test validación exitosa de configuración válida."""
        valid_config = {
            "seeds": ["https://example.com"],
            "allowed_domains": ["example.com"],
            "user_agent": "TestBot/1.0",
            "delay": 1.0,
            "output_dir": "./data",
            "log_level": "INFO",
            "chroma_path": "./chroma",
            "embedding_model": "text-embedding-ada-002"
        }
        
        # No debería lanzar excepción
        validate_config(valid_config)
    
    def test_validate_config_missing_required_fields(self):
        """Test error de validación con campos requeridos faltantes."""
        invalid_config = {
            "seeds": ["https://example.com"],
            "allowed_domains": ["example.com"],
            # Faltan campos requeridos
        }
        
        with pytest.raises(ConfigError) as exc_info:
            validate_config(invalid_config)
        
        error_message = str(exc_info.value)
        assert "Error de validación en la configuración" in error_message
        assert "user_agent" in error_message
    
    def test_validate_config_invalid_types(self):
        """Test error de validación con tipos incorrectos."""
        invalid_config = {
            "seeds": "not_a_list",
            "allowed_domains": ["example.com"],
            "user_agent": "TestBot/1.0",
            "delay": 1.0,
            "output_dir": "./data",
            "log_level": "INFO",
            "chroma_path": "./chroma",
            "embedding_model": "text-embedding-ada-002"
        }
        
        with pytest.raises(ConfigError) as exc_info:
            validate_config(invalid_config)
        
        error_message = str(exc_info.value)
        assert "Error de validación en la configuración" in error_message


class TestGetConfig:
    """Tests para la función get_config."""
    
    @patch('meribot.crawler.config.load_yaml_config')
    @patch('meribot.crawler.config.override_with_env')
    @patch('meribot.crawler.config.validate_config')
    def test_get_config_success(self, mock_validate, mock_override, mock_load):
        """Test flujo exitoso de get_config."""
        # Configurar mocks
        yaml_config = {
            "seeds": ["https://example.com"],
            "allowed_domains": ["example.com"],
            "user_agent": "TestBot/1.0",
            "delay": 1.0,
            "output_dir": "./data",
            "log_level": "INFO",
            "chroma_path": "./chroma",
            "embedding_model": "text-embedding-ada-002"
        }
        
        override_config = yaml_config.copy()
        override_config["delay"] = 2.0  # Simulando override
        
        mock_load.return_value = yaml_config
        mock_override.return_value = override_config
        mock_validate.return_value = None  # Validación exitosa
        
        # Ejecutar
        result = get_config()
        
        # Verificar
        assert result == override_config
        mock_load.assert_called_once()
        mock_override.assert_called_once_with(yaml_config)
        mock_validate.assert_called_once_with(override_config)
    
    @patch('meribot.crawler.config.load_yaml_config')
    def test_get_config_yaml_load_error(self, mock_load):
        """Test error en carga de YAML."""
        mock_load.side_effect = FileNotFoundError("Config file not found")
        
        with pytest.raises(FileNotFoundError):
            get_config()
    
    @patch('meribot.crawler.config.load_yaml_config')
    @patch('meribot.crawler.config.override_with_env')
    @patch('meribot.crawler.config.validate_config')
    def test_get_config_validation_error(self, mock_validate, mock_override, mock_load):
        """Test error en validación de configuración."""
        mock_load.return_value = {"incomplete": "config"}
        mock_override.return_value = {"incomplete": "config"}
        mock_validate.side_effect = ConfigError("Invalid configuration")
        
        with pytest.raises(ConfigError):
            get_config()
    
    @patch.dict(os.environ, {"CRAWLER_CONFIG_YAML": "/custom/path/config.yaml"})
    @patch('meribot.crawler.config.load_yaml_config')
    @patch('meribot.crawler.config.override_with_env')
    @patch('meribot.crawler.config.validate_config')
    def test_get_config_custom_path(self, mock_validate, mock_override, mock_load):
        """Test uso de path personalizado desde variable de entorno."""
        valid_config = {
            "seeds": ["https://example.com"],
            "allowed_domains": ["example.com"],
            "user_agent": "TestBot/1.0",
            "delay": 1.0,
            "output_dir": "./data",
            "log_level": "INFO",
            "chroma_path": "./chroma",
            "embedding_model": "text-embedding-ada-002"
        }
        
        mock_load.return_value = valid_config
        mock_override.return_value = valid_config
        mock_validate.return_value = None
        
        get_config()
        
        # Verificar que se usa el path personalizado
        mock_load.assert_called_once_with("/custom/path/config.yaml")


class TestConfigError:
    """Tests para la excepción ConfigError."""
    
    def test_config_error_instantiation(self):
        """Test creación de excepción ConfigError."""
        error_message = "Test configuration error"
        error = ConfigError(error_message)
        
        assert str(error) == error_message
        assert isinstance(error, Exception)
    
    def test_config_error_inheritance(self):
        """Test que ConfigError hereda de Exception."""
        error = ConfigError("Test error")
        assert isinstance(error, Exception)


# Tests de integración para casos específicos
class TestConfigIntegration:
    """Tests de integración para casos específicos del módulo config."""
    
    def test_config_integration_with_env_overrides(self):
        """Test integración completa con overrides de variables de entorno."""
        yaml_content = """
        seeds:
          - https://example.com
        allowed_domains:
          - example.com
        user_agent: YamlBot/1.0
        delay: 1.0
        output_dir: ./yaml_data
        log_level: INFO
        chroma_path: ./chroma
        embedding_model: text-embedding-ada-002
        max_depth: 3
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_path = f.name
        
        try:
            # Simular variables de entorno
            with patch.dict(os.environ, {
                "CRAWLER_CONFIG_YAML": temp_path,
                "CRAWLER_USER_AGENT": "EnvBot/2.0",
                "CRAWLER_DELAY": "2.5",
                "CRAWLER_MAX_DEPTH": "5",
                "CRAWLER_LOG_LEVEL": "DEBUG"
            }):
                config = get_config()
                
                # Verificar que los valores del YAML se mantienen donde no hay override
                assert config["seeds"] == ["https://example.com"]
                assert config["allowed_domains"] == ["example.com"]
                assert config["output_dir"] == "./yaml_data"
                
                # Verificar que los overrides de env funcionan
                assert config["user_agent"] == "EnvBot/2.0"
                assert config["delay"] == 2.5
                assert config["max_depth"] == 5
                assert config["log_level"] == "DEBUG"
                
        finally:
            os.unlink(temp_path)
    
    def test_config_integration_validation_with_defaults(self):
        """Test integración de validación con valores por defecto."""
        minimal_config = {
            "seeds": ["https://example.com"],
            "allowed_domains": ["example.com"],
            "user_agent": "TestBot/1.0",
            "delay": 1.0,
            "output_dir": "./data",
            "log_level": "INFO",
            "chroma_path": "./chroma",
            "embedding_model": "text-embedding-ada-002"
            # max_depth y file_types se usan valores por defecto
        }
        
        # La validación debería pasar usando CrawlerConfig internamente
        validate_config(minimal_config)
        
        # Verificar que Pydantic aplicaría los valores por defecto
        pydantic_config = CrawlerConfig(**minimal_config)
        assert pydantic_config.max_depth == 3
        assert pydantic_config.file_types == ["html", "pdf", "docx", "xlsx"]


# Fixtures para uso común en otros tests
@pytest.fixture
def valid_config():
    """Fixture que proporciona una configuración válida básica."""
    return {
        "seeds": ["https://example.com"],
        "allowed_domains": ["example.com"],
        "user_agent": "TestBot/1.0",
        "delay": 1.0,
        "output_dir": "./data",
        "log_level": "INFO",
        "chroma_path": "./chroma",
        "embedding_model": "text-embedding-ada-002"
    }


@pytest.fixture
def temp_yaml_config(valid_config):
    """Fixture que crea un archivo YAML temporal con configuración válida."""
    yaml_content = yaml.dump(valid_config)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(yaml_content)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def invalid_config():
    """Fixture que proporciona una configuración inválida para tests."""
    return {
        "seeds": "not_a_list",  # Tipo incorrecto
        "allowed_domains": ["example.com"],
        "delay": "not_a_number",  # Tipo incorrecto
        # Faltan campos requeridos
    }