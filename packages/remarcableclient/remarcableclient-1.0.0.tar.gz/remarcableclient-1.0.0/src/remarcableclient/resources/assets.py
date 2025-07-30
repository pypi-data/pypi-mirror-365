from datetime import datetime

import pandas as pd
import requests

from ..utils import paginate_request, paginate_request_df

# Stops circular import issues with type checking
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from ..client import RemarcableClient

AssetItems = NamedTuple(
    "AssetItems",
    [
        ("model_type", str),
        ("category", str),
        ("sub_category", str),
        ("warehouse_id", str),
        ("avail_items", int),
        ("on_hand_qty", int),
        ("committed_qty", int),
        ("asset_list", pd.DataFrame),
    ],
)

allowed_filter_request_statuses = (
    "new",
    "acked",
    "partly shipped",
    "picked",
    "partly received",
    "complete",
    "canceled",
)
allowed_update_request_statuses = (
    "acked",
    "picked",
    "partly picked",
    "partly shipped",
    "partly received",
    "in transit",
    "awaiting shipment",
    "shipped",
    "received",
    "canceled",
)
allowed_update_item_statuses = (
    "ok",
    "staging",
    "servicing",
    "need certification",
    "need repair",
    "need inspection",
    "recalibration",
)
allowed_model_types = ("Tools", "Prefab", "Stock", "Temp Power")


