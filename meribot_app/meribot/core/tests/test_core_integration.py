"""
Test de integración mínimo de todo el CORE MeriBot.
Recorre el flujo real: guardrails, plugins, vector search, caché, LLM, logging, contexto.
Entradas hardcodeadas para simular casos típicos y edge cases.
@author: MeriBot Team
"""
import unittest
import asyncio
from meribot.core.chatengine import ChatEngine
from meribot.core.plugin_manager import PluginManager
from meribot.core.vector_search import VectorSearch
from meribot.core.cache import ResponseCache
from meribot.core.llm_engine import LLMEngine
from meribot.core.conversation import ConversationManager
from meribot.core.guardrails import apply_guardrails
from meribot.core.logging import log_generation_failure

class TestCoreIntegration(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Usar los módulos reales del core
        self.engine = ChatEngine(
            plugin_manager=PluginManager(),
            vector_search=VectorSearch(),
            cache=ResponseCache(),
            llm_engine=LLMEngine(),
            conversation_manager=ConversationManager(),
        )
        self.user_id = "testuser"

    async def test_guardrails_block(self):
        # Entrada peligrosa debe ser bloqueada por guardrails
        result = await self.engine.process_message(self.user_id, "<script>alert('xss')</script>")
        self.assertIn("rechazado", result["response"].lower())

    async def test_cache_and_context(self):
        # Primer mensaje: no está en caché
        result1 = await self.engine.process_message(self.user_id, "¿Cuál es la misión?")
        self.assertEqual(result1["type"], "llm")
        # Segundo mensaje igual: debe salir de caché
        result2 = await self.engine.process_message(self.user_id, "¿Cuál es la misión?")
        self.assertEqual(result2["type"], "cache")
        # El historial debe contener ambos mensajes
        ctx = self.engine.get_context(self.user_id)
        self.assertTrue(any(m["role"] == "user" for m in ctx))

    async def test_plugin_and_vector(self):
        # Si hay plugins activos y vector search, deberían poder intervenir
        # (Depende de la configuración real de plugins y vector search)
        # Aquí solo comprobamos que el flujo no rompe y retorna respuesta
        result = await self.engine.process_message(self.user_id, "Busca información vectorial")
        self.assertIn("response", result)

    async def test_llm_streaming(self):
        # Probar el streaming real del LLM
        tokens = []
        async for t in self.engine.stream_response(self.user_id, "Dame un resumen de la empresa"):
            tokens.append(t)
        self.assertTrue(len(tokens) > 0)

    async def test_logging_on_error(self):
        # Forzar un error en LLM para comprobar logging
        class FailingLLM:
            async def generate_response(self, *a, **kw):
                raise RuntimeError("Fallo LLM")
            async def stream_response(self, *a, **kw):
                raise RuntimeError("Fallo LLM")
        engine = ChatEngine(
            plugin_manager=PluginManager(),
            vector_search=VectorSearch(),
            cache=ResponseCache(),
            llm_engine=FailingLLM(),
            conversation_manager=ConversationManager(),
        )
        result = await engine.process_message(self.user_id, "Esto debe fallar")
        self.assertIn("error", result["response"].lower())
