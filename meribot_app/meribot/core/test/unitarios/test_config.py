"""
Tests unitarios para meribot.core.config
"""

import os
import tempfile
from unittest.mock import patch, mock_open
import pytest
import yaml

from meribot.core.config import load_config_from_yaml, load_system_prompt


class TestLoadConfigFromYaml:
    """Tests para la función load_config_from_yaml"""
    
    def test_load_config_existing_param(self, mock_environ_config):
        """Test cargar parámetro existente desde YAML"""
        result = load_config_from_yaml('allowed_domains')
        
        expected = ["onboarding", "training", "cca", "sdo"]
        assert result == expected
    
    def test_load_config_nonexistent_param(self, mock_environ_config):
        """Test cargar parámetro que no existe en YAML"""
        result = load_config_from_yaml('nonexistent_param')
        
        assert result is None
    
    def test_load_config_integer_param(self, mock_environ_config):
        """Test cargar parámetro entero desde YAML"""
        result = load_config_from_yaml('max_message_length')
        
        assert result == 4000
        assert isinstance(result, int)
    
    def test_load_config_list_param(self, mock_environ_config):
        """Test cargar parámetro tipo lista desde YAML"""
        result = load_config_from_yaml('dangerous_patterns')
        
        expected = ["delete", "drop table", "rm -rf", "<script>"]
        assert result == expected
        assert isinstance(result, list)
    
    def test_load_config_file_not_found(self):
        """Test cuando el archivo de configuración no existe"""
        with patch.dict(os.environ, {"CRAWLER_CONFIG_PATH": "nonexistent_file.yaml"}):
            result = load_config_from_yaml('any_param')
            
            assert result is None
    
    @patch.dict(os.environ, {"CRAWLER_CONFIG_PATH": ""})
    def test_load_config_empty_path(self):
        """Test con path vacío en variable de entorno"""
        result = load_config_from_yaml('any_param')
        
        assert result is None
    
    def test_load_config_invalid_yaml(self, temp_directory):
        """Test con archivo YAML inválido"""
        invalid_yaml_path = os.path.join(temp_directory, "invalid.yaml")
        
        # Crear archivo con YAML inválido
        with open(invalid_yaml_path, 'w', encoding='utf-8') as f:
            f.write("invalid: yaml: content:\n  - malformed")
        
        with patch.dict(os.environ, {"CRAWLER_CONFIG_PATH": invalid_yaml_path}):
            result = load_config_from_yaml('any_param')
            
            assert result is None
    
    def test_load_config_empty_yaml(self, temp_directory):
        """Test con archivo YAML vacío"""
        empty_yaml_path = os.path.join(temp_directory, "empty.yaml")
        
        with open(empty_yaml_path, 'w', encoding='utf-8') as f:
            f.write("")
        
        with patch.dict(os.environ, {"CRAWLER_CONFIG_PATH": empty_yaml_path}):
            result = load_config_from_yaml('any_param')
            
            assert result is None
    
    def test_load_config_permission_error(self, temp_directory):
        """Test cuando no hay permisos para leer el archivo"""
        config_path = os.path.join(temp_directory, "restricted.yaml")
        
        # Crear archivo
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write("test: value")
        
        # Simular error de permisos
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with patch.dict(os.environ, {"CRAWLER_CONFIG_PATH": config_path}):
                result = load_config_from_yaml('test')
                
                assert result is None
    
    def test_load_config_nested_param(self, temp_directory):
        """Test cargar parámetro anidado (no soportado por la función actual)"""
        nested_config = """
        database:
          host: localhost
          port: 5432
        api:
          timeout: 30
        """
        
        config_path = os.path.join(temp_directory, "nested.yaml")
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(nested_config)
        
        with patch.dict(os.environ, {"CRAWLER_CONFIG_PATH": config_path}):
            # La función actual solo busca en el nivel raíz
            result = load_config_from_yaml('database')
            
            expected = {"host": "localhost", "port": 5432}
            assert result == expected
    
    def test_load_config_default_path(self, temp_directory):
        """Test usando path por defecto cuando no está definida la env var"""
        default_config = os.path.join(temp_directory, "crawler_config.yaml")
        
        config_content = "test_param: default_value"
        with open(default_config, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        # Cambiar directorio de trabajo para que el path relativo funcione
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_directory)
            
            # Remover la variable de entorno si existe
            with patch.dict(os.environ, {}, clear=True):
                result = load_config_from_yaml('test_param')
                
                assert result == "default_value"
        finally:
            os.chdir(original_cwd)


