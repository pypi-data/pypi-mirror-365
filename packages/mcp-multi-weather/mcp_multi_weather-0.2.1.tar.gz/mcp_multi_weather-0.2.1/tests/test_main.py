# type: ignore[reportUnknownMemberType]
from datetime import date, timedelta

import pytest
from aioresponses import aioresponses
from fastmcp import Client
from fastmcp.exceptions import ToolError

from mcp_multi_weather.mcp import MCPWeather
from mcp_multi_weather.providers import OpenWeather

from .mocks import ow_error, ow_geocode_mock, ow_timemachine_mock


class TestMCPWeather:
    mcp: MCPWeather

    def setup_method(self):
        self.mcp = MCPWeather(provider=OpenWeather(api_key='dummy'))
        self.mcp.register_all()

    async def test_get_weather_with_good_arguments(self):
        geocode_url, geocode_response = ow_geocode_mock(
            city='Madrid', country='ES', lat=50.0, lon=0.0
        )
        timemachine_url, timemachine_response = ow_timemachine_mock(
            lat=50.0, lon=0.0, temp=20, day='2024-01-01', description='cloudy'
        )

        with aioresponses() as mock:
            mock.get(geocode_url, payload=geocode_response)
            mock.get(timemachine_url, payload=timemachine_response)

            async with Client(self.mcp.server) as client:
                result = await client.call_tool(
                    'get_historical_weather', {'address': 'Madrid, ES', 'day': '2024-01-01'}
                )
                assert result.data == {
                    'address': 'Madrid, ES',
                    'description': 'cloudy',
                    'temperature': 20.0,
                }

    async def test_get_weather_with_future_day(self):
        future_day = (date.today() + timedelta(days=1)).isoformat()

        async with Client(self.mcp.server) as client:
            with pytest.raises(ToolError, match='Date should be in the past'):
                await client.call_tool(
                    'get_historical_weather', {'address': 'London, UK', 'day': future_day}
                )

    async def test_get_weather_with_invalid_auth(self):
        geocode_url, geocode_response = ow_geocode_mock(
            city='Madrid', country='ES', lat=50.0, lon=0.0
        )
        timemachine_url, _ = ow_timemachine_mock(lat=50.0, lon=0.0, day='2024-01-01')

        with aioresponses() as mock:
            mock.get(geocode_url, payload=geocode_response)
            mock.get(
                timemachine_url, payload=ow_error(code=401, message='Invalid API key'), status=401
            )

            async with Client(self.mcp.server) as client:
                with pytest.raises(ToolError, match='Invalid API key'):
                    await client.call_tool(
                        'get_historical_weather', {'address': 'Madrid, ES', 'day': '2024-01-01'}
                    )

    async def test_get_weather_with_quota_exceeded(self):
        geocode_url, geocode_response = ow_geocode_mock(
            city='Madrid', country='ES', lat=50.0, lon=0.0
        )
        timemachine_url, _ = ow_timemachine_mock(lat=50.0, lon=0.0, day='2024-01-01')

        with aioresponses() as mock:
            mock.get(geocode_url, payload=geocode_response)
            mock.get(
                timemachine_url,
                payload=ow_error(code=429, message='API rate limit exceeded'),
                status=429,
            )

            async with Client(self.mcp.server) as client:
                with pytest.raises(ToolError, match='API rate limit exceeded'):
                    await client.call_tool(
                        'get_historical_weather', {'address': 'Madrid, ES', 'day': '2024-01-01'}
                    )

    async def test_get_weather_with_city_not_found(self):
        geocode_url, _ = ow_geocode_mock(city='NonExistentCity', country='ES', lat=5, lon=0)

        with aioresponses() as mock:
            mock.get(geocode_url, payload=[])

            async with Client(self.mcp.server) as client:
                result = await client.call_tool(
                    'get_historical_weather',
                    {'address': 'NonExistentCity, ES', 'day': '2025-01-01'},
                )
                assert result.data is None
