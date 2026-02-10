import argparse
import os
import uuid
from mcp_memory.db import store

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def chunk_text(text: str, max_chunk_size=1000) -> list[str]:
    # Simple chunking by double newline (paragraphs) first
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = []
    current_length = 0
    
    for p in paragraphs:
        if current_length + len(p) > max_chunk_size and current_chunk:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = []
            current_length = 0
        
        current_chunk.append(p)
        current_length += len(p)
    
    if current_chunk:
        chunks.append("\n\n".join(current_chunk))
        
    return chunks

def main():
    parser = argparse.ArgumentParser(description="Ingest markdown files into MCP memory")
    parser.add_argument("--project", required=True, help="Project ID")
    parser.add_argument("files", nargs="+", help="Files to ingest")
    
    args = parser.parse_args()
    
def ingest_file(project_id: str, file_path: str):
    """Ingest a single file into the memory store."""
    if not os.path.exists(file_path):
        print(f"Skipping {file_path}: File not found")
        return

    print(f"Ingesting {file_path}...")
    try:
        content = read_file(file_path)
        chunks = chunk_text(content)
        
        base_name = os.path.basename(file_path)
        
        # Ensure store is initialized before adding
        store.initialize()

        count = 0
        for i, chunk in enumerate(chunks):
            doc_id = f"{base_name}#{i}"
            store.add(
                project_id, 
                doc_id, 
                chunk, 
                {"source": file_path, "chunk_index": i}
            )
            count += 1
        print(f"  Added {count} chunks.")
        
    except Exception as e:
        print(f"  Error ingesting {file_path}: {e}")
        # Re-raise so tests can catch it if needed, or handle gracefully
        raise e

def main():
    parser = argparse.ArgumentParser(description="Ingest markdown files into MCP memory")
    parser.add_argument("--project", required=True, help="Project ID")
    parser.add_argument("files", nargs="+", help="Files to ingest")
    
    args = parser.parse_args()
    
    # Initialize once
    store.initialize()
    
    for file_path in args.files:
        try:
            ingest_file(args.project, file_path)
        except Exception:
            # Continue to next file on error
            continue

if __name__ == "__main__":
    main()
