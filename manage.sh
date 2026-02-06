#!/bin/bash
# Wrapper script for project management

# Get absolute path to the virtual environment python
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_CMD="$SCRIPT_DIR/.venv/bin/python"

# Check if venv exists
if [ ! -f "$PYTHON_CMD" ]; then
    echo "Error: Virtual environment not found."
    exit 1
fi

# Run the manage module
"$PYTHON_CMD" -m mcp_memory.manage "$@"
