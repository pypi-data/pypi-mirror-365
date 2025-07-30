import pytest
from pytest import FixtureRequest, Parser


def pytest_addoption(parser: Parser) -> None:
    parser.addoption(
        '--ow-api-key',
        action='store',
        default=None,
        help='OpenWeather API key for real API tests',
    )


@pytest.fixture
def ow_api_key(request: FixtureRequest) -> str | None:
    return request.config.getoption('--ow-api-key')
