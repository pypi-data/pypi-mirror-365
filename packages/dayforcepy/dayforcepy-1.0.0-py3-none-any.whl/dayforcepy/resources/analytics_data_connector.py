from .base_resource import BaseResource

# TODO: Test pagination
# TODO: Add PGP support


class AnalyticsDataConnector(BaseResource):
    """Resource to connect to Dayforce reports.

    For most use cases, prefer the higher-level ReportFactory and ReportJob classes for easier workflows and metadata editing.
    """

    def __init__(self, client):
        super().__init__(client, "Analytics")

    def get_reports(self) -> list[dict]:
        """Get a list of Dayforce reports.

        Returns
        -------
        list[dict]
            A list of dictionaries containing the ReportId, Name, and Description of each report.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Data-and-Analytics/Analytics-Data-Connector/GET-Report.aspx
        """
        return self._send_request_get_data(endpoint="Reports")

    def get_report_metadata(self, report_id: str | int) -> dict:
        """Get metadata for a specific Dayforce report.

        Parameters
        ----------
        report_id : str
            The ID of the report to retrieve metadata for.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Data-and-Analytics/Analytics-Data-Connector/GET-Dataset-Metadata.aspx
        """
        return self._send_request_get_data(endpoint=f"Reports/{report_id}/Metadata")

    def create_dataset(
        self, report_id: str | int, dataset: dict, isValidateOnly: bool = True
    ) -> dict:
        """Creates a dataset in Dayforce.

        Parameters
        ----------
        report_id
            The ID of the report to create a dataset for.
        dataset : dict
            The dataset to create. Must include the ReportId, Filters, Columns, and other required fields.
        isValidateOnly : bool, optional
            If True, only validates the dataset without creating it. Defaults to True.

        Returns
        -------
        dict
            The metadata of the created dataset

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Data-and-Analytics/Analytics-Data-Connector/POST-Report.aspx"""
        return self._send_request_get_data(
            method="POST",
            endpoint=f"Reports/{report_id}",
            json=dataset,
            params={"isValidateOnly": isValidateOnly},
        )

    def get_dataset_metadata(self, dataset_id: str | int) -> dict:
        """Get metadata for a specific dataset.

        Parameters
        ----------
        dataset_id : str
            The ID of the dataset to retrieve metadata for.

        Returns
        -------
        dict
            The metadata of the dataset.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Data-and-Analytics/Analytics-Data-Connector/GET-Dataset-Metadata-(1).aspx
        """
        return self._send_request_get_data(endpoint=f"Datasets/{dataset_id}/Metadata")

    def get_dataset(self, dataset_id: str | int, paginate: bool = False) -> list[dict]:
        """Gets the data for a specific dataset by its ID.

        Parameters
        ----------
        dataset_id : str
            The ID of the dataset to retrieve data for.
        total_pages : int
            The total number of pages to retrieve from the dataset.
            In order to use pagination, it must be enabled on the report in Dayforce.

        Returns
        -------
        list[dict]
            The data from the report.
        """
        request = self._prepare_request(method="GET", endpoint=f"Datasets/{dataset_id}")
        response_data = self._send_prepared_request(request).json()

        if paginate:
            # TODO: Test this actually works, as the API differs from the documentation.
            data = response_data["Data"]
            current_page = response_data["Page"]
            current_page += 1

            while current_page <= response_data["TotalPages"]:
                request.params = {"page": current_page}
                response_data = self._send_prepared_request(request).json()
                data.extend(response_data["Data"])
                current_page += 1

            return data
        else:
            return response_data

    def refresh_dataset(
        self, dataset_id: str | int, dataset: dict = {}, isValidateOnly: bool = True
    ) -> dict:
        """Refreshes a dataset in Dayforce.

        Parameters
        ----------
        dataset_id : str
            The ID of the dataset to refresh.
        dataset : dict
            The dataset to refresh. If empty, it re-uses the last dataset filters. Must include the Filters, and other required fields.
        isValidateOnly : bool, optional
            If True, only validates the dataset without refreshing it. Defaults to True.

        Returns
        -------
        dict
            The metadata of the refreshed dataset.

        See Also
        --------
        https://developers.dayforce.com/Build/API-Explorer/Data-and-Analytics/Analytics-Data-Connector/POST-Refresh-Dataset.aspx
        """
        return self._send_request_get_data(
            method="POST",
            endpoint=f"Datasets/{dataset_id}",
            json=dataset,
            params={"isValidateOnly": isValidateOnly},
        )
