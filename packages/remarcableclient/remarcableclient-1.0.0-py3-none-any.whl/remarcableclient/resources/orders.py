from datetime import datetime

import pandas as pd
import requests

from ..utils import paginate_request_df

# Stops circular import issues with type checking
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import RemarcableClient


class Orders:
    def __init__(self, client: "RemarcableClient"):
        self._client = client

    def list_po(
        self,
        last: int | None = None,
        project_id: str | None = None,
        job_number: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        phase_code: str | None = None,
    ) -> pd.DataFrame:
        """
        Retrieve a list of purchase orders (POs) with optional filtering.

        Parameters
        ----------
        last : int, optional
            The number of most recently updated days to include. If not provided, defaults to 3.
            Must range from 1 to 365.
            Ignored if both `start_date` and `end_date` are provided.
        project_id : str, optional
            The project GUID string. Max length is 20.
        job_number : str, optional
            The user employee ID. Max length is 200.
        start_date : datetime, optional
            Return POs updated after this ISO 8601 date. Used with `end_date` to specify a date range.
            If both `start_date` and `end_date` are provided, `last` is ignored.
            The range between `start_date` and `end_date` cannot exceed 180 days.
        end_date : datetime, optional
            Return POs updated before this ISO 8601 date. Used with `start_date` to specify a date range.
            If both `start_date` and `end_date` are provided, `last` is ignored.
            The range between `start_date` and `end_date` cannot exceed 180 days.
        phase_code : str, optional
            The phase code tied to the PO.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the list of purchase orders, filtered by the provided parameters.

        Notes
        -----
        - If both `start_date` and `end_date` are provided, the `last` parameter is ignored.
        - The date range between `start_date` and `end_date` cannot exceed 180 days.
        """
        # Validate parameters
        if last is not None and (last < 1 or last > 365):
            raise ValueError("Parameter 'last' must be between 1 and 365.")
        if start_date and end_date and (end_date - start_date).days > 180:
            raise ValueError("The date range cannot exceed 180 days.")
        if len(project_id or "") > 20:
            raise ValueError("Parameter 'project_id' must not exceed 20 characters.")
        if len(job_number or "") > 200:
            raise ValueError("Parameter 'job_number' must not exceed 200 characters.")

        # Paginate the request
        return paginate_request_df(
            self._client,
            self._client._session.prepare_request(
                requests.Request(
                    method="GET",
                    url=f"{self._client._config.base_uri}/general_api/v1/ListPO/",
                    params={
                        "last": last,
                        "project_id": project_id,
                        "job_num": job_number,
                        "start_date": start_date.isoformat() if start_date else None,
                        "end_date": end_date.isoformat() if end_date else None,
                        "phase_code": phase_code,
                    },
                )
            ),
        )

    def list_po_items(
        self,
        po_ids: list[str] | None = None,
        po_numbers: str | None = None,
        last: int | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> pd.DataFrame:
        """
        Retrieve a list of purchase order items (PO items) with optional filtering.

        Parameters
        ----------
        po_ids : list of str, optional
            List of one or more PO IDs (GUID strings). Limited to 100 PO IDs per request.
        po_numbers : str, optional
            One or more PO numbers, separated by commas. Limited to 100 PO numbers per request.
        last : int, optional
            Integer representing the last n days. Used only if both `po_ids` and `po_numbers` are not provided.
            If not provided, defaults to 3 days.
        start_date : datetime, optional
            Return PO items updated after this ISO 8601 date. Used with `end_date` to specify a date range.
            If both `start_date` and `end_date` are provided, `last` is ignored.
        end_date : datetime, optional
            Return PO items updated before this ISO 8601 date. Used with `start_date` to specify a date range.
            If both `start_date` and `end_date` are provided, `last` is ignored.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the list of purchase order items, filtered by the provided parameters.

        Notes
        -----
        - If both `start_date` and `end_date` are provided, the `last` parameter is ignored.
        - If both `po_ids` and `po_numbers` are not provided, `last` is used (defaults to 3).
        - Limited to 100 PO IDs or PO numbers per request.
        """
        # Validate parameters
        if po_ids and len(po_ids) > 100:
            raise ValueError("Parameter 'po_ids' must not exceed 100 IDs.")
        if po_numbers and len(po_numbers.split(",")) > 100:
            raise ValueError("Parameter 'po_numbers' must not exceed 100 numbers.")
        if last is not None and (last < 1 or last > 365):
            raise ValueError("Parameter 'last' must be between 1 and 365.")
        if start_date and end_date and (end_date - start_date).days > 180:
            raise ValueError("The date range cannot exceed 180 days.")

        return paginate_request_df(
            self._client,
            self._client._session.prepare_request(
                requests.Request(
                    method="GET",
                    url=f"{self._client._config.base_uri}/buyer_api/v1/ListPOItem/",
                    params={
                        "po_ids": ",".join(po_ids) if po_ids else None,
                        "po_numbers": po_numbers,
                        "last": last,
                        "start_date": start_date.isoformat() if start_date else None,
                        "end_date": end_date.isoformat() if end_date else None,
                    },
                )
            ),
        )

    def retrieve_po(
        self,
        po_ids: list[str] | None = None,
        po_numbers: list[str] | None = None,
    ) -> pd.DataFrame:
        """
        Retrieve purchase orders by PO IDs or PO numbers.

        One of `po_ids` or `po_numbers` is required.

        Parameters
        ----------
        po_ids : list of str, optional
            List of one or more PO IDs (GUID strings). Limited to 100 PO IDs per request.
            One of `po_ids` or `po_numbers` must be provided.
        po_numbers : list of str, optional
            List of one or more PO numbers. Limited to 100 PO numbers per request.
            One of `po_ids` or `po_numbers` must be provided.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the retrieved purchase orders.

        Raises
        ------
        ValueError
            If neither `po_ids` nor `po_numbers` is provided, or if both are provided,
            or if the number of IDs/numbers exceeds 100.
        """
        # Validation
        if (not po_ids and not po_numbers) or (po_ids and po_numbers):
            raise ValueError(
                "Exactly one of 'po_ids' or 'po_numbers' must be provided."
            )
        if po_ids and len(po_ids) > 100:
            raise ValueError("Parameter 'po_ids' must not exceed 100 IDs.")
        if po_numbers and len(po_numbers) > 100:
            raise ValueError("Parameter 'po_numbers' must not exceed 100 numbers.")

        response = self._client._session.get(
            f"{self._client._config.base_uri}/general_api/v1/RetrievePO/",
            params={
                "po_ids": ",".join(po_ids) if po_ids else None,
                "po_numbers": ",".join(po_numbers) if po_numbers else None,
            },
        )
        response.raise_for_status()
        return pd.DataFrame(response.json())

    def list_so_items(
        self,
        so_ids: list[str] | None = None,
        so_numbers: list[str] | None = None,
        po_ids: list[str] | None = None,
        po_numbers: list[str] | None = None,
        last: int | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> pd.DataFrame:
        """Retrieve a list of sales order (SO) items with optional filtering.

        Parameters
        ----------
        so_ids : list of str, optional
            List of one or more SO IDs (GUID strings). Limited to 100 SO IDs per request.
        so_numbers : list of str, optional
            One or more SO numbers. Limited to 100 SO numbers per request.
        po_ids : list of str, optional
            List of one or more PO IDs (GUID strings). Limited to 100 PO IDs per request.
        po_numbers : list of str, optional
            One or more PO numbers. Limited to 100 PO numbers per request.
        last : int, optional
            Integer representing the last n days. Used only if both SO and PO IDs/numbers are not provided.
            If not provided, defaults to 3 days.
        start_date : datetime, optional
            Return SO items updated after this date. Used with `end_date` to specify a date range.
            If both `start_date` and `end_date` are provided, `last` is ignored.
            The range between `start_date` and `end_date` cannot exceed 180 days.
        end_date : datetime, optional
            Return SO items updated before this date. Used with `start_date` to specify a date range.
            If both `start_date` and `end_date` are provided, `last` is ignored.
            The range between `start_date` and `end_date` cannot exceed 180 days.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the list of sales order items, filtered by the provided parameters.

        Raises
        ------
        ValueError
            If any of the parameters exceed their limits or if the date range exceeds 180 days.

        Notes
        -----
        - If both `start_date` and `end_date` are provided, the `last` parameter is ignored.
        - If no SO or PO IDs/numbers are provided, `last` is used (defaults to 3).
        """
        # Validate parameters
        if so_ids and len(so_ids) > 100:
            raise ValueError("Parameter 'so_ids' must not exceed 100 IDs.")
        if so_numbers and len(so_numbers) > 100:
            raise ValueError("Parameter 'so_numbers' must not exceed 100 numbers.")
        if po_ids and len(po_ids) > 100:
            raise ValueError("Parameter 'po_ids' must not exceed 100 IDs.")
        if po_numbers and len(po_numbers) > 100:
            raise ValueError("Parameter 'po_numbers' must not exceed 100 numbers.")
        if last is not None and (last < 1 or last > 365):
            raise ValueError("Parameter 'last' must be between 1 and 365.")
        if start_date and end_date and (end_date - start_date).days > 180:
            raise ValueError("The date range cannot exceed 180 days.")

        return paginate_request_df(
            self._client,
            self._client._session.prepare_request(
                requests.Request(
                    method="GET",
                    url=f"{self._client._config.base_uri}/buyer_api/v1/ListSOItem/",
                    params={
                        "so_ids": ",".join(so_ids) if so_ids else None,
                        "so_numbers": ",".join(so_numbers) if so_numbers else None,
                        "po_ids": ",".join(po_ids) if po_ids else None,
                        "po_numbers": ",".join(po_numbers) if po_numbers else None,
                        "last": last,
                        "start_date": start_date.isoformat() if start_date else None,
                        "end_date": end_date.isoformat() if end_date else None,
                    },
                )
            ),
        )
