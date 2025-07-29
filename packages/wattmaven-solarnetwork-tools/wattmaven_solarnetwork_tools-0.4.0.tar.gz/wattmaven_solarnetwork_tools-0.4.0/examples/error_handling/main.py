"""
Example of how to handle errors from the SolarNetworkClient.
"""

from settings import settings

from wattmaven_solarnetwork_tools.core.solarnetwork_client import (
    SolarNetworkClient,
    SolarNetworkClientAuthenticationError,
    SolarNetworkCredentials,
)


def get_nodes() -> list[int]:
    """
    Get all nodes from the SolarNetwork API. This will raise a SolarNetworkClientAuthenticationError if the credentials
    are invalid.

    Returns:
        list[int]: A list of node IDs.
    """
    try:
        with SolarNetworkClient(
            host=settings.solarnetwork_host,
            proxy=settings.solarnetwork_solarquery_proxy,
            credentials=SolarNetworkCredentials(
                token="invalid-token",
                secret="invalid-secret",
            ),
        ) as client:
            response = client.request("GET", "/solarquery/api/v1/sec/nodes")
            json = response.json()
            return json["data"]
    except SolarNetworkClientAuthenticationError as e:
        print(f"Authentication error: {e}")
        return []


def main():
    nodes = get_nodes()
    print(nodes)


if __name__ == "__main__":
    main()
