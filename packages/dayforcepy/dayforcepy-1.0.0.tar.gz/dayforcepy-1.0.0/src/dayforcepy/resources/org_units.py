from datetime import datetime
from .base_resource import BaseResource
from ..client import DayforceClient

from typing import NamedTuple


class OrgUnitExpander(NamedTuple):
    """NamedTuple to specify which related data to include in the response for organization unit details.

    Attributes
    ----------
    OrgUnitParents : bool
        Include parent organization units.
    OrgUnitLegalEntities : bool
        Include legal entities associated with the organization unit.
    OrgUnitLocationTypes : bool
        Include location types associated with the organization unit.
    """

    OrgUnitParents: bool = False
    OrgUnitLegalEntities: bool = False
    OrgUnitLocationTypes: bool = False


class OrgUnits(BaseResource):
    """Resource for managing organization units in the Dayforce API."""

    def __init__(self, client: DayforceClient):
        super().__init__(client, "OrgUnits")

    def get(self, filter: str | None = None) -> list[dict]:
        """Get a list of organization units.

        Parameters
        ----------
        filter : str, optional
            Filter to apply to the organization units. TODO: What is this, documentation is not clear if its a date, xRefCode, etc.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Configuration/Organization-Data/Org-Units/GET-Org-Units.aspx
        """
        return self._send_request_get_data(
            params={"filter": filter} if filter else None,
        )

    def get_details(
        self,
        xRefCodes: list[str] | str | None = None,
        expander: OrgUnitExpander | None = None,
        contextDate: datetime | None = None,
        includeChildOrgUnits: bool | None = None,
    ) -> dict:
        """Get details of a specific organization unit.

        Parameters
        ----------
        xRefCodes : list[str] | str, optional
            If None, retrieves details for all organization units.
            If provided, retrieves details for the specified reference code(s).
        expander : OrgUnitExpand, optional
            Specifies which related data to include in the response. Defaults to None.
        contextDate : datetime, optional
            Retrieves the organization unit as of a specific date. Defaults to None.
        includeChildOrgUnits : bool, optional
            If True, includes child organization units in the response. Defaults to None.

        Returns
        -------
        dict
            A dictionary where the keys are the xRefCodes and the values are the data returned from the API for each xRefCode.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Configuration/Organization-Data/Org-Units/PATCH-Org-Units.aspx
        """
        if xRefCodes is None:
            xRefCodes = [data["XRefCode"] for data in self.get()]

        return self._send_request_get_details(
            xRefCodes=xRefCodes if isinstance(xRefCodes, list) else [xRefCodes],
            method="GET",
            params={
                "expand": expander,
                "contextDate": contextDate.isoformat() if contextDate else None,
                "includeChildOrgUnits": includeChildOrgUnits,
            },
        )

    def create(
        self,
        org_unit: dict,
        isValidateOnly: bool = True,
        calibrateOrg: bool | None = None,
    ) -> bool:
        """Create or update an organization unit.

        Parameters
        ----------
        org_unit : dict
            The organization unit data to create or update.
        isValidateOnly : bool, optional
            If True, performs validation only without making changes. Defaults to True.
        calibrateOrg : bool, optional
            If True, recalibrates the organization unit after creation or update. Defaults to None.

        Returns
        -------
        bool
            True if the operation was successful, False otherwise.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Configuration/Organization-Data/Org-Units/POST-Org-Units.aspx
        """
        response = self._send_request(
            method="POST",
            json=org_unit,
            params={
                "isValidateOnly": isValidateOnly,
                "calibrateOrg": calibrateOrg,
            },
        )
        return response.status_code == 200

    def update(
        self,
        xRefCode: str,
        org_unit: dict,
        isValidateOnly: bool = True,
        replaceExisting: str | None = None,
        calibrateOrg: bool | None = None,
    ) -> bool:
        """Update an existing organization unit.

        Parameters
        ----------
        xRefCode : str
            The unique reference code of the organization unit to update.
        org_unit : dict
            The updated organization unit data.
        isValidateOnly : bool, optional
            If True, performs validation only without making changes. Defaults to True.
        replaceExisting : str, optional
            This parameter accepts a comma-separated list of OrgUnit sub-entities where the respective data provided will replace all existing records.
            This currently applies to OrgUnitLocationTypes sub-entities, which are considered as a list and are not effective dated.
        calibrateOrg : bool, optional
            If True, recalibrates the organization unit after update. Defaults to None.

        Returns
        -------
        bool
            True if the operation was successful, False otherwise.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Configuration/Organization-Data/Org-Units/PATCH-Org-Unit.aspx
        """
        response = self._send_request(
            method="PATCH",
            endpoint=xRefCode,
            json=org_unit,
            params={
                "isValidateOnly": isValidateOnly,
                "replaceExisting": replaceExisting,
                "calibrateOrg": calibrateOrg,
            },
        )
        return response.status_code == 200
