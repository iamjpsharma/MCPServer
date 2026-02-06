import sys
import os

# Add src to path just in case
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from mcp_memory.db import store

def test():
    print("Initializing Storage...")
    store.initialize()
    
    pid = "test_project"
    
    print("Adding memory...")
    store.add(pid, "doc1", "The quick brown fox jumps over the lazy dog.", {"type": "test"})
    store.add(pid, "doc2", "Machine learning provides vector memory capabilities.", {"type": "test"})
    
    print("Searching for 'fox'...")
    results = store.search(pid, "fox", k=1)
    if results and "fox" in results[0]['text']:
        print("PASS: Found fox.")
    else:
        print("FAIL: Did not find fox.", results)
        
    print("Searching for 'vector'...")
    results = store.search(pid, "vector memory", k=1)
    if results and "Machine learning" in results[0]['text']:
        print("PASS: Found vector memory.")
    else:
        print("FAIL: Did not find vector memory.", results)

if __name__ == "__main__":
    test()
