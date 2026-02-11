# Use a lightweight Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MCP_MEMORY_PATH=/data

# Install system dependencies if needed (e.g., for building some python packages)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ && rm -rf /var/lib/apt/lists/*

# Copy project configuration
COPY pyproject.toml README.md ./

# Install dependencies
# We install the package in editable mode or just install it.
# Since we copy source, we can just install .
COPY src ./src
RUN pip install --no-cache-dir .

# Create directory for data persistence
# The user should mount a volume here
RUN mkdir -p /data

# Expose the HTTP port (default 8000)
EXPOSE 8000

# Default command: Run the HTTP server
CMD ["python", "-m", "mcp_memory.server_http"]
