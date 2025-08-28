"""
Pruebas unitarias e integración para ChatEngine.
@author: MeriBot Team
"""
import unittest
import asyncio
from meribot.core.chatengine import ChatEngine

class DummyPluginManager:
    async def run_pre_llm_plugins(self, message, context, metadata):
        if "plugin" in message:
            return "[PLUGIN]"
        return None
    async def run_post_llm_plugins(self, response, context, metadata):
        return response

class DummyVectorSearch:
    def search(self, message, domain=None, metadata=None):
        if "vector" in message:
            return [{"source": "doc1", "domain": domain or "default"}]
        return []

class DummyCache:
    def __init__(self):
        self._store = {}
    def get(self, message, domain=None):
        return self._store.get((message, domain))
    def set(self, message, response, domain=None):
        self._store[(message, domain)] = response

class DummyLLMEngine:
    async def generate_response(self, message, context=None, metadata=None):
        return f"LLM:{message}"
    async def stream_response(self, message, context=None, metadata=None):
        for c in f"LLM:{message}":
            yield c

class DummyConversationManager:
    class DummySession:
        def __init__(self):
            self.history = []
        def add_message(self, msg):
            self.history.append(msg)
    def __init__(self):
        self.sessions = {}
    def get_or_create_session(self, user_id):
        if user_id not in self.sessions:
            self.sessions[user_id] = self.DummySession()
        return self.sessions[user_id]
    def close_session(self, user_id):
        self.sessions.pop(user_id, None)

class TestChatEngine(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.engine = ChatEngine(
            plugin_manager=DummyPluginManager(),
            vector_search=DummyVectorSearch(),
            cache=DummyCache(),
            llm_engine=DummyLLMEngine(),
            conversation_manager=DummyConversationManager(),
        )

    async def test_cache_hit(self):
        self.engine.cache.set("hola", "cached!", domain=None)
        result = await self.engine.process_message("u1", "hola")
        self.assertEqual(result["type"], "cache")
        self.assertEqual(result["response"], "cached!")

    async def test_plugin_pre_llm(self):
        result = await self.engine.process_message("u1", "usa plugin")
        self.assertEqual(result["type"], "plugin")
        self.assertIn("PLUGIN", result["response"])

    async def test_vector_search_and_llm(self):
        result = await self.engine.process_message("u1", "usa vector")
        self.assertEqual(result["type"], "llm")
        self.assertIn("LLM:usa vector", result["response"])
        self.assertIn("doc1", result["citations"][0])

    async def test_stream_response(self):
        tokens = []
        async for t in self.engine.stream_response("u1", "hola stream"):
            tokens.append(t)
        self.assertTrue("LLM:hola stream".startswith("".join(tokens)[:4]))

    async def test_context_and_close(self):
        await self.engine.process_message("u1", "hola")
        ctx = self.engine.get_context("u1")
        self.assertTrue(any(m["role"] == "user" for m in ctx))
        self.engine.close_session("u1")
        ctx2 = self.engine.get_context("u1")
        self.assertEqual(ctx2, [])
