from datetime import datetime
import pandas as pd
import requests

from ..utils import paginate_request, paginate_request_df

# Stops circular import issues with type checking
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import RemarcableClient


class Invoices:
    def __init__(self, client: "RemarcableClient"):
        self._client = client

    def list_invoices(
        self,
        last: int | None = None,
        po_number: str | None = None,
        job_num: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[dict]:
        """Retrieve a list of invoices with optional filtering.

        Parameters
        ----------
        last : int, optional
            Integer string representing the last n days. Defaults to 3 if not provided. Must be between 1 and 365.
        po_number : str, optional
            Invoice PO number.
        job_num : str, optional
            Invoice job number.
        start_date : datetime, optional
            Return invoices updated after this date.
        end_date : datetime, optional
            Return invoices updated before this date.

        Returns
        -------
        list of dict
            A list of invoice records.

        Raises
        ------
        ValueError
            If parameters are invalid.
        """
        if last is not None and (last < 1 or last > 365):
            raise ValueError("Parameter 'last' must be between 1 and 365.")
        if start_date and end_date and (end_date - start_date).days > 180:
            raise ValueError(
                "The date range between start_date and end_date cannot exceed 180 days."
            )

        return paginate_request(
            self._client,
            self._client._session.prepare_request(
                requests.Request(
                    method="GET",
                    url=f"{self._client._config.base_uri}/buyer_api/v1/ListInvoice/",
                    params={
                        "last": last,
                        "po_number": po_number,
                        "job_num": job_num,
                        "start_date": start_date.isoformat() if start_date else None,
                        "end_date": end_date.isoformat() if end_date else None,
                    },
                )
            ),
        )

    def list_invoice_items(
        self,
        so_numbers: list[str] | None = None,
        po_numbers: list[str] | None = None,
        job_num: str | None = None,
        last: int | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> pd.DataFrame:
        """Retrieve a list of invoice items with optional filtering.

        Parameters
        ----------
        so_numbers : list of str, optional
            List of one or more SO numbers. If provided, job_num will be ignored.
        po_numbers : list of str, optional
            List of one or more PO numbers. If provided, job_num will be ignored.
        job_num : str, optional
            Invoice job number. Ignored if so_numbers or po_numbers are provided.
        last : int, optional
            Integer representing the last n days. Used only if so_numbers, po_numbers, and job_num are not provided.
            Must be between 1 and 365.
        start_date : datetime, optional
            Return invoice items updated after this date. If both start_date and end_date are provided, last is ignored.
            The range between start_date and end_date cannot exceed 180 days.
        end_date : datetime, optional
            Return invoice items updated before this date. If both start_date and end_date are provided, last is ignored.
            The range between start_date and end_date cannot exceed 180 days.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the list of invoice items.

        Raises
        ------
        ValueError
            If parameters are invalid.
        """
        if last is not None and (last < 1 or last > 365):
            raise ValueError("Parameter 'last' must be between 1 and 365.")
        if start_date and end_date and (end_date - start_date).days > 180:
            raise ValueError(
                "The date range between start_date and end_date cannot exceed 180 days."
            )

        return paginate_request_df(
            self._client,
            self._client._session.prepare_request(
                requests.Request(
                    method="GET",
                    url=f"{self._client._config.base_uri}/buyer_api/v1/ListInvoiceItem/",
                    params={
                        "so_numbers": ",".join(so_numbers) if so_numbers else None,
                        "po_numbers": ",".join(po_numbers) if po_numbers else None,
                        "job_num": job_num,
                        "last": last,
                        "start_date": start_date.isoformat() if start_date else None,
                        "end_date": end_date.isoformat() if end_date else None,
                    },
                )
            ),
        )
