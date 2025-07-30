from datetime import datetime, timedelta
from requests.auth import AuthBase
import requests
import logging

from .config import DayforceConfig

logger = logging.getLogger(__name__)


class DayforceAuth(AuthBase):
    """Authentication handler for Dayforce API.

    Attaches an Bearer token to the request headers, and automatically refreshes the token when it expires.

    Attributes
    ----------
    token: str
    token_expires: datetime
    """

    CLIENT_ID: str = "Dayforce.HCMAnywhere.Client"
    GRANT_TYPE: str = "password"
    DEFAULT_EXPIRES_IN: timedelta = timedelta(hours=1)

    _token: str = ""
    token_expires: datetime = datetime.min

    def __init__(self, config: DayforceConfig):
        self.config = config

    @property
    def token(self) -> str:
        """Get the Dayforce token, fetching a new one if token is expired."""

        # Return the cached token if it is still valid
        if self._token and datetime.now() < self.token_expires:
            return self._token

        logger.debug("Fetching new Dayforce token...")

        # Otherwise, fetch a new token
        response = requests.post(
            self.config.auth_url,
            data={
                "grant_type": self.GRANT_TYPE,
                "companyId": self.config.company_id,
                "username": self.config.username,
                "password": self.config.password,
                "client_id": self.CLIENT_ID,
            },
        )
        response.raise_for_status()

        logger.debug("Successfully recieved new Dayforce token.")

        token_data = response.json()
        self._token = token_data["access_token"]
        self.token_expires = datetime.now() + timedelta(
            seconds=token_data.get(
                "expires_in", self.DEFAULT_EXPIRES_IN.total_seconds()
            )
        )  # Set the token expiration time, defaulting to 1 hour if not provided

        return self._token

    def __call__(self, r: requests.PreparedRequest) -> requests.PreparedRequest:
        """Attach the token to the request."""
        r.headers["Authorization"] = f"Bearer {self.token}"
        return r