class Assets:
    def __init__(self, client: "RemarcableClient"):
        self._client = client

    def list_asset_items(
        self,
        model_type: str | None = None,
        category: str | None = None,
        sub_category: str | None = None,
        warehouse_id: str | None = None,
    ) -> AssetItems:
        """
        Retrieve a list of asset items with optional filtering.

        Parameters
        ----------
        model_type : str, optional
            Type of asset model, can be "Tools", "Prefab", "Stock", or "Temp Power".
        category : str, optional
            Asset model category, obtainable from the Warehouse Tab/Tool Model list view from the filter dialog.
        sub_category : str, optional
            Asset model sub_category, obtainable from the Warehouse Tab/Tool Model list view from the filter dialog.
        warehouse_id : str, optional
            Warehouse ID, obtainable from the warehouse settings view.

        Returns
        -------
        AssetItems
            A named tuple containing the asset items and their details.
        """
        if model_type and model_type not in (
            "Tools",
            "Prefab",
            "Stock",
            "Temp Power",
        ):
            raise ValueError(
                f"Invalid model_type: {model_type}. Must be one of 'Tools', 'Prefab', 'Stock', or 'Temp Power'."
            )

        response = self._client._session.get(
            url=f"{self._client._config.base_uri}/buyer_api/v1/ListAssetItem/",
            params={
                "model_type": model_type,
                "category": category,
                "sub_category": sub_category,
                "warehouse_id": warehouse_id,
            },
        )
        response.raise_for_status()
        data = response.json()

        asset_list = pd.DataFrame(data["results"]["asset_list"])

        # Pagination logic is exactly the same as in paginate_request, however has to be handled
        # differently due to the returned dict being different.
        while data["next"] is not None:
            response = self._client._session.get(data["next"])
            response.raise_for_status()

            data = response.json()
            asset_list = pd.concat(
                [asset_list, pd.DataFrame(data["results"]["asset_list"])],
                ignore_index=True,
            )

        return AssetItems(
            model_type=data["results"]["model_type"],
            category=data["results"]["category"],
            sub_category=data["results"]["sub_category"],
            warehouse_id=data["results"]["warehouse_id"],
            avail_items=data["results"]["avail_items"],
            on_hand_qty=data["results"]["on_hand_qty"],
            committed_qty=data["results"]["committed_qty"],
            asset_list=asset_list,
        )

    def retrieve_asset_request(
        self,
        tool_request_id: str,
    ) -> dict:
        """
        Retrieve a specific asset request by its Remarcable asset request ID.

        Parameters
        ----------
        tool_request_id : str
            Remarcable asset request ID, obtainable by using the list asset request API.

        Returns
        -------
        dict
            The response data for the requested asset.

        Raises
        ------
        ValueError
            If `tool_request_id` is not provided.
        """
        if not tool_request_id:
            raise ValueError("Parameter 'tool_request_id' is required.")

        response = self._client._session.get(
            url=f"{self._client._config.base_uri}/buyer_api/v1/RetrieveToolRequest/",
            params={"tool_request_id": tool_request_id},
        )
        response.raise_for_status()
        return response.json()

    def list_asset_requests(
        self,
        last: int | None = None,
        last_updated: int | None = None,
        project_id: str | None = None,
        job_num: str | None = None,
        owner_email: str | None = None,
        from_warehouse_id: str | None = None,
        warehouse_id: str | None = None,
        request_type: str | None = None,
        request_status: list[str] | None = None,
    ) -> list[dict]:
        """
        Retrieve a paginated list of asset requests with optional filtering.

        Parameters
        ----------
        last : int, optional
            Integer representing the last n days. Defaults to 90 if unspecified. Returns asset requests submitted in the last n days.
        last_updated : int, optional
            Integer representing the last updated m days. Returns asset requests updated in the last m days. Used with 'last' to filter by submission and update time frames.
        project_id : str, optional
            Project ID obtainable from the project settings view.
        job_num : str, optional
            Project job number.
        owner_email : str, optional
            Owner email obtainable from the all users view under settings in the Remarcable app.
        from_warehouse_id : str, optional
            ID of the warehouse from which assets are requested or returned, obtainable from the warehouse settings view.
        warehouse_id : str, optional
            Warehouse ID obtainable from the warehouse settings view.
        request_type : str, optional
            Can be 'project', 'warehouse', 'owner', or 'return' based on the asset request or return context.
        request_status : list of str, optional
            Can be one or many values: 'new', 'acked', 'partly shipped', 'picked', 'partly received', 'complete', 'canceled'. Returns requests with specified statuses.

        Returns
        -------
        list[dict]
            A list of dictionaries containing the asset requests.

        Raises
        ------
        ValueError
            If any parameter is invalid.
        """
        if last is not None and (last < 1 or last > 365):
            raise ValueError("Parameter 'last' must be between 1 and 365.")
        if last_updated is not None and (last_updated < 1 or last_updated > 365):
            raise ValueError("Parameter 'last_updated' must be between 1 and 365.")
        if project_id is not None and len(project_id) > 50:
            raise ValueError("Parameter 'project_id' must not exceed 50 characters.")
        if job_num is not None and len(job_num) > 200:
            raise ValueError("Parameter 'job_num' must not exceed 200 characters.")
        if owner_email is not None and len(owner_email) > 100:
            raise ValueError("Parameter 'owner_email' must not exceed 100 characters.")
        if from_warehouse_id is not None and len(from_warehouse_id) > 50:
            raise ValueError(
                "Parameter 'from_warehouse_id' must not exceed 50 characters."
            )
        if warehouse_id is not None and len(warehouse_id) > 50:
            raise ValueError("Parameter 'warehouse_id' must not exceed 50 characters.")
        if request_type is not None and request_type not in (
            "project",
            "warehouse",
            "owner",
            "return",
        ):
            raise ValueError(
                "Parameter 'request_type' must be one of: 'project', 'warehouse', 'owner', 'return'."
            )
        if request_status:
            for s in request_status:
                if s not in allowed_filter_request_statuses:
                    raise ValueError(
                        f"Invalid request_status: '{s}'. Allowed values are: {', '.join(allowed_filter_request_statuses)}"
                    )

        return paginate_request(
            self._client,
            self._client._session.prepare_request(
                requests.Request(
                    method="GET",
                    url=f"{self._client._config.base_uri}/buyer_api/v1/ListToolRequest/",
                    params={
                        "last": last,
                        "last_updated": last_updated,
                        "project_id": project_id,
                        "job_num": job_num,
                        "owner_email": owner_email,
                        "from_warehouse_id": from_warehouse_id,
                        "warehouse_id": warehouse_id,
                        "request_type": request_type,
                        "request_status": ",".join(request_status)
                        if request_status
                        else None,
                    },
                )
            ),
        )

    def get_project_po_total_to_date(
        self,
        main_job_num: str | None = None,
    ) -> pd.DataFrame:
        """Retrieve all active projects grand_total to date or the main job number grand_total to date.

        Parameters
        ----------
        main_job_num : str, optional
            Main job number to filter projects. If None, retrieves all active projects grand_total to date.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the grand_total to date for all active projects or the specified main job number.
        """
        return paginate_request_df(
            self._client,
            self._client._session.prepare_request(
                requests.Request(
                    method="GET",
                    url=f"{self._client._config.base_uri}/buyer_api/v1/GetProjectPOTotalToDate/",
                    params={"main_job_num": main_job_num},
                )
            ),
        )

    def list_prefab_asset_rates(self) -> pd.DataFrame:
        """Retrieve a list of prefab asset rates.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the prefab asset rates.
        """
        return paginate_request_df(
            self._client,
            self._client._session.prepare_request(
                requests.Request(
                    method="GET",
                    url=f"{self._client._config.base_uri}/buyer_api/v1/ListModelConfigurationRate/",
                )
            ),
        )

    def list_transfer_items(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        project_id_list: list[str] | None = None,
        tool_transfer_id: str | None = None,
        tool_item_id: str | None = None,
        tool_model_id: str | None = None,
        transfer_direction: str | None = None,
        search_terms: str | None = None,
    ) -> pd.DataFrame:
        """Retrieve a list of transfer items with optional filtering.

        Parameters
        ----------
        start_date : str, optional
            The start date for the transfer range (ISO 8601). Required if end_date, project_id_list, tool_transfer_id, tool_item_id, or tool_model_id is provided.
        end_date : str, optional
            The end date for the transfer range (ISO 8601). Required if start_date is provided.
        project_id_list : list of str, optional
            Array of project IDs to filter.
        tool_transfer_id : str, optional
            The tool transfer ID.
        tool_item_id : str, optional
            The tool item ID.
        tool_model_id : str, optional
            The tool model ID.
        transfer_direction : str, optional
            Can be "inbound" or "outbound".
        search_terms : str, optional
            Search terms covering origin and destination names and item description.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the transfer items.
        """
        if (start_date and not end_date) or (end_date and not start_date):
            raise ValueError(
                "Both 'start_date' and 'end_date' must be provided together."
            )
        if transfer_direction and transfer_direction not in ("inbound", "outbound"):
            raise ValueError(
                "Parameter 'transfer_direction' must be 'inbound' or 'outbound'."
            )

        return paginate_request_df(
            self._client,
            self._client._session.prepare_request(
                requests.Request(
                    method="GET",
                    url=f"{self._client._config.base_uri}/buyer_api/v1/ListTransferItem/",
                    params={
                        "start_date": start_date,
                        "end_date": end_date,
                        "project_id_list": ",".join(project_id_list)
                        if project_id_list
                        else None,
                        "tool_transfer_id": tool_transfer_id,
                        "tool_item_id": tool_item_id,
                        "tool_model_id": tool_model_id,
                        "transfer_direction": transfer_direction,
                        "search_terms": search_terms,
                    },
                )
            ),
        )

    def list_asset_charges(
        self,
        start_date: datetime,
        end_date: datetime,
        model_type: str | None = None,
        charge_id: str | None = None,
    ) -> pd.DataFrame:
        """
        Retrieve a paginated list of asset charge items with optional filtering.

        Parameters
        ----------
        start_date : datetime, optional
            Start date (ISO 8601) for the required time range. Required if end_date is provided.
        end_date : datetime, optional
            End date (ISO 8601) for the required time range. Required if start_date is provided.
        model_type : str, optional
            Type of asset model. Allowed values: "Tools", "Prefab", "Stock", "Temp Power".
        charge_id : str, optional
            Asset charge ID to filter charges.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the asset charge items.

        Raises
        ------
        ValueError
            If required parameters are missing or invalid.
        """
        if model_type and model_type not in allowed_model_types:
            raise ValueError(
                f"Parameter 'model_type' must be one of {allowed_model_types}"
            )
        if ((end_date - start_date).days > 365) or ((end_date - start_date).days < 0):
            raise ValueError(
                "The date range between start_date and end_date must be between 0 and 365 days."
            )

        return paginate_request_df(
            self._client,
            self._client._session.prepare_request(
                requests.Request(
                    method="GET",
                    url=f"{self._client._config.base_uri}/buyer_api/v1/ListAssetCharges/",
                    params={
                        "model_type": model_type,
                        "charge_id": charge_id,
                        "start_date": start_date,
                        "end_date": end_date,
                    },
                )
            ),
        )

    def list_rental_rates(self, search_terms: str | None = None) -> pd.DataFrame:
        """Retrieve a list of rental rates with optional filtering.

        Parameters
        ----------
        search_terms : str, optional
            Search terms to filter rental rates. If provided, returns rental rates matching the search terms.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the rental rates.
        """
        return paginate_request_df(
            self._client,
            self._client._session.prepare_request(
                requests.Request(
                    method="GET",
                    url=f"{self._client._config.base_uri}/buyer_api/v1/ListRentalRate/",
                    params={"search_terms": search_terms},
                )
            ),
        )

    def update_asset_request_status(self, asset_request_id: str, status: str) -> dict:
        """Update the status of an asset request.

        Parameters
        ----------
        asset_request_id : str
            The Remarcable asset request ID.
        status : str
            The new status to set for the asset request. Must be one of the allowed update statuses.
            'acked', 'picked', 'partly picked', 'partly shipped', 'partly received', 'in transit', 'awaiting shipment', 'shipped', 'received', 'canceled'.

        Returns
        -------
        dict
            The asset request record with the updated status.
        """
        if status not in allowed_update_request_statuses:
            raise ValueError(
                f"Invalid status: {status}. Must be one of {allowed_update_request_statuses}."
            )

        response = self._client._session.post(
            url=f"{self._client._config.base_uri}/buyer_api/v1/UpdateAssetRequestStatus/",
            json={
                "asset_request_id": asset_request_id,
                "status": status,
            },
        )
        response.raise_for_status()
        return response.json()

    def update_asset_item_status(
        self, asset_item_id: str, new_status: str, quantity: int
    ) -> dict:
        """Update the status of an asset item.

        Parameters
        ----------
        asset_item_id : str
            The Remarcable asset item ID.
        new_status : str
            The new status to set for the asset item. Must be one of the allowed update item statuses.
            'ok', 'staging', 'servicing', 'need certification', 'need repair', 'need inspection', 'recalibration'.
        quantity : int
            Documentation does not specify the purpose of this parameter, but it is required.

        Returns
        -------
        dict
            The asset item record with the updated status.
        """
        if new_status not in allowed_update_item_statuses:
            raise ValueError(
                f"Invalid new_status: {new_status}. Must be one of {allowed_update_item_statuses}."
            )
        response = self._client._session.post(
            url=f"{self._client._config.base_uri}/buyer_api/v1/UpdateAssetItemStatus/",
            json={
                "asset_item_id": asset_item_id,
                "new_status": new_status,
                "quantity": quantity,
            },
        )
        response.raise_for_status()
        return response.json()
