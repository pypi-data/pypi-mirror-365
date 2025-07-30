FROM ghcr.io/astral-sh/uv:python3.13-alpine

WORKDIR /app
EXPOSE 4200

# Enable bytecode compilation and copy from cache instead of linking
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Install the project's dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
  --mount=type=bind,source=uv.lock,target=uv.lock \
  --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
  uv sync --locked --no-install-project --no-dev

# Add the rest of the project
COPY pyproject.toml uv.lock README.md /app/
COPY src /app/src

# Install the app
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --locked --no-dev

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# App Env Vars
ENV MCP_TRANSPORT=http \
  MCP_HOST=0.0.0.0 \
  MCP_PORT=4200 \
  MCP_LOG_LEVEL=info \
  MCP_SHOW_BANNER=false

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# Run the application
CMD ["python", "./src/mcp_multi_weather/cli/server.py"]
