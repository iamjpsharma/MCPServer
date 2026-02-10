import os
import lancedb
import logging
import json
from sentence_transformers import SentenceTransformer
from typing import List, Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-memory")

# Constants
DB_PATH = os.environ.get("MCP_MEMORY_PATH", os.path.join(os.getcwd(), "mcp_memory_data"))
MODEL_NAME = "all-MiniLM-L6-v2"

class VectorStore:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorStore, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def initialize(self):
        if self.initialized:
            return
            
        logger.info(f"Initializing VectorStore at {DB_PATH}")
        os.makedirs(DB_PATH, exist_ok=True)
        
        self.db = lancedb.connect(DB_PATH)
        
        # Load embedding model (downloads on first run)
        logger.info(f"Loading embedding model: {MODEL_NAME}")
        self.model = SentenceTransformer(MODEL_NAME)
        
        self.table_name = "memory_store"
        self._ensure_table()
        self.initialized = True

    def _ensure_table(self):
        # We store: id, vector, text, project_id, metadata_json (string)
        # Using string for metadata is more robust for varying schema than LanceDB structs
        
        tables = self.db.list_tables()
        if hasattr(tables, "tables"):
            tables = tables.tables
            
        if self.table_name not in tables:
            # Create a dummy entry to initialize schema
            dummy_vector = self.model.encode("init").tolist()
            schema_data = [{
                "id": "init_schema", 
                "vector": dummy_vector, 
                "text": "init", 
                "project_id": "system", 
                "metadata_json": "{}"
            }]
            self.tbl = self.db.create_table(self.table_name, data=schema_data)
            self.tbl.delete("id = 'init_schema'")
        else:
            self.tbl = self.db.open_table(self.table_name)

    def add(self, project_id: str, doc_id: str, text: str, meta: Dict[str, Any] = None):
        self.initialize()
        
        logger.info(f"Adding document {doc_id} to project {project_id}")
        vector = self.model.encode(text).tolist()
        
        data = [{
            "id": doc_id,
            "vector": vector,
            "text": text,
            "project_id": project_id,
            "metadata_json": json.dumps(meta or {})
        }]
        
        # Update if exists
        try:
            self.tbl.delete(f"id = '{doc_id}' AND project_id = '{project_id}'")
        except Exception:
            pass 
            
        self.tbl.add(data)
        
    def search(self, project_id: str, query: str, k: int = 5) -> List[Dict[str, Any]]:
        self.initialize()
        
        query_vec = self.model.encode(query).tolist()
        
        results = self.tbl.search(query_vec)\
            .where(f"project_id = '{project_id}'")\
            .limit(k)\
            .to_list()
            
        # Parse metadata_json back to dict for the consumer
        for res in results:
            if 'metadata_json' in res:
                try:
                    res['metadata'] = json.loads(res['metadata_json'])
                except:
                    res['metadata'] = {}
            else:
                res['metadata'] = {}
                
        return results

    def delete_project(self, project_id: str) -> bool:
        self.initialize()
        logger.info(f"Deleting all memories for project {project_id}")
        try:
            self.tbl.delete(f"project_id = '{project_id}'")
            return True
        except Exception as e:
            logger.error(f"Error deleting project {project_id}: {e}")
            return False

# Singleton global access
store = VectorStore()
