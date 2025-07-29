import pytest
from pydantic_settings import BaseSettings, SettingsConfigDict

from wattmaven_solarnetwork_tools.core.solarnetwork_client import (
    SolarNetworkCredentials,
)


class Settings(BaseSettings):
    """
    Settings for the tests.
    """

    solarnetwork_host: str
    solarnetwork_solarquery_proxy: str
    solarnetwork_token: str
    solarnetwork_secret: str
    solarnetwork_test_node_id: str

    model_config: SettingsConfigDict = SettingsConfigDict(env_file=".env")


settings = Settings()


@pytest.fixture
def host():
    """The host of the SolarNetwork instance to test against."""
    return settings.solarnetwork_host


@pytest.fixture
def solarquery_proxy():
    """The SolarQuery proxy to use for testing."""
    return settings.solarnetwork_solarquery_proxy


@pytest.fixture
def credentials():
    """The credentials to use for testing."""
    return SolarNetworkCredentials(
        token=settings.solarnetwork_token,
        secret=settings.solarnetwork_secret,
    )


@pytest.fixture
def test_node_id():
    """The node ID to use for testing."""
    return settings.solarnetwork_test_node_id
