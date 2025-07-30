from ..client import DayforceClient
from .base_resource import BaseResource


class PayrollElections(BaseResource):
    """Resource for managing payroll elections in Dayforce."""

    def __init__(self, client: DayforceClient):
        super().__init__(client, "Payroll")

    def get(
        self,
        source: str | None = None,
        codeType: str | None = None,
        electionStatus: str | None = None,
        payGroupXRefCode: str | None = None,
        employeeXRefCodes: list[str] | None = None,
        employmentStatusXRefCode: str | None = None,
    ) -> list[dict]:
        """Get a list of payroll elections.

        Documentation does not specify the exact parameters, so these are inferred.

        Parameters
        ----------
        source: str, optional
            The source of the payroll election, such as "Payroll" or "Benefits".
        codeType: str, optional
            The type of code for the payroll election, such as "ELECTION" or "DEDUCTION".
        electionStatus: str, optional
            Current status of election, Documentation does not specify values.
        payGroupXRefCode: str, optional
            The cross-reference code for a pay group, such as "USA_BI_WEEKLY" or "USA_WEEKLY".
        employeeXRefCodes: list[str], optional
            A list of employee cross-reference codes to filter the payroll elections by.
        employmentStatusXRefCode: str, optional
            The cross-reference code for employment status, such as "ACTIVE" or "TERMINATED".

        Returns
        -------
        list[dict]
            A list of payroll elections matching the specified filters.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Employee-Payroll-Information/Payroll-Elections/GET-Payroll-Elections.aspx
        """
        return self._paginate_request(
            self._prepare_request(
                method="GET",
                endpoint="PayrollElection",
                params={
                    "source": source,
                    "codeType": codeType,
                    "electionStatus": electionStatus,
                    "payGroupXRefCode": payGroupXRefCode,
                    "employeeXRefCodes": ",".join(employeeXRefCodes)
                    if employeeXRefCodes
                    else None,
                    "employmentStatusXRefCode": employmentStatusXRefCode,
                },
            )
        )

    def create(
        self,
        payroll_elections: list[dict],
        isValidateOnly: bool = True,
        autoUpdateExisting: bool | None = None,
    ) -> list[dict]:
        """Create new payroll elections.
        Parameters
        ----------
        payroll_elections: list[dict]
            A list of payroll election data to create.
        isValidateOnly: bool, optional
            If True, only validate the creation without making changes. Defaults to True.
        autoUpdateExisting: bool, optional
            If True, all other elections of the same eployee will be end-dated. Defaults to None.

        Returns
        -------
        list[dict]
            A list of created payroll elections with their details.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Employee-Payroll-Information/Payroll-Elections/POST-Payroll-Elections.aspx
        """
        return self._send_request_get_data(
            method="POST",
            endpoint="PayrollElections",
            json=payroll_elections,
            params={
                "isValidateOnly": isValidateOnly,
                "AutoUpdateExisting": autoUpdateExisting,
            },
        )

    def update(
        self,
        payroll_elections: list[dict],
        isValidateOnly: bool = True,
        autoUpdateExisting: bool | None = None,
    ) -> list[dict]:
        """Update existing payroll elections.

        Parameters
        ----------
        payroll_elections: list[dict]
            A list of payroll election data to update.
        isValidateOnly: bool, optional
            If True, only validate the update without making changes. Defaults to True.
        autoUpdateExisting: bool, optional
            If True, all other elections of the same employee will be end-dated. Defaults to None.

        Returns
        -------
        list[dict]
            A list of updated payroll elections with their details.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Employee-Payroll-Information/Payroll-Elections/PATCH-Payroll-Elections.aspx
        """
        return self._send_request_get_data(
            method="PATCH",
            endpoint="PayrollElections",
            json=payroll_elections,
            params={
                "isValidateOnly": isValidateOnly,
                "AutoUpdateExisting": autoUpdateExisting,
            },
        )

    def delete(self, data: list[dict], isValidateOnly: bool = True) -> list[dict]:
        """Delete payroll elections.

        Parameters
        ----------
        data: list[dict]
            A list of payroll election data to delete.
        isValidateOnly: bool, optional
            If True, only validate the deletion without making changes. Defaults to True.

        Returns
        -------
        list[dict]
            A list of deleted payroll elections with their details.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Employee-Payroll-Information/Payroll-Elections/DELETE-Payroll-Elections.aspx
        """
        return self._send_request_get_data(
            method="PATCH",
            endpoint="DeletePayrollElections",
            json=data,
            params={"isValidateOnly": isValidateOnly},
        )
