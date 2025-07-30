from pydantic import BaseModel

Scalar = str | int | float | bool


class Weather(BaseModel):
    address: str
    temperature: float
    description: str

    def explain(self):
        return f'The temperature in {self.address} was {self.temperature}C. The weather was {self.description}'


class GeoCode(BaseModel):
    name: str
    country: str
    lat: float
    lon: float


class InvalidAuth(ValueError):
    pass


class QuotaExceeded(Exception):
    pass
