from datetime import datetime, date, time
from enum import Enum
from typing import Any


class DataType(Enum):
    """Enum for the data types used in Dayforce reports."""

    STRING = "String"
    BOOLEAN = "Boolean"
    INTEGER = "Integer"
    DECIMAL = "Decimal"
    CURRENCY = "Currency"
    DATE = "Date"
    TIME = "Time"
    DATETIME = "DateTime"
    REFERENCE = "Reference"
    BIG_INTEGER = "BigInteger"  # FIXME: A guess, not sure if this is correct


class ReportMetadata:
    """Represents report metadata in Dayforce.

    Allows the manipulation and validation of metadata from Dayforce reports."""

    def __init__(self, metadata: dict):
        self.input_metadata = metadata
        self.report_id = metadata["ReportId"]
        self.max_rows = metadata["MaxRows"]
        self.only_include_unique_records = metadata["OnlyIncludeUniqueRecords"]
        self.filters = []

    # User helper functions to know what editable

    # API functions

    def _get_output_value(self, value: Any, input_filter: dict) -> str:
        """Converts and verifies the value to be used in the output metadata."""

        def verify_type(expected_types: list[str] | str) -> None:
            if isinstance(expected_types, str):
                expected_types = [expected_types]
            if input_filter["DataType"] not in expected_types:
                raise ValueError(
                    f"Filter ({input_filter['Name']}) is of type ({input_filter['DataType']}), cannot set value of type ({type(value).__name__})."
                )

        if isinstance(value, bool):
            verify_type(DataType.BOOLEAN.value)
            return "True" if value else "False"
        elif isinstance(value, int):
            verify_type([DataType.INTEGER.value, DataType.BIG_INTEGER.value])
            return str(value)
        elif isinstance(value, float):
            verify_type([DataType.DECIMAL.value, DataType.CURRENCY.value])
            return str(value)
        elif isinstance(value, datetime):
            verify_type(DataType.DATETIME.value)
            return value.isoformat()
        elif isinstance(value, date):
            verify_type(DataType.DATE.value)
            return value.isoformat()
        elif isinstance(value, time):
            verify_type(DataType.TIME.value)
            return value.isoformat()
        elif isinstance(value, list) and all(isinstance(item, str) for item in value):
            verify_type(DataType.REFERENCE.value)
            ids = []

            # Verify that the values exist in the AvailableValues of the filter
            for item in value:
                for available_value in input_filter["AvailableValues"]:
                    if item == available_value["Name"]:
                        ids.append(available_value["ListValueId"])
                        break
                else:
                    raise ValueError(
                        f"Reference value name ({item}) does not exist in the report metadata for filter ({input_filter['Name']})."
                    )

            return ",".join(ids)
        elif isinstance(value, list) and all(isinstance(item, int) for item in value):
            verify_type(DataType.REFERENCE.value)

            # Verify that the values exist in the AvailableValues of the filter
            for item in value:
                for available_value in input_filter["AvailableValues"]:
                    if item == available_value["ListValueId"]:
                        break
                else:
                    raise ValueError(
                        f"Reference value id ({item}) does not exist in the report metadata for filter ({input_filter['Name']})."
                    )

            return ",".join(value)
        elif isinstance(value, str):
            # Allow any string value, as it can be used for strings, as a column name, etc.
            return value
        else:
            raise ValueError(
                f"Unsupported value type ({type(value)}) for filter ({input_filter['Name']})"
            )

    def update_filter(self, name: str, value: Any, sequence: int | None = None) -> None:
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
        if name in [f["Name"] for f in self.filters]:
            raise ValueError(f"Filter ({name}) is already set.")

        for input_filter in self.input_metadata["Filters"]:
            if input_filter["Name"] == name:
                if not input_filter["IsEditable"]:
                    raise ValueError(f"Filter ({name}) is not editable.")

                self.filters.append(
                    {
                        "Name": name,
                        "Value": self._get_output_value(value, input_filter),
                        "Sequence": sequence
                        if sequence is not None
                        else input_filter["Sequence"],
                    }
                )
                break
        else:
            raise ValueError(f"Filter ({name}) does not exist in the report metadata.")

    def update_parameter(self, name: str, value: Any) -> None:
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
        if not name.startswith("@"):
            raise ValueError(f"Parameter ({name}) must start with '@'.")

        if name in [f["Name"] for f in self.filters]:
            raise ValueError(f"Parameter ({name}) is already set.")

        for input_parameter in self.input_metadata["Filters"]:
            if input_parameter["Name"] == name:
                if not input_parameter["IsEditable"]:
                    raise ValueError(f"Parameter ({name}) is not editable.")

                self.filters.append(
                    {
                        "Name": name,
                        "Value": self._get_output_value(value, input_parameter),
                    }
                )
                break
        else:
            raise ValueError(
                f"Parameter ({name}) does not exist in the report metadata."
            )

    def output_metadata(self) -> dict:
        """Returns the metadata for report submission to Dayforce.

        Returns
        -------
        dict
            The POST metadata for the report

        Raises
        ------
        ValueError
            If the user has not correctly set the required filters and parameters that have a isRequired flag set to True, and the value is not set.
            If the user tries to set a filter that is not editable or does not exist in the report metadata.
        """
        for input_filter in self.input_metadata["Filters"]:
            user_filter = None

            for check_filter in self.filters:
                if check_filter["Name"] == input_filter["Name"]:
                    user_filter = check_filter
                    break

            # If the filter is required and not set by default, raise an error if it is not set by the user
            if input_filter["IsRequired"] and input_filter["Value"] == "":
                if user_filter is None or user_filter["Value"] == "":
                    raise ValueError(
                        f"Filter ({input_filter['Name']}) is required but not set."
                    )

            # Check if the filter is editable
            if not input_filter["IsEditable"] and user_filter is not None:
                raise ValueError(
                    f"Filter ({input_filter['Name']}) is not editable and cannot be modified."
                )

        for check_filter in self.filters:
            input_filter = None

            for filter_check in self.input_metadata["Filters"]:
                if check_filter["Name"] == filter_check["Name"]:
                    input_filter = filter_check
                    break
            else:  # If the filter is not in the input metadata, raise an error
                raise ValueError(
                    f"Filter ({check_filter['Name']}) does not exist in the report metadata."
                )

        return {
            "ReportId": self.report_id,
            "MaxRows": self.max_rows,
            "OnlyIncludeUniqueRecords": self.only_include_unique_records,
            "Filters": self.filters,
        }
