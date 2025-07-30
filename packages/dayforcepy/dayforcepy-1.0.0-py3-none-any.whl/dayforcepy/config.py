from dataclasses import dataclass
from enum import Enum

import logging
import requests
from urllib3 import Retry

logger = logging.getLogger(__name__)

Environment = Enum(
    "Environment", ["production", "touch", "config", "test", "stage", "train"]
)


@dataclass
class EnvironmentConfig:
    production: str | None = None
    touch: str | None = None
    config: str | None = None
    test: str | None = None
    stage: str | None = None
    train: str | None = None


@dataclass
class DayforceConfig:
    """Configuration for Dayforce API.

    Attributes
    ----------
    username : str, optional
        Username for Dayforce API authentication
    password : str, optional
        Password for Dayforce API authentication
    ps_api_key : str, optional
        API key for PasswordState, used to retrieve `username` and `password` if not provided
    ps_password_id : str, optional
        Password ID for PasswordState, used to retrieve `username` and `password` if not provided
    environment : Environment
        Flag indicating Dayforce environment (production, touch, config, test, stage, train)
    company_id : EnvironmentConfig
        Company ID for different environments
    auth_url : EnvironmentConfig
        Authentication URL for different environments
    api_url : EnvironmentConfig
        API URL for different environments. Update these URLs if your company has differing API URLs for each environment
    retry_options : Retry
        Retry options for HTTP requests
    """

    username: str
    password: str

    environment: Environment

    company_id_config: EnvironmentConfig
    auth_url_config: EnvironmentConfig = EnvironmentConfig(
        production="https://dfid.dayforcehcm.com/connect/token",
        touch="https://dfid.dayforcehcm.com/connect/token",
        config="https://dfidconfig.np.dayforcehcm.com/connect/token",
        test="https://dfidtst.np.dayforcehcm.com/connect/token",
        stage="https://dfidtst.np.dayforcehcm.com/connect/token",
        train="https://dfidconfig.np.dayforcehcm.com/connect/token",
    )

    api_url_config: EnvironmentConfig = EnvironmentConfig(
        production="https://www.dayforcehcm.com/api/",
        touch="https://www.dayforcehcm.com/api/",
        config="https://www.dayforcehcm.com/api/",
        test="https://www.dayforcehcm.com/api/",
        stage="https://wwws.dayforcehcm.com/api/",
        train="https://www.dayforcehcm.com/api/",
    )

    retry_options: Retry = Retry(
        total=3,
        backoff_factor=1.0,
        status_forcelist=[500, 502, 503, 504, 429],
        allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    )

    def __post_init__(self):
        self.company_id = getattr(self.company_id_config, self.environment.name, "")
        self.auth_url = getattr(self.auth_url_config, self.environment.name, "")
        self.api_url = getattr(self.api_url_config, self.environment.name, "")
