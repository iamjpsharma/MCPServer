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
        # We store: id, vector, text, project_id, source, metadata_json
        # Added 'source' column in v0.2.0 for better governance
        
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
                "source": "system",
                "metadata_json": "{}"
            }]
            self.tbl = self.db.create_table(self.table_name, data=schema_data)
            self.tbl.delete("id = 'init_schema'")
        else:
            self.tbl = self.db.open_table(self.table_name)
            # Check for schema migration (v0.1.0 -> v0.2.0)
            try:
                # pyarrow schema
                schema = self.tbl.schema
                if "source" not in schema.names:
                    logger.info("Migrating database schema to v0.2.0 (adding 'source' column)...")
                    # Naive migration: fetch all, drop, recreate
                    # This is safe-ish for local single-user, provided memory fits
                    all_data = self.tbl.to_arrow().to_pylist()
                    
                    # Transform data
                    new_data = []
                    for row in all_data:
                        # Skip if it's the init schema (shouldn't be there but just in case)
                        if row['id'] == 'init_schema':
                            continue
                            
                        meta = {}
                        if 'metadata_json' in row:
                            try:
                                meta = json.loads(row['metadata_json'])
                            except:
                                pass
                        
                        row['source'] = meta.get('source', '')
                        new_data.append(row)
                    
                    # Recreate table
                    self.db.drop_table(self.table_name)
                    
                    if new_data:
                        self.tbl = self.db.create_table(self.table_name, data=new_data)
                    else:
                        # Empty table re-init
                        dummy_vector = self.model.encode("init").tolist()
                        schema_data = [{
                            "id": "init_schema", 
                            "vector": dummy_vector, 
                            "text": "init", 
                            "project_id": "system",
                            "source": "system",
                            "metadata_json": "{}"
                        }]
                        self.tbl = self.db.create_table(self.table_name, data=schema_data)
                        self.tbl.delete("id = 'init_schema'")
                        
                    logger.info(f"Migration complete. {len(new_data)} records updated.")
            except Exception as e:
                logger.error(f"Error checking/migrating schema: {e}")

    def add(self, project_id: str, doc_id: str, text: str, meta: Dict[str, Any] = None):
        self.initialize()
        
        logger.info(f"Adding document {doc_id} to project {project_id}")
        vector = self.model.encode(text).tolist()
        meta = meta or {}
        # Extract source from meta if present, otherwise default to empty
        source = meta.get("source", "")
        
        data = [{
            "id": doc_id,
            "vector": vector,
            "text": text,
            "project_id": project_id,
            "source": source,
            "metadata_json": json.dumps(meta)
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

    def list_sources(self, project_id: str) -> List[str]:
        self.initialize()
        try:
            # LanceDB SQL support varies by version/backend. 
            # If 'source' column exists, we can query it.
            # If strictly using Arrow, we can fetch all and distinct in python (ok for small-medium scale)
            # or use projection.
            
            # Efficient approach: Fetch only 'source' column for project
            # .search(None) -> no vector search, just filter
            results = self.tbl.search(None)\
                .where(f"project_id = '{project_id}'")\
                .select(["source"])\
                .limit(10000)\
                .to_list()
                
            sources = set(r["source"] for r in results if r.get("source"))
            return sorted(list(sources))
        except Exception as e:
            logger.error(f"Error listing sources: {e}")
            return []

    def delete_source(self, project_id: str, source: str) -> bool:
        self.initialize()
        logger.info(f"Deleting source '{source}' for project {project_id}")
        try:
            # If source column exists
            self.tbl.delete(f"project_id = '{project_id}' AND source = '{source}'")
            return True
        except Exception as e:
            logger.error(f"Error deleting source {source}: {e}")
            # Fallback: try deleting by metadata_json if schema upgrade didn't happen
            try:
                # This is risky/slow but a fallback
                self.tbl.delete(f"project_id = '{project_id}' AND metadata_json LIKE '%\"source\": \"{source}\"%'")
                return True
            except:
                return False

    def get_stats(self, project_id: str) -> Dict[str, Any]:
        self.initialize()
        try:
            # Count chunks
            count = self.tbl.search(None).where(f"project_id = '{project_id}'").limit(100000).to_arrow().num_rows
            return {"chunk_count": count}
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"chunk_count": 0, "error": str(e)}

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
