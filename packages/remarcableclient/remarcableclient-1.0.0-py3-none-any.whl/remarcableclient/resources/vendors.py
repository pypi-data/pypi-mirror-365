import pandas as pd
import requests
from ..utils import paginate_request_df

# Stops circular import issues with type checking
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import RemarcableClient

allowed_supplier_types = ("manufacturer", "distributor", "subcontractor")
allowed_supplier_tiers = ("1", "2", "3")


class Vendors:
    def __init__(self, client: "RemarcableClient"):
        self._client = client

    def list_vendors(
        self,
        search_terms: str | None = None,
        supplier_type: str | None = None,
        status: bool | None = None,
        edi_enabled: bool | None = None,
        supplier_tier: str | None = None,
        is_minority_owned: bool | None = None,
        is_women_owned: bool | None = None,
        is_veteran_owned: bool | None = None,
        is_diversity_owned: bool | None = None,
        is_hubzone: bool | None = None,
        is_small_disadvantaged_business: bool | None = None,
        is_small_business: bool | None = None,
        auto_po: bool | None = None,
        exclude_auto_po: bool | None = None,
        web_tracking_completed: bool | None = None,
        is_without_contact_group: bool | None = None,
        quick_edi_api_enabled: bool | None = None,
        email_pdf_invoice_enabled: bool | None = None,
        price_file_enabled: bool | None = None,
        new_completed: bool | None = None,
        restricted_supplier: bool | None = None,
        stock_level_completed: bool | None = None,
    ) -> pd.DataFrame:
        """Retrieve a list of vendors with optional filtering.

        Parameters
        ----------
        search_terms : str, optional
            Search term covering categories, site/type, descriptions, etc.
        supplier_type : str, optional
            Supplier type. Allowed: 'manufacturer', 'distributor', 'subcontractor', 'service', 'other'.
        status : bool, optional
            True returns active suppliers, False returns non-active suppliers.
        edi_enabled : bool, optional
            True returns suppliers with EDI/API enabled.
        supplier_tier : str, optional
            Supplier tier. Allowed: '1', '2', '3'.
        is_minority_owned : bool, optional
            True returns suppliers which are minority-owned.
        is_women_owned : bool, optional
            True returns suppliers which are women-owned.
        is_veteran_owned : bool, optional
            True returns suppliers which are veteran-owned.
        is_diversity_owned : bool, optional
            True returns suppliers which are diversity-owned.
        is_hubzone : bool, optional
            True returns HUBZone small business suppliers.
        is_small_disadvantaged_business : bool, optional
            True returns small disadvantaged business suppliers.
        is_small_business : bool, optional
            True returns small business suppliers.
        auto_po : bool, optional
            True returns suppliers with auto-create PO enabled.
        exclude_auto_po : bool, optional
            True excludes suppliers with auto-create PO enabled.
        web_tracking_completed : bool, optional
            True returns suppliers that have completed web tracking.
        is_without_contact_group : bool, optional
            True returns suppliers that have no contact group.
        quick_edi_api_enabled : bool, optional
            True returns suppliers with quick EDI/API enabled.
        email_pdf_invoice_enabled : bool, optional
            True returns suppliers with email PDF invoice enabled.
        price_file_enabled : bool, optional
            True returns suppliers with price file enabled.
        new_completed : bool, optional
            True returns suppliers with new completed status.
        restricted_supplier : bool, optional
            True returns restricted suppliers.
        stock_level_completed : bool, optional
            True returns suppliers with stock level completed.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the list of vendors.

        Raises
        ------
        ValueError
            If any parameter is invalid.
        """
        if supplier_type and supplier_type not in allowed_supplier_types:
            raise ValueError(f"supplier_type must be one of {allowed_supplier_types}")
        if supplier_tier and supplier_tier not in allowed_supplier_tiers:
            raise ValueError(f"supplier_tier must be one of {allowed_supplier_tiers}")

        return paginate_request_df(
            self._client,
            self._client._session.prepare_request(
                requests.Request(
                    method="GET",
                    url=f"{self._client._config.base_uri}/buyer_api/v1/ListVendor/",
                    params={
                        "search_terms": search_terms,
                        "supplier_type": supplier_type,
                        "status": status,
                        "edi_enabled": edi_enabled,
                        "supplier_tier": supplier_tier,
                        "is_minority_owned": is_minority_owned,
                        "is_women_owned": is_women_owned,
                        "is_veteran_owned": is_veteran_owned,
                        "is_diversity_owned": is_diversity_owned,
                        "is_hubzone": is_hubzone,
                        "is_small_disadvantaged_business": is_small_disadvantaged_business,
                        "is_small_business": is_small_business,
                        "auto_po": auto_po,
                        "exclude_auto_po": exclude_auto_po,
                        "web_tracking_completed": web_tracking_completed,
                        "is_without_contact_group": is_without_contact_group,
                        "quick_edi_api_enabled": quick_edi_api_enabled,
                        "email_pdf_invoice_enabled": email_pdf_invoice_enabled,
                        "price_file_enabled": price_file_enabled,
                        "new_completed": new_completed,
                        "restricted_supplier": restricted_supplier,
                        "stock_level_completed": stock_level_completed,
                    },
                )
            ),
        )
