from datetime import datetime
from ..client import DayforceClient
from .base_resource import BaseResource


class BackgroundJobs(BaseResource):
    """Resource for managing background jobs in Dayforce."""

    def __init__(self, client: DayforceClient):
        super().__init__(client, "BackgroundJobs")

    def get_parameters(self, jobShortName: str | None = None) -> list[dict]:
        """Retrieve the parameters for background jobs.

        Parameters
        ----------
        jobShortName : str, optional
            The short name of the background job to filter parameters by.

        Returns
        -------
        list[dict]
            A list of dictionaries containing the parameters for the background jobs.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Background-Jobs/GET-Background-Job-Parameters.aspx
        """
        return self._send_request_get_data(
            method="GET",
            params={"jobShortName": jobShortName} if jobShortName else None,
        )

    def get_logs(
        self,
        codeName: list[str] | None = None,
        status: str | None = None,
        hasItemLevelErrors: bool | None = None,
        queueTimeUtcStart: datetime | None = None,
        queueTimeUtcEnd: datetime | None = None,
        wasScheduled: bool | None = None,
        submittedBy: str | None = None,
        filterUpdateTimeUtcStart: datetime | None = None,
        filterUpdateTimeUtcEnd: datetime | None = None,
        includeSuppressedTaskTypes: bool | None = None,
        backgroundJobLogId: int | None = None,
        fileName: str | None = None,
    ):
        """Retrieve logs, statuses, and more identifying information for background jobs.

        Parameters
        ----------
        codeName : list[str] | None, optional
            The code names of the background jobs to filter by.
        status : str | None, optional
            The status of the background jobs to filter by. Must be one of:
            'Queued', 'In Progress', 'Paused', 'Completed', 'Cancelled', 'Error'.
        hasItemLevelErrors : bool | None, optional
            Whether to filter by item-level errors.
        queueTimeUtcStart : datetime | None, optional
            The start time of the queue in UTC to filter by.
        queueTimeUtcEnd : datetime | None, optional
            The end time of the queue in UTC to filter by.
        wasScheduled : bool | None, optional
            Whether to filter by jobs that were scheduled or on-demand.
        submittedBy : str | None, optional
            The user who submitted the background job to filter by.
        filterUpdateTimeUtcStart : datetime | None, optional
            The start time of the filter update in UTC to filter by.
        filterUpdateTimeUtcEnd : datetime | None, optional
            The end time of the filter update in UTC to filter by.
        includeSuppressedTaskTypes : bool | None, optional
            Whether to include suppressed task types in the results.
        backgroundJobLogId : int | None, optional
            The ID of the background job log to filter by.
        fileName : str | None, optional
            The name of the file to filter by.

        Returns
        -------
        list[dict]
            A list of dictionaries containing the logs and statuses of the background jobs.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Background-Jobs/GET-Background-Job-Logs.aspx
        """
        if status not in (
            "Queued",
            "In Progress",
            "Paused",
            "Completed",
            "Cancelled",
            "Error",
        ):
            raise ValueError(
                "Invalid status. Must be one of: 'Queued', 'In Progress', 'Paused', 'Completed', 'Cancelled', 'Error'."
            )

        return self._paginate_request(
            self._prepare_request(
                method="GET",
                endpoint="Logs",
                params={
                    "codeName": ",".join(codeName) if codeName else None,
                    "status": status,
                    "hasItemLevelErrors": hasItemLevelErrors,
                    "queueTimeUtcStart": queueTimeUtcStart.isoformat()
                    if queueTimeUtcStart
                    else None,
                    "queueTimeUtcEnd": queueTimeUtcEnd.isoformat()
                    if queueTimeUtcEnd
                    else None,
                    "wasScheduled": wasScheduled,
                    "submittedBy": submittedBy,
                    "filterUpdateTimeUtcStart": filterUpdateTimeUtcStart.isoformat()
                    if filterUpdateTimeUtcStart
                    else None,
                    "filterUpdateTimeUtcEnd": filterUpdateTimeUtcEnd.isoformat()
                    if filterUpdateTimeUtcEnd
                    else None,
                    "includeSuppressedTaskTypes": includeSuppressedTaskTypes,
                    "backgroundJobLogId": backgroundJobLogId,
                    "fileName": fileName,
                },
            )
        )

    def get_log_details(
        self,
        backgroundJobLogId: list[str] | str,
        includeDetailedJobLogs: bool | None = None,
    ) -> dict:
        """Retrieve detailed information about specific background job logs.

        Parameters
        ----------
        backgroundJobLogId : list[str] | str
            The ID(s) of the background job log(s) to retrieve details for.
        includeDetailedJobLogs : bool, optional
            Whether to include detailed job logs in the response.

        Returns
        -------
        dict
            A dictionary mapping background job log IDs to their details.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Background-Jobs/GET-Background-Job-Logs-Detail.aspx
        """
        return self._send_request_get_details(
            method="GET",
            xRefCodes=backgroundJobLogId
            if isinstance(backgroundJobLogId, list)
            else [backgroundJobLogId],
            build_uri=lambda code: f"logs/{code}",
            params={"includeDetailedJobLogs": includeDetailedJobLogs},
        )

    def queue_job(
        self,
        job_data: dict,
        isValidateOnly: bool = True,
    ) -> dict:
        """Queue a background job with the provided data.

        Parameters
        ----------
        job_data : dict
            The data for the background job to be queued.
        isValidateOnly : bool, optional
            If True, the job will be validated but not actually queued. Defaults to True.

        Returns
        -------
        dict
            A dictionary containing the result of the job queueing operation.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Background-Jobs/POST-Background-Job-Queue.aspx
        """
        return self._send_request_get_data(
            method="POST",
            endpoint="Queue",
            json=job_data,
            params={"isValidateOnly": isValidateOnly},
        )
