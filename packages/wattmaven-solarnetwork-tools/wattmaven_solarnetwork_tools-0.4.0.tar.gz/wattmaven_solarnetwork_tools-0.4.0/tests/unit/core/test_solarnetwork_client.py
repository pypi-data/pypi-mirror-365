from unittest.mock import Mock, patch

import pytest
import requests
from urllib3 import Retry

from wattmaven_solarnetwork_tools.core.solarnetwork_client import (
    SolarNetworkClient,
    SolarNetworkClientAuthenticationError,
    SolarNetworkClientConnectionError,
    SolarNetworkClientError,
    SolarNetworkClientRetryExhaustedError,
    SolarNetworkCredentials,
)


@pytest.mark.unit
class TestSolarNetworkClientExceptions:
    """Test the SolarNetworkClient exception hierarchy."""

    def test_base_exception(self):
        """Test the base SolarNetworkClientError exception."""
        error = SolarNetworkClientError("Base error message")

        assert str(error) == "Base error message"
        assert isinstance(error, Exception)

    def test_connection_error_inheritance(self):
        """Test that SolarNetworkClientConnectionError inherits from SolarNetworkClientError."""
        error = SolarNetworkClientConnectionError("Connection failed")

        assert str(error) == "Connection failed"
        assert isinstance(error, SolarNetworkClientError)
        assert isinstance(error, Exception)

    def test_authentication_error_inheritance(self):
        """Test that SolarNetworkClientAuthenticationError inherits from SolarNetworkClientError."""
        error = SolarNetworkClientAuthenticationError("Auth failed")

        assert str(error) == "Auth failed"
        assert isinstance(error, SolarNetworkClientError)
        assert isinstance(error, Exception)

    def test_retry_exhausted_error_basic(self):
        """Test SolarNetworkClientRetryExhaustedError without last_exception."""
        error = SolarNetworkClientRetryExhaustedError("Retries exhausted")

        assert str(error) == "Retries exhausted"
        assert error.last_exception is None
        assert isinstance(error, SolarNetworkClientError)
        assert isinstance(error, Exception)

    def test_retry_exhausted_error_with_last_exception(self):
        """Test SolarNetworkClientRetryExhaustedError with last_exception."""
        original_error = ValueError("Original error")
        error = SolarNetworkClientRetryExhaustedError(
            "Retries exhausted", last_exception=original_error
        )

        assert str(error) == "Retries exhausted"
        assert error.last_exception == original_error
        assert isinstance(error.last_exception, ValueError)

    def test_exception_catching_hierarchy(self):
        """Test that all specific exceptions can be caught by base exception."""
        exceptions = [
            SolarNetworkClientConnectionError("Connection error"),
            SolarNetworkClientAuthenticationError("Auth error"),
            SolarNetworkClientRetryExhaustedError("Retry error"),
        ]

        for exc in exceptions:
            # All should be catchable by the base exception
            assert isinstance(exc, SolarNetworkClientError)

            # Test actual exception catching
            try:
                raise exc
            except SolarNetworkClientError:
                pass  # Should catch all SolarNetwork exceptions

    def test_specific_exception_catching(self):
        """Test catching specific exception types."""
        # Test SolarNetworkClientConnectionError
        try:
            raise SolarNetworkClientConnectionError("Connection failed")
        except SolarNetworkClientConnectionError as e:
            assert str(e) == "Connection failed"

        # Test SolarNetworkClientAuthenticationError
        try:
            raise SolarNetworkClientAuthenticationError("Auth failed")
        except SolarNetworkClientAuthenticationError as e:
            assert str(e) == "Auth failed"

        # Test SolarNetworkClientRetryExhaustedError
        try:
            raise SolarNetworkClientRetryExhaustedError("Retries exhausted")
        except SolarNetworkClientRetryExhaustedError as e:
            assert str(e) == "Retries exhausted"

    def test_retry_exhausted_error_chaining(self):
        """Test exception chaining with SolarNetworkClientRetryExhaustedError."""
        try:
            # Simulate original failure
            try:
                raise ConnectionError("Network unreachable")
            except ConnectionError as e:
                raise SolarNetworkClientRetryExhaustedError(
                    "Failed after 3 retries", last_exception=e
                ) from e
        except SolarNetworkClientRetryExhaustedError as retry_error:
            assert "Failed after 3 retries" in str(retry_error)
            assert isinstance(retry_error.last_exception, ConnectionError)
            assert str(retry_error.last_exception) == "Network unreachable"
            assert retry_error.__cause__ is retry_error.last_exception

    def test_exception_attributes_preserved(self):
        """Test that custom exception attributes are preserved."""
        original_error = RuntimeError("Runtime issue")
        retry_error = SolarNetworkClientRetryExhaustedError(
            "Max retries reached", last_exception=original_error
        )

        # Verify attributes are preserved when re-raising
        try:
            raise retry_error
        except SolarNetworkClientRetryExhaustedError as caught:
            assert caught.last_exception is original_error
            assert str(caught) == "Max retries reached"


