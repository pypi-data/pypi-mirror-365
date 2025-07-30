from dataclasses import dataclass
from urllib3 import Retry


@dataclass(frozen=True)
class RemarcableConfig:
    """Immutable configuration for RemarcableClient.

    Attributes
    ----------
    email : str or None
        User email for authentication. Required if `api_key` is not provided.
    password : str or None
        User password for authentication. Required if `api_key` is not provided.
    api_key : str or None
        API key for authentication. If provided, takes precedence over email/password.
    base_uri : str, default="https://app.remarcable.com"
        Base URI for the Remarcable API.
    retry_options : Retry, default=Retry(...)
        Retry configuration for HTTP requests.
        Defaults to 3 retries with exponential backoff for certain status codes.

    Raises
    ------
    ValueError
        If neither `api_key` nor both `email` and `password` are provided.
    """

    # Authentication uses either email & password or an API key.
    # If both are provided, the API key will be used.
    email: str | None = None
    password: str | None = None

    api_key: str | None = None

    base_uri: str = "https://app.remarcable.com"

    retry_options: Retry = Retry(
        total=3,
        backoff_factor=1.0,
        status_forcelist=[500, 502, 503, 504, 429],
        allowed_methods=["GET", "POST", "PUT", "DELETE"],
    )

    def __post_init__(self):
        if not self.api_key and not (self.email and self.password):
            raise ValueError(
                "Either api_key or both email and password must be provided."
            )
