import requests

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ..client import DayforceClient


class BaseResource:
    """Base class for all resources in the Dayforce API.

    Methods
    -------
    _generate_url(endpoint: str, g_resource_name: str | None, g_api_version: str | None) -> str
        Generate a full URL for the given endpoint.
    _prepare_request(method: str, endpoint: str | None, resource_name: str | None, api_version: str | None, **kwargs) -> requests.Request
        Prepare a request to be used for other methods, such as `_send_prepared_request`, `_paginate_request`, etc.
    _send_prepared_request(request: requests.Request) -> requests.Response
        Send a prepared request to the Dayforce API.
    _send_prepared_request_get_data(request: requests.Request)
        Wrapper around `_send_prepared_request` that converts to JSON and returns `Data` from response.
    _send_request(method: str, endpoint: str | None, resource_name: str | None, api_version: str | None, **kwargs) -> requests.Response
        Wrapper around `_prepare_request` and `_send_prepared_request` to simplify sending requests.
    _send_request_get_data(method: str, endpoint: str | None, resource_name: str | None, api_version: str | None, **kwargs)
        Wrapper around `_send_prepared_request_get_data` and `_prepare_request`, returns `Data` from response.
    _paginate_request(request: requests.Request) -> list[dict]
        Paginate through a request that returns multiple pages of results.
    _send_request_get_details(xRefCodes: list[str], build_uri: Callable[[str], str] = lambda code: code, method: str = "GET", resource_name: str | None = None, api_version: str | None = None, **kwargs) -> dict
        Can be used
    """

    def __init__(
        self, client: "DayforceClient", resource_name: str, api_version: str = "V1"
    ):
        self.config = client.config
        self.session = client.session

        self.resource_name = resource_name
        self.api_version = api_version

    def _generate_url(
        self, endpoint: str, g_resource_name: str | None, g_api_version: str | None
    ) -> str:
        """Generate a full URL for the given endpoint.

        Parameters
        ----------
        endpoint : str
            The endpoint to append to the base URL.
        g_resource_name : str, optional
            Optional service name to override the default service name.
        g_api_version : str, optional
            Optional API version to override the default API version.

        Returns
        -------
        str
            The full URL for the endpoint. Returns `https://<api_domain>/<company_id>/<api_version>/<resource_name>/<endpoint>`
        """

        api_version = g_api_version or self.api_version
        resource_name = g_resource_name or self.resource_name

        return f"{self.config.api_url}{self.config.company_id}/{api_version}/{resource_name}/{endpoint}"

    def _prepare_request(
        self,
        method: str = "GET",
        endpoint: str | None = None,
        resource_name: str | None = None,
        api_version: str | None = None,
        **kwargs,
    ) -> requests.Request:
        """Make a request to the Dayforce API.

        Parameters
        ----------
        method : str
            HTTP method (GET, POST, PUT, DELETE).
        endpoint : str
            The endpoint to call.
        resource_name : str, optional
            Optional service name to override the default service name.
        api_version : str, optional
            Optional API version to override the default API version.
        **kwargs
            Additional keyword arguments to pass to the request, such as `params`, `json`, or `data`.
        """
        return requests.Request(
            method,
            self._generate_url(endpoint or "", resource_name, api_version),
            **kwargs,
        )

    def _send_prepared_request(self, request: requests.Request) -> requests.Response:
        """Prepares and sends a request to the Dayforce API."""
        return self.session.send(self.session.prepare_request(request))

    def _send_prepared_request_get_data(self, request: requests.Request):
        """A wrapper around `send_prepared_request` to simplify sending requests and getting the data from the response."""
        return self._send_prepared_request(request).json()["Data"]

    def _send_request(
        self,
        method: str = "GET",
        endpoint: str | None = None,
        resource_name: str | None = None,
        api_version: str | None = None,
        **kwargs,
    ) -> requests.Response:
        """A wrapper around `request` and `send_prepared_request` to simplify sending requests."""
        return self._send_prepared_request(
            self._prepare_request(
                method=method,
                endpoint=endpoint,
                resource_name=resource_name,
                api_version=api_version,
                **kwargs,
            )
        )

    def _send_request_get_data(
        self,
        method: str = "GET",
        endpoint: str | None = None,
        resource_name: str | None = None,
        api_version: str | None = None,
        **kwargs,
    ):
        """A wrapper around `send_prepared_request_get_data` and `prepare_request` to simplify sending requests and getting the data from the response."""
        return self._send_prepared_request_get_data(
            self._prepare_request(
                method=method,
                endpoint=endpoint,
                resource_name=resource_name,
                api_version=api_version,
                **kwargs,
            )
        )

    def _paginate_request(self, request: requests.Request) -> list[dict]:
        """Paginate through a request that returns multiple pages of results.

        TODO: Test this method with an actual paginated endpoint."""
        data = []
        while True:
            response = self._send_prepared_request(request)
            response_data = response.json()
            data.extend(response_data["Data"])

            if response_data["Paging"]["Next"] != "":
                request.url = response_data["Paging"]["Next"]
            else:
                break

        return data

    def _send_request_get_details(
        self,
        xRefCodes: list[str],
        build_uri: Callable[[str], str] = lambda code: code,
        method: str = "GET",
        resource_name: str | None = None,
        api_version: str | None = None,
        **kwargs,
    ) -> dict:
        """Repeatidly get details for a list of xRefCodes.

        Parameters
        ----------
        xRefCodes : list[str]
            List of xRefCodes to get details for.
        build_uri : Callable[[str], str], optional
            A function to build the URI for each xRefCode that is appended after <resource_name>. Defaults to <xRefCode>.
        method : str, optional
            HTTP method to use for the request. Defaults to "GET".
        resource_name : str, optional
            Optional service name to override the default service name. Defaults to None.
        api_version : str, optional
            Optional API version to override the default API version. Defaults to None.
        **kwargs
            Additional keyword arguments to pass to the request, such as `params`, `json`, or `data`.

        Returns
        -------
        dict
            A dictionary where the keys are the xRefCodes and the values are the data returned from the API for each xRefCode.
        """
        data = {}

        for xRefCode in xRefCodes:
            data[xRefCode] = self._send_request_get_data(
                method=method,
                endpoint=build_uri(xRefCode),
                resource_name=resource_name,
                api_version=api_version,
                **kwargs,
            )

        return data
