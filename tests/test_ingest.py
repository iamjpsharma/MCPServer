import pytest
from unittest.mock import patch, MagicMock
from mcp_memory.ingest import ingest_file

@pytest.fixture
def mock_ingest_store(mock_store):
    """Patch the store object imported in ingest.py"""
    with patch("mcp_memory.ingest.store", mock_store):
        yield mock_store

def test_ingest_file(mock_ingest_store, tmp_path):
    """Test ingestion of a file."""
    # Create a dummy file
    d = tmp_path / "subdir"
    d.mkdir()
    p = d / "hello.md"
    p.write_text("# Hello\n\nThis is a test file.")
    
    project_id = "ingest-test"
    
    # Run ingestion
    ingest_file(project_id, str(p))
    
    # Verify it was added to store
    # The current chunking might be simple (sentence based or paragraph)
    # Let's search for content
    results = mock_ingest_store.search(project_id, "test file", k=1)
    
    assert len(results) >= 1
    assert "test file" in results[0]["text"]
    assert results[0]["metadata"]["source"] == str(p)
