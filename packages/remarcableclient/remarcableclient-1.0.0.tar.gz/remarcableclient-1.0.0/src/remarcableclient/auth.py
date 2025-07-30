from datetime import datetime, timedelta
import requests
from requests.auth import AuthBase

# Hacky solution to avoid circular import issues
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import RemarcableClient


class RemarcableAuth(AuthBase):
    """Authentication handler for Remarcable API requests.

    This class manages authentication for the Remarcable API, supporting both API key and
    email/password-based authentication. If an API key is provided in the configuration,
    it is used directly. Otherwise, the class will obtain and cache an authentication token
    using the provided email and password, automatically refreshing the token as needed.

    Parameters
    ----------
    client : RemarcableClient
        The RemarcableClient instance containing configuration and logger.

    Attributes
    ----------
    token : str
        Returns the current authentication token, refreshing it if necessary.

    Notes
    -----
    - If the API key is present in the configuration, it is always used for authentication.
    - If using email and password, the token is automatically refreshed when expired.
    - No retry logic is implemented for token refresh failures.
    """

    _TOKEN_EXPIRES_DEFAULT = timedelta(hours=8)

    # Used if no API key is provided, and email and password are used instead.
    _token: str = ""
    _token_expires: datetime = datetime.min

    def __init__(self, client: "RemarcableClient"):
        self._client = client
        self._config = client._config

    @property
    def token(self) -> str:
        """API Token for authentication.

        Based on the provided configuration, this property will return the API key
        or if an email and password are provided, it will return a found token, or
        refresh the token if necessary.

        Returns
        -------
        str
            Token used for authentication with the Remarcable API.

        Notes
        -----
        No retry logic is implemented on token refresh.
        """
        if self._config.api_key:
            return self._config.api_key

        if self._token and self._token_expires > datetime.now(
            self._token_expires.tzinfo
        ):
            return self._token

        response = requests.post(
            f"{self._config.base_uri}/api/v1/auth/token/",
            json={
                "email": self._config.email,
                "password": self._config.password,
            },
        )

        response.raise_for_status()

        data = response.json()
        self._token = data["token"]
        self._token_expires = (
            datetime.fromisoformat(data["created_on"]) + self._TOKEN_EXPIRES_DEFAULT
        )

        return self._token

    def __call__(self, r: requests.PreparedRequest) -> requests.PreparedRequest:
        r.headers["Authorization"] = f"token {self.token}"
        return r
