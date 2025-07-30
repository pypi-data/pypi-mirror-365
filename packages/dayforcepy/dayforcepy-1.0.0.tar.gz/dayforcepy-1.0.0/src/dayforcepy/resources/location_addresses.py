from ..client import DayforceClient
from .base_resource import BaseResource


class LocationAddresses(BaseResource):
    """Resource for managing location addresses in Dayforce."""

    def __init__(self, client: DayforceClient):
        super().__init__(client, "LocationAddresses")

    def get(
        self,
        shortName: str | None = None,
        countryCode: str | None = None,
        stateProvinceCode: str | None = None,
    ) -> list[dict]:
        """Get a list of location addresses.

        Parameters
        ----------
        shortName : str, optional
            The short name of the location address to filter by.
        countryCode : str, optional
            The country code to filter the location addresses by.
        stateProvinceCode : str, optional
            The state or province code to filter the location addresses by.

        Returns
        -------
        list[dict]
            A list of location addresses matching the specified filters.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Configuration/Organization-Data/Location-Addresses/Get-Location-Addresses.aspx
        """
        return self._send_request_get_data(
            method="GET",
            params={
                "ShortName": shortName,
                "CountryCode": countryCode,
                "StateProvinceCode": stateProvinceCode,
            },
        )

    def update(
        self, xRefCode: str, location_address: dict, isValidateOnly: bool = True
    ) -> bool:
        """Update a location address.

        Parameters
        ----------
        xRefCode : str
            The cross-reference code of the location address to update.
        isValidateOnly : bool, optional
            If True, only validate the update without making changes. Defaults to True.

        Returns
        -------
        bool
            True if the update was successful, False otherwise.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Configuration/Organization-Data/Location-Addresses/PATCH-Location-Addresses.aspx
        """
        response = self._send_request(
            method="PATCH",
            json=location_address,
            param={"IsValidateOnly": isValidateOnly},
        )
        return response.status_code == 200

    def create(self, location_address: dict, isValidateOnly: bool = True) -> bool:
        """Create a new location address.

        Parameters
        ----------
        location_address : dict
            The location address data to create.
        isValidateOnly : bool, optional
            If True, only validate the creation without making changes. Defaults to True.

        Returns
        -------
        bool
            True if the creation was successful, False otherwise.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Configuration/Organization-Data/Location-Addresses/POST-Location-Addresses.aspx
        """
        response = self._send_request(
            method="POST",
            json=location_address,
            param={"IsValidateOnly": isValidateOnly},
        )
        return response.status_code == 200
