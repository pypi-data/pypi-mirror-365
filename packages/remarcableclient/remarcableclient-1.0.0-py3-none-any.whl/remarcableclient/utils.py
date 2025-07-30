import pandas as pd
from requests import PreparedRequest

# Stops circular import issues with type checking
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import RemarcableClient


def paginate_request(
    client: "RemarcableClient", request: PreparedRequest
) -> list[dict]:
    """Paginate through a request to retrieve all results.

    Parameters
    ----------
    client : RemarcableClient
        The client instance used to make the request.
    request : PreparedRequest
        The prepared request to paginate through.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing all results from the paginated request.
    """
    response = client._session.send(request)
    response.raise_for_status()

    data = response.json()
    results = data["results"]

    # NOTE: Pagination delay is handled by urllib3's Retry mechanism when a 429 status code is returned
    while data["next"] is not None:
        response = client._session.get(data["next"])
        response.raise_for_status()

        data = response.json()
        results.append(data["results"])

    return results


def paginate_request_df(
    client: "RemarcableClient", request: PreparedRequest
) -> pd.DataFrame:
    """
    Paginate through a request to retrieve all results as a DataFrame.

    Parameters
    ----------
    client : RemarcableClient
        The client instance used to make the request.
    request : PreparedRequest
        The prepared request to paginate through.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing all results from the paginated request.
    """
    return pd.DataFrame(paginate_request(client, request))
