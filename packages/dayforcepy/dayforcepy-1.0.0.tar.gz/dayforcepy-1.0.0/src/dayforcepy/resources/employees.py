from datetime import datetime
from ..client import DayforceClient
from .base_resource import BaseResource

from typing import NamedTuple


class EmployeeExpander(NamedTuple):
    """Specifies which related data to include in the response for employee details.

    Attributes
    ----------
    Addresses : bool, optional
        Include employee addresses.
    AuthorizationAssignments : bool, optional
        Include authorization assignments.
    ClockDeviceGroups : bool, optional
        Include clock device groups.
    CompensationSummary : bool, optional
        Include compensation summary.
    Contacts : bool, optional
        Include employee contacts.
    Courses : bool, optional
        Include courses.
    DirectDeposit : bool, optional
        Include direct deposit information.
    DocumentedManagementSecurityGroups : bool, optional
        Include documented management security groups.
    EIRates : bool, optional
        Include EI rates.
    EmployeeCertifications : bool, optional
        Include employee certifications.
    EmergencyContacts : bool, optional
        Include emergency contacts.
    EmployeeManagers : bool, optional
        Include employee managers.
    EmployeeProperties : bool, optional
        Include employee properties.
    EmployeePayAdjustCodeGroups : bool, optional
        Include employee pay adjust code groups.
    EmployeeWorkAssignmentManagers : bool, optional
        Include employee work assignment managers.
    EmploymentAgreements : bool, optional
        Include employment agreements.
    EmploymentStatuses : bool, optional
        Include employment statuses.
    EmploymentTypes : bool, optional
        Include employment types.
    Ethnicities : bool, optional
        Include ethnicities.
    GlobalProperties : bool, optional
        Include global properties.
    GLSplits : bool, optional
        Include GL splits.
    HealthWellnessDetails : bool, optional
        Include health and wellness details.
    HighlyCompensatedEmployees : bool, optional
        Include highly compensated employees.
    HRIncidents : bool, optional
        Include HR incidents.
    LaborDefaults : bool, optional
        Include labor defaults.
    Locations : bool, optional
        Include locations.
    MaritalStatuses : bool, optional
        Include marital statuses.
    OnboardingPolicies : bool, optional
        Include onboarding policies.
    OrgUnitInfos : bool, optional
        Include organizational unit information.
    PayGradeRates : bool, optional
        Include pay grade rates.
    PerformanceRatings : bool, optional
        Include performance ratings.
    Roles : bool, optional
        Include roles.
    Skills : bool, optional
        Include skills.
    SSOAccounts : bool, optional
        Include SSO accounts.
    TrainingPrograms : bool, optional
        Include training programs.
    UnionMemberships : bool, optional
        Include union memberships.
    UserPayAdjustCodeGroups : bool, optional
        Include user pay adjust code groups.
    USFederalTaxes : bool, optional
        Include US federal taxes.
    USStateTaxes : bool, optional
        Include US state taxes.
    USTaxStatuses : bool, optional
        Include US tax statuses.
    WorkAssignments : bool, optional
        Include work assignments.
    WorkContracts : bool, optional
        Include work contracts.

    See Also
    --------
    https://developers.dayforce.com/Build/API-Explorer/Employee/GET-Employee-Details/Expanders.aspx
    """

    Addresses: bool = False
    AuthorizationAssignments: bool = False
    ClockDeviceGroups: bool = False
    CompensationSummary: bool = False
    Contacts: bool = False
    Courses: bool = False
    DirectDeposit: bool = False
    DocumentedManagementSecurityGroups: bool = False
    EIRates: bool = False
    EmployeeCertifications: bool = False
    EmergencyContacts: bool = False
    EmployeeManagers: bool = False
    EmployeeProperties: bool = False
    EmployeePayAdjustCodeGroups: bool = False
    EmployeeWorkAssignmentManagers: bool = False
    EmploymentAgreements: bool = False
    EmploymentStatuses: bool = False
    EmploymentTypes: bool = False
    Ethnicities: bool = False
    GlobalProperties: bool = False
    GLSplits: bool = False
    HealthWellnessDetails: bool = False
    HighlyCompensatedEmployees: bool = False
    HRIncidents: bool = False
    LaborDefaults: bool = False
    Locations: bool = False
    MaritalStatuses: bool = False
    OnboardingPolicies: bool = False
    OrgUnitInfos: bool = False
    PayGradeRates: bool = False
    PerformanceRatings: bool = False
    Roles: bool = False
    Skills: bool = False
    SSOAccounts: bool = False
    TrainingPrograms: bool = False
    UnionMemberships: bool = False
    UserPayAdjustCodeGroups: bool = False
    USFederalTaxes: bool = False
    USStateTaxes: bool = False
    USTaxStatuses: bool = False
    WorkAssignments: bool = False
    WorkContracts: bool = False