class TestLoadSystemPrompt:
    """Tests para la función load_system_prompt"""
    
    def test_load_system_prompt_success(self, mock_environ_config):
        """Test cargar system prompt exitosamente"""
        result = load_system_prompt()
        
        assert isinstance(result, str)
        assert "MeriBot" in result
        assert "asistente conversacional" in result
        assert len(result) > 50  # Verificar que no está vacío
    
    def test_load_system_prompt_file_not_found(self):
        """Test cuando el archivo de system prompt no existe"""
        with patch.dict(os.environ, {"SYSTEM_PROMPT_PATH": "nonexistent_prompt.txt"}):
            with pytest.raises(FileNotFoundError):
                load_system_prompt()
    
    def test_load_system_prompt_empty_path(self):
        """Test con path vacío o None"""
        with patch.dict(os.environ, {"SYSTEM_PROMPT_PATH": ""}):
            with pytest.raises((FileNotFoundError, TypeError)):
                load_system_prompt()
        
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises((FileNotFoundError, TypeError)):
                load_system_prompt()
    
    def test_load_system_prompt_permission_error(self, temp_directory):
        """Test cuando no hay permisos para leer el archivo"""
        prompt_path = os.path.join(temp_directory, "restricted_prompt.txt")
        
        # Crear archivo
        with open(prompt_path, 'w', encoding='utf-8') as f:
            f.write("Test prompt content")
        
        # Simular error de permisos
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with patch.dict(os.environ, {"SYSTEM_PROMPT_PATH": prompt_path}):
                with pytest.raises(PermissionError):
                    load_system_prompt()
    
    def test_load_system_prompt_empty_file(self, temp_directory):
        """Test cargar system prompt desde archivo vacío"""
        empty_prompt_path = os.path.join(temp_directory, "empty_prompt.txt")
        
        with open(empty_prompt_path, 'w', encoding='utf-8') as f:
            f.write("")
        
        with patch.dict(os.environ, {"SYSTEM_PROMPT_PATH": empty_prompt_path}):
            result = load_system_prompt()
            
            assert result == ""
            assert isinstance(result, str)
    
    def test_load_system_prompt_unicode_content(self, temp_directory):
        """Test cargar system prompt con contenido Unicode"""
        unicode_prompt_path = os.path.join(temp_directory, "unicode_prompt.txt")
        
        unicode_content = """Eres MeriBot 🤖, un asistente conversacional para C&CA.
        Tu función es ayudar con información sobre:
        • Políticas empresariales 📋
        • Procedimientos de RR.HH. 👥
        • Documentación técnica 🔧
        
        Mantén siempre un tono profesional y amigable. ¡Saludos! 👋"""
        
        with open(unicode_prompt_path, 'w', encoding='utf-8') as f:
            f.write(unicode_content)
        
        with patch.dict(os.environ, {"SYSTEM_PROMPT_PATH": unicode_prompt_path}):
            result = load_system_prompt()
            
            assert "🤖" in result
            assert "📋" in result
            assert "C&CA" in result
            assert isinstance(result, str)
    
    def test_load_system_prompt_large_file(self, temp_directory):
        """Test cargar system prompt desde archivo grande"""
        large_prompt_path = os.path.join(temp_directory, "large_prompt.txt")
        
        # Crear contenido grande (repetir texto)
        base_content = "Esta es una línea de contenido del system prompt. " * 100
        large_content = base_content * 50  # ~250KB aprox
        
        with open(large_prompt_path, 'w', encoding='utf-8') as f:
            f.write(large_content)
        
        with patch.dict(os.environ, {"SYSTEM_PROMPT_PATH": large_prompt_path}):
            result = load_system_prompt()
            
            assert len(result) > 100000  # Verificar que se cargó contenido grande
            assert "system prompt" in result
            assert isinstance(result, str)