@pytest.mark.unit
class TestSolarNetworkClient:
    """Test the SolarNetworkClient class."""

    @pytest.fixture
    def client(self):
        """Create a basic client for testing."""
        credentials = SolarNetworkCredentials(token="test-token", secret="test-secret")
        return SolarNetworkClient(credentials=credentials)

    @pytest.fixture
    def client_with_retry(self):
        """Create a client with retry configuration."""
        credentials = SolarNetworkCredentials(token="test-token", secret="test-secret")
        retry = Retry(total=3, backoff_factor=1.0)
        return SolarNetworkClient(credentials=credentials, retry=retry)

    def test_connection_error_handling(self, client):
        """Test that ConnectionError is properly wrapped and chained."""
        original_error = requests.exceptions.ConnectionError("Network unreachable")

        with patch.object(client._session, "send", side_effect=original_error):
            with pytest.raises(SolarNetworkClientConnectionError) as exc_info:
                client.request("GET", "/test/path")

            # Verify the error message format
            assert f"Failed to connect to {client.host}" in str(exc_info.value)
            assert "Network unreachable" in str(exc_info.value)

            # Verify exception chaining
            assert exc_info.value.__cause__ is original_error

    def test_connection_error_with_custom_host(self):
        """Test ConnectionError with a custom host."""
        custom_host = "custom.solarnetwork.net"
        client = SolarNetworkClient(host=custom_host)
        original_error = requests.exceptions.ConnectionError("DNS resolution failed")

        with patch.object(client._session, "send", side_effect=original_error):
            with pytest.raises(SolarNetworkClientConnectionError) as exc_info:
                client.request("GET", "/test/path")

            assert f"Failed to connect to {custom_host}" in str(exc_info.value)

    def test_retry_error_without_retry_config(self, client):
        """Test RetryError handling when no retry is configured."""
        original_error = requests.exceptions.RetryError("Max retries exceeded")

        with patch.object(client._session, "send", side_effect=original_error):
            with pytest.raises(SolarNetworkClientRetryExhaustedError) as exc_info:
                client.request("GET", "/test/path")

            # Should show 0 retries when no retry config
            assert "Exhausted all 0 retry attempts for GET /test/path" in str(
                exc_info.value
            )
            assert exc_info.value.last_exception is original_error
            assert exc_info.value.__cause__ is original_error

    def test_retry_error_with_retry_config(self, client_with_retry):
        """Test RetryError handling when retry is configured."""
        original_error = requests.exceptions.RetryError("Max retries exceeded")

        with patch.object(
            client_with_retry._session, "send", side_effect=original_error
        ):
            with pytest.raises(SolarNetworkClientRetryExhaustedError) as exc_info:
                client_with_retry.request("POST", "/api/data", {"key": "value"})

            # Should show configured retry count
            assert "Exhausted all 3 retry attempts for POST /api/data" in str(
                exc_info.value
            )
            assert exc_info.value.last_exception is original_error
            assert exc_info.value.__cause__ is original_error

    @pytest.mark.parametrize(
        "method,path",
        [
            ("GET", "/solarquery/api/v1/sec/nodes"),
            ("POST", "/solarin/api/v1/sec/datum"),
            ("PUT", "/solaruser/api/v1/sec/user/me"),
            ("DELETE", "/solaruser/api/v1/sec/auth-tokens/123"),
        ],
    )
    def test_retry_error_with_different_methods_and_paths(
        self, client_with_retry, method, path
    ):
        """Test that method and path are correctly included in retry error messages."""
        original_error = requests.exceptions.RetryError("Retries failed")

        with patch.object(
            client_with_retry._session, "send", side_effect=original_error
        ):
            with pytest.raises(SolarNetworkClientRetryExhaustedError) as exc_info:
                client_with_retry.request(method, path)

            expected_msg = f"Exhausted all 3 retry attempts for {method} {path}"
            assert expected_msg in str(exc_info.value)

    def test_connection_error_preserves_request_details(self, client):
        """Test that connection errors preserve request context."""
        original_error = requests.exceptions.ConnectionError("Connection timeout")

        # Test with various request parameters
        with patch.object(client._session, "send", side_effect=original_error):
            with pytest.raises(SolarNetworkClientConnectionError):
                client.request(
                    "GET",
                    "/test/path",
                    params={"param1": "value1"},
                    data={"data": "test"},
                )

    def test_retry_error_with_zero_retry_config(self):
        """Test RetryError when retry is explicitly set to 0."""
        credentials = SolarNetworkCredentials(token="test-token", secret="test-secret")
        retry = Retry(total=0)
        client = SolarNetworkClient(credentials=credentials, retry=retry)

        original_error = requests.exceptions.RetryError("No retries allowed")

        with patch.object(client._session, "send", side_effect=original_error):
            with pytest.raises(SolarNetworkClientRetryExhaustedError) as exc_info:
                client.request("GET", "/test")

            assert "Exhausted all 0 retry attempts for GET /test" in str(exc_info.value)

    def test_other_request_exceptions_not_caught(self, client):
        """Test that other request exceptions are not wrapped."""
        # Test that non-ConnectionError/RetryError exceptions pass through
        original_error = requests.exceptions.Timeout("Request timeout")

        with patch.object(client._session, "send", side_effect=original_error):
            with pytest.raises(requests.exceptions.Timeout):
                client.request("GET", "/test/path")

    def test_successful_request_after_error_setup(self, client):
        """Test that client works normally when no errors occur."""
        # Mock a successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}

        with patch.object(client._session, "send", return_value=mock_response):
            response = client.request("GET", "/test/path")
            assert response.status_code == 200

    def test_retry_config_update_affects_error_messages(self, client):
        """Test that updating retry config affects error messages."""
        original_error = requests.exceptions.RetryError("Retries failed")

        # Initially no retry config
        with patch.object(client._session, "send", side_effect=original_error):
            with pytest.raises(SolarNetworkClientRetryExhaustedError) as exc_info:
                client.request("GET", "/test")
            assert "Exhausted all 0 retry attempts" in str(exc_info.value)

        # Update retry config
        new_retry = Retry(total=5)
        client.update_retry(new_retry)

        # Should now show updated retry count
        with patch.object(client._session, "send", side_effect=original_error):
            with pytest.raises(SolarNetworkClientRetryExhaustedError) as exc_info:
                client.request("GET", "/test")
            assert "Exhausted all 5 retry attempts" in str(exc_info.value)

    def test_exception_attributes_preservation(self, client_with_retry):
        """Test that all exception attributes are properly preserved."""
        original_retry_error = requests.exceptions.RetryError("Custom retry message")

        with patch.object(
            client_with_retry._session, "send", side_effect=original_retry_error
        ):
            with pytest.raises(SolarNetworkClientRetryExhaustedError) as exc_info:
                client_with_retry.request("PATCH", "/api/update")

            retry_error = exc_info.value

            # Check all attributes
            assert retry_error.last_exception is original_retry_error
            assert retry_error.__cause__ is original_retry_error
            assert "PATCH /api/update" in str(retry_error)
            assert "3 retry attempts" in str(retry_error)
