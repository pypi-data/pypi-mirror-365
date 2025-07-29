import json
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional, Union
from urllib.parse import urlencode

import requests
import requests.adapters
from urllib3.util import Retry

from wattmaven_solarnetwork_tools.core.authentication import (
    generate_auth_header,
    get_x_sn_date,
)


class HTTPMethod(Enum):
    """The available SolarNetwork API methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


@dataclass
class SolarNetworkCredentials:
    """Credentials for authenticating with SolarNetwork."""

    token: str
    secret: str


class SolarNetworkClientError(Exception):
    """Base exception for all SolarNetwork client errors."""

    pass


class SolarNetworkClientConnectionError(SolarNetworkClientError):
    """Raised when client connection to SolarNetwork fails."""

    pass


class SolarNetworkClientAuthenticationError(SolarNetworkClientError):
    """
    Raised when client authentication with SolarNetwork fails.

    This can occur from either a 401 or 403 response.
    """

    pass


class SolarNetworkClientRetryExhaustedError(SolarNetworkClientError):
    """Raised when all client retry attempts have been exhausted."""

    def __init__(self, message: str, last_exception: Exception = None):
        super().__init__(message)
        self.last_exception = last_exception


class SolarNetworkClient:
    """
    Client for interacting with the SolarNetwork API.

    Example:
    Basic usage without retries (default):

    >>> with SolarNetworkClient() as client:
    ...     response = client.request("GET", "/solarquery/api/v1/pub/location", {
    ...         "location.timeZoneId": "Pacific/Auckland",
    ...     })

    Basic usage with retry configuration:

    >>> from urllib3.util import Retry
    >>> retry = Retry(total=5, backoff_factor=1.0, status_forcelist=[429, 500, 502, 503, 504])
    >>> with SolarNetworkClient(retry=retry) as client:
    ...     response = client.request("GET", "/solarquery/api/v1/pub/location", {
    ...         "location.timeZoneId": "Pacific/Auckland",
    ...     })
    """

    # The default host for the SolarNetwork API.
    DEFAULT_HOST = "data.solarnetwork.net"

    def __init__(
        self,
        host: str = DEFAULT_HOST,
        proxy: Optional[str] = None,
        credentials: Optional[SolarNetworkCredentials] = None,
        retry: Optional[Retry] = None,
    ):
        """
        Initialize the SolarNetwork client.

        If credentials are provided, authentication will be handled automatically.

        See https://github.com/SolarNetwork/solarnetwork/wiki/SolarNet-API-authentication-scheme-V2

        Args:
            host: The host of the SolarNetwork API.
            proxy: The proxy to use for the SolarNetwork API. If not provided, the host will be used.
            credentials: SolarNetwork authentication credentials.
            retry: Retry configuration.
        """
        self.host = host
        self.proxy = proxy
        self.credentials = credentials
        self.retry = retry
        self._session = requests.Session()

        # Configure adapter with retry behavior.
        adapter = requests.adapters.HTTPAdapter(max_retries=retry)
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)

    def _prepare_request(
        self,
        method: Union[str, HTTPMethod],
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        accept: Optional[str] = "application/json",
        use_proxy: bool = True,
    ) -> requests.Request:
        """Prepare a request with authentication headers.

        Args:
            method: HTTP method
            path: API endpoint path
            params: Query parameters
            data: Request body data
            accept: Accept header value, defaults to application/json
            use_proxy: Whether to use the proxy if it is configured.

        Returns:
            Prepared request
        """
        now = datetime.now(timezone.utc)
        date = get_x_sn_date(now)

        headers = {
            "accept": accept,
            # The host is always used in the request, rather than the proxy.
            # See https://github.com/SolarNetwork/solarnetwork/wiki/SolarQuery-Caching-Proxy
            "host": self.host,
            "x-sn-date": date,
        }

        method_str = method.value if isinstance(method, HTTPMethod) else method.upper()

        # Generate auth header only if credentials are provided
        if self.credentials:
            auth = generate_auth_header(
                self.credentials.token,
                self.credentials.secret,
                method_str,
                path,
                urlencode(params) if params else "",
                headers,
                json.dumps(data) if data else "",
                now,
            )
            headers["Authorization"] = auth

        if isinstance(data, dict):
            headers["Content-Type"] = "application/json"

        # Use the proxy if:
        # - the proxy is configured
        # - the use_proxy flag is True
        # Otherwise, use the host.
        base_url = self.proxy if (use_proxy and self.proxy) else self.host

        return requests.Request(
            method=method_str,
            url=f"https://{base_url}{path}",
            params=params,
            headers=headers,
            json=data if isinstance(data, dict) else None,
        )

    def request(
        self,
        method: Union[str, HTTPMethod],
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        accept: Optional[str] = "application/json",
        use_proxy: bool = True,
    ) -> requests.Response:
        """
        Make an authenticated request to the SolarNetwork API.

        Args:
            method: HTTP method
            path: API endpoint path
            params: Query parameters
            data: Request body data
            accept: Accept header value, defaults to application/json
            use_proxy: Whether to use the proxy if it is configured.

        Returns:
            API response

        Raises:
            SolarNetworkClientConnectionError: When connection fails
            SolarNetworkClientAuthenticationError: When authentication fails (401)
            SolarNetworkClientRetryExhaustedError: When all retry attempts are exhausted
            requests.HTTPError: For other HTTP errors
        """
        request = self._prepare_request(method, path, params, data, accept, use_proxy)
        prepared = request.prepare()

        try:
            response = self._session.send(prepared)

            # Check for authentication errors (both 401 and 403)
            if response.status_code in (401, 403):
                raise SolarNetworkClientAuthenticationError(
                    f"Authentication failed for {method} {path}: {response.text}"
                )

            return response

        except requests.exceptions.ConnectionError as e:
            raise SolarNetworkClientConnectionError(
                f"Failed to connect to {self.host}: {str(e)}"
            ) from e
        except requests.exceptions.RetryError as e:
            retry_total = self.retry.total if self.retry else 0

            raise SolarNetworkClientRetryExhaustedError(
                f"Exhausted all {retry_total} retry attempts for {method} {path}",
                last_exception=e,
            ) from e

    def __enter__(self):
        return self

    def update_retry(self, retry: Optional[Retry]) -> None:
        """Update the retry configuration for the client.

        This will affect all subsequent requests made with this client instance.

        Args:
            retry: New retry configuration. If None, disables retries.
        """
        self.retry = retry

        # Recreate the adapter with new retry strategy
        adapter = requests.adapters.HTTPAdapter(max_retries=retry)
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()
