import argparse
import os

from dotenv import load_dotenv

from mcp_multi_weather.mcp import MCPWeather

# Load env vars from .env file
load_dotenv()

# Create app and expose the MCP object for FastMCP's claude-desktop installer
app = MCPWeather.from_env()
app.register_all()
mcp = app.server


def args_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Run the mcp-multi-weather service')

    parser.add_argument(
        '--transport',
        choices=['http', 'stdio'],
        default=os.environ.get('MCP_TRANSPORT', 'stdio'),
        help='Transport to use: http or stdio (default: stdio)',
    )

    parser.add_argument(
        '--host',
        default=os.environ.get('MCP_HOST', '127.0.0.1'),
        help='Host to use (default: 127.0.0.1)',
    )

    parser.add_argument(
        '--port',
        default=int(os.environ.get('MCP_PORT', 4200)),
        help='Port to use (default: 4200)',
    )

    parser.add_argument(
        '--log-level',
        default=os.environ.get('MCP_LOG_LEVEL', 'INFO'),
        help='Log level to use (default INFO)',
    )

    parser.add_argument(
        '--show-banner',
        default=os.environ.get('MCP_SHOW_BANNER', 'True'),
        help='Show the FastMCP banner (default True)',
    )

    return parser.parse_args()


def main() -> None:
    cli_args = args_parser()
    run_cmd_args = {
        'transport': cli_args.transport,
        'show_banner': cli_args.show_banner.lower() == 'true',
    }

    match cli_args.transport:
        case 'http':
            run_cmd_args.update(
                {
                    'log_level': cli_args.log_level,
                    'host': cli_args.host,
                    'port': cli_args.port,
                }
            )
        case _:
            pass

    app.run(**run_cmd_args)


if __name__ == '__main__':
    main()
