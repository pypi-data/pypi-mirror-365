from ..client import DayforceClient
from .base_resource import BaseResource


class Departments(BaseResource):
    """Resource for managing departments in the Dayforce API."""

    def __init__(self, client: DayforceClient):
        super().__init__(client, "Departments")

    def get(self) -> list[dict]:
        """Get a list of departments.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Configuration/Organization-Data/Departments/GET-Departments.aspx
        """
        return self._send_request_get_data()

    def get_details(
        self, xRefCodes: list[str] | str | None = None, isValidateOnly: bool = True
    ) -> dict:
        """Get details of specific departments.

        Parameters
        ----------
        xRefCodes : list[str] | str, optional
            XRefCode(s) for specific departments to retrieve details for.
            If None, retrieves details for all departments.
        isValidateOnly : bool, optional
            The documentation does not specify the purpose of this parameter, and typically this is not used in GET requests.
            However, it is included here to match the method signature from the documentation

        Returns
        -------
        dict
            Details of the specified departments.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Configuration/Organization-Data/Departments/GET-Department-Details.aspx
        """
        if xRefCodes is None:
            xRefCodes = [data["XRefCode"] for data in self.get()]

        return self._send_request_get_details(
            xRefCodes=xRefCodes if isinstance(xRefCodes, list) else [xRefCodes],
            method="GET",
            params={"isValidateOnly": isValidateOnly},
        )

    def create(self, department: dict, isValidateOnly: bool = True) -> bool:
        """Create a new department.

        Parameters
        ----------
        department : dict
            The department data to create.
        isValidateOnly : bool, optional
            If True, the request will only validate the data without creating the department. Defaults to True.

        Returns
        -------
        bool
            True if the department was created successfully, False otherwise.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Configuration/Organization-Data/Departments/POST-Departments.aspx
        """
        response = self._send_request(
            method="POST",
            json=department,
            params={"isValidateOnly": isValidateOnly},
        )
        return response.status_code == 200

    def update(
        self,
        xRefCode: str,
        department: dict,
        isValidateOnly: bool = True,
    ) -> bool:
        """Update an existing department.

        Parameters
        ----------
        xRefCode : str
            The XRefCode of the department to update.
        department : dict
            The updated department data.
        isValidateOnly : bool, optional
            If True, the request will only validate the data without updating the department. Defaults to True.

        Returns
        -------
        bool
            True if the department was updated successfully, False otherwise.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Configuration/Organization-Data/Departments/PATCH-Departments.aspx
        """
        response = self._send_request(
            method="PATCH",
            json=department,
            params={"isValidateOnly": isValidateOnly},
            endpoint=xRefCode,
        )
        return response.status_code == 200
