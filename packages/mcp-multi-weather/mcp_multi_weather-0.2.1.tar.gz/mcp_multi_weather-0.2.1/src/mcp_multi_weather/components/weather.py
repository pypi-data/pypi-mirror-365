from fastmcp import Context
from fastmcp.contrib.mcp_mixin import MCPMixin, mcp_tool
from mcp.types import ToolAnnotations
from pydantic import PastDate

from ..providers import WeatherProvider
from ..providers.types import Weather


class WeatherComponent(MCPMixin):
    weather_provider: WeatherProvider

    def __init__(self, provider: WeatherProvider):
        self.weather_provider = provider

    @mcp_tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def get_historical_weather(
        self, address: str, day: PastDate, ctx: Context
    ) -> Weather | None:
        """
        Get historical weather data for a specific city and date.

        Returns temperature, sky conditions, and general weather information for past dates only.

        Arguments:
            `address`: City and country (format: "City, Country")
            `day`: Date in ISO8601 format (YYYY-MM-DD)
        """
        await ctx.debug(f'Getting historical weather for {address} on {day}')
        result = await self.weather_provider.daily_weather(address, day)

        if not result:
            await ctx.debug(f'No historical weather for {address} on {day}')
            return None

        return result
