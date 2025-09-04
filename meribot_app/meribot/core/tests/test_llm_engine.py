"""
Pruebas unitarias para el motor LLMEngine de MeriBot CORE.
Mockea el proveedor LLM y cubre generación, streaming, citación y errores.
@author: MeriBot Team
"""
import unittest
import asyncio
from meribot.core.llm_engine import LLMEngine, LLMProvider

class MockLLMProvider(LLMProvider):
    async def generate(self, prompt, context=None):
        return f"MOCKED: {prompt}"
    async def stream(self, prompt, context=None):
        for c in prompt:
            yield c

class TestLLMEngine(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.engine = LLMEngine(provider=MockLLMProvider("mock", {}))

    async def test_generate_response_ok(self):
        resp = await self.engine.generate_response("Hola", context=["previo"], metadata={"user_id": "u1"})
        self.assertIn("MOCKED", resp)

    async def test_generate_response_guardrail(self):
        resp = await self.engine.generate_response("<script>alert('xss')</script>", context=None, metadata={"user_id": "u2"})
        self.assertIn("rechazado", resp)

    async def test_generate_response_citation(self):
        resp = await self.engine.generate_response("Hola", context=None, metadata={"user_id": "u3", "citar_fuentes": True})
        self.assertIn("Fuente", resp)

    async def test_generate_response_error(self):
        class FailingProvider(MockLLMProvider):
            async def generate(self, prompt, context=None):
                raise RuntimeError("Fallo LLM")
        engine = LLMEngine(provider=FailingProvider("mock", {}))
        resp = await engine.generate_response("Hola", context=None, metadata={"user_id": "u4"})
        self.assertIn("Error", resp)

    async def test_stream_response_error(self):
        class FailingProvider:
            async def generate(self, prompt, context=None):
                raise RuntimeError("Fallo LLM")
            def stream(self, prompt, context=None):
                async def gen():
                    raise RuntimeError("Fallo LLM")
                    yield  # never reached
                return gen()
        engine = LLMEngine(provider=FailingProvider())
        tokens = []
        async for t in engine.stream_response("Hola", context=None, metadata={"user_id": "u8"}):
            tokens.append(t)
        self.assertIn("Error", tokens[0])
        tokens = []
        async for t in self.engine.stream_response("Hola", context=None, metadata={"user_id": "u7", "citar_fuentes": True}):
            tokens.append(t)
        self.assertTrue(any("Fuente" in t for t in tokens))

    async def test_stream_response_error(self):
        class FailingProvider(MockLLMProvider):
            async def stream(self, prompt, context=None):
                raise RuntimeError("Fallo LLM")
        engine = LLMEngine(provider=FailingProvider("mock", {}))
        tokens = []
        async for t in engine.stream_response("Hola", context=None, metadata={"user_id": "u8"}):
            tokens.append(t)
        self.assertIn("Error", tokens[0])

if __name__ == "__main__":
    unittest.main()
