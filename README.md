# MCP Memory Server

![License](https://img.shields.io/github/license/iamjpsharma/MCPServer?color=blue)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Release](https://img.shields.io/github/v/release/iamjpsharma/MCPServer?include_prereleases)

A persistent vector memory server for Windsurf, VS Code, and other MCP-compliant editors.

## 🌟 Philosophy

- **Privacy-first, local-first AI memory:** Your data stays on your machine.
- **No vendor lock-in:** Uses open standards and local files.
- **Built for MCP:** Designed specifically to enhance Windsurf, Cursor, and other MCP-compatible IDEs.

## ℹ️ Status (v0.1.0)

**Stable:**
- ✅ Local MCP memory with Windsurf/Cursor
- ✅ Multi-project isolation
- ✅ Ingestion of Markdown docs

**Not stable yet:**
- 🚧 Auto-ingest (file watching)
- 🚧 Memory pruning
- 🚧 Remote sync

> **Note:** This server uses **MCP stdio transport** (not HTTP) to match Windsurf/Cursor’s native MCP integration. Do not try to connect via `curl`.


## 🏥 Health Check

To verify the server binary runs correctly:

```bash
# From within the virtual environment
python -m mcp_memory.server --help
```


## ✅ Quickstart (5-Minute Setup)

**1. Clone and Setup**

```bash
git clone https://github.com/iamjpsharma/MCPServer.git
cd MCPServer

# Create virtual environment
# Mac/Linux:
python3 -m venv .venv
source .venv/bin/activate

# Windows (Command Prompt):
# python -m venv .venv
# .venv\Scripts\activate

# Install dependencies AND the package in editable mode
# (Critical step: -e . ensures the 'mcp_memory' module is found)
pip install -e .
```

**2. Configure Windsurf / VS Code**

Add this to your `mcpServers` configuration (e.g., `~/.codeium/windsurf/mcp_config.json`):

**Note:** Replace `/ABSOLUTE/PATH/TO/MCPServer` with the actual full path to the cloned directory.

```json
{
  "mcpServers": {
    "memory": {
      "command": "/ABSOLUTE/PATH/TO/MCPServer/.venv/bin/python",
      "args": ["-m", "mcp_memory.server"],
      "env": {
        "MCP_MEMORY_PATH": "/ABSOLUTE/PATH/TO/MCPServer/mcp_memory_data"
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

### 💡 Project ID Naming Convention

It is recommended to use a consistent prefix for your project IDs to avoid collisions:

- `project-thaama`
- `project-openclaw`
- `project-myapp`

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

## 🗺️ Roadmap

- [x] Local vector storage (LanceDB)
- [x] Multi-project isolation
- [x] Markdown ingestion
- [x] Fix installation instructions (Windows support, editable install)
- [x] Fix resource listing error
- [x] Improved chunking strategies (semantic chunking)
- [ ] Support for PDF ingestion
- [ ] HTTP transport wrapper
