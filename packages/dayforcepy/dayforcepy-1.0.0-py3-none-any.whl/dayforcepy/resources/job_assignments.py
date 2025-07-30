from datetime import datetime
from ..client import DayforceClient
from .base_resource import BaseResource


class JobAssignments(BaseResource):
    """Resource for managing positions in Dayforce."""

    def __init__(self, client: DayforceClient):
        super().__init__(client, "Positions")

    def get(
        self,
        contextData: datetime | None = None,
    ) -> list[dict]:
        """Get a list of job assignments.

        Parameters
        ----------
        contextData : datetime, optional
            The Context Date value is an “as-of” date used to determine which Position data to search when records have specific start and end dates.
            The service defaults to the current datetime if the requester does not specify a value.

        Returns
        -------
        list[dict]
            A list of positions matching the specified filters.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Configuration/Organization-Data/Positions/Get-Positions.aspx
        """
        return self._send_request_get_data(
            method="GET",
            params={
                "contextData": contextData.isoformat() if contextData else None,
            },
        )

    def get_details(
        self,
        xRefCode: str,
        contextData: datetime | None = None,
        expander: list[str] | None = None,
    ) -> dict:
        """Get details of a specific job assignment.

        Parameters
        ----------
        xRefCode : str
            The cross-reference code of the job assignment to retrieve details for.
        contextData : datetime, optional
            The Context Date value is an “as-of” date used to determine which Position data to search when records have specific start and end dates.
            The service defaults to the current datetime if the requester does not specify a value.
        expander : list[str], optional
            A list of fields to expand in the response, such as "PositionDetails" or "PositionAssignments".
            There is no documentation on the exact values, so this is inferred.

        Returns
        -------
        dict
            A dictionary containing the details of the specified job assignment.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Configuration/Organization-Data/Positions/GET-Position-Details.aspx
        """
        return self._send_request_get_data(
            method="GET",
            endpoint=xRefCode,
            params={
                "contextData": contextData.isoformat() if contextData else None,
                "expander": ",".join(expander) if expander else None,
            },
        )

    def create(
        self,
        job_assignment: dict,
        isValidateOnly: bool = True,
    ) -> bool:
        """Create a new job assignment.

        Parameters
        ----------
        job_assignment : dict
            The job assignment data to create.
        isValidateOnly : bool, optional
            If True, only validate the creation without making changes. Defaults to True.

        Returns
        -------
        bool
            True if the creation was successful, False otherwise.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Configuration/Organization-Data/Positions/POST-Positions.aspx
        """
        response = self._send_request(
            method="POST",
            json=job_assignment,
            params={"isValidateOnly": isValidateOnly},
        )
        return response.status_code == 200

    def update(
        self,
        xRefCode: str,
        job_assignment: dict,
        isValidateOnly: bool = True,
    ) -> bool:
        """Update an existing job assignment.

        Parameters
        ----------
        xRefCode : str
            The cross-reference code of the job assignment to update.
        job_assignment : dict
            The job assignment data to update.
        isValidateOnly : bool, optional
            If True, only validate the update without making changes. Defaults to True.

        Returns
        -------
        bool
            True if the update was successful, False otherwise.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Configuration/Organization-Data/Positions/PATCH-Positions.aspx
        """
        response = self._send_request(
            method="PATCH",
            endpoint=xRefCode,
            json=job_assignment,
            params={"isValidateOnly": isValidateOnly},
        )
        return response.status_code == 200
