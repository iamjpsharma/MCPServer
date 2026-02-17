import pytest
from fremem.chunking import RecursiveCharacterChunker, SemanticChunker
from unittest.mock import MagicMock, patch

def test_recursive_chunker():
    chunker = RecursiveCharacterChunker(chunk_size=10, chunk_overlap=2, separators=["\n", " "])
    text = "Hello world\nThis is a test"
    chunks = chunker.chunk(text)
    
    assert len(chunks) > 1
    # "Hello" (5) + " " (1) + "world" (5) = 11 > 10. Split.
    assert "Hello" in chunks[0] or "world" in chunks[1]

def test_recursive_chunker_simple():
    """Test standard behavior with defaults."""
    chunker = RecursiveCharacterChunker(chunk_size=100, chunk_overlap=0)
    text = "A" * 50 + "\n\n" + "B" * 50
    chunks = chunker.chunk(text)
    assert len(chunks) == 2
    assert chunks[0] == "A" * 50
    assert chunks[1] == "B" * 50

@patch("fremem.chunking.store")
def test_semantic_chunker(mock_store):
    """Test embedding-based chunking."""
    # Mock embedding model
    mock_model = MagicMock()
    # Return fake embeddings: [1,0], [1,0] (sim=1), [0,1] (sim=0)
    # Sentence 1 & 2 are similar. Sentence 3 is different.
    mock_model.encode.return_value = [
        [1.0, 0.0], 
        [1.0, 0.0], 
        [0.0, 1.0]
    ]
    mock_store.model = mock_model
    
    chunker = SemanticChunker(threshold=0.8)
    text = "Sentence one. Sentence two. Sentence three."
    
    chunks = chunker.chunk(text)
    
    # Should lump 1 and 2 together, and 3 separate
    assert len(chunks) == 2
    assert "Sentence one" in chunks[0] and "Sentence two" in chunks[0]
    assert "Sentence three" in chunks[1]
