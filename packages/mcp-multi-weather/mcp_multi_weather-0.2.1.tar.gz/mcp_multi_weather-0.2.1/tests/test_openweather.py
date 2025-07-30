from datetime import date

import pytest

from mcp_multi_weather.providers.openweather import OpenWeather
from mcp_multi_weather.providers.types import Weather


class TestOpenWeatherClient:
    async def test_daily_weather(self, ow_api_key: str | None):
        if not ow_api_key:
            pytest.skip('No OpenWeather API key provided via --ow-api-key')

        ow = OpenWeather(api_key=str(ow_api_key))
        day = date(2023, 1, 1)

        weather = await ow.daily_weather('London', day)

        assert isinstance(weather, Weather)
        assert weather.address == 'London, GB'
        assert weather.temperature == 12.54
        assert weather.description == 'light rain'
