from requests import Session
from requests.adapters import HTTPAdapter

from .config import RemarcableConfig
from .auth import RemarcableAuth
from .resources import assets, invoices, orders, vendors, price_files, projects, users


class RemarcableClient:
    """Client for interacting with the Remarcable API.

    This class manages the HTTP session, authentication, and connection configuration
    for making requests to the Remarcable API. It uses the provided configuration to
    set up authentication (API key or email/password) and retry logic.

    Parameters
    ----------
    config : RemarcableConfig
        Configuration object containing authentication and connection settings.

    Attributes
    ----------
    session : requests.Session
        The HTTP session configured with authentication and retry logic.
    orders : orders.Orders
        Resource for managing orders.
    assets : assets.Assets
        Resource for managing assets.
    invoices : invoices.Invoices
        Resource for managing invoices.
    price_files : price_files.PriceFiles
        Resource for managing price files.
    projects : projects.Projects
        Resource for managing projects.
    users : users.Users
        Resource for managing users.
    vendors : vendors.Vendors
        Resource for managing vendors.

    Examples
    --------
    >>> from remarcable_client import RemarcableClient, RemarcableConfig
    >>> client = RemarcableClient(RemarcableConfig(api_key='your_api_key))
    >>> users = client.users.list_users()
    >>> assets = client.assets.list_asset_items().assets
    """

    def __init__(self, config: RemarcableConfig):
        self._config = config

        self._session = Session()
        self._session.auth = RemarcableAuth(self)
        self._session.mount(
            config.base_uri, HTTPAdapter(max_retries=config.retry_options)
        )

        self.orders = orders.Orders(self)
        self.assets = assets.Assets(self)
        self.invoices = invoices.Invoices(self)
        self.price_files = price_files.PriceFiles(self)
        self.projects = projects.Projects(self)
        self.users = users.Users(self)
        self.vendors = vendors.Vendors(self)
