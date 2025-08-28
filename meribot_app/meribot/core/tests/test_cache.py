import time
import pytest
from meribot.core.cache import ResponseCache

@pytest.fixture
def cache():
    return ResponseCache(default_ttl=1, max_size=3)

def test_set_and_get(cache):
    cache.set('key1', 'value1')
    assert cache.get('key1') == 'value1'

def test_expire_entry(cache):
    cache.set('key2', 'value2', ttl=0.1)
    time.sleep(0.2)
    assert cache.get('key2') is None

def test_lru_eviction(cache):
    cache.set('a', 1)
    cache.set('b', 2)
    cache.set('c', 3)
    cache.get('a')  # a es el más reciente
    cache.set('d', 4)  # b debe salir (el menos usado)
    assert cache.get('b') is None
    assert cache.get('a') == 1
    assert cache.get('c') == 3
    assert cache.get('d') == 4

def test_invalidate(cache):
    cache.set('x', 'y')
    cache.invalidate('x')
    assert cache.get('x') is None

def test_clear(cache):
    cache.set('foo', 'bar')
    cache.set('baz', 'qux')
    cache.clear()
    assert cache.get('foo') is None
    assert cache.get('baz') is None
