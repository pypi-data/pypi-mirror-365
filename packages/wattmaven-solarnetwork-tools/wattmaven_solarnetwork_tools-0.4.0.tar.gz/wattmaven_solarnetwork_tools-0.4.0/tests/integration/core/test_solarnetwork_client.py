import pytest

from wattmaven_solarnetwork_tools.core.solarnetwork_client import (
    HTTPMethod,
    SolarNetworkClient,
    SolarNetworkClientAuthenticationError,
    SolarNetworkCredentials,
)


@pytest.mark.integration
class TestSolarNetworkClient:
    """Test the SolarNetworkClient class."""

    def test_get_nodes_with_valid_credentials(self, host, credentials):
        """Test that valid credentials return a 200 response."""
        with SolarNetworkClient(
            host=host,
            credentials=credentials,
        ) as client:
            response = client.request("GET", "/solarquery/api/v1/sec/nodes")
            assert response.status_code == 200
            assert response.json()["success"] is True

    def test_get_nodes_with_invalid_credentials(self, host):
        """Test that invalid credentials raise SolarNetworkClientAuthenticationError."""

        invalid_credentials = SolarNetworkCredentials(
            token="invalid-token", secret="invalid-secret"
        )
        with SolarNetworkClient(
            host=host,
            credentials=invalid_credentials,
        ) as client:
            # Should raise SolarNetworkClientAuthenticationError
            with pytest.raises(SolarNetworkClientAuthenticationError) as exc_info:
                client.request("GET", "/solarquery/api/v1/sec/nodes")

            # Verify the exception contains useful information
            assert "Authentication failed" in str(exc_info.value)
            assert "/solarquery/api/v1/sec/nodes" in str(exc_info.value)

    def test_get_nodes_without_credentials(self, host):
        """Test that missing credentials raise SolarNetworkClientAuthenticationError."""
        with SolarNetworkClient(host=host) as client:
            # Should raise SolarNetworkClientAuthenticationError
            with pytest.raises(SolarNetworkClientAuthenticationError) as exc_info:
                client.request("GET", "/solarquery/api/v1/sec/nodes")

            assert "Authentication failed" in str(exc_info.value)

    def test_get_nodes_without_token_and_secret(self, host):
        """Test that missing credentials raise SolarNetworkClientAuthenticationError."""
        with SolarNetworkClient(
            host=host,
        ) as client:
            with pytest.raises(SolarNetworkClientAuthenticationError) as exc_info:
                client.request("GET", "/solarquery/api/v1/sec/nodes")

            assert "Authentication failed" in str(exc_info.value)

    def test_lookup_locations_without_credentials(self, host):
        """Test that looking up locations is a public endpoint, so it should return 200 even if no credentials are provided."""
        with SolarNetworkClient(
            host=host,
        ) as client:
            response = client.request(
                "GET",
                "/solarquery/api/v1/pub/location",
                {
                    "location.timeZoneId": "Pacific/Auckland",
                },
            )
            assert response.status_code == 200
            assert response.json()["success"] is True

    def test_get_nodes_with_valid_credentials_using_solarquery_proxy(
        self, host, credentials, solarquery_proxy
    ):
        """Test that valid credentials return a 200 response using the SolarQuery proxy."""
        with SolarNetworkClient(
            host=host,
            proxy=solarquery_proxy,
            credentials=credentials,
        ) as client:
            response = client.request("GET", "/solarquery/api/v1/sec/nodes")
            assert response.status_code == 200
            assert response.json()["success"] is True

    def test_get_nodes_with_valid_credentials_using_method_enum(
        self, host, credentials
    ):
        """Test that the client can use the HTTPMethod enum."""
        with SolarNetworkClient(
            host=host,
            credentials=credentials,
        ) as client:
            response = client.request(HTTPMethod.GET, "/solarquery/api/v1/sec/nodes")
            assert response.status_code == 200
            assert response.json()["success"] is True

    def test_get_datum_list_with_random_order_of_parameters(
        self, host, credentials, test_node_id
    ):
        """Test that the client can handle parameters that _aren't_ in alphabetical order."""
        with SolarNetworkClient(
            host=host,
            credentials=credentials,
        ) as client:
            response = client.request(
                "GET",
                "/solarquery/api/v1/sec/datum/list",
                # Should be able to handle parameters that _aren't_ in alphabetical order.
                params={
                    "nodeId": test_node_id,
                    "startDate": "2025-01-07",
                    "endDate": "2025-01-01",
                    "aggregation": "Day",
                },
            )
            assert response.status_code == 200
            assert response.json()["success"] is True

    def test_get_datum_list_with_source_id(self, host, credentials, test_node_id):
        """Test that the client can handle source IDs."""
        with SolarNetworkClient(
            host=host,
            credentials=credentials,
        ) as client:
            response = client.request(
                "GET",
                "/solarquery/api/v1/sec/datum/list",
                params={
                    "nodeId": test_node_id,
                    # Source IDs are good to test because they must be correctly encoded.
                    "sourceId": "*/**",
                    "startDate": "2025-01-07",
                    "endDate": "2025-01-01",
                    "aggregation": "Day",
                },
            )
            assert response.status_code == 200
            assert response.json()["success"] is True

    def test_get_datum_list_with_accept_header(self, host, credentials, test_node_id):
        """Test that the client can handle the accept header."""
        with SolarNetworkClient(
            host=host,
            credentials=credentials,
        ) as client:
            response = client.request(
                "GET",
                "/solarquery/api/v1/sec/datum/list",
                params={
                    "nodeId": test_node_id,
                    "startDate": "2025-01-07",
                    "endDate": "2025-01-01",
                    "aggregation": "Day",
                },
                accept="text/csv",
            )
            assert response.status_code == 200
            assert response.headers["Content-Type"].startswith("text/csv")
