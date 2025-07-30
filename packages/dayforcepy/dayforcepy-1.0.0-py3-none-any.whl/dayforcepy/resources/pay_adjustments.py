from datetime import datetime
from ..client import DayforceClient
from .base_resource import BaseResource


class PayAdjustments(BaseResource):
    """Resource for managing pay adjustments in Dayforce."""

    def __init__(self, client: DayforceClient):
        super().__init__(client, "EmployeePayAdjustments")

    def get(
        self,
        filterPayAdjustmentStartDate: datetime | None = None,
        filterPayAdjustmentEndDate: datetime | None = None,
        filterLastModifiedStartDateUTC: datetime | None = None,
        filterLastModifiedEndDateUTC: datetime | None = None,
        orgUnitXRefCode: str | None = None,
        employeeXRefCode: str | None = None,
        payAdjustmentCodeXRefCode: str | None = None,
        projectXRefCode: str | None = None,
        departmentXRefCode: str | None = None,
        jobXRefCode: str | None = None,
        docketXRefCode: str | None = None,
        referenceDate: datetime | None = None,
        managerAuthorized: bool | None = None,
        employeeAuthorized: bool | None = None,
        employeePayAdjustXRefCode: str | None = None,
        isDeleted: bool | None = None,
    ) -> list[dict]:
        """Get a list of pay adjustments.

        Parameters
        ----------
        filterPayAdjustmentStartDate : datetime, optional
            The inclusive start date to filter pay adjustments by.
        filterPayAdjustmentEndDate : datetime, optional
            The inclusive end date to filter pay adjustments by.
        filterLastModifiedStartDateUTC : datetime, optional
            The inclusive start date to filter pay adjustments by last modified date.
        filterLastModifiedEndDateUTC : datetime, optional
            The inclusive end date to filter pay adjustments by last modified date.
        orgUnitXRefCode : str, optional
            The organization unit cross-reference code to filter pay adjustments by.
        employeeXRefCode : str, optional
            The employee cross-reference code to filter pay adjustments by.
        payAdjustmentCodeXRefCode : str, optional
            The pay adjustment code cross-reference code to filter pay adjustments by.
        projectXRefCode : str, optional
            The project cross-reference code to filter pay adjustments by.
        departmentXRefCode : str, optional
            The department cross-reference code to filter pay adjustments by.
        jobXRefCode : str, optional
            The job cross-reference code to filter pay adjustments by.
        docketXRefCode : str, optional
            The docket cross-reference code to filter pay adjustments by.
        referenceDate : datetime, optional
            The reference date to filter pay adjustments by.
        managerAuthorized : bool, optional
            A flag to determine if a pay adjustment is manager authorized
        employeeAuthorized : bool, optional
            A flag to determine if a pay adjustment is employee authorized
        employeePayAdjustXRefCode : str, optional
            The employee pay adjustment cross-reference code to filter pay adjustments by.
        isDeleted : bool, optional
            A flag to determine if a pay adjustment is deleted

        Returns
        -------
        list[dict]
            A list of pay adjustments matching the specified filters.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Time-Management/Pay-Adjustments/Get-Employee-Pay-Adjustments.aspx
        """
        return self._paginate_request(
            self._prepare_request(
                method="GET",
                params={
                    "filterPayAdjustmentStartDate": filterPayAdjustmentStartDate,
                    "filterPayAdjustmentEndDate": filterPayAdjustmentEndDate,
                    "filterLastModifiedStartDateUTC": filterLastModifiedStartDateUTC,
                    "filterLastModifiedEndDateUTC": filterLastModifiedEndDateUTC,
                    "orgUnitXRefCode": orgUnitXRefCode,
                    "employeeXRefCode": employeeXRefCode,
                    "payAdjustmentCodeXRefCode": payAdjustmentCodeXRefCode,
                    "projectXRefCode": projectXRefCode,
                    "departmentXRefCode": departmentXRefCode,
                    "jobXRefCode": jobXRefCode,
                    "docketXRefCode": docketXRefCode,
                    "referenceDate": referenceDate,
                    "managerAuthorized": managerAuthorized,
                    "employeeAuthorized": employeeAuthorized,
                    "employeePayAdjustXRefCode": employeePayAdjustXRefCode,
                    "isDeleted": isDeleted,
                },
            )
        )

    def create(
        self,
        pay_adjustment: dict,
        isValidateOnly: bool = True,
        isValidateLabor: bool | None = None,
    ) -> bool:
        """Create a new pay adjustment.

        Parameters
        ----------
        pay_adjustment : dict
            The pay adjustment data to create.
        isValidateOnly : bool, optional
            If True, only validate the creation without making changes. Defaults to True.

        Returns
        -------
        bool
            True if the creation was successful, False otherwise.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Time-Management/Pay-Adjustments/POST-Employee-Pay-Adjustments.aspx
        """
        response = self._send_request(
            method="POST",
            json=pay_adjustment,
            params={
                "IsValidateOnly": isValidateOnly,
                "isValidateLabor": isValidateLabor,
            },
        )
        return response.status_code == 200

    def update(
        self,
        xRefCode: str,
        pay_adjustment: dict,
        isValidateOnly: bool = True,
        isValidateLabor: bool | None = None,
    ) -> bool:
        """Update an existing pay adjustment.

        Parameters
        ----------
        xRefCode : str
            The cross-reference code of the pay adjustment to update.
        pay_adjustment : dict
            The pay adjustment data to update.
        isValidateOnly : bool, optional
            If True, only validate the update without making changes. Defaults to True.

        Returns
        -------
        bool
            True if the update was successful, False otherwise.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Time-Management/Pay-Adjustments/PATCH-Employee-Pay-Adjustments.aspx
        """
        response = self._send_request(
            endpoint=xRefCode,
            method="PATCH",
            json=pay_adjustment,
            params={
                "IsValidateOnly": isValidateOnly,
                "isValidateLabor": isValidateLabor,
            },
        )
        return response.status_code == 200
