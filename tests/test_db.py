import pytest
import json

def test_store_initialization(mock_store):
    """Test that the store initializes and creates the table."""
    assert mock_store.initialized
    assert mock_store.db is not None
    tables = mock_store.db.list_tables()
    if hasattr(tables, "tables"):
        tables = tables.tables
    assert "memory_store" in tables

def test_add_and_search(mock_store):
    """Test adding a document and searching for it."""
    project_id = "test-project"
    doc_id = "doc1"
    text = "The quick brown fox jumps over the lazy dog."
    meta = {"source": "test", "page": 1}
    
    # Add document
    mock_store.add(project_id, doc_id, text, meta)
    
    # Search for it
    results = mock_store.search(project_id, "brown fox", k=1)
    
    assert len(results) == 1
    assert results[0]["id"] == doc_id
    assert results[0]["project_id"] == project_id
    assert results[0]["text"] == text
    assert results[0]["metadata"]["source"] == "test"

def test_project_isolation(mock_store):
    """Test that searches are isolated by project_id."""
    # Add to Project A
    mock_store.add("proj-A", "docA", "secret info for A")
    
    # Add to Project B
    mock_store.add("proj-B", "docB", "secret info for B")
    
    # Search Project A
    results_a = mock_store.search("proj-A", "secret", k=5)
    assert len(results_a) == 1
    assert results_a[0]["project_id"] == "proj-A"
    
    # Search Project B
    results_b = mock_store.search("proj-B", "secret", k=5)
    assert len(results_b) == 1
    assert results_b[0]["project_id"] == "proj-B"

def test_delete_project(mock_store):
    """Test deleting all memories for a project."""
    mock_store.add("proj-delete", "doc1", "content 1")
    mock_store.add("proj-delete", "doc2", "content 2")
    
    # Verify added
    assert len(mock_store.search("proj-delete", "content")) == 2
    
    # Delete
    mock_store.delete_project("proj-delete")
    
    # Verify empty
    assert len(mock_store.search("proj-delete", "content")) == 0
