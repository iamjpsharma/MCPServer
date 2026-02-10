import pytest
import io
from unittest.mock import patch, MagicMock
from mcp_memory.ingest import ingest_file

@pytest.fixture
def mock_ingest_dependencies(mock_store):
    """Patch dependencies in ingest.py"""
    with patch("mcp_memory.ingest.store", mock_store), \
         patch("mcp_memory.ingest.PdfReader") as mock_pdf:
        yield mock_store, mock_pdf

def test_pdf_ingestion(mock_ingest_dependencies):
    mock_store, mock_pdf_class = mock_ingest_dependencies
    
    # Mock PDF behavior
    mock_pdf_instance = MagicMock()
    mock_page1 = MagicMock()
    mock_page1.extract_text.return_value = "Page 1 content."
    mock_page2 = MagicMock()
    mock_page2.extract_text.return_value = "Page 2 content."
    
    mock_pdf_instance.pages = [mock_page1, mock_page2]
    mock_pdf_class.return_value = mock_pdf_instance
    
    project_id = "pdf-test"
    file_path = "document.pdf"
    
    # Mock the add method on the real store instance so we can inspect calls
    mock_store.add = MagicMock()
    
    # Run ingest
    with patch("os.path.exists", return_value=True):
        ingest_file(project_id, file_path)
    
    # Verify PdfReader was called
    mock_pdf_class.assert_called_with(file_path)
    
    # Verify content was added.
    assert mock_store.add.called
    args = mock_store.add.call_args[0] 
    # args: (project_id, doc_id, text, metadata)
    
    assert args[0] == project_id
    assert "Page 1 content." in args[2]
    assert "Page 2 content." in args[2]
    assert args[3]["source"] == file_path
