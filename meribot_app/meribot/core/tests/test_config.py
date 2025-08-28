
import os
import unittest
from meribot.core.config import MeriBotConfig
from pydantic import ValidationError

class TestMeriBotConfig(unittest.TestCase):
    def setUp(self):
        # Limpiar variables de entorno relevantes
        for var in ["LLM_MODEL", "SYSTEM_PROMPT", "TEMPERATURE", "MAX_TOKENS"]:
            if var in os.environ:
                del os.environ[var]

    def test_default_values(self):
        config = MeriBotConfig(_env_file=None)  # No lee .env
        self.assertEqual(config.LLM_MODEL, 'gpt-3.5-turbo')
        self.assertTrue(config.SYSTEM_PROMPT.startswith('Eres MeriBot'))
        self.assertEqual(config.TEMPERATURE, 0.7)
        self.assertEqual(config.MAX_TOKENS, 1024)

    def test_env_override(self):
        os.environ['LLM_MODEL'] = 'gpt-4'
        os.environ['SYSTEM_PROMPT'] = 'Hola!'
        os.environ['TEMPERATURE'] = '1.2'
        os.environ['MAX_TOKENS'] = '2048'
        config = MeriBotConfig()
        self.assertEqual(config.LLM_MODEL, 'gpt-4')
        self.assertEqual(config.SYSTEM_PROMPT, 'Hola!')
        self.assertEqual(config.TEMPERATURE, 1.2)
        self.assertEqual(config.MAX_TOKENS, 2048)

    def test_invalid_temperature(self):
        with self.assertRaises(ValidationError):
            MeriBotConfig(TEMPERATURE=3.0)

    def test_invalid_tokens(self):
        with self.assertRaises(ValidationError):
            MeriBotConfig(MAX_TOKENS=99999)

    def test_empty_model(self):
        with self.assertRaises(ValidationError):
            MeriBotConfig(LLM_MODEL='   ')

if __name__ == "__main__":
    unittest.main()
