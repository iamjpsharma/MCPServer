# MCP Memory Server

A persistent vector memory server for Windsurf, VS Code, and other MCP-compliant editors.

## ✅ Quickstart (5-Minute Setup)

**1. Clone and Setup**

```bash
git clone https://github.com/iamjpsharma/MCPServer.git
cd MCPServer/mcp-memory-server

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .
```

**2. Configure Windsurf / VS Code**

Add this to your `mcpServers` configuration (e.g., `~/.codeium/windsurf/mcp_config.json`):

**Note:** Replace `/ABSOLUTE/PATH/TO/...` with the actual full path to this directory.

```json
{
  "mcpServers": {
    "memory": {
      "command": "/ABSOLUTE/PATH/TO/mcp-memory-server/.venv/bin/python",
      "args": ["-m", "mcp_memory.server"],
      "env": {
        "MCP_MEMORY_PATH": "/ABSOLUTE/PATH/TO/mcp-memory-server/mcp_memory_data"
      }
    }
  }
}
```

## 🚀 Usage

### 1. Ingestion (Adding Context)

Use the included helper script `ingest.sh` to add files to a specific project.

```bash
# ingest.sh <project_name> <file1> <file2> ...

# Example: Project "Thaama"
./ingest.sh project-thaama \
  docs/architecture.md \
  src/main.py

# Example: Project "OpenClaw"
./ingest.sh project-openclaw \
  README.md \
  CONTRIBUTING.md
```

### 2. Connect in Editor

Once configured, the following tools will be available to the AI Assistant:

- **`memory_search(project_id, q)`**: Semantic search for "project-thaama", "project-openclaw", etc.
- **`memory_add(project_id, id, text)`**: Manual addition of memory fragments.

The AI will effectively have "long-term memory" of the files you ingested.

## 🛠 Troubleshooting

- **"No MCP server found" or Connection errors**:
  - Check the output of `pwd` to ensure your absolute paths in `mcp_config.json` are 100% correct.
  - Ensure the virtual environment (`.venv`) is created and dependencies are installed.

- **"Wrong project_id used"**:
  - The AI sometimes guesses the project ID. You can explicitly tell it: "Use project_id 'project-thaama'".

- **Embedding Model Downloads**:
  - On the first run, the server downloads the `all-MiniLM-L6-v2` model (approx 100MB). This may cause a slight delay on the first request.

## 📁 Repo Structure

```
/
├── src/mcp_memory/
│   ├── server.py       # Main MCP server entry point
│   ├── ingest.py       # Ingestion logic
│   └── db.py           # LanceDB wrapper
├── ingest.sh           # Helper script
├── requirements.txt    # Top-level dependencies
├── pyproject.toml      # Package config
├── mcp_memory_data/    # Persistent vector storage (gitignored)
└── README.md
```
