from abc import ABC, abstractmethod

from pydantic import PastDate

from .types import Weather


class WeatherProvider(ABC):
    @abstractmethod
    async def daily_weather(self, address: str, day: PastDate) -> Weather | None:
        pass
