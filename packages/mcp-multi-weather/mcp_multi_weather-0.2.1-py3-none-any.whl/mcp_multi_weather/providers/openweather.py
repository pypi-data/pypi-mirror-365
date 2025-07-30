import os
import time

import aiohttp
from pydantic import PastDate

from .base import WeatherProvider
from .types import GeoCode, InvalidAuth, QuotaExceeded, Scalar, Weather


class OpenWeather(WeatherProvider):
    BASE_URL: str = 'https://api.openweathermap.org'

    api_key: str
    units: str
    lang: str

    @staticmethod
    def from_env() -> 'OpenWeather':
        api_key = os.environ.get('OPENWEATHER_API_KEY')

        if not api_key:
            raise ValueError('Missing OPENWEATHER_API_KEY env var')

        return OpenWeather(api_key=api_key)

    def __init__(self, api_key: str, units: str = 'metric', lang: str = 'en'):
        self.api_key = api_key
        self.units = units
        self.lang = lang

    async def daily_weather(self, address: str, day: PastDate) -> Weather | None:
        geocode = await self._find_geocode(address)

        if not geocode:
            return None

        response = await self._call(
            'data/3.0/onecall/timemachine',
            {
                'lat': geocode.lat,
                'lon': geocode.lon,
                'dt': int(time.mktime(day.timetuple())),
            },
        )

        if not response or 'data' not in response or not len(response['data']) > 0:
            return None

        data = response['data'][0]

        if 'weather' not in data or not len(data['weather']) > 0:
            return None

        return Weather(
            address=f'{geocode.name}, {geocode.country}',
            temperature=data['temp'],
            description=data['weather'][0]['description'],
        )

    async def _find_geocode(self, address: str) -> GeoCode | None:
        response = await self._call(
            'geo/1.0/direct',
            {
                'q': address,
                'limit': 1,
            },
        )

        if len(response) == 0:
            return None

        return GeoCode(
            name=response[0]['name'],
            country=response[0]['country'],
            lat=response[0]['lat'],
            lon=response[0]['lon'],
        )

    async def _call(self, path: str, params: dict[str, Scalar]):
        all_params = {
            'appid': self.api_key,
            'units': self.units,
            'lang': self.lang,
            **params,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(f'{OpenWeather.BASE_URL}/{path}', params=all_params) as r:
                body = await r.json()

                match r.status:
                    case 200:
                        return body
                    case 401:
                        raise InvalidAuth(body['message'])
                    case 429:
                        raise QuotaExceeded(body['message'])
                    case _:
                        raise ValueError('Error calling OpenWeather: ' + body['message'])
