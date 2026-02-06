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
    
    store.initialize()
    
    for file_path in args.files:
        if not os.path.exists(file_path):
            print(f"Skipping {file_path}: File not found")
            continue
            
        print(f"Ingesting {file_path}...")
        try:
            content = read_file(file_path)
            chunks = chunk_text(content)
            
            base_name = os.path.basename(file_path)
            
            for i, chunk in enumerate(chunks):
                doc_id = f"{base_name}#{i}"
                store.add(
                    args.project, 
                    doc_id, 
                    chunk, 
                    {"source": file_path, "chunk_index": i}
                )
            print(f"  Added {len(chunks)} chunks.")
            
        except Exception as e:
            print(f"  Error ingesting {file_path}: {e}")

if __name__ == "__main__":
    main()
