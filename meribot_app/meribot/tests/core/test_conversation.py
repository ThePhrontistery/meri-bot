
import sys
import os
import pytest

# Añadir la raíz del proyecto al sys.path para permitir imports absolutos
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
meribot_app_path = os.path.join(project_root, 'meribot_app')
if meribot_app_path not in sys.path:
    sys.path.insert(0, meribot_app_path)

from meribot.core.conversation import ConversationContext, ConversationManager

def test_conversation_context_add_and_history():
    ctx = ConversationContext(user_id="user1")
    ctx.add_message(role="user", content="Hola")
    ctx.add_message(role="bot", content="¡Hola!")
    history = ctx.get_history()
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "bot"
    ctx.close()
    assert ctx.is_active is False
    assert ctx.get_history() == []

def test_conversation_manager_create_and_close():
    manager = ConversationManager()
    ctx = manager.create_session(user_id="user2")
    assert ctx.user_id == "user2"
    assert manager.get_session(ctx.conversation_id) is ctx
    assert manager.close_session(ctx.conversation_id) is True
    assert manager.get_session(ctx.conversation_id) is None
