"""
Pruebas unitarias para el módulo guardrails de MeriBot CORE.
Cubre validación, sanitización, edge cases y ataques comunes.
@author: MeriBot Team
"""
import unittest
from meribot.core import guardrails

class TestGuardrails(unittest.TestCase):
    def test_valid_input(self):
        self.assertTrue(guardrails.validate_input("Hola, ¿cómo estás?"))

    def test_input_too_long(self):
        long_input = "a" * (guardrails.DEFAULT_GUARDRAILS['max_length'] + 1)
        self.assertFalse(guardrails.validate_input(long_input))

    def test_forbidden_pattern_xss(self):
        xss = "<script>alert('xss')</script>"
        self.assertFalse(guardrails.validate_input(xss))

    def test_forbidden_pattern_sqli(self):
        sqli = "DROP TABLE users;"
        self.assertFalse(guardrails.validate_input(sqli))

    def test_forbidden_pattern_sensitive(self):
        sensitive = "Mi contraseña es 1234"
        self.assertFalse(guardrails.validate_input(sensitive))

    def test_sanitize_removes_html_and_scripts(self):
        dirty = "<script>alert('xss')</script><b>negrita</b> texto"
        sanitized = guardrails.sanitize_input(dirty)
        self.assertNotIn("<script", sanitized)
        self.assertNotIn("<b>", sanitized)
        self.assertIn("negrita", sanitized)
        self.assertIn("texto", sanitized)

    def test_apply_guardrails_valid(self):
        clean = "Hola mundo"
        self.assertEqual(guardrails.apply_guardrails(clean), "Hola mundo")

    def test_apply_guardrails_invalid(self):
        bad = "<script>alert('xss')</script>"
        self.assertIsNone(guardrails.apply_guardrails(bad))

    def test_enforce_accessibility(self):
        self.assertTrue(guardrails.enforce_accessibility("Texto normal"))

    def test_edge_case_empty(self):
        self.assertTrue(guardrails.validate_input(""))
        self.assertEqual(guardrails.sanitize_input(""), "")

    def test_non_string_input(self):
        self.assertFalse(guardrails.validate_input(12345))

if __name__ == "__main__":
    unittest.main()
