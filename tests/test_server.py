import pytest
from unittest.mock import patch, MagicMock
from mcp_memory.server import list_tools, call_tool, list_resources, read_resource

@pytest.fixture
def mock_server_store(mock_store):
    """Patch the store object imported in server.py"""
    with patch("mcp_memory.server.store", mock_store):
        yield mock_store

@pytest.mark.asyncio
async def test_list_tools():
    """Test that tools are listed correctly."""
    tools = await list_tools()
    tool_names = [t.name for t in tools]
    assert "memory_search" in tool_names
    assert "memory_add" in tool_names

@pytest.mark.asyncio
async def test_memory_add_tool(mock_server_store):
    """Test the memory_add tool."""
    args = {
        "project_id": "test-proj",
        "id": "doc1",
        "text": "verify me",
        "meta": {"foo": "bar"}
    }
    
    result = await call_tool("memory_add", args)
    
    assert len(result) == 1
    assert result[0].type == "text"
    assert "Successfully added" in result[0].text
    
    # Verify it actually went to the store
    results = mock_server_store.search("test-proj", "verify", k=1)
    assert len(results) == 1
    assert results[0]["text"] == "verify me"

@pytest.mark.asyncio
async def test_memory_search_tool(mock_server_store):
    """Test the memory_search tool."""
    # Seed data
    mock_server_store.add("search-proj", "s1", "found duplicate")
    
    args = {
        "project_id": "search-proj",
        "q": "duplicate",
        "k": 1
    }
    
    result = await call_tool("memory_search", args)
    
    assert len(result) == 1
    assert result[0].type == "text"
    assert "found duplicate" in result[0].text

@pytest.mark.asyncio
async def test_resource_handlers():
    """Test the resource handlers."""
    # List resources
    resources = await list_resources()
    assert resources == []
    
    # Read resource (should fail)
    with pytest.raises(ValueError):
        await read_resource("some://uri")
