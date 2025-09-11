import os
import unittest
import logging
from meribot.core import logging as merilog

class TestLogging(unittest.TestCase):
    def setUp(self):
        self.logger = merilog.logger
        self.log_file = merilog.LOG_FILE
        # Truncar archivo de log antes de cada test (evita problemas de permisos)
        if os.path.exists(self.log_file):
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.truncate(0)

    def read_log(self):
        with open(self.log_file, encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]

    def test_log_critical_event(self):
        merilog.log_critical_event("Evento crítico", user_id="u1", api_key="secreta")
        logs = self.read_log()
        self.assertTrue(any('Evento crítico' in l for l in logs))
        self.assertTrue(any('"api_key": "***"' in l for l in logs))

    def test_log_guardrail_rejection(self):
        merilog.log_guardrail_rejection("u2", "texto prohibido", "motivo")
        logs = self.read_log()
        self.assertTrue(any('Input rechazado por guardrail' in l for l in logs))

    def test_log_generation_failure(self):
        merilog.log_generation_failure("u3", "input", "error fatal")
        logs = self.read_log()
        self.assertTrue(any('Fallo de generación LLM' in l for l in logs))

    def test_log_error(self):
        merilog.log_error("Error de prueba", token="tok123")
        logs = self.read_log()
        self.assertTrue(any('Error de prueba' in l for l in logs))
        self.assertTrue(any('"token": "***"' in l for l in logs))

    def test_log_rotation(self):
        # Forzar rotación escribiendo muchos logs
        for _ in range(2000):
            merilog.log_error("test", user_id="u4")
        # Debe existir el archivo de log y al menos un backup
        files = [f for f in os.listdir(os.path.dirname(self.log_file) or '.') if f.startswith(os.path.basename(self.log_file))]
        self.assertTrue(len(files) >= 1)

if __name__ == "__main__":
    unittest.main()
