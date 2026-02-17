# MCP Memory Server

![License](https://img.shields.io/github/license/iamjpsharma/MCPServer?color=blue)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Release](https://img.shields.io/github/v/release/iamjpsharma/MCPServer?include_prereleases)

A persistent vector memory server for Windsurf, VS Code, and other MCP-compliant editors.

## 🌟 Philosophy

- **Privacy-first, local-first AI memory:** Your data stays on your machine.
- **No vendor lock-in:** Uses open standards and local files.
- **Built for MCP:** Designed specifically to enhance Windsurf, Cursor, and other MCP-compatible IDEs.

## ℹ️ Status (v0.2.0)

**Stable:**
- ✅ Local MCP memory with Windsurf/Cursor
- ✅ Multi-project isolation
- ✅ Ingestion of Markdown docs

**Not stable yet:**
- 🚧 Auto-ingest (file watching)
- 🚧 Memory pruning
- 🚧 Remote sync

> **Note:** There are two ways to run this server:
> 1. **Local IDE (stdio)**: Used by Windsurf/Cursor (default).
> 2. **Docker/Server (HTTP)**: Used for remote deployments or Docker (exposes port 8000).


## 🏥 Health Check

To verify the server binary runs correctly:

```bash
# From within the virtual environment
python -m mcp_memory.server --help
```


## ✅ Quickstart (5-Minute Setup)

There are two ways to set this up: **Global Install** (recommended for ease of use) or **Local Dev**.

### Option A: Global Install (Like `npm -g`)

This method allows you to run `mcp-memory` from anywhere without managing virtual environments manually.

**Prerequisites:**
- Python 3.10+
- [`pipx`](https://github.com/pypa/pipx) (Recommended: `brew install pipx` on macOS)

```bash
# Install directly from GitHub
pipx install git+https://github.com/iamjpsharma/MCPServer.git

# Verify installation
mcp-memory --help
```

**Configure Windsurf / VS Code:**

Since `pipx` puts the executable in your PATH, the config is simpler:

```json
{
  "mcpServers": {
    "memory": {
      "command": "mcp-memory",
      "args": [],
      "env": {
        "MCP_MEMORY_PATH": "/ABSOLUTE/PATH/TO/YOUR/DATA/DIR"
      }
    }
  }
}
```

### Option B: Local Dev Setup

**1. Clone and Setup**

```bash
git clone https://github.com/iamjpsharma/MCPServer.git
cd MCPServer

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies AND the package in editable mode
pip install -e .
```

**2. Configure Windsurf / VS Code (Local Dev)**

## 🚀 Usage

### 0. HTTP Server (New)

You can run the server via HTTP (SSE) if you prefer:

```bash
# Run on port 8000
python -m mcp_memory.server_http
```

Access the SSE endpoint at `http://localhost:8000/sse` and send messages to `http://localhost:8000/messages`.

### 🐳 Run with Docker

To run the server in a container:

```bash
# Build the image
docker build -t mcp-memory .

# Run the container
# Mount your local data directory to /data inside the container
docker run -p 8000:8000 -v $(pwd)/mcp_memory_data:/data mcp-memory
```

The server will be available at `http://localhost:8000/sse`.

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

- **`memory_search(project_id, q, filter=None)`**: Semantic search. Supports metadata filtering (e.g., `filter={"type": "code"}`). Returns distance scores.
- **`memory_add(project_id, id, text)`**: Manual addition.
- **`memory_list_sources(project_id)`**: specific files ingested.
- **`memory_delete_source(project_id, source)`**: Remove a specific file.
- **`memory_stats(project_id)`**: Get chunk count.
- **`memory_reset(project_id)`**: Clear all memories for a project.

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

### ✅ Completed (v0.1.x)
- [x] Local vector storage (LanceDB)
- [x] Multi-project isolation
- [x] Markdown ingestion
- [x] PDF ingestion
- [x] Semantic chunking strategies
- [x] Windows support + editable install fixes
- [x] HTTP transport wrapper (SSE)
- [x] Fix resource listing errors (clean MCP UX)
- [x] Robust docs + 5-minute setup
- [x] Multi-IDE support (Windsurf, Cursor-compatible MCP)

### 🚀 Near-Term (v0.2.x – Production Readiness)
**🧠 Memory Governance**
- [x] List memory sources per project
- [x] Delete memory by source (file-level deletion)
- [x] Reset memory per project
- [x] Replace / reindex mode (prevent stale chunks)
- [x] Memory stats (chunk count, last updated, size)

**🎯 Retrieval Quality**
- [x] Metadata filtering (e.g., type=decision | rules | context)
- [x] Similarity scoring in results
- [ ] Hybrid search (semantic + keyword)
- [ ] Return evidence + similarity scores with search results
- [ ] Configurable top_k defaults per project

**⚙️ Dev Workflow**
- [ ] Auto-ingest on git commit / file change
- [ ] `mcp-memory init <project-id>` bootstrap command
- [ ] Project templates (PROJECT_CONTEXT.md, DECISIONS.md, AI_RULES.md)

### 🧠 Advanced RAG (v0.3.x – Differentiators)
- [ ] Hierarchical retrieval (summary-first, detail fallback)
- [ ] Memory compression (old chunks → summaries)
- [ ] Temporal ranking (prefer newer decisions)
- [ ] Scoped retrieval (planner vs coder vs reviewer agents)
- [ ] Query rewrite / expansion for better recall

### 🏢 Team / SaaS Mode (Optional)
*Philosophy: Local-first remains the default. SaaS is an optional deployment mode.*

**🔐 Auth & Multi-Tenancy**
- [ ] Project-level auth (API keys or JWT)
- [ ] Org / team separation
- [ ] Audit logs for memory changes

**☁️ Remote Storage Backends (Pluggable)**
- [ ] S3-compatible vector store backend
- [ ] Postgres / pgvector backend
- [ ] Sync & Federation (Local ↔ Remote)

### 🚫 Non-Goals
- ❌ No mandatory cloud dependency
- ❌ No vendor lock-in
- ❌ No chat history as “memory” by default (signal > noise)
- ❌ No model fine-tuning
