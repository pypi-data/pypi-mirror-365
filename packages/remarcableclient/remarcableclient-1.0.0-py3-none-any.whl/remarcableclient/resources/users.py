import pandas as pd


# Stops circular import issues with type checking
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import RemarcableClient


class Users:
    def __init__(self, client: "RemarcableClient"):
        self._client = client

    def list_users(self) -> pd.DataFrame:
        """Retrieve a list of users.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the list of users.
        """
        response = self._client._session.get(
            f"{self._client._config.base_uri}/buyer_api/v1/ListUserAccounts/"
        )
        response.raise_for_status()
        return pd.DataFrame(response.json())

    def upsert_user(
        self,
        first_name: str,
        last_name: str,
        email: str,
        phone: str | None = None,
        employee_id: str | None = None,
        company_branch_name: str | None = None,
        user_group_name: str | None = None,
        job_title: str | None = None,
        po_submit_confirmation: bool | None = None,
        po_ack_confirmation: bool | None = None,
        asset_transfer_confirmation: bool | None = None,
        asset_request_change: bool | None = None,
        quote_submit_confirmation: bool | None = None,
        quote_response_started_confirmation: bool | None = None,
        quote_response_submitted: bool | None = None,
        indirect_quote_message_notification: bool | None = None,
        order_change_alert: bool | None = None,
        remind_items_in_cart: bool | None = None,
        notifications_summary_email: bool | None = None,
        items_ordered_summary_email: bool | None = None,
    ) -> dict:
        """
        Create or update a user account.

        Parameters
        ----------
        first_name : str
            User first name. Required. Max length 40.
        last_name : str
            User last name. Required. Max length 40.
        email : str
            User email. Required. Max length 180.
        phone : str, optional
            User phone number. Max length 20.
        employee_id : str, optional
            User employee ID. Max length 200.
        company_branch_name : str, optional
            Company branch name. Must match exactly as in Remarcable.
        user_group_name : str, optional
            User group name. Must match exactly as in Remarcable.
        job_title : str, optional
            User job title. Max length 200.
        po_submit_confirmation : bool, optional
            Order submission confirmation notification setting.
        po_ack_confirmation : bool, optional
            Order acknowledged confirmation notification setting.
        asset_transfer_confirmation : bool, optional
            Asset transfer confirmation notification setting.
        asset_request_change : bool, optional
            Asset request change notification setting.
        quote_submit_confirmation : bool, optional
            Quote submission confirmation notification setting.
        quote_response_started_confirmation : bool, optional
            Quote response started confirmation notification setting.
        quote_response_submitted : bool, optional
            Quote response submitted notification setting.
        indirect_quote_message_notification : bool, optional
            Indirect quote message notification setting.
        order_change_alert : bool, optional
            Order change alert notification setting.
        remind_items_in_cart : bool, optional
            Cart item checkout reminder notification setting.
        notifications_summary_email : bool, optional
            Notifications summary email setting.
        items_ordered_summary_email : bool, optional
            Items ordered summary email setting.

        Returns
        -------
        dict
            The response from the API.

        Notes
        -----
        - Use the double-splat operator (**) to easily pass parameters from another data source
        """
        # Validate required fields
        if not first_name or not isinstance(first_name, str) or len(first_name) > 40:
            raise ValueError(
                "Parameter 'first_name' is required and must be a string of max length 40."
            )
        if not last_name or not isinstance(last_name, str) or len(last_name) > 40:
            raise ValueError(
                "Parameter 'last_name' is required and must be a string of max length 40."
            )
        if not email or not isinstance(email, str) or len(email) > 180:
            raise ValueError(
                "Parameter 'email' is required and must be a string of max length 180."
            )
        if phone and len(phone) > 20:
            raise ValueError("Parameter 'phone' must be a string of max length 20.")
        if employee_id and len(employee_id) > 200:
            raise ValueError(
                "Parameter 'employee_id' must be a string of max length 200."
            )
        if job_title and len(job_title) > 200:
            raise ValueError(
                "Parameter 'job_title' must be a string of max length 200."
            )

        response = self._client._session.post(
            f"{self._client._config.base_uri}/buyer_api/v1/CreateUpdateUserAccount/",
            json={
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone": phone,
                "employee_id": employee_id,
                "company_branch_name": company_branch_name,
                "user_group_name": user_group_name,
                "job_title": job_title,
                "po_submit_confirmation": po_submit_confirmation,
                "po_ack_confirmation": po_ack_confirmation,
                "asset_transfer_confirmation": asset_transfer_confirmation,
                "asset_request_change": asset_request_change,
                "quote_submit_confirmation": quote_submit_confirmation,
                "quote_response_started_confirmation": quote_response_started_confirmation,
                "quote_response_submitted": quote_response_submitted,
                "indirect_quote_message_notification": indirect_quote_message_notification,
                "order_change_alert": order_change_alert,
                "remind_items_in_cart": remind_items_in_cart,
                "notifications_summary_email": notifications_summary_email,
                "items_ordered_summary_email": items_ordered_summary_email,
            },
        )
        response.raise_for_status()
        return response.json()
