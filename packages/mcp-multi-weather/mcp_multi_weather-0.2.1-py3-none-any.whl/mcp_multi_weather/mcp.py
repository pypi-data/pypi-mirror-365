import os
import pathlib
import tomllib

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse

from .components.weather import WeatherComponent
from .providers import OpenWeather, WeatherProvider


class MCPWeather:
    server: FastMCP[None]
    weather_component: WeatherComponent

    @staticmethod
    def from_env() -> 'MCPWeather':
        provider_name = os.environ.get('WEATHER_PROVIDER')

        if not provider_name:
            raise ValueError('Missing WEATHER_PROVIDER env var')

        match provider_name.lower():
            case 'openweather':
                return MCPWeather(OpenWeather.from_env())
            case _:
                raise ValueError(f'Unsupported WEATHER_PROVIDER: {provider_name}')

    def __init__(self, provider: WeatherProvider) -> None:
        self.server = FastMCP(
            name='mcp-multi-weather',
            dependencies=[
                'aiohttp[speedups]>=3.12.14',
                'dotenv>=0.9.9',
                'fastmcp>=2.10.6',
            ]
        )

        self.weather_component = WeatherComponent(provider=provider)

    def register_all(self) -> None:
        self.weather_component.register_all(mcp_server=self.server)  # pyright: ignore[reportUnknownMemberType]
        self.server.custom_route('/health', methods=['GET'])(self._health)

    def run(self, **kwargs: object):
        self.server.run(**kwargs)  # pyright: ignore[reportArgumentType]

    async def _health(self, _request: Request) -> PlainTextResponse:
        return PlainTextResponse('OK')

    def _load_dependencies(self):
        root_path = pathlib.Path(os.path.dirname(os.path.abspath(__file__))).parent.parent

        with open(root_path / 'pyproject.toml', 'rb') as f:
            pyproject = tomllib.load(f)

        dependencies = pyproject.get('project', {}).get('dependencies', [])

        return [d for d in dependencies if not d.startswith('fastmcp')]