class TestIntegration:
    """Tests de integración para el módulo config"""
    
    def test_config_functions_integration(self, mock_environ_config):
        """Test integración entre ambas funciones de config"""
        # Cargar configuración
        max_length = load_config_from_yaml('max_message_length')
        domains = load_config_from_yaml('allowed_domains')
        
        # Cargar system prompt
        prompt = load_system_prompt()
        
        # Verificar que ambas funcionan correctamente
        assert isinstance(max_length, int)
        assert isinstance(domains, list)
        assert isinstance(prompt, str)
        assert max_length > 0
        assert len(domains) > 0
        assert len(prompt) > 0
    
    def test_config_yaml_structure_validation(self, mock_environ_config):
        """Test validar estructura esperada del YAML de configuración"""
        required_params = [
            'allowed_domains',
            'max_message_length',
            'max_conversation_id_length',
            'max_domains_count',
            'dangerous_patterns'
        ]
        
        for param in required_params:
            result = load_config_from_yaml(param)
            assert result is not None, f"Parámetro requerido '{param}' no encontrado"
    
    def test_config_types_validation(self, mock_environ_config):
        """Test validar tipos de datos de configuración"""
        # Verificar tipos enteros
        int_params = ['max_message_length', 'max_conversation_id_length', 'max_domains_count']
        for param in int_params:
            value = load_config_from_yaml(param)
            assert isinstance(value, int), f"Parámetro '{param}' debe ser entero"
            assert value > 0, f"Parámetro '{param}' debe ser positivo"
        
        # Verificar tipos lista
        list_params = ['allowed_domains', 'dangerous_patterns', 'sensitive_keys']
        for param in list_params:
            value = load_config_from_yaml(param)
            assert isinstance(value, list), f"Parámetro '{param}' debe ser lista"


class TestEdgeCases:
    """Tests para casos edge y manejo de errores"""
    
    def test_config_with_special_characters(self, temp_directory):
        """Test configuración con caracteres especiales"""
    def test_config_with_special_characters(self, temp_directory):
        """Test configuración con caracteres especiales"""
        special_config = """test_param: "Test con ñ"
unicode_list:
  - "Español"
  - "Русский"
"""
        
        config_path = os.path.join(temp_directory, "special.yaml")
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(special_config)
        
        with patch.dict(os.environ, {"CRAWLER_CONFIG_PATH": config_path}):
            result1 = load_config_from_yaml('test_param')
            result2 = load_config_from_yaml('unicode_list')
            
            # Verificar que los resultados no son None antes de hacer assert
            assert result1 is not None, "No se pudo cargar test_param"
            assert result2 is not None, "No se pudo cargar unicode_list"
            
            assert "ñ" in result1
            assert "Русский" in result2
    
    def test_config_with_null_values(self, temp_directory):
        """Test configuración con valores nulos"""
        null_config = """
        null_param: null
        empty_string: ""
        zero_value: 0
        empty_list: []
        """
        
        config_path = os.path.join(temp_directory, "nulls.yaml")
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(null_config)
        
        with patch.dict(os.environ, {"CRAWLER_CONFIG_PATH": config_path}):
            assert load_config_from_yaml('null_param') is None
            assert load_config_from_yaml('empty_string') == ""
            assert load_config_from_yaml('zero_value') == 0
            assert load_config_from_yaml('empty_list') == []
    
    def test_config_path_resolution_error(self):
        """Test error en resolución de path absoluto"""
        # Simular un archivo de config que no existe
        with patch.dict(os.environ, {"CRAWLER_CONFIG_PATH": "/path/inexistente/config.yaml"}):
            result = load_config_from_yaml('any_param')
            assert result is None