import re
from typing import List, Optional
import numpy as np
from mcp_memory.db import store

class Chunker:
    def chunk(self, text: str) -> List[str]:
        raise NotImplementedError

class RecursiveCharacterChunker(Chunker):
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200, separators: Optional[List[str]] = None):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", " ", ""]

    def chunk(self, text: str) -> List[str]:
        return self._split_text(text, self.separators)

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        final_chunks = []
        separator = separators[-1]
        new_separators = []

        # Find the appropriate separator
        for i, sep in enumerate(separators):
            if sep == "":
                separator = ""
                break
            if re.search(re.escape(sep), text):
                separator = sep
                new_separators = separators[i + 1:]
                break

        # Split text
        splits = self._split_on_separator(text, separator)

        # Merge splits
        good_splits = []
        _separator = separator if separator else ""
        
        for s in splits:
            if len(s) < self.chunk_size:
                good_splits.append(s)
            else:
                if good_splits:
                    merged = self._merge_splits(good_splits, _separator)
                    final_chunks.extend(merged)
                    good_splits = []
                if not new_separators:
                    # No more separators, but chunk is still too big. 
                    # Force split by character (if separator was "") or keep as is?
                    # Standard behavior: take it as is or force strict cut.
                    final_chunks.append(s)
                else:
                    final_chunks.extend(self._split_text(s, new_separators))

        if good_splits:
            merged = self._merge_splits(good_splits, _separator)
            final_chunks.extend(merged)

        return final_chunks

    def _split_on_separator(self, text: str, separator: str) -> List[str]:
        if separator:
            # We want to keep the separator attached to the chunk usually, but simple split is easier for now.
            # Langchain keeps it. Let's try simple split.
            return text.split(separator)
        return list(text)

    def _merge_splits(self, splits: List[str], separator: str) -> List[str]:
        chunks = []
        current_chunk = []
        current_len = 0

        for s in splits:
            s_len = len(s)
            if current_len + s_len + len(separator) > self.chunk_size:
                if current_chunk:
                    doc = separator.join(current_chunk)
                    if doc:
                         chunks.append(doc)
                    
                    # Overlap logic (simplified: dropping validation for now)
                    while current_len > self.chunk_overlap and current_chunk:
                        current_chunk.pop(0)
                        current_len = sum(len(c) + len(separator) for c in current_chunk)
                    
                if not current_chunk:
                    # If clean slate, just append (it might be too big but verified by recursion)
                    pass

            current_chunk.append(s)
            current_len += s_len + (len(separator) if len(current_chunk) > 1 else 0)

        if current_chunk:
            chunks.append(separator.join(current_chunk))
            
        return chunks

class SemanticChunker(Chunker):
    """
    Splits text into sentences, then groups them based on semantic similarity.
    """
    def __init__(self, threshold: float = 0.6, max_chunk_size: int = 1500):
        self.threshold = threshold
        self.max_chunk_size = max_chunk_size
        
    def chunk(self, text: str) -> List[str]:
        # 1. Split into sentences (simple approach)
        # In prod, use nltk or spacy. Here, regex.
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return []
            
        # 2. Embed sentences
        # Ensure model is ready
        store.initialize()
        embeddings = store.model.encode(sentences)
        
        # 3. Calculate cosine similarity between adjacent sentences
        distances = []
        for i in range(len(embeddings) - 1):
            v1 = np.array(embeddings[i])
            v2 = np.array(embeddings[i+1])
            sim = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            distances.append(sim)
            
        # 4. Group
        chunks = []
        current_chunk = [sentences[0]]
        current_len = len(sentences[0])
        
        for i in range(len(distances)):
            sim = distances[i]
            next_sent = sentences[i+1]
            
            # If similar enough AND fits in max size
            if sim >= self.threshold and (current_len + len(next_sent)) < self.max_chunk_size:
                current_chunk.append(next_sent)
                current_len += len(next_sent)
            else:
                chunks.append(" ".join(current_chunk))
                current_chunk = [next_sent]
                current_len = len(next_sent)
                
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        return chunks
