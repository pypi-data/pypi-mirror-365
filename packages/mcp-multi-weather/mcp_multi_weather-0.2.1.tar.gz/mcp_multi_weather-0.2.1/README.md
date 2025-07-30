# mcp-multi-weather

## Description

MCP server for checking the weather history and forecast. This Model Context Protocol (MCP) server
provides weather data functionality through a FastMCP-based service that integrates with weather
providers to deliver historical weather information.

The server exposes a `get_historical_weather` tool that allows checking weather conditions for
specific cities on past dates, making it useful for applications that need historical weather data.

## How to run it

First you need to create a valid API key with OpenWeather, and set it in your env file:

```
$ cp .env.example .env
$ vim .env # Modify the values
```

Now you can run the server locally:

```
$ uv run mcp-multi-weather
```

Or, you can install the package in your claude-desktop:

```
$ uv run fastmcp install claude-desktop src/mcp_multi_weather/cli/server.py --env-file .env --env PYTHONPATH=$PWD/src/
```

## Development

You can run the tests using pytest:

```
$ uv run pytest
$ uv run pytest --ow-api-key=DUMMY  # To run tests against the real OpenWeather API
```

You can also check the syntax and lint the code with pyright and ruff:

```
$ uv run pyright
$ uv run ruff check
$ uv run ruff format
```
