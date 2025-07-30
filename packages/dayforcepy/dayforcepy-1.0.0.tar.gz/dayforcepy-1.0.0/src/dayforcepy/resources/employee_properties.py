from datetime import datetime
from ..client import DayforceClient
from .base_resource import BaseResource


class EmployeeProperties(BaseResource):
    """Resource for managing employee properties in the Dayforce API."""

    def __init__(self, client: DayforceClient):
        super().__init__(client, "Employees")

    def get(
        self,
        xRefCode: list[str] | str,
        contextDate: datetime | None = None,
        contextDateRangeFrom: datetime | None = None,
        contextDateRangeTo: datetime | None = None,
    ) -> dict:
        """Get a list of employee properties.

        Parameters
        ----------
        xRefCode : list[str] | str
            XRefCode(s) for specific employees to retrieve properties for.
            If a single string is provided, it will be treated as a single employee.
        contextDate : datetime, optional
            The Context Date value is an “as-of” date used to determine which employee data to search when records have specific start and end dates.
            The service defaults to the current datetime if the requester does not specify a value.
        contextDateRangeFrom : datetime, optional
            The start date for the context date range. If not specified, defaults to null.
        contextDateRangeTo : datetime, optional
            The end date for the context date range. If not specified, defaults to null.

        Returns
        -------
        dict
            A dictionary with they key being the xRefCode and the value containing the employee properties for the specified employee.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Employee-Employment-Information/Properties/GET-Employee-Properties.aspx
        """
        return self._send_request_get_details(
            method="GET",
            xRefCodes=xRefCode if isinstance(xRefCode, list) else [xRefCode],
            build_uri=lambda code: f"{code}/EmployeeProperties",
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
        properties: dict,
        isValidateOnly: bool = True,
    ) -> bool:
        """Create a new employee property.

        Parameters
        ----------
        xRefCode : str
            The XRefCode of the employee to create the property for.
        properties : dict
            The properties to create for the employee.
        isValidateOnly : bool, optional
            If True, the request will only validate the data without creating the property. Defaults to True.

        Returns
        -------
        bool
            True if the property was created successfully, False otherwise.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Employee-Employment-Information/Properties/POST-Employee-Properties.aspx
        """
        response = self._send_request(
            method="POST",
            endpoint=f"{xRefCode}/EmployeeProperties",
            json=properties,
            params={"isValidateOnly": isValidateOnly},
        )
        return response.status_code == 200

    def update(
        self,
        xRefCode: str,
        properties: dict,
        isValidateOnly: bool = True,
    ) -> bool:
        """Updates a employee property.

        Parameters
        ----------
        xRefCode : str
            The XRefCode of the employee to update for.
        properties : dict
            The properties to update for the employee.
        isValidateOnly : bool, optional
            If True, the request will only validate the data without creating the property. Defaults to True.

        Returns
        -------
        bool
            True if the property was updated successfully, False otherwise.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Employee-Employment-Information/Properties/PATCH-Employee-Properties.aspx
        """
        response = self._send_request(
            method="PATCH",
            endpoint=f"{xRefCode}/EmployeeProperties",
            json=properties,
            params={"isValidateOnly": isValidateOnly},
        )
        return response.status_code == 200
