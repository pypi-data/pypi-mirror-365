from datetime import datetime
from ..client import DayforceClient
from .base_resource import BaseResource


class WorkAssignments(BaseResource):
    """Resource for managing work assignments in Dayforce."""

    def __init__(self, client: DayforceClient):
        super().__init__(client, "Employees")

    def get(
        self,
        xRefCodes: list[str] | str,
        contextDate: datetime | None = None,
        contextDateRangeFrom: datetime | None = None,
        contextDateRangeTo: datetime | None = None,
    ) -> dict:
        """Retrieve work assignments for one or more employees.

        Parameters
        ----------
        xRefCodes : list[str] | str
            The external reference code(s) of the employees to retrieve work assignments for.
        contextDate : datetime, optional
            The specific date for which to retrieve the work assignment.
        contextDateRangeFrom : datetime, optional
            The start date of the range for which to retrieve work assignments.
        contextDateRangeTo : datetime, optional
            The end date of the range for which to retrieve work assignments.

        Returns
        -------
        dict
            Dictionary mapping employee xRefCodes to a list of their work assignments.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Employee-Work-Information/Work-Assignments/GET-Employee-Work-Assignments.aspx
        """
        return self._send_request_get_details(
            method="GET",
            xRefCodes=xRefCodes if isinstance(xRefCodes, list) else [xRefCodes],
            build_uri=lambda code: f"{code}/WorkAssignments",
            params={
                "contextDate": contextDate.isoformat() if contextDate else None,
                "contextDateRangeFrom": contextDateRangeFrom.isoformat()
                if contextDateRangeFrom
                else None,
                "contextDateRangeTo": contextDateRangeTo.isoformat()
                if contextDateRangeTo
                else None,
            },
        )

    def create(
        self,
        xRefCode: str,
        work_assignment: dict,
        isValidateOnly: bool = True,
    ) -> bool:
        """Create a new work assignment for an employee.

        Parameters
        ----------
        xRefCode : str
            The external reference code of the employee for whom to create the work assignment.
        work_assignment : dict
            The work assignment details to create.
        isValidateOnly : bool, optional
            If True, only validates the work assignment without creating it. Defaults to True.

        Returns
        -------
        bool
            True if the work assignment was successfully created or validated, False otherwise.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Employee-Work-Information/Work-Assignments/POST-Employee-Work-Assignments.aspx
        """
        response = self._send_request(
            method="POST",
            endpoint=f"{xRefCode}/WorkAssignments",
            json=work_assignment,
            params={"isValidateOnly": isValidateOnly},
        )
        return response.status_code == 200

    def update(
        self,
        xRefCode: str,
        work_assignment: dict,
        isValidateOnly: bool = True,
    ) -> bool:
        """Update an existing work assignment for an employee.

        Parameters
        ----------
        xRefCode : str
            The external reference code of the employee whose work assignment is to be updated.
        work_assignment : dict
            The updated work assignment details.
        isValidateOnly : bool, optional
            If True, only validates the work assignment without updating it. Defaults to True.

        Returns
        -------
        bool
            True if the work assignment was successfully updated or validated, False otherwise.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Employee-Work-Information/Work-Assignments/PATCH-Employee-Work-Assignments.aspx
        """
        response = self._send_request(
            method="PATCH",
            endpoint=f"{xRefCode}/WorkAssignments",
            json=work_assignment,
            params={"isValidateOnly": isValidateOnly},
        )
        return response.status_code == 200

    def replace(
        self,
        xRefCode: str,
        work_assignment: dict,
        replaceFrom: datetime | None = None,
        replaceTo: datetime | None = None,
        isValidateOnly: bool = True,
    ) -> bool:
        """Replace an existing work assignment for an employee within a date range.

        Parameters
        ----------
        xRefCode : str
            The external reference code of the employee whose work assignment is to be replaced.
        work_assignment : dict
            The new work assignment details to replace the existing one.
        replaceFrom : datetime, optional
            The start date of the replacement period.
        replaceTo : datetime, optional
            The end date of the replacement period.
        isValidateOnly : bool, optional
            If True, only validates the replacement without applying it. Defaults to True.

        Returns
        -------
        bool
            True if the work assignment was successfully replaced or validated, False otherwise.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Employee-Work-Information/Work-Assignments/PATCH-Replace-Employee-Work-Assignment.aspx
        """
        response = self._send_request(
            method="PATCH",
            endpoint=f"{xRefCode}/WorkAssignments/Replacement",
            json=work_assignment,
            params={
                "replaceFrom": replaceFrom.isoformat() if replaceFrom else None,
                "replaceTo": replaceTo.isoformat() if replaceTo else None,
                "isValidateOnly": isValidateOnly,
            },
        )
        return response.status_code == 200
