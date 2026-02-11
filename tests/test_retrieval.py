import pytest
from mcp_memory.db import store
import os
import shutil
import tempfile
from unittest.mock import patch, MagicMock

@pytest.fixture
def test_project():
    return "test_retrieval_project"

@pytest.fixture(autouse=True)
def cleanup(test_project):
    import mcp_memory.db as db
    
    # Use temp db
    tmp_dir = tempfile.mkdtemp()
    original_path = db.DB_PATH
    db.DB_PATH = tmp_dir
    
    store.initialized = False
    store.initialize()
    
    yield
    
    shutil.rmtree(tmp_dir)
    db.DB_PATH = original_path
    store.initialized = False

def test_metadata_filtering(test_project):
    # Add docs with different metadata
    store.add(test_project, "doc1", "python code function", {"type": "code", "lang": "py"})
    store.add(test_project, "doc2", "javascript code function", {"type": "code", "lang": "js"})
    store.add(test_project, "doc3", "documentation about python", {"type": "docs", "lang": "py"})
    
    # 1. Search without filter
    results = store.search(test_project, "function", k=10)
    assert len(results) >= 2
    
    # 2. Search with filter type=code
    results_code = store.search(test_project, "function", k=10, filter_meta={"type": "code"})
    assert len(results_code) == 2
    for res in results_code:
        assert res["metadata"]["type"] == "code"
        
    # 3. Search with filter lang=js
    results_js = store.search(test_project, "function", k=10, filter_meta={"lang": "js"})
    assert len(results_js) == 1
    assert results_js[0]["id"] == "doc2"

def test_score_returned(test_project):
    store.add(test_project, "doc1", "apple banana")
    
    results = store.search(test_project, "apple", k=1)
    assert len(results) == 1
    # Check if _distance is present
    assert "_distance" in results[0]
    # L2 distance for identical vector should be close to 0
    # (SentenceTransformers might not be perfectly deterministic or 0 if quantized, but very small)
    # Actually we encode "apple" vs "apple banana", won't be 0
    
    # Exact match check
    store.add(test_project, "exact", "apple")
    results_exact = store.search(test_project, "apple", k=1)
    # Should be very close to 0
    assert results_exact[0]["_distance"] < 0.1
