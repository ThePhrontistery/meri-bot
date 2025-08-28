import asyncio
from meribot.core.chatengine import ChatEngine
from meribot.core.plugin_manager import PluginManager
from meribot.core.vector_search import VectorSearch
from meribot.core.cache import ResponseCache
from meribot.core.llm_engine import LLMEngine
from meribot.core.conversation import ConversationManager

async def main():
    engine = ChatEngine(
        plugin_manager=PluginManager(),
        vector_search=VectorSearch(),
        cache=ResponseCache(),
        llm_engine=LLMEngine(),
        conversation_manager=ConversationManager(),
    )
    result = await engine.process_message('usuario_demo', 'cuál es la temperatura actual en Madrid?')
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
