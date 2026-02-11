import pytest
from mcp_memory.db import store
from mcp_memory.ingest import ingest_file
import os
from unittest.mock import MagicMock, patch

@pytest.fixture
def test_project():
    return "test_gov_project"

@pytest.fixture(autouse=True)
def cleanup(test_project):
    import tempfile
    import shutil
    from mcp_memory import db
    
    # Create temp dir for independent test DB
    tmp_dir = tempfile.mkdtemp()
    original_path = db.DB_PATH
    db.DB_PATH = tmp_dir
    
    # Re-initialize store with new path
    store.initialized = False
    store.initialize()
    
    yield
    
    # Cleanup
    shutil.rmtree(tmp_dir)
    db.DB_PATH = original_path
    store.initialized = False

def test_list_and_delete_source(test_project):
    # Add chunks from two sources
    store.add(test_project, "doc1", "content1", {"source": "file_a.txt"})
    store.add(test_project, "doc2", "content2", {"source": "file_a.txt"})
    store.add(test_project, "doc3", "content3", {"source": "file_b.txt"})
    
    # 1. List sources
    sources = store.list_sources(test_project)
    assert "file_a.txt" in sources
    assert "file_b.txt" in sources
    assert len(sources) == 2
    
    # 2. Get stats
    stats = store.get_stats(test_project)
    assert stats["chunk_count"] == 3
    
    # 3. Delete source
    store.delete_source(test_project, "file_a.txt")
    
    # 4. Verify deletion
    sources_after = store.list_sources(test_project)
    assert "file_a.txt" not in sources_after
    assert "file_b.txt" in sources_after
    assert len(sources_after) == 1
    
    stats_after = store.get_stats(test_project)
    assert stats_after["chunk_count"] == 1

def test_reset_project(test_project):
    store.add(test_project, "doc1", "content", {"source": "f1"})
    store.add(test_project, "doc2", "content", {"source": "f2"})
    
    assert store.get_stats(test_project)["chunk_count"] == 2
    
    store.delete_project(test_project)
    
    assert store.get_stats(test_project)["chunk_count"] == 0
    assert len(store.list_sources(test_project)) == 0

def test_ingest_replace_logic(test_project):
    # Create a dummy file
    dummy_file = "test_ingest.md"
    with open(dummy_file, "w") as f:
        f.write("Hello world")
        
    try:
        # 1. Ingest first time
        ingest_file(test_project, dummy_file)
        stats1 = store.get_stats(test_project)
        assert stats1["chunk_count"] > 0
        
        # 2. Ingest again with replace=True (default)
        # Should delete old chunks first.
        # Since content is same, count should remain same, but doc IDs might shift if chunker is non-deterministic (it is deterministic here)
        # To verify delete happened, let's manually add a "stale" chunk for this source first
        
        store.add(test_project, "stale_chunk", "stale content", {"source": dummy_file})
        stats_stale = store.get_stats(test_project)
        # Should have the 1 ingest chunk + 1 stale chunk
        assert stats_stale["chunk_count"] == stats1["chunk_count"] + 1
        
        # 3. Ingest again - should clean up stale chunk
        ingest_file(test_project, dummy_file, replace=True)
        
        stats_final = store.get_stats(test_project)
        # Should be back to original count (stale chunk removed)
        assert stats_final["chunk_count"] == stats1["chunk_count"]
        
    finally:
        if os.path.exists(dummy_file):
            os.remove(dummy_file)
