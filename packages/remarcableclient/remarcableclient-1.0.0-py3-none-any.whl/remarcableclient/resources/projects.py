import pandas as pd
import requests

from ..utils import paginate_request, paginate_request_df

# Stops circular import issues with type checking
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import RemarcableClient

allowed_orders = ("name", "-name", "created_date", "-created_date")
allowed_statuses = ("active", "archived", "deleted")


class Projects:
    def __init__(self, client: "RemarcableClient"):
        self._client = client

    def list_projects(
        self,
        search: str | None = None,
        order: str | None = None,
        current_status: str | None = None,
        is_job: bool | None = None,
        main_job_num: str | None = None,
    ) -> list[dict]:
        """Retrieve a list of projects with optional filtering.

        Parameters
        ----------
        search : str, optional
            Search string to match project name or description.
        order : str, optional
            Field to order the results by. Allowed: 'name', 'created_date', 'current_status', 'order', 'main_job_num'.
        current_status : str, optional
            Status of a project. Allowed: 'active', 'archived', 'deleted'.
        is_job : bool, optional
            If True, filter projects that are jobs. If False, filter projects that are work orders.
        main_job_num : str, optional
            Main job number to filter projects.

        Returns
        -------
        list of dict
            A list of project records.

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

        return paginate_request(
            self._client,
            self._client._session.prepare_request(
                requests.Request(
                    method="GET",
                    url=f"{self._client._config.base_uri}/buyer_api/v1/ListProject/",
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

    def retrieve_project(
        self,
        project_id: str,
    ) -> dict:
        """Retrieve a project by its Remarcable project ID.

        Parameters
        ----------
        project_id : str
            The Remarcable project ID. Obtainable using the 'List Projects' API.

        Returns
        -------
        dict
            The project record as a dictionary.

        Raises
        ------
        ValueError
            If project_id is not provided.
        """
        response = self._client._session.get(
            url=f"{self._client._config.base_uri}/buyer_api/v1/RetrieveProject/",
            params={"project_id": project_id},
        )
        response.raise_for_status()

        return response.json()

    def list_project_categories(self) -> pd.DataFrame:
        """Retrieve a list of project categories.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the project categories.
        """
        return paginate_request_df(
            self._client,
            self._client._session.prepare_request(
                requests.Request(
                    method="GET",
                    url=f"{self._client._config.base_uri}/buyer_api/v1/ListProjectCategory/",
                )
            ),
        )

    def bulk_import_projects(self, projects: list[dict]) -> bool:
        """Bulk import projects from a list of projects.

        TODO: Verify the structure of the projects list and the required fields.

        Parameters
        ----------
        projects : list of dict
            A list of project records to import. Each record must contain the required fields.
            Look at 9.9 Bulk Import Projects in the Remarcable API documentation for details.

        Returns
        -------
        boolean
            True if the import was successful, False otherwise.
        """
        response = self._client._session.post(
            url=f"{self._client._config.base_uri}/buyer_api/v1/BulkImportProject/",
            json={"projects": projects},
        )
        response.raise_for_status()
        return response.status_code == 200

    def send_po_to_project(
        self,
        project_id: str,
        user_email: str,
        po_number: str,
        phase_code: str | None = None,
        job_num: str | None = None,
        orer_name: str | None = None,
    ) -> bool:
        """Send a PO to a project.

        Parameters
        ----------
        project_id : str
            The Remarcable project ID.
        user_email : str
            The email of the user that will be using the PO#.
        po_number : str
            The PO number to send to the project. Maxmimum 50 characters.
        phase_code : str, optional
            The phase code to use for the PO. Maxmum 50 characters.
        job_num : str, optional
            The job number to use for the PO. Maximum 100 characters.
        orer_name : str, optional
            The order name to use for the PO. Maximum 100 characters.

        Returns
        -------
        boolean
            True if the PO was sent successfully, False otherwise.
        """
        if len(po_number) > 50:
            raise ValueError("PO number must not exceed 50 characters.")
        if phase_code and len(phase_code) > 50:
            raise ValueError("Phase code must not exceed 50 characters.")
        if job_num and len(job_num) > 100:
            raise ValueError("Job number must not exceed 100 characters.")
        if orer_name and len(orer_name) > 100:
            raise ValueError("Order name must not exceed 100 characters.")

        response = self._client._session.post(
            url=f"{self._client._config.base_uri}/buyer_api/v1/SendPOToProject/",
            json={
                "project_id": project_id,
                "user_email": user_email,
                "po_number": po_number,
                "phase_code": phase_code,
                "job_num": job_num,
                "order_name": orer_name,
            },
        )
        response.raise_for_status()
        return response.status_code == 200

    def create_project_list(
        self,
        job_num: str,
        overwrite_existing: bool,
        project_lists: list[dict],
        project_id: str | None = None,
    ) -> dict:
        """Create/Update/Append project lists for a project.

        Parameters
        ----------
        job_num : str
            The job number to associate with the project list.
        overwrite_existing : bool
            If True, overwrites existing project lists. If False, appends to existing lists.
        project_lists : list of dict
            A list of project list items to create or update. Each item must contain the required fields.
        project_id : str, optional
            Creates project if provided.

        Returns
        -------
        dict
            The response from the API containing details if it was successful or not.
        """
        if len(project_lists) == 0:
            raise ValueError("Parameter 'project_lists' must not be empty.")

        response = self._client._session.post(
            url=f"{self._client._config.base_uri}/buyer_api/v1/CreateProjectList/",
            json={
                "job_num": job_num,
                "overwrite_existing": overwrite_existing,
                "project_lists": project_lists,
                "project_id": project_id,
            },
        )
        response.raise_for_status()
        return response.json()
