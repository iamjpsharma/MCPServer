import pytest
import os
from unittest.mock import patch, MagicMock
from fremem.ingest import ingest_file

# Path to real PDF (relative to this test file)
# ../../TestData/AI in HR Automation.pdf
REAL_PDF_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../TestData/AI in HR Automation.pdf"))

@pytest.fixture
def mock_ingest_store(mock_store):
    """Patch the store object imported in ingest.py with our test store fixture"""
    with patch("fremem.ingest.store", mock_store):
        yield mock_store

def test_pdf_ingestion_mocked(mock_store):
    """Test with mocked PDF reader (keeping for unit isolation)"""
    with patch("fremem.ingest.store", mock_store), \
         patch("fremem.ingest.PdfReader") as mock_pdf_class:
        
        # Mock PDF behavior
        mock_pdf_instance = MagicMock()
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Page 1 content."
        mock_pdf_instance.pages = [mock_page1]
        mock_pdf_class.return_value = mock_pdf_instance
        
        project_id = "pdf-test-mock"
        file_path = "dummy.pdf"
        
        # Mock add to verify call
        mock_store.add = MagicMock()
        
        with patch("os.path.exists", return_value=True):
            ingest_file(project_id, file_path)
        
        assert mock_store.add.called
        args = mock_store.add.call_args[0]
        assert "Page 1 content." in args[2]

@pytest.mark.skipif(not os.path.exists(REAL_PDF_PATH), reason="Real PDF file not found")
def test_pdf_ingestion_real_file(mock_store):
    """Test with the real PDF file from TestData"""
    
    # Patch only the store, let PdfReader be real
    with patch("fremem.ingest.store", mock_store):
        project_id = "pdf-test-real"
        
        # Spy on perform add to check content
        # We can't easily spy on the real method if we don't mock it, 
        # but mock_store IS a real object (just using temp db).
        # So we can wrap its add method or just inspect the DB after.
        
        # Inspection via search is better for integration test.
        # But for direct verification, let's spy.
        original_add = mock_store.add
        mock_store.add = MagicMock(side_effect=original_add)
        
        ingest_file(project_id, REAL_PDF_PATH)
        
        assert mock_store.add.called
        
        # Check that we got some text
        # We don't know exact content, but we expect non-empty text
        call_args = mock_store.add.call_args_list
        full_text = ""
        for call in call_args:
            args = call[0] # (project_id, doc_id, text, metadata)
            text = args[2]
            full_text += text
            
        assert len(full_text) > 100
        print(f"DEBUG: Extracted {len(full_text)} chars from PDF")
        
        # Verify it contains some expected keywords (based on filename)
        assert "HR" in full_text or "Automation" in full_text or "Artificial Intelligence" in full_text