class Employees(BaseResource):
    """Resource for managing employees in the Dayforce API."""

    def __init__(self, client: DayforceClient):
        super().__init__(client, "Employees")

    def get(
        self,
        employeeNumber: str | None = None,
        displayName: str | None = None,
        socialSecurityNumber: str | None = None,
        employmentStatusXRefCode: list[str] | str | None = None,
        orgUnitXRefCode: str | None = None,
        departmentXRefCode: str | None = None,
        jobXRefCode: str | None = None,
        positionXRefCode: str | None = None,
        payClassXRefCode: str | None = None,
        payGroupXRefCode: str | None = None,
        payPolicyXRefCode: str | None = None,
        payTypeXRefCode: str | None = None,
        payrollPolicyXRefCode: str | None = None,
        filterHireStartDate: datetime | None = None,
        filterHireEndDate: datetime | None = None,
        filterTerminationStartDate: datetime | None = None,
        filterTerminationEndDate: datetime | None = None,
        filterUpdatedStartDate: datetime | None = None,
        filterUpdatedEndDate: datetime | None = None,
        filterUpdatedEntites: list[str] | str | None = None,
        filterOriginalHireStartDate: datetime | None = None,
        filterOriginalHireEndDate: datetime | None = None,
        filterSeniorityStartDate: datetime | None = None,
        filterSeniorityEndDate: datetime | None = None,
        filterBaseSalaryFrom: float | None = None,
        filterBaseSalaryTo: float | None = None,
        filterBaseRateFrom: float | None = None,
        filterBaseRateTo: float | None = None,
        contextDate: datetime | None = None,
    ):
        """Get a list of employees.

        Parameters
        ----------
        employeeNumber : str, optional
            Unique identifier assigned to an employee. Partial value allowed for a wider search.
        displayName : str, optional
            Employee name. Partial value allowed for a wider search.
        socialSecurityNumber : str, optional
            Social Security Number of the employee. Partial value allowed for a wider search.
        employmentStatusXRefCode : list[str] | str, optional
            Employment status xrefcode(s), can be a single value or list. Allows searching by one or more employment statuses.
        orgUnitXRefCode : str, optional
            Organizational unit xrefcode. Allows searching by org unit at a point in time.
        departmentXRefCode : str, optional
            Department xrefcode. Allows searching by department at a point in time.
        jobXRefCode : str, optional
            Job xrefcode. Allows searching by job at a point in time.
        positionXRefCode : str, optional
            Position xrefcode. Allows searching by position at a point in time.
        payClassXRefCode : str, optional
            Pay class xrefcode. Allows searching by pay class at a point in time.
        payGroupXRefCode : str, optional
            Pay group xrefcode. Allows searching by pay group at a point in time.
        payPolicyXRefCode : str, optional
            Pay policy xrefcode. Allows searching by pay policy at a point in time.
        payTypeXRefCode : str, optional
            Pay type xrefcode. Allows searching by pay type at a point in time.
        payrollPolicyXRefCode : str, optional
            Payroll policy xrefcode. Allows searching by payroll policy at a point in time.
        filterHireStartDate : datetime, optional
            Search for employees whose hire date is greater than or equal to this value.
        filterHireEndDate : datetime, optional
            Search for employees whose hire date is less than or equal to this value.
        filterTerminationStartDate : datetime, optional
            Search for employees whose termination date is greater than or equal to this value.
        filterTerminationEndDate : datetime, optional
            Search for employees whose termination date is less than or equal to this value.
        filterUpdatedStartDate : datetime, optional
            Search for employees with updates (and newly effective records) since this date.
        filterUpdatedEndDate : datetime, optional
            Search for employees with updates (and newly effective records) up to this date.
        filterUpdatedEntites : list[str] | str, optional
            Search for employees with changes to specific employee sub-entities.
        filterOriginalHireStartDate : datetime, optional
            Search for employees with original hire date greater than or equal to this value.
        filterOriginalHireEndDate : datetime, optional
            Search for employees with original hire date less than or equal to this value.
        filterSeniorityStartDate : datetime, optional
            Search for employees whose seniority date is greater than or equal to this value.
        filterSeniorityEndDate : datetime, optional
            Search for employees whose seniority date is less than or equal to this value.
        filterBaseSalaryFrom : float, optional
            Search for employees whose base salary is greater than or equal to this value.
        filterBaseSalaryTo : float, optional
            Search for employees whose base salary is less than or equal to this value.
        filterBaseRateFrom : float, optional
            Search for employees whose base rate is greater than or equal to this value.
        filterBaseRateTo : float, optional
            Search for employees whose base rate is less than or equal to this value.
        contextDate : datetime, optional
            The "as of" date used to determine which employee data to select.

        Returns
        -------
        list[dict]
            A list of dictionaries containing employee XRefCodes.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Employee/GET-Employees.aspx
        """
        return self._send_request_get_data(
            method="GET",
            params={
                "employeeNumber": employeeNumber,
                "displayName": displayName,
                "socialSecurityNumber": socialSecurityNumber,
                "employmentStatusXRefCode": ",".join(employmentStatusXRefCode)
                if isinstance(employmentStatusXRefCode, list)
                else employmentStatusXRefCode,
                "orgUnitXRefCode": orgUnitXRefCode,
                "departmentXRefCode": departmentXRefCode,
                "jobXRefCode": jobXRefCode,
                "positionXRefCode": positionXRefCode,
                "payClassXRefCode": payClassXRefCode,
                "payGroupXRefCode": payGroupXRefCode,
                "payPolicyXRefCode": payPolicyXRefCode,
                "payTypeXRefCode": payTypeXRefCode,
                "payrollPolicyXRefCode": payrollPolicyXRefCode,
                "filterHireStartDate": filterHireStartDate.isoformat()
                if filterHireStartDate
                else None,
                "filterHireEndDate": filterHireEndDate.isoformat()
                if filterHireEndDate
                else None,
                "filterTerminationStartDate": filterTerminationStartDate.isoformat()
                if filterTerminationStartDate
                else None,
                "filterTerminationEndDate": filterTerminationEndDate.isoformat()
                if filterTerminationEndDate
                else None,
                "filterUpdatedStartDate": filterUpdatedStartDate.isoformat()
                if filterUpdatedStartDate
                else None,
                "filterUpdatedEndDate": filterUpdatedEndDate.isoformat()
                if filterUpdatedEndDate
                else None,
                "filterUpdatedEntites": ",".join(filterUpdatedEntites)
                if isinstance(filterUpdatedEntites, list)
                else filterUpdatedEntites,
                "filterOriginalHireStartDate": filterOriginalHireStartDate.isoformat()
                if filterOriginalHireStartDate
                else None,
                "filterOriginalHireEndDate": filterOriginalHireEndDate.isoformat()
                if filterOriginalHireEndDate
                else None,
                "filterSeniorityStartDate": filterSeniorityStartDate.isoformat()
                if filterSeniorityStartDate
                else None,
                "filterSeniorityEndDate": filterSeniorityEndDate.isoformat()
                if filterSeniorityEndDate
                else None,
                "filterBaseSalaryFrom": filterBaseSalaryFrom,
                "filterBaseSalaryTo": filterBaseSalaryTo,
                "filterBaseRateFrom": filterBaseRateFrom,
                "filterBaseRateTo": filterBaseRateTo,
                "contextDate": contextDate.isoformat() if contextDate else None,
            },
        )

    def get_details(
        self,
        xRefCodes: list[str] | str,
        contextDate: datetime | None = None,
        expander: EmployeeExpander | None = None,
        contextDateRangeFrom: datetime | None = None,
        contextDateRangeTo: datetime | None = None,
        amfEntity: str | None = None,
        amfLevel: str | None = None,
        amfLevelValue: str | None = None,
    ) -> dict:
        """Get details of specific employees.

        Parameters
        ----------
        xRefCodes : list[str] | str
            XRefCode(s) for specific employees to retrieve details for.
        contextDate : datetime, optional
            The Context Date value is an “as-of” date used to determine which employee data to search when records have specific start and end dates.
            The service defaults to the current datetime if the requester does not specify a value.
        expander : EmployeeExpander, optional
            Specifies which related data to include in the response. Defaults to None.
        contextDateRangeFrom : datetime, optional
            The start date for the context date range. If not specified, defaults to null.
        contextDateRangeTo : datetime, optional
            The end date for the context date range. If not specified, defaults to null.
        amfEntity : str, optional
            This parameter is to identify the application object for Application Metadata Framework (AMF) request.
        amfLevel : str, optional
            This parameter is to identify the level for Application Metadata Framework (AMF) request.
        amfLevelValue : str, optional
            This parameter is to identify context specific to amfLevel for Application Metadata Framework (AMF) request.

        Returns
        -------
        dict
            A dictionary where the keys are the xRefCodes and the values are the data returned from the API for each xRefCode.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Employee/GET-Employee-Details.aspx
        """
        return self._send_request_get_details(
            xRefCodes=xRefCodes if isinstance(xRefCodes, list) else [xRefCodes],
            method="GET",
            build_uri=lambda code: f"{code}/Details",
            params={
                "contextDate": contextDate.isoformat() if contextDate else None,
                "expand": expander,
                "contextDateRangeFrom": contextDateRangeFrom.isoformat()
                if contextDateRangeFrom
                else None,
                "contextDateRangeTo": contextDateRangeTo.isoformat()
                if contextDateRangeTo
                else None,
                "amfEntity": amfEntity,
                "amfLevel": amfLevel,
                "amfLevelValue": amfLevelValue,
            },
        )

    def create(
        self,
        employee: dict,
        isValidateOnly: bool = True,
    ) -> bool:
        """Create a new employee.

        Parameters
        ----------
        employee : dict
            The employee data to create.
        isValidateOnly : bool, optional
            If True, the request will only validate the data without creating the employee. Defaults to True.

        Returns
        -------
        bool
            True if the employee was created successfully, False otherwise.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Employee/POST-Employee.aspx
        """
        response = self._send_request(
            method="POST",
            json=employee,
            params={"isValidateOnly": isValidateOnly},
        )
        return response.status_code == 200

    def update(
        self,
        xRefCode: str,
        employee: dict,
        isValidateOnly: bool = True,
        replaceExisting: list[str] | None = None,
    ) -> bool:
        """Update an existing employee.

        Parameters
        ----------
        xRefCode : str
            The XRefCode of the employee to update.
        employee : dict
            The updated employee data.
        isValidateOnly : bool, optional
            If True, the request will only validate the data without updating the employee. Defaults to True.
        replaceExisting : list[str], optional
            List of employee-subordinate entities where the respective data provided will replace all existing records

        Returns
        -------
        bool
            True if the employee was updated successfully, False otherwise.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Employee/PATCH-Employee.aspx
        """
        response = self._send_request(
            method="PATCH",
            endpoint=f"{xRefCode}",
            json=employee,
            params={
                "isValidateOnly": isValidateOnly,
                "replaceExisting": ",".join(replaceExisting)
                if replaceExisting
                else None,
            },
        )
        return response.status_code == 200
