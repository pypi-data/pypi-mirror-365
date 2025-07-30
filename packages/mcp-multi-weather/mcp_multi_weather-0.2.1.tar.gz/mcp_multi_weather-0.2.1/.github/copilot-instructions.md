# MCP Weather Server - AI Coding Instructions

## Architecture Overview

This is a **Model Context Protocol (MCP) server** built with FastMCP that provides historical
weather data through a `get_historical_weather` tool. The architecture follows a clean provider
pattern:

- **Entry Point**: `src/mcp_multi_weather/cli/server.py` - CLI module with args parser and server initialization
- **MCP Server**: `src/mcp_multi_weather/mcp.py` - FastMCP server setup with health endpoint
- **Components**: `src/mcp_multi_weather/components/weather.py` - MCP tools using `@mcp_tool` decorator
- **Providers**: `src/mcp_multi_weather/providers/` - Abstract weather provider pattern with OpenWeather implementation

## Key Patterns & Conventions

### Provider Pattern

- Abstract base in `providers/base.py` with `WeatherProvider` interface
- Concrete implementations like `OpenWeatherProvider` with static `from_env()` factory methods
- Environment-driven provider selection in `MCPWeather.from_env()`

### FastMCP Integration

- Use `MCPMixin` for components with `@mcp_tool` decorated methods
- Tools return human-readable strings, not structured data
- `PastDate` type validation ensures historical-only queries
- Context parameter for debug logging: `await ctx.debug(message)`
- **CLI Module Pattern**: `cli/server.py` exposes module-level `app` and `mcp` objects for FastMCP's claude-desktop installer

### Error Handling

- Custom exceptions: `InvalidAuth`, `QuotaExceeded` in provider types
- Graceful degradation: return `None` for missing data, descriptive messages for failures
- HTTP status code mapping in OpenWeather provider (401→InvalidAuth, 429→QuotaExceeded)

## Development Workflow

### Environment Setup

```bash
# Required: Copy and configure API key
cp .env.example .env

# Install and run locally
uv run mcp-multi-weather

# Install in Claude Desktop
uv run fastmcp install claude-desktop src/mcp_multi_weather/cli/server.py --env-file .env --env PYTHONPATH=$PWD/src/
```

### Testing Patterns

- Mock external APIs using `aioresponses` in test files
- Test helper functions in `tests/mocks.py` generate OpenWeather API URLs and responses
- Use `# type: ignore[reportUnknownMemberType]` for FastMCP-related type issues

### Code Quality

- **Pyright strict mode** with selective ignores in `pyproject.toml`
- **Ruff formatting**: single quotes, 100-char line length
- **Async-first**: all external calls are async, use `pytest-asyncio`

## Critical Files to Understand

- `src/mcp_multi_weather/cli/server.py` - CLI entry point with module-level app/mcp exports for FastMCP integration
- `src/mcp_multi_weather/mcp.py` - Server initialization and component registration pattern
- `src/mcp_multi_weather/components/weather.py` - MCP tool implementation with proper annotations
- `src/mcp_multi_weather/providers/openweather.py` - API integration with error handling patterns
- `tests/test_main.py` - Integration testing with mocked external services

## Transport & Deployment

- Supports both HTTP (default, port 4200) and stdio transports
- Environment variables: `MCP_TRANSPORT`, `MCP_HOST`, `MCP_PORT`, `WEATHER_PROVIDER`
- Docker containerization available via `Makefile`
- Health endpoint at `/health` returns plain text "OK"
