# MCP Memory Server

A persistent vector memory server for Windsurf, VS Code, and other MCP-compliant editors.

## Features
- **Local Vectors**: Uses `LanceDB` and `all-MiniLM-L6-v2` locally. No API keys required.
- **Persistence**: Memories are saved to disk (`./mcp_memory_data`).
- **Isolation**: Supports multiple projects via `project_id`.

## Installation

You need Python 3.10+ installed.

1. **Setup Virtual Environment**
   It's recommended to use a virtual environment to avoid conflicts.
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -e .
   ```

## Configuration

Add this to your `mcpServers` configuration (e.g., in `~/.codeium/windsurf/mcp_config.json` or VS Code MCP settings).

### Windsurf / VS Code Config

Replace `/ABSOLUTE/PATH/TO/...` with the actual path to this directory.

```json
{
  "mcpServers": {
    "memory": {
      "command": "/ABSOLUTE/PATH/TO/mcp-memory-server/.venv/bin/python",
      "args": [
        "-m",
        "mcp_memory.server"
      ],
      "env": {
        "MCP_MEMORY_PATH": "/ABSOLUTE/PATH/TO/mcp-memory-server/mcp_memory_data"
      }
    }
  }
}
```

## Usage

### Ingestion

Use the included helper script `ingest.sh` to ingest context files.

```bash
# General Usage
./ingest.sh --project <PROJECT_NAME> <FILES...>
```

**Real Example (Project "Thaama"):**
```bash
/ABSOLUTE/PATH/TO/mcp-memory-server/ingest.sh --project project-thaama \
  /path/to/PROJECT_CONTEXT.md \
  /path/to/DECISIONS.md \
  /path/to/AI_RULES.md
```

### Tools

The server exposes:
- `memory_search(project_id, q)`
- `memory_add(project_id, id, text)`

## Troubleshooting

- **First Run**: The first time you run it, it will download the embedding model (approx 100MB). This might take a few seconds.
- **Logs**: Check the editor's MCP logs if connection fails.
