import sys
import os
# Añadir la raíz del proyecto al sys.path para permitir imports absolutos
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
meribot_app_path = os.path.join(project_root, 'meribot_app')
if meribot_app_path not in sys.path:
    sys.path.insert(0, meribot_app_path)
import unittest
from meribot.core.plugin_manager import PluginManager, BasePlugin

class DummyPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.activated = False
        self.deactivated = False
        self.last_query = None
        self.last_context = None

    def activate(self):
        self.activated = True

    def deactivate(self):
        self.deactivated = True

    def process(self, query, context):
        self.last_query = query
        self.last_context = context
        return f"Processed: {query}"

class TestPluginManager(unittest.TestCase):
    def setUp(self):
        self.manager = PluginManager()
        self.plugin = DummyPlugin()
        self.manager.register('dummy', self.plugin)

    def test_register_and_get_plugin(self):
        self.assertIs(self.manager.get_plugin('dummy'), self.plugin)

    def test_activate_plugin(self):
        self.manager.activate('dummy')
        self.assertTrue(self.plugin.activated)
        self.assertIn('dummy', self.manager.list_active_plugins())

    def test_deactivate_plugin(self):
        self.manager.activate('dummy')
        self.manager.deactivate('dummy')
        self.assertTrue(self.plugin.deactivated)
        self.assertNotIn('dummy', self.manager.list_active_plugins())

    def test_process_with_active_plugins(self):
        self.manager.activate('dummy')
        result = self.manager.process_with_active_plugins('hola', {'user': 'test'})
        self.assertIn('dummy', result)
        self.assertEqual(result['dummy'], 'Processed: hola')
        self.assertEqual(self.plugin.last_query, 'hola')
        self.assertEqual(self.plugin.last_context, {'user': 'test'})

    def test_register_duplicate_plugin_raises(self):
        with self.assertRaises(ValueError):
            self.manager.register('dummy', DummyPlugin())

    def test_activate_nonexistent_plugin_raises(self):
        with self.assertRaises(KeyError):
            self.manager.activate('nope')

    def test_deactivate_nonexistent_plugin_raises(self):
        with self.assertRaises(KeyError):
            self.manager.deactivate('nope')

if __name__ == '__main__':
    unittest.main()
