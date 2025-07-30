from datetime import datetime
from ..client import DayforceClient
from .base_resource import BaseResource


class Projects(BaseResource):
    """Resource for managing projects in Dayforce."""

    def __init__(self, client: DayforceClient):
        super().__init__(client, "Projects")

    def get(
        self,
        shortName: str | None = None,
        longName: str | None = None,
        projectClientXRefCode: str | None = None,
        projectTypeXRefCode: str | None = None,
        projectPhaseXRefCode: str | None = None,
        productGroupXRefCode: str | None = None,
        productModuleXRefCode: str | None = None,
        creationOrgUnitXRefCode: str | None = None,
        lastModifedStartDate: datetime | None = None,
        lastModifedEndDate: datetime | None = None,
        filterStartDateFrom: datetime | None = None,
        filterStartDateTo: datetime | None = None,
        filterDueDateFrom: datetime | None = None,
        filterDueDateTo: datetime | None = None,
        filterCompletedDateFrom: datetime | None = None,
        filterCompletedDateTo: datetime | None = None,
        certifiedPayrollProjectNumber: int | None = None,
        parentProjectXRefCode: str | None = None,
        isDeleted: bool | None = None,
        ledgerCode: str | None = None,
        clockTransferCode: str | None = None,
        accountNum: str | None = None,
        iFRSClassification: bool | None = None,
        filterProjectPriorityFrom: int | None = None,
        filterProjectPriorityTo: int | None = None,
        filterBudgetHoursFrom: float | None = None,
        filterBudgetHoursTo: float | None = None,
        filterBudgetAmountFrom: float | None = None,
        filterBudgetAmountTo: float | None = None,
        filterPctCompleteFrom: float | None = None,
        filterPctCompleteTo: float | None = None,
    ) -> list[dict]:
        """
        Get a list of client projects matching the search criteria.

        Parameters
        ----------
        shortName : str, optional
            Project Name. Partial value allowed for a wider search.
        longName : str, optional
            Project Description. Partial value allowed for a wider search.
        projectClientXRefCode : str, optional
            Identifies a unique Project Client.
        projectTypeXRefCode : str, optional
            Identifies a unique Project Type.
        projectPhaseXRefCode : str, optional
            Identifies a unique Project Phase.
        productGroupXRefCode : str, optional
            Identifies a unique Product Group.
        productModuleXRefCode : str, optional
            Identifies a unique Product Module.
        creationOrgUnitXRefCode : str, optional
            Search for projects based on Organizational Unit xrefcode.
        lastModifedStartDate : datetime, optional
            The start date used when searching for projects with updates in a specified timeframe.
        lastModifedEndDate : datetime, optional
            The end date used when searching for projects with updates in a specified timeframe.
        filterStartDateFrom : datetime, optional
            Search for projects with Start Date values greater than or equal to the specified value.
        filterStartDateTo : datetime, optional
            Search for projects with Start Date values less than or equal to the specified value.
        filterDueDateFrom : datetime, optional
            Search for projects with Due Date values greater than or equal to the specified value.
        filterDueDateTo : datetime, optional
            Search for projects with Due Date values less than or equal to the specified value.
        filterCompletedDateFrom : datetime, optional
            Search for projects with Completed Date values greater than or equal to the specified value.
        filterCompletedDateTo : datetime, optional
            Search for projects with Completed Date values less than or equal to the specified value.
        certifiedPayrollProjectNumber : int, optional
            Search for projects with Certified Payroll Project Number.
        parentProjectXRefCode : str, optional
            Search for projects with immediate Parent Project.
        isDeleted : bool, optional
            Filter projects based on whether they are deleted or not.
        ledgerCode : str, optional
            Search for projects with Ledger Code.
        clockTransferCode : str, optional
            Search for projects with Clock Code.
        accountNum : str, optional
            Search for projects with Account Number.
        iFRSClassification : bool, optional
            Search for projects with IFRS Classification.
        filterProjectPriorityFrom : int, optional
            Search for projects with Project Priority value greater than or equal to the specified value.
        filterProjectPriorityTo : int, optional
            Search for projects with Project Priority value less than or equal to the specified value.
        filterBudgetHoursFrom : float, optional
            Search for projects with Budget Hours value greater than or equal to the specified value.
        filterBudgetHoursTo : float, optional
            Search for projects with Budget Hours value less than or equal to the specified value.
        filterBudgetAmountFrom : float, optional
            Search for projects with Budget Amount value greater than or equal to the specified value.
        filterBudgetAmountTo : float, optional
            Search for projects with Budget Amount value less than or equal to the specified value.
        filterPctCompleteFrom : float, optional
            Search for projects with Percent Complete value greater than or equal to the specified value.
        filterPctCompleteTo : float, optional
            Search for projects with Percent Complete value less than or equal to the specified value.

        Returns
        -------
        list of dict
            A collection of client project objects matching the search criteria.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Time-Management/Projects/Get-List-of-Projects.aspx
        """
        return self._paginate_request(
            self._prepare_request(
                method="GET",
                params={
                    "shortName": shortName,
                    "longName": longName,
                    "projectClientXRefCode": projectClientXRefCode,
                    "projectTypeXRefCode": projectTypeXRefCode,
                    "projectPhaseXRefCode": projectPhaseXRefCode,
                    "productGroupXRefCode": productGroupXRefCode,
                    "productModuleXRefCode": productModuleXRefCode,
                    "creationOrgUnitXRefCode": creationOrgUnitXRefCode,
                    "lastModifedStartDate": lastModifedStartDate,
                    "lastModifedEndDate": lastModifedEndDate,
                    "filterStartDateFrom": filterStartDateFrom,
                    "filterStartDateTo": filterStartDateTo,
                    "filterDueDateFrom": filterDueDateFrom,
                    "filterDueDateTo": filterDueDateTo,
                    "filterCompletedDateFrom": filterCompletedDateFrom,
                    "filterCompletedDateTo": filterCompletedDateTo,
                    "certifiedPayrollProjectNumber": certifiedPayrollProjectNumber,
                    "parentProjectXRefCode": parentProjectXRefCode,
                    "isDeleted": isDeleted,
                    "ledgerCode": ledgerCode,
                    "clockTransferCode": clockTransferCode,
                    "accountNum": accountNum,
                    "iFRSClassification": iFRSClassification,
                    "filterProjectPriorityFrom": filterProjectPriorityFrom,
                    "filterProjectPriorityTo": filterProjectPriorityTo,
                    "filterBudgetHoursFrom": filterBudgetHoursFrom,
                    "filterBudgetHoursTo": filterBudgetHoursTo,
                    "filterBudgetAmountFrom": filterBudgetAmountFrom,
                    "filterBudgetAmountTo": filterBudgetAmountTo,
                    "filterPctCompleteFrom": filterPctCompleteFrom,
                    "filterPctCompleteTo": filterPctCompleteTo,
                },
            )
        )

    def get_details(self, xRefCodes: list[str] | str) -> dict:
        """
        Get details of the projects with the specified cross-reference code(s).

        Parameters
        ----------
        xRefCodes : list[str] | str
            The cross-reference code(s) of the project to retrieve details for.

        Returns
        -------
        dict
            A dictionary mapping project XRefCode to its details.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Time-Management/Projects/Get-Projects.aspx
        """
        return self._send_request_get_details(
            method="GET",
            xRefCodes=xRefCodes if isinstance(xRefCodes, list) else [xRefCodes],
        )

    def create(
        self,
        project: dict,
        isValidateOnly: bool = True,
    ) -> dict:
        """
        Create a new project.

        Parameters
        ----------
        project : dict
            The project data to create.
        isValidateOnly : bool, optional
            If True, only validate the creation without making changes. Defaults to True.

        Returns
        -------
        dict
            The created project with its details.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Time-Management/Projects/Post-Projects.aspx
        """
        return self._send_request(
            method="POST",
            json=project,
            params={"isValidateOnly": isValidateOnly},
        ).json()

    def update(
        self,
        xRefCode: str,
        project: dict,
        isValidateOnly: bool = True,
    ) -> bool:
        """
        Update an existing project.

        Parameters
        ----------
        xRefCode : str
            The cross-reference code of the project to update.
        project : dict
            The project data to update.
        isValidateOnly : bool, optional
            If True, only validate the update without making changes. Defaults to True.

        Returns
        -------
        bool
            True if the update was successful, False otherwise.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Time-Management/Projects/Patch-Projects.aspx
        """
        response = self._send_request(
            method="PATCH",
            json=project,
            params={"projectXRefCode": xRefCode, "isValidateOnly": isValidateOnly},
        )
        return response.status_code == 200
