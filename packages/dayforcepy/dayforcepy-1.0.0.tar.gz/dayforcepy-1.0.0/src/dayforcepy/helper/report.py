import asyncio
import time
import pandas as pd

from typing import Any
from typing_extensions import Self
from datetime import timedelta
from enum import Enum

from .report_metadata import ReportMetadata
from ..resources.analytics_data_connector import AnalyticsDataConnector


class ReportSteps(Enum):
    """Enum for report steps in the report workflow."""

    GET_METADATA = 0
    QUEUE_DATASET = 1
    DATASET_GENERATED = 2
    DATASET_RECIEVED = 3


class ReportJob:
    """Factory class for creating report objects with metadata modification capabilities."""

    def __init__(
        self,
        client,
        report_id: str | int,
        paginate: bool = False,
        retry_delay: timedelta = timedelta(seconds=5),
        max_attempts: int = 20,
    ):
        self.client = client
        self.analytics = AnalyticsDataConnector(client)

        self.report_id = report_id
        self.paginate = paginate
        self.retry_delay = retry_delay
        self.max_attempts = max_attempts
        self.completed_steps = []

    # Methods for report workflow

    def get_report_metadata(self) -> Self:
        """Fetch the metadata for the report."""
        self.metadata = ReportMetadata(
            self.analytics.get_report_metadata(self.report_id)
        )
        self.completed_steps.append(ReportSteps.GET_METADATA)
        return self

    def generate_dataset(self) -> Self:
        """Instructs Dayforce to begin generating the report.

        Raises
        ------
        RuntimeError
            If metadata has not been fetched before creating a dataset.
        """
        if ReportSteps.GET_METADATA not in self.completed_steps:
            raise RuntimeError("Metadata must be fetched before creating a dataset.")

        dataset = self.analytics.create_dataset(
            report_id=self.report_id,
            dataset=self.metadata.output_metadata(),
            isValidateOnly=False,
        )
        self.dataset_id = dataset["DatasetId"]
        return self

    def get_report(self) -> Self:
        """Fetch the report data.

        Raises
        ------
        RuntimeError
            If the dataset has not been generated before fetching report data.
        """
        if ReportSteps.DATASET_GENERATED not in self.completed_steps:
            raise RuntimeError("Dataset must be generated before fetching report data.")

        self.report_data = self.analytics.get_dataset(
            self.dataset_id, paginate=self.paginate
        )
        self.completed_steps.append(ReportSteps.DATASET_RECIEVED)
        return self

    def refresh(self) -> Self:
        """Refresh the report data by re-fetching the dataset.

        Must be called after the dataset has been fetched, and also must re-wait and retrieve the dataset again."""
        if ReportSteps.DATASET_RECIEVED not in self.completed_steps:
            raise RuntimeError("Report data must be fetched before refreshing.")

        self.analytics.refresh_dataset(self.dataset_id)
        return self

    # Methods for returning results

    def as_records(self) -> list[dict]:
        """Return the report data as a list of dictionaries.

        Raises
        ------
        RuntimeError
            If the report data has not been fetched yet.
        """
        if ReportSteps.DATASET_RECIEVED not in self.completed_steps:
            raise RuntimeError(
                "Report data must be fetched before converting to records."
            )
        return self.report_data

    def as_dataframe(self) -> pd.DataFrame:
        """Return the report data as a pandas DataFrame.

        Raises
        ------
        RuntimeError
            If the report data has not been fetched yet.
        """
        if ReportSteps.DATASET_RECIEVED not in self.completed_steps:
            raise RuntimeError(
                "Report data must be fetched before converting to DataFrame."
            )
        return pd.DataFrame.from_records(self.report_data)

    # Methods for modifying metadata

    def update_filter(self, name: str, value: Any, sequence: int | None = None) -> Self:
        """Edit a filter in the metadata.

        Parameters
        ----------
        name : str
            The name of the filter to edit.
        value : str
            The value to set for the filter. Try to use python types as it will convert them to the correct type, and verify the datatype of the filter.
            Example: `True`, `123`, `45.67`, `datetime.now()`, `date.today()`, `time(12, 30)`, `"A string"`, a list of int for reference ids, a list of strings for refrence names, etc.
        sequence : int | None, optional
            The sequence number of the filter, by default it is the input's sequence number.

        Raises
        ------
        ValueError
            If the filter is not editable, does not exist, the refrence does not exist in the report metadata, the value type is incorrect, or the filter has already been set.
        """
        if ReportSteps.GET_METADATA not in self.completed_steps:
            raise RuntimeError("Metadata must be fetched before updating filters.")
        self.metadata.update_filter(name, value, sequence)
        return self

    def update_parameter(self, name: str, value: Any) -> Self:
        """Edit a parameter in the metadata.

        Parameters
        ----------
        name : str
            The name of the parameter to edit. MUST start with `@` to indicate it is a parameter.
        value : Any
            The value to set for the parameter. Try to use python types as it will convert them to the correct type, and verify the datatype of the parameter.
            Example: `True`, `123`, `45.67`, `datetime.now()`, `date.today()`, `time(12, 30)`, `"A string"`, etc.

        Raises
        ------
        ValueError
            If the name does not start with `@`
            If the parameter is not editable, does not exist, the refrence does not exist in the report metadata, the value type is incorrect, or the parameter has already been set.
        """
        if ReportSteps.GET_METADATA not in self.completed_steps:
            raise RuntimeError("Metadata must be fetched before updating parameters.")
        self.metadata.update_parameter(name, value)
        return self

    def wait_until_complete(self) -> Self:
        """Block until the dataset is completed."""
        if ReportSteps.QUEUE_DATASET not in self.completed_steps:
            raise RuntimeError("Dataset must be queued before waiting for completion.")

        attempts = 0

        while attempts < self.max_attempts:
            dataset_metadata = self.analytics.get_dataset_metadata(self.dataset_id)

            if dataset_metadata["Status"] == "Completed":
                break

            attempts += 1
            time.sleep(self.retry_delay.total_seconds())

        self.completed_steps.append(ReportSteps.DATASET_GENERATED)
        return self

    async def async_wait_until_complete(self) -> Self:
        """Async method to wait until the dataset is completed."""
        if ReportSteps.QUEUE_DATASET not in self.completed_steps:
            raise RuntimeError("Dataset must be queued before waiting for completion.")

        attempts = 0

        while attempts < self.max_attempts:
            dataset_metadata = await asyncio.to_thread(
                self.analytics.get_dataset_metadata, self.dataset_id
            )

            if dataset_metadata["Status"] == "Completed":
                break

            attempts += 1
            await asyncio.sleep(self.retry_delay.total_seconds())

        self.completed_steps.append(ReportSteps.DATASET_GENERATED)
        return self

    # Helper methods to condense workflow steps

    def simple_report_as_df(self) -> pd.DataFrame:
        """Helper function to generate simple reports, not requiring metadata changes.

        Runs through all the workflow proccess in one function, blocking each step"""
        self.get_report_metadata()
        self.generate_dataset()
        self.wait_until_complete()
        self.get_report()
        return self.as_dataframe()

    def metadata_report_as_df(self) -> pd.DataFrame:
        """Helper function to generate reports with metadata changes.

        Runs through all the workflow proccess after the metdata has been changed, blocking each step"""
        self.generate_dataset()
        self.wait_until_complete()
        self.get_report()
        return self.as_dataframe()


class ReportFactory:
    """Factory class for creating report jobs."""

    def __init__(
        self,
        client,
        retry_delay: timedelta = timedelta(seconds=5),
        max_attempts: int = 20,
    ):
        self.client = client
        self.retry_delay = retry_delay
        self.max_attempts = max_attempts

    def create_job(self, report_id: str | int, paginate: bool = False) -> ReportJob:
        """Create a synchronous report job.

        Parameters
        ----------
        report_id : str | int
            The ID of the report to create a job for.
        paginate : bool, optional
            Whether to paginate the report data, by default False

        Returns
        -------
        ReportJob
            An instance of ReportJob for the specified report ID."""
        return ReportJob(
            self.client,
            report_id,
            paginate=paginate,
            retry_delay=self.retry_delay,
            max_attempts=self.max_attempts,
        )
