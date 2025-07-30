# dayforcepy

A Python connector for the Dayforce HCM API, providing convenient access to Dayforce resources such as employees, departments, projects, job assignments, and more.

## Installation

```sh
pip install dayforcepy
```

## Overview

This package provides a set of resource classes that map to Dayforce API endpoints. Each resource class encapsulates methods for retrieving, creating, updating, and managing Dayforce data entities. The resource classes are the lowest level implementation of the Dayforce API, a direction translation.

Higher level implementations that are easier to use exist. For example for the low level `AnalyticsDataConnector`, there is the `ReportFactory` that allows high-level editting of the filters, parameters, and retry logic without needing to expose the base API.

```py
import asyncio
from datetime import datetime
import pandas as pd
from dayforcepy import (
    DayforceClient,
    DayforceConfig,
    ReportFactory,
)

client = DayforceClient(
    DayforceConfig(
        username="<username>",
        password="<password>",
        environment=Environment.test,
        company_id_config=EnvironmentConfig(test="<company_test_id>")
    )
)

factory = ReportFactory(client=client)

# SYNC Example
df1 = factory.create_job(report_id="<report>").simple_report_as_df()
# OR
df2 = (
    factory.create_job(report_id="<report>")
    .get_report_metadata()
    .update_filter("Status", ["Terminated", "Pre-start", "Pre-term"])
    .update_parameter("@StartDate", datetime(2023, 1, 1))
    .metadata_report_as_df()
)

# ASYNC Example, that polls for the completion of the reports asynchronously to avoid blocking
def retrieve_reports() -> list[pd.DataFrame]:
    job1 = (
        factory.create_job(report_id="<REPORT>")
        .get_report_metadata()
        .update_filter("Status", ["Terminated", "Pre-start", "Pre-term"])
        .generate_dataset()
    )

    job2 = (
        factory.create_job(report_id="<REPORT>")
        .get_report_metadata()
        .generate_dataset()
    )

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(
        asyncio.gather(
            *[
                job1.async_wait_until_complete(),
                job2.async_wait_until_complete(),
            ]
        )
    )

    job1.get_report()
    job2.get_report()

    return [
        job1.as_dataframe(),
        job2.as_dataframe(),
    ]


retrieve_reports()
```

### Main Classes

#### Departments

-   Purpose: Manage department records.
-   Key Methods:
    -   `get()`: Retrieve all departments.
    -   `get_details(xRefCodes=None, isValidateOnly=True)`: Get details for one or more departments.
    -   `create(department, isValidateOnly=True)`: Create a new department.
    -   `update(xRefCode, department, isValidateOnly=True)`: Update an existing department.

#### EmployeeProperties

-   Purpose: Manage employee properties.
-   Key Methods:
    -   `get(xRefCode, contextDate=None, contextDateRangeFrom=None, contextDateRangeTo=None)`: Retrieve properties for one or more employees, with optional date filters.
    -   `create(xRefCode, properties, isValidateOnly=True)`: Create new properties for an employee.
    -   `update(xRefCode, properties, isValidateOnly=True)`: Update properties for an employee.

#### Employees

-   Purpose: Manage employee records in Dayforce.
-   Key Methods:
    -   `get(...)`: Retrieve a list of employees with extensive filtering options. See source docstring for all filters.
    -   `get_details(xRefCodes, contextDate=None, expander=None, contextDateRangeFrom=None, contextDateRangeTo=None, amfEntity=None, amfLevel=None, amfLevelValue=None)`: Get detailed information for one or more employees, with support for expanders and date filters.
    -   `create(employee, isValidateOnly=True)`: Create a new employee.
    -   `update(xRefCode, employee, isValidateOnly=True, replaceExisting=None)`: Update an existing employee.

#### JobAssignments

-   Purpose: Manage job assignments (positions).
-   Key Methods:
    -   `get(contextData=None)`: Retrieve job assignments.
    -   `get_details(xRefCode, contextData=None, expander=None)`: Get details for a job assignment.
    -   `create(job_assignment, isValidateOnly=True)`: Create a new job assignment.
    -   `update(xRefCode, job_assignment, isValidateOnly=True)`: Update an existing job assignment.

#### LocationAddresses

-   Purpose: Manage location addresses.
-   Key Methods:
    -   `get(shortName=None, countryCode=None, stateProvinceCode=None)`: Retrieve a list of location addresses with optional filters.
    -   `create(location_address, isValidateOnly=True)`: Create a new location address.
    -   `update(xRefCode, location_address, isValidateOnly=True)`: Update an existing location address.

#### PayAdjustments

-   Purpose: Manage pay adjustments for employees.
-   Key Methods:
    -   `get(...)`: Retrieve pay adjustments with various filters. Look at source docustring to see filters
    -   `create(pay_adjustment, isValidateOnly=True, isValidateLabor=None)`: Create a new pay adjustment.
    -   `update(xRefCode, pay_adjustment, isValidateOnly=True, isValidateLabor=None)`: Update an existing pay adjustment.

#### OrgUnits

-   Purpose: Manage organization units (departments, locations, etc.).
-   Key Methods:
    -   `get(filter=None)`: Retrieve a list of organization units, optionally filtered.
    -   `get_details(xRefCodes=None, expander=None, contextDate=None, includeChildOrgUnits=None)`: Get details for one or more organization units, with optional expansion and filtering.
    -   `create(org_unit, isValidateOnly=True, calibrateOrg=None)`: Create a new organization unit.
    -   `update(xRefCode, org_unit, isValidateOnly=True, replaceExisting=None, calibrateOrg=None)`: Update an existing organization unit.

