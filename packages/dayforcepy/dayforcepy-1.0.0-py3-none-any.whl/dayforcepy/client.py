import requests
import logging

from requests.adapters import HTTPAdapter

from .config import DayforceConfig
from .auth import DayforceAuth

logger = logging.getLogger(__name__)


class DayforceClient:
    """Central client for interacting with the Dayforce API.

    This client holds the configuration, session, and resources for interacting with the Dayforce API.

    Attributes
    ----------
    config: DayforceConfig
        Configuration object containing API credentials and settings.
    session: requests.Session
        A requests session that handles authentication and retries.
    """

    def __init__(self, config: DayforceConfig):
        self.config = config
        self.session = requests.Session()

        self.session.auth = DayforceAuth(config=config)
        self.session.mount(
            "https://",
            HTTPAdapter(max_retries=self.config.retry_options),
        )  # Add retry logic for HTTPS requests
        self.session.hooks = {"response": [self._api_response_hook]}

    def _api_response_hook(self, response: requests.Response):
        """Handle the response from the API.

        Logs Dayforce processResults if they exist.
        Raises an error if the response status code is not 2xx.
        """
        # Log Dayforce results if they exist
        data = response.json()
        if "processResults" in data:
            for result in data["processResults"]:
                message = f"Context: ({result['context']}) Code: ({result['code']}) Message: {result['message']}"
                match result["level"]:
                    case "ERROR":
                        logger.error(message)
                    case "WARNING":
                        logger.warning(message)
                    case "INFO":
                        logger.info(message)

        # Raise an error if the response status code is not 2xx
        response.raise_for_status()
