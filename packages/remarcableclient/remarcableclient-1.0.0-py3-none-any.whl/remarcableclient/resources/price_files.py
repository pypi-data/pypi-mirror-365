import requests
import pandas as pd

from ..utils import paginate_request_df

# Stops circular import issues with type checking
from typing import TYPE_CHECKING

allowed_orders = {"name", "-name", "created_date", "-created_date"}
allowed_statuses = {"active", "archived", "deleted"}

if TYPE_CHECKING:
    from ..client import RemarcableClient


class PriceFiles:
    def __init__(self, client: "RemarcableClient"):
        self._client = client

    def list_price_files(
        self,
        search: str | None = None,
        order: str | None = None,
        current_status: str | None = None,
        is_job: bool | None = None,
        main_job_num: str | None = None,
    ) -> pd.DataFrame:
        """Retrieve a paginated list of price files with optional filtering.

        Parameters
        ----------
        search : str, optional
            Search string to match price file name or description.
        order : str, optional
            Field to order the results by. Allowed: 'name', '-name', 'created_date', '-created_date'.
        current_status : str, optional
            Status of a price file. Allowed: 'active', 'archived', 'deleted'.
        is_job : bool, optional
            If True, filter price files that are jobs. If False, filter price files that are work orders.
        main_job_num : str, optional
            Main job number to filter price files.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the list of price files.

        Raises
        ------
        ValueError
            If parameters are invalid.
        """
        if order and order not in allowed_orders:
            raise ValueError(f"Parameter 'order' must be one of {allowed_orders}")
        if current_status and current_status not in allowed_statuses:
            raise ValueError(
                f"Parameter 'current_status' must be one of {allowed_statuses}"
            )

        return paginate_request_df(
            self._client,
            self._client._session.prepare_request(
                requests.Request(
                    method="GET",
                    url=f"{self._client._config.base_uri}/buyer_api/v1/ListPriceFile/",
                    params={
                        "search": search,
                        "order": order,
                        "current_status": current_status,
                        "is_job": is_job,
                        "main_job_num": main_job_num,
                    },
                )
            ),
        )

    def get_price_file_items(
        self,
        price_file_id: str,
    ) -> pd.DataFrame:
        """Retrieve a paginated list of items for a specific price file.

        Parameters
        ----------
        price_file_id : str
            The Remarcable price file ID. Required.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the list of price file items.
        """
        return paginate_request_df(
            self._client,
            self._client._session.prepare_request(
                requests.Request(
                    method="GET",
                    url=f"{self._client._config.base_uri}/buyer_api/v1/GetPriceFileItems/",
                    params={
                        "price_file_id": price_file_id,
                    },
                )
            ),
        )

    def get_price_file_item_prices(
        self,
        upc_list: list[str],
        pricefile_id: str | None = None,
        allow_substitute: bool | None = None,
    ) -> dict:
        """Retrieve price data for a list of UPC numbers, optionally filtered by price file and substitute rules.

        Parameters
        ----------
        upc_list : list of str
            A list of UPC numbers. Required. Up to 4000 UPC numbers per request.
        pricefile_id : str, optional
            The identifier for the price file, obtainable by calling the List Price File API.
        allow_substitute : bool, optional
            Determines how price data is returned based on the presence of pricefile_id and whether substitutes are allowed.

        Returns
        -------
        dict
            The response data containing price information.

        Raises
        ------
        ValueError
            If upc_list is not provided or exceeds 4000 items.
        """
        if len(upc_list) > 4000:
            raise ValueError(
                "Parameter 'upc_list' cannot contain more than 4000 UPC numbers."
            )

        response = self._client._session.post(
            url=f"{self._client._config.base_uri}/buyer_api/v1/GetPriceFileItemPrices/",
            json={
                "pricefile_id": pricefile_id,
                "allow_substitute": allow_substitute,
                "upc_list": upc_list,
            },
        )
        response.raise_for_status()
        return response.json()

    def import_price_file(
        self,
        price_file_id: str,
        buyer_company_id: str,
        data: pd.DataFrame,
    ) -> bool:
        """Import or update price file items.

        Parameters
        ----------
        price_file_id : str
            GUID for the price file, obtainable from the List Price File API or by the seller company via email.
        buyer_company_id : str
            Remarcable ID for the buying company, obtainable from the price file upload page.
        data : pd.DataFrame
            DataFrame containing the list of price file items to import.

        Returns
        -------
        bool
            True if the import request was accepted (HTTP 200), otherwise False.
        """
        if data.empty:
            raise ValueError("Parameter 'data' must not be empty.")

        response = self._client._session.post(
            url=f"{self._client._config.base_uri}/general_api/v1/ImportPriceFile/",
            json={
                "price_file_id": price_file_id,
                "buyer_company_id": buyer_company_id,
                "json_data": data.to_dict(orient="records"),
            },
        )
        response.raise_for_status()
        return response.status_code == 200

    def import_stock_file(
        self,
        company_branch_id: str,
        data: pd.DataFrame,
    ) -> bool:
        """Import or update stock quantity.

        Parameters
        ----------
        company_branch_id : str
            Seller company branch Remarcable ID.
        data : pd.DataFrame
            DataFrame containing the list of stock quantities to import.

        Returns
        -------
        bool
            True if the import request was accepted (HTTP 200), otherwise False.
        """
        if data.empty:
            raise ValueError("Parameter 'data' must not be empty.")

        response = self._client._session.post(
            url=f"{self._client._config.base_uri}/seller_api/v1/ImportStockFile/",
            json={
                "company_branch_id": company_branch_id,
                "json_data": data.to_dict(orient="records"),
            },
        )
        response.raise_for_status()
        return response.status_code == 200