##### OrgUnitExpander

-   Purpose: Specify which related data to include in the response for organization unit details.
-   Fields:
    -   `OrgUnitParents`: Include parent organization units.
    -   `OrgUnitLegalEntities`: Include legal entities associated with the organization unit.
    -   `OrgUnitLocationTypes`: Include location types associated with the organization unit.

#### PayrollElections

-   Purpose: Manage payroll elections for employees.
-   Key Methods:
    -   `get(source=None, codeType=None, electionStatus=None, payGroupXRefCode=None, employeeXRefCodes=None, employmentStatusXRefCode=None)`: Retrieve payroll elections with various filters.
    -   `create(payroll_elections, isValidateOnly=True, autoUpdateExisting=None)`: Create new payroll elections.
    -   `update(payroll_elections, isValidateOnly=True, autoUpdateExisting=None)`: Update existing payroll elections.
    -   `delete(data, isValidateOnly=True)`: Delete payroll elections.

#### Projects

-   Purpose: Manage project records.
-   Key Methods:
    -   `get(...)`: Retrieve a list of projects with various filters. Look at source docstring to see filters
    -   `get_details(xRefCodes)`: Get details for one or more projects.
    -   `create(project, isValidateOnly=True)`: Create a new project.
    -   `update(xRefCode, project, isValidateOnly=True)`: Update an existing project.

#### WorkAssignments

-   Purpose: Manage work assignments for employees.
-   Key Methods:
    -   `get(xRefCodes, contextDate=None, contextDateRangeFrom=None, contextDateRangeTo=None)`: Retrieve work assignments for one or more employees, with optional date filters.
    -   `create(xRefCode, work_assignment, isValidateOnly=True)`: Create a new work assignment for an employee.
    -   `update(xRefCode, work_assignment, isValidateOnly=True)`: Update an existing work assignment for an employee.
    -   `replace(xRefCode, work_assignment, replaceFrom=None, replaceTo=None, isValidateOnly=True)`: Replace an existing work assignment for an employee within a date range.

#### BaseResource

-   Purpose: Abstract base class for all resource classes. Handles API session, configuration, and common request logic. This class is not intended for direct use.
-   Key Methods:
    -   `_generate_url(endpoint, resource_name, api_version)`: Generate a full URL for the given endpoint.
    -   `_prepare_request(...)`: Prepare a request with custom Dayforce parameters.
    -   `_send_prepared_request(request)`: Prepare and send a request.
    -   `_send_prepared_request_get_data(request)`: Send a prepared request and return the response data.
    -   `_send_request(...)`: Prepare and send a request in one step.
    -   `_send_request_get_data(...)`: Prepare, send, and return the response data.
    -   `_paginate_request(request)`: Paginate through a request that returns multiple pages of results.
    -   `_send_request_get_details(xRefCodes, build_uri=lambda code: code, ...)`: Get details for a list of xRefCodes, optionally customizing the URI for each.

### AnalyticsDataConnector

-   Purpose: Low-level resource for interacting directly with Dayforce Analytics Data Connector API endpoints.
-   Usage: Use this class for direct API access to reports, datasets, and metadata. Most users should prefer the higher-level ReportFactory and ReportJob classes for easier workflows.
-   Key Methods:
    -   `get_reports()`: List available reports.
    -   `get_report_metadata(report_id)`: Get metadata for a specific report.
    -   `create_dataset(report_id, dataset, isValidateOnly=True)`: Start report generation or validate dataset.
    -   `get_dataset_metadata(dataset_id)`: Get status and metadata for a generated dataset.
    -   `get_dataset(dataset_id, paginate=False)`: Retrieve report data for a completed dataset.
    -   `refresh_dataset(dataset_id, dataset={}, isValidateOnly=True)`: Refresh or validate an existing dataset.

### ReportFactory

-   Purpose: High-level factory for creating and managing report jobs. Simplifies workflows for generating, customizing, and retrieving Dayforce reports.
-   Usage: Instantiate with a DayforceClient, then use `create_job()` to start a report workflow.
-   Key Methods:
    -   `create_job(report_id, paginate=False)`: Create a new ReportJob for the given report ID.

### ReportJob

-   Purpose: Encapsulates the workflow for generating, customizing, and retrieving a Dayforce report. Supports both synchronous and asynchronous execution.
-   Usage: Created via ReportFactory. Allows step-by-step or one-shot report generation, including metadata editing and waiting for completion.
-   Key Methods:
    -   `get_report_metadata()`: Fetch report metadata for editing filters/parameters.
    -   `update_filter(name, value, sequence=None)`: Edit a filter in the report metadata.
    -   `update_parameter(name, value)`: Edit a parameter in the report metadata.
    -   `generate_dataset()`: Start report generation after metadata is set.
    -   `wait_until_complete()`: Block until report generation is finished.
    -   `async_wait_until_complete()`: Async version for non-blocking workflows.
    -   `get_report()`: Retrieve the completed report data.
    -   `as_dataframe()`: Return report data as a pandas DataFrame.
    -   `simple_report_as_df()`: One-shot helper for simple reports.
    -   `metadata_report_as_df()`: One-shot helper for reports with metadata changes.

## Requirements

-   Python >= 3.10
-   requests
-   pandas
