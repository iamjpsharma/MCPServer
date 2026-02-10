import os
import sys
import pytest
import shutil
import tempfile
from unittest.mock import patch

# Ensure src is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from mcp_memory.db import VectorStore

@pytest.fixture
def temp_db_path():
    """Create a temporary directory for the vector DB."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def mock_store(temp_db_path):
    """
    Initialize a clean VectorStore with a temporary path.
    Patches module-level DB_PATH and resets the singleton.
    """
    with patch("mcp_memory.db.DB_PATH", temp_db_path):
        # Reset singleton to force re-initialization
        VectorStore._instance = None
        store = VectorStore()
        
        # We also need to patch the internal property if it was already read, 
        # but since we reset usage, just calling initialize() is key.
        # However, db.py reads DB_PATH at module level. 
        # The patching above handles future reads, but VectorStore might rely on global.
        # Let's verify initialize uses the patched global.
        
        store.initialize()
        yield store
