"""This module provides classes and methods used to interface with Google Sheet files to extract the stored data or
write new data. Primarily, these tools are used to synchronize the data acquired and stored during training and
experiment runtimes with the data inside the lab's Google Sheets."""

import re
from typing import Any
from pathlib import Path
from datetime import (
    date as dt_date,
    time as dt_time,
    datetime,
    timezone,
)

import pytz
from sl_shared_assets import DrugData, ImplantData, SubjectData, SurgeryData, InjectionData, ProcedureData
from ataraxis_base_utilities import LogLevel, console
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

# Stores schemas for supported date formats.
_supported_date_formats: set[str] = {"%m-%d-%y", "%m-%d-%Y", "%m/%d/%y", "%m/%d/%Y"}

# Defines all headers (columns) that must exist in a validly formatted Surgery log Google Sheet
_required_surgery_headers: set[str] = {
    # Subject Data headers
    "id",
    "ear punch",
    "sex",
    "genotype",
    "dob",
    "weight (g)",
    "cage #",
    "location housed",
    "status",
    # Procedure Data headers
    "date",
    "start",
    "end",
    "surgeon",
    "protocol",
    "surgery notes",
    "post-op notes",
    "surgery quality",
    # Drug Data headers (required)
    "lrs (ml)",
    "ketoprofen (ml)",
    "buprenorphine (ml)",
    "dexamethasone (ml)",
    # Updating surgery quality:
    "surgery quality",
}

_required_water_restriction_headers: set[str] = {
    "date",
    "weight (g)",
    "given by:",
    "water given (ml)",
    "behavior",
    "time",
}


def _convert_date_time_to_timestamp(date: str, time: str) -> int:
    """Converts the input date and time strings into the UTC timestamp.

    This function is used to convert date and time strings parsed from the Google Sheet into the microseconds since
    UTC epoch onset, which is the primary time format used by all other library components.

    Args:
        date: The date string in the format "%m-%d-%y" or "%m-%d-%Y".
        time: The time string in the format "%H:%M".

    Returns:
        The number of microseconds elapsed since UTC epoch onset as an integer.

    Raises:
        ValueError: If date or time are not non-empty strings. If the date or time format does not match any of the
            supported formats.
    """

    # Ensures date and time are provided
    if not isinstance(date, str) or len(date) < 1:
        message = (
            f"Unable to convert the input date and time into a UTC timestamp when parsing Google Sheet data. Expected "
            f"non-empty string inputs for 'date' argument, but encountered {date} of type {type(date).__name__}."
        )
        console.error(message=message, error=ValueError)

    if not isinstance(time, str) or len(time) < 1:
        message = (
            f"Unable to convert the input date and time into a UTC timestamp when parsing Google Sheet data. Expected "
            f"non-empty string inputs for 'time' argument, but encountered {time} of type {type(time).__name__}."
        )
        console.error(message=message, error=ValueError)

    # Precreates date and time object placeholders.
    date_obj: dt_date = dt_date(1990, 1, 1)
    time_obj: dt_time = dt_time(0, 0)

    # Parses the time object
    try:
        time_obj = datetime.strptime(time, "%H:%M").time()
    except ValueError:
        message = (
            f"Invalid time format encountered when parsing Google Sheet data. Expected the supported time format "
            f"(%H:%M), but encountered {time}."
        )
        console.error(message=message, error=ValueError)

    # Parses the date object
    for date_format in _supported_date_formats:
        try:
            date_obj = datetime.strptime(date, date_format).date()
            break
        except ValueError:
            continue
    else:
        message = (
            f"Invalid date format encountered when parsing Google Sheet data. Expected one of the supported formats "
            f"({sorted(_supported_date_formats)}), but encountered {date}."
        )
        console.error(message=message, error=ValueError)

    # Constructs the full DT object and converts it into the UTC timestamp in microseconds.
    full_datetime = datetime.combine(date=date_obj, time=time_obj)
    full_datetime = full_datetime.replace(tzinfo=timezone.utc)

    # Gets and translates the second timestamp (float) into microseconds (int). Then, returns it to the caller
    return int(full_datetime.timestamp() * 1_000_000)


def _extract_coordinate_value(substring: str) -> float:
    """Extracts the numeric value from the input stereotactic coordinate substring.

    This worker function is used to extract the numeric value for each implant and injection coordinate parsed from the
    Google Sheet data.

    Args:
        substring: The stereotactic coordinate substring that contains the numeric value to be extracted.

    Returns:
        The extracted numeric value, formatted as a float.

    Raises:
        ValueError: If the input substring does not contain a numerical value for the anatomical coordinate.
    """

    # Finds the coordinate number that precedes the anatomical axis designator (AP, ML, DV) and extracts it as a float.
    match = re.search(r"([-+]?\d*\.?\d+)\s*(AP|ML|DV)", substring)

    # If the coordinate value is extracted, returns the extracted value as a float
    if match is not None:
        return float(match.group(1))

    # Otherwise, raises an error
    message = f"Unable to extract the numerical anatomical coordinate value from the input substring {substring}."
    console.error(message=message, error=ValueError)

    # This should not be reachable, it is a fall-back to appease mypy
    raise ValueError(message)  # pragma: no cover


def _parse_stereotactic_coordinates(coordinate_string: str) -> tuple[float, float, float]:
    """Parses the AP, ML, and DV stereotactic coordinates from the input coordinate string, extracted from the Google
    Sheet data.

    This method is used when generating ImplantData and InjectionData classes to process the coordinates for each
    implant and injection.

    Notes:
        This method expects the coordinates to be stored as a string formatted as: "-1.8 AP, 2 ML, .25 DV".

    Args:
        coordinate_string: The input string containing the stereotactic coordinates, formatted as described above.

    Returns:
        The tuple of 3 floats, each storing the numeric value of the coordinates in the following order: AP, ML, DV.
    """
    ap_coordinate = 0.0
    ml_coordinate = 0.0
    dv_coordinate = 0.0
    for substring in coordinate_string.split(","):
        substring = substring.strip()
        if "AP" in substring.upper():
            ap_coordinate = _extract_coordinate_value(substring)
        elif "ML" in substring.upper():
            ml_coordinate = _extract_coordinate_value(substring)
        elif "DV" in substring.upper():
            dv_coordinate = _extract_coordinate_value(substring)

    return ap_coordinate, ml_coordinate, dv_coordinate


def _convert_index_to_column_letter(index: int) -> str:
    """Converts a 0-based column index to an Excel-style (Google Sheet) column letter (A, B, C, ... Z, AA, AB, ...).

    This is used when parsing the available headers from the Google Sheet to generate the initial column-to-header
    mapping dictionary.

     Args:
        index: The 0-based column index to be converted.

    Returns:
        The Excel-style column letter corresponding to the input index.
    """
    result = ""
    while index >= 0:
        remainder = index % 26
        result = chr(65 + remainder) + result  # 65 is ASCII for 'A'
        index = index // 26 - 1
    return result


def _replace_empty_values(row_data: list[str]) -> list[str | None]:
    """Replaces empty cells and cells containing 'n/a', '--' or '---' inside the input row_data list with None.

    This is used when retrieving animal data to filter out empty cells and values.

    Args:
        row_data: The list of cell values from a single Google Sheet row.

    Returns:
        The filtered version of the input list.
    """
    return [None if cell.strip().lower() in {"", "n/a", "--", "---"} else cell for cell in row_data]


class SurgerySheet:
    """Encapsulates the access to the target Google Sheet that contains shared lab surgery logs.

    This class uses Google Sheets API to connect to and extract the data stored in the surgery log Google Sheet file.
    It functions as the central access point used to extract surgery data for each animal and project combination and
    save it as a .yaml file alongside other recorded training or experiment data.

    The class is explicitly designed to work with the data of a single animal, which matches the case of how the class
    is used during data acquisition in the lab. It carries out all necessary checks at instantiation to ensure correct
    operation of all methods. Make sure the class is instantiated early in the session initialization hierarchy to abort
    the runtime if necessary.

    Notes:
        This class is purpose-built to work with the specific surgery log format used in the Sun lab. If the target
        sheet or project tab layout does not conform to expectations, this class will likely not behave as intended.

        Since version 2.0.0 this class is also used to write the Surgery Quality column value as the result of
        running the "window checking" session.

    Args:
        project_name: The name of the project whose data should be parsed by the class instance. It is expected that the
            target sheet stores all Sun Lab projects as individual tabs.
        animal_id: The numeric ID of the animal whose data should be parsed by the class instance. It is expected that
            all animals use numeric IDs (either project-specific or unique across all projects) as 'names'.
        credentials_path: The path to the JSON file containing the service account credentials for accessing the Google
            Sheet.
        sheet_id: The ID of the Google Sheet containing the surgery data.

    Attributes:
        _project_name: Stores the target project name.
        _animal_id: Stores the target animal ID.
        _sheet_id: Stores the ID of the target Google Sheet.
        _service: The Google Sheets API service instance used to fetch data from the target Google Sheet.
        _headers: A dictionary that uses headers (column names) as keys and Google Sheet column names (A, B, etc.) as
            values. This dictionary stores all user-defined headers used by the target Google Sheet tab.
        _animals: Stores all animal IDs (names) whose data is stored in the target Google Sheet tab.

    Raises:
        ValueError: If the sheet is not formatted correctly or does not contain expected data.
    """

    def __init__(
        self,
        project_name: str,
        animal_id: int,
        credentials_path: Path,
        sheet_id: str,
    ):
        # Saves ID data to be reused during later instance method calls.
        self._project_name = project_name
        self._animal_id = animal_id
        self._sheet_id = sheet_id

        # Generates the credentials' object to access the target Google Sheet.
        credentials = Credentials.from_service_account_file(  # type: ignore
            filename=str(credentials_path), scopes=("https://www.googleapis.com/auth/spreadsheets",)
        )

        # Uses the credentials' object to build the access service for the target Google Sheet. This service is then
        # used to fetch the sheet data via HTTP request(s).
        self._service = build(serviceName="sheets", version="v4", credentials=credentials)

        # Retrieves all values stored in the first row of the target sheet tab. Each tab represents a particular
        # project. The first row contains the headers for all data columns stored in the sheet.
        headers = (
            self._service.spreadsheets()
            .values()
            .get(spreadsheetId=sheet_id, range=f"'{self._project_name}'!1:1")  # extracts the entire first row
            .execute()
        )

        # Converts headers to a list of strings and raises an error if the header list is empty
        header_values = headers.get("values", [[]])[0]
        if not header_values:
            message = (
                f"Unable to parse the surgery data for the project {project_name} and animal {animal_id}. The first "
                f"row of the target tab appears to be empty. Instead, the first row should contain the column headers."
            )
            console.error(message, error=ValueError)

        # Creates a dictionary mapping header values to Google Sheet column letters
        self._headers: dict[str, str] = {}
        for i, header in enumerate(header_values):
            # Converts column index to column letter (0 -> A, 1 -> B, etc.)
            column_letter = _convert_index_to_column_letter(i)
            self._headers[str(header).strip().lower()] = column_letter

        # Checks for missing headers (column names)
        missing_headers = []
        for required_header in _required_surgery_headers:
            if required_header.lower() not in self._headers:
                missing_headers.append(required_header)

        # If any required headers are missing, raises an error with a detailed message
        if missing_headers:
            missing_headers_str = ", ".join([f"'{h}'" for h in sorted(missing_headers)])
            message = (
                f"Unable to parse the surgery data for the project {project_name} and animal {animal_id}. "
                f"The following required headers are missing from the surgery log Google Sheet: {missing_headers_str}."
            )
            console.error(message, error=ValueError)

        # Retrieves all animal names (IDs) from the 'ID' column. Each ID is z-filled to a triple-digit string for
        # sorting to behave predictably. This data is stored as a tuple of IDs.
        id_column = self._get_column_id("id")
        animal_ids = (
            self._service.spreadsheets()
            .values()
            .get(
                spreadsheetId=sheet_id,
                range=f"{self._project_name}!{id_column}2:{id_column}",  # row 2 onward, row 1 stores headers
                majorDimension="COLUMNS",  # Gets data in column-major order
            )
            .execute()
        )
        id_list = animal_ids.get("values", [[]])[0]
        self._animals: tuple[str, ...] = tuple([str(animal_id).zfill(5) for animal_id in id_list])
        if len(self._animals) == 0:
            message = (
                f"Unable to parse the surgery data for the project {project_name} and animal {animal_id}. The ID "
                f"column of the sheet contains no data, indicating that the log does not contain any animals."
            )
            console.error(message, error=ValueError)

        # Converts input animal ID to the same format as IDs stored in the id_list generated above for comparison
        formatted_id = str(self._animal_id).zfill(5)

        # Checks if the animal ID exists in the tuple of all known animal IDs. If not, it raises an error.
        if formatted_id not in self._animals:
            message = (
                f"Unable to parse the surgery data for the project {project_name} and animal {animal_id}. The "
                f"specified animal ID is not contained in the 'ID' column of the parsed Google Sheet."
            )
            console.error(message=message, error=ValueError)

    def __del__(self) -> None:
        """Terminates the Google Sheets API service when the class is garbage-collected."""
        self._service.close()

    def extract_animal_data(self) -> SurgeryData:
        """Extracts the surgery data for the target animal and returns it as a SurgeryData object.

        This method is used by all acquisition systems at the beginning of each data acquisition session to extract and
        cache the surgery intervention data of the processed animal.

        Returns:
            A fully configured SurgeryData instance that stores the extracted data.
        """

        # Finds the index of the target animal in the ID value tuple to determine the row number to parse from the
        # sheet. The index is modified by 2 because: +1 for 0-indexing to 1-indexing conversion, +1 to account for the
        # header row
        animal_index = self._animals.index(str(self._animal_id).zfill(5))
        row_number = animal_index + 2

        # Retrieves the entire row of data for the target animal
        row_data = (
            self._service.spreadsheets()
            .values()
            .get(spreadsheetId=self._sheet_id, range=f"'{self._project_name}'!{row_number}:{row_number}")
            .execute()
        )

        # Converts the data from dictionary format into a list of strings.
        row_values = row_data.get("values")[0]  # type: ignore

        # Replaces empty cells and value placeholders ('n/a'', '--' or '---') with None.
        row_values = _replace_empty_values(row_values)

        # Creates a dictionary mapping headers (column names) to the animal-specific extracted values for these
        # headers. This procedure assumes that the headers are contiguous, start from row A, and the animal has data for
        # all or most present headers in the same sequential order as headers are encountered.
        animal_data: dict[str, Any] = {}
        for i, header in enumerate(self._headers):
            # Handles unlikely scenario of animal having more data than headers
            animal_data[header.lower()] = row_values[i] if i < len(row_values) else None

        # Parses the animal data and packages it into the SurgeryData instance:

        # Subject Data. We expect all subject data headers to always be present in all surgery sheets.
        subject_data = SubjectData(
            id=animal_data["id"],
            ear_punch=animal_data["ear punch"],
            sex=animal_data["sex"],
            genotype=animal_data["genotype"],
            date_of_birth_us=_convert_date_time_to_timestamp(date=animal_data["dob"], time="12:00"),
            weight_g=float(animal_data["weight (g)"]),
            cage=int(animal_data["cage #"]),
            location_housed=animal_data["location housed"],
            status=animal_data["status"],
        )

        # Procedure Data. Similar to subject data, we expect all required headers to be present for all procedures.
        procedure_data = ProcedureData(
            surgery_start_us=_convert_date_time_to_timestamp(date=animal_data["date"], time=animal_data["start"]),
            surgery_end_us=_convert_date_time_to_timestamp(date=animal_data["date"], time=animal_data["end"]),
            surgeon=animal_data["surgeon"],
            protocol=animal_data["protocol"],
            surgery_notes=animal_data["surgery notes"],
            post_op_notes=animal_data["post-op notes"],
            surgery_quality=animal_data["surgery quality"],
        )

        # Drug Data. Since early surgery log versions did not use drug / injection / implant codes, code parsing has
        # fall-back default values (0). A code value of 0 should be interpreted as not having a code.
        drug_data = DrugData(
            lactated_ringers_solution_volume_ml=animal_data["lrs (ml)"],
            lactated_ringers_solution_code=animal_data.get("lrs code", 0),
            ketoprofen_volume_ml=animal_data["ketoprofen (ml)"],
            ketoprofen_code=animal_data.get("ketoprofen code", 0),
            buprenorphine_volume_ml=animal_data["buprenorphine (ml)"],
            buprenorphine_code=animal_data.get("buprenorphine code", 0),
            dexamethasone_volume_ml=animal_data["dexamethasone (ml)"],
            dexamethasone_code=animal_data.get("dexamethasone code", 0),
        )

        # Determines the number of implants and injections performed during the processed surgery. This is based on the
        # assumption that all implants and injections are named like 'Implant1', 'Injection2_location', etc.

        # Compiles the regex pattern once for efficiency
        digit_pattern = re.compile(r"\d+")

        # Precreates the lists to store the digits associated with each implant and injection.
        implant_numbers = []
        injection_numbers = []

        # Loops over all available headers and determines which implant(s) and injection(s) were performed.
        for key in animal_data:
            # This extraction only considers the 'main' column that stores the name of each implant and injection.
            # Such columns do not contain the whitespace separators between multiple words.
            if " " not in key.strip() and ("implant" in key or "injection" in key):
                # Finds the first occurrence of one or more digits and parses the digits as a number
                match = digit_pattern.search(key)
                if match:
                    number = int(match.group())
                    if "implant" in key:
                        implant_numbers.append(number)
                    else:  # If the key is not 'implant,' it must be an injection.
                        injection_numbers.append(number)

        # Extracts and packages the data for each implant into an ImplantData class instance. If the processed surgery
        # did not use any implants, no ImplantData instances will be created. This is determined either by the
        # placeholder list being empty or all implant column values being None (empty).
        implants = []
        for number in implant_numbers:
            base_key = f"implant{number}"  # Precomputes the 'base' implant name, based on the number
            implant_name = animal_data.get(base_key)  # Gets the name stored in the 'main' implant column

            # If the implant name is 'None', the processed subject does not have this implant, despite the
            # header being present. If the name is a string, it processes the rest of the data
            if implant_name is not None:
                # Some surgeries (training ones) do not make use of stereotactic coordinates. In such cases, defaults
                # to a set of zeroes to indicate no valid coordinates to parse.
                ap, ml, dv = 0.0, 0.0, 0.0

                # If a valid coordinate string is found, parses ap, ml, and dv coordinates from the string.
                coordinate_string = animal_data.get(f"{base_key} coordinates")
                if coordinate_string is not None:
                    ap, ml, dv = _parse_stereotactic_coordinates(coordinate_string)

                # Packages the data into an ImplantData class and appends it to the storage list.
                implants.append(
                    ImplantData(
                        implant=implant_name,
                        implant_target=animal_data[f"{base_key} location"],
                        implant_code=animal_data.get(f"{base_key} code", 0),
                        implant_ap_coordinate_mm=ap,
                        implant_ml_coordinate_mm=ml,
                        implant_dv_coordinate_mm=dv,
                    )
                )

        # Same as implants, but parses injection data. The only minor difference is that InjectionData has an additional
        # field to store injection volume in nanoliters.
        injections = []
        for num in injection_numbers:
            base_key = f"injection{num}"
            injection_name = animal_data.get(base_key)

            if injection_name is not None:
                ap, ml, dv = 0.0, 0.0, 0.0

                coordinate_string = animal_data.get(f"{base_key} coordinates")
                if coordinate_string is not None:
                    ap, ml, dv = _parse_stereotactic_coordinates(coordinate_string)

                injections.append(
                    InjectionData(
                        injection=injection_name,
                        injection_target=animal_data[f"{base_key} location"],
                        injection_volume_nl=animal_data[f"{base_key} volume (nl)"],
                        injection_code=animal_data.get(f"{base_key} code", 0),
                        injection_ap_coordinate_mm=ap,
                        injection_ml_coordinate_mm=ml,
                        injection_dv_coordinate_mm=dv,
                    )
                )

        # Aggregates all data into a SurgeryData instance and returns it to caller
        surgery_data = SurgeryData(
            subject=subject_data, procedure=procedure_data, drugs=drug_data, implants=implants, injections=injections
        )
        return surgery_data

    def update_surgery_quality(self, quality: int) -> None:
        """Updates the surgery quality value for the specified animal.

        This method is used to write an integer value to the 'Surgery Quality' column for the specified animal.
        The value represents the quality assessment of the surgical intervention performed on the animal, typically
        made after the first pre-training imaging session ("window checking" session).

        Args:
            quality: The integer value representing the surgery quality to be written. The value reflects the quality
                of the animal for scientific data acquisition: 0 means unusable, 1 means usable for testing (but not
                publications), 2 means publication-grade quality.
        """
        # Finds the column for "surgery quality"
        quality_column = self._get_column_id("surgery quality")

        # Finds the index of the target animal in the ID value tuple
        animal_index = self._animals.index(str(self._animal_id).zfill(5))
        row_number = animal_index + 2  # +2 to account for header row and 0-indexing

        # Writes the quality value to the appropriate cell
        cell_range = f"{quality_column}{row_number}"
        body = {"values": [[quality]]}
        self._service.spreadsheets().values().update(
            spreadsheetId=self._sheet_id,
            range=f"'{self._project_name}'!{cell_range}",
            valueInputOption="USER_ENTERED",
            body=body,  # type: ignore
        ).execute()

        # Transforms the column letter and the row index to the format necessary to apply formatting to the newly
        # written value.
        col_index = 0
        for char in quality_column.upper():  # type: ignore
            col_index = col_index * 26 + (ord(char) - ord("A") + 1)
        col_index -= 1  # Convert to 0-based index
        row_index_zero_based = row_number - 1

        # Gets the sheet ID for the project tab
        sheet_metadata = self._service.spreadsheets().get(spreadsheetId=self._sheet_id).execute()
        sheet_id = None
        for sheet in sheet_metadata.get("sheets", []):
            if sheet["properties"]["title"] == self._project_name:
                sheet_id = sheet["properties"]["sheetId"]
                break

        if sheet_id is not None:
            # Applies center alignment formatting to the cell
            requests = [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": row_index_zero_based,
                            "endRowIndex": row_index_zero_based + 1,
                            "startColumnIndex": col_index,
                            "endColumnIndex": col_index + 1,
                        },
                        "cell": {"userEnteredFormat": {"horizontalAlignment": "CENTER", "verticalAlignment": "MIDDLE"}},
                        "fields": "userEnteredFormat.horizontalAlignment,userEnteredFormat.verticalAlignment",
                    }
                }
            ]
            self._service.spreadsheets().batchUpdate(
                spreadsheetId=self._sheet_id,
                body={"requests": requests},  # type: ignore
            ).execute()

    def _get_column_id(self, column_name: str) -> str | None:
        """Returns the Google Sheet column ID (letter) for the given column name.

        This method assumes that the header name comes from the data extracted from the header row of the processed
        sheet. The method is used during animal-specific data parsing to retrieve data from specific columns.

        Args:
            column_name: The name of the column as it appears in the header row.

        Returns:
            The column ID (e.g., "A", "B", "C") corresponding to the column name. If the target column header does not
            exist, the method returns None to indicate the header is not available.
        """

        if column_name.lower() in self._headers:
            return self._headers[column_name]
        else:
            return None


class WaterSheet:
    """Encapsulates the access to the target Google Sheet that contains project water-restriction data.

    This class uses Google Sheets API to connect to and update the data stored in the water restriction log Google Sheet
    file. It functions as the central access point used to update the water restriction data for each animal after
    training and experiment sessions. Primarily, this is used as a convenience feature that allows experimenters to
    synchronize runtime data with the Google Sheet tracker instead of entering it manually.

    The class is explicitly designed to work with the data of a single data acquisition session and animal, which
    matches the case of how the class is used during data acquisition in the lab. It carries out all necessary checks at
    instantiation to ensure correct operation of all methods. Make sure the class is instantiated early in the session
    initialization hierarchy to abort the runtime if necessary.

    Notes:
        This class is purpose-built to work with the specific water restriction log format used in the Sun lab. If the
        target sheet layout does not conform to expectations, this class will likely not perform as intended.

        In contrast to the surgery log, the water restriction log does not store project-specific information. While
        the general assumption is that each project uses a unique water restriction log file, the system also supports
        experimenters that use unique IDs for all mice, across all projects.

    Args:
        animal_id: The ID of the animal whose data will be written by this class instance.
        session_date: The date of the session whose data will be written by this class instance. Date is used as the
            'id' of each session in the format YYYY-MM-DD-HH-MM-SS-US, so setting this to session name (id) is the
            expected behavior.
        credentials_path: The path to the JSON file containing the service account credentials for accessing the Google
            Sheet.
        sheet_id: The ID of the Google Sheet containing the water restriction data for the target project.


    Attributes:
        _sheet_id: Stores the ID of the target Google Sheet.
        _service: The Google Sheets API service instance used to write data to the target Google Sheet.

        _animals: Stores all animal IDs (names) whose data is stored in the target Google Sheet.
        _headers: A dictionary that uses headers (column names) as keys and Google Sheet column names (A, B, etc.) as
            values. This dictionary stores all user-defined headers used by the target Google Sheet tab (animal tab).
        _sheet_id_numeric: The numeric ID of the tab that stores the data for the managed animal. This is used to write
         the data to the target animal's tab.
         _current_time: Stores the time (HH:MM) of the session.
         _session_row_index: Stores the index of the Google Sheet row where to write the managed session's data.

    Raises:
        ValueError: If the sheet is not formatted correctly or does not contain expected data.
    """

    def __init__(
        self,
        animal_id: int,
        session_date: str,
        credentials_path: Path,
        sheet_id: str,
    ):
        # Saves ID data to be reused during later instance method calls.
        self._animal_id = animal_id
        self._sheet_id = sheet_id

        # Generates the credentials' object to access the target Google Sheet. In contrast to surgery data, this object
        # requires write access.
        credentials = Credentials.from_service_account_file(  # type: ignore
            filename=str(credentials_path), scopes=("https://www.googleapis.com/auth/spreadsheets",)
        )

        # Uses the credentials' object to build the access service for the target Google Sheet. This service is then
        # used to write the sheet data via HTTP request(s).
        self._service = build(serviceName="sheets", version="v4", credentials=credentials)

        # Gets all tab names from the sheet metadata
        sheet_metadata = self._service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        tabs = sheet_metadata.get("sheets", [])

        # Filters for tabs with digit-only names and extract them as animal IDs. This relies on all water restriction
        # logs following the general lab design, where tabs are named after animal numeric IDs and each tab is used to
        # store the animals' data.
        animal_ids = []
        self._sheet_id_numeric = None  # Initialize the numeric sheet ID

        for tab in tabs:
            tab_name = tab["properties"]["title"]
            tab_id = tab["properties"]["sheetId"]

            if tab_name.isdigit():  # Checks if the tab name contains only digits
                animal_ids.append(tab_name)

                # If this tab matches the target animal ID, stores its numeric sheet ID to the attribute
                if int(tab_name) == self._animal_id:
                    self._sheet_id_numeric = tab_id

        # Formats the animal IDs with zero-padding for consistent sorting
        self._animals: tuple[str, ...] = tuple([str(animal_id).zfill(5) for animal_id in animal_ids])

        # If no IDs are extracted, raises an error. This usually indicates that the target Google Sheet is not formatted
        # appropriately.
        if len(self._animals) == 0:
            message = (
                f"Unable to interface with the water restriction log file for the animal with id {self._animal_id}. No "
                f"tabs with digit-only names found, indicating that the target Google Sheet file does not contain any "
                f"animal data."
            )
            console.error(message, error=ValueError)

        # Otherwise, if the target animal ID is not in the extracted IDs list, raises an error.
        if str(self._animal_id).zfill(5) not in self._animals:
            message = (
                f"Unable to interface with the water restriction log file for the animal with id {self._animal_id}. "
                f"The target Google Sheet only contains the tabs for animals with IDs: "
                f"{[int(animal) for animal in sorted(self._animals)]}."
            )
            console.error(message, error=ValueError)

        # Retrieves all values stored in the second row of the Google Sheet tab with the name that matches the target
        # animal ID. Note, this is in contrast to the Surgery data log, where the headers are stored in the first sheet
        # row.
        headers = (
            self._service.spreadsheets()
            .values()
            .get(spreadsheetId=sheet_id, range=f"'{self._animal_id}'!2:2")  # extracts the entire second row
            .execute()
        )

        # Converts headers to a list of strings and raises an error if the header list is empty
        header_values = headers.get("values", [[]])[0]
        if not header_values:
            message = (
                f"Unable to interface with the water restriction log file for the animal with id {self._animal_id}. "
                f"The second row of the target tab appears to be empty. Instead, the second row should contain the "
                f"column headers."
            )
            console.error(message, error=ValueError)

        # Creates a dictionary mapping header values to Google Sheet column letters
        self._headers: dict[str, str] = {}
        for i, header in enumerate(header_values):
            # Converts column index to column letter (0 -> A, 1 -> B, etc.)
            column_letter = _convert_index_to_column_letter(i)
            self._headers[str(header).strip().lower()] = column_letter

        # Checks for missing headers (column names)
        missing_headers = []
        for required_header in _required_water_restriction_headers:
            if required_header.lower() not in self._headers:
                missing_headers.append(required_header)

        # If any required headers are missing, raises an error
        if missing_headers:
            missing_headers_str = ", ".join([f"'{h}'" for h in sorted(missing_headers)])
            message = (
                f"Unable to interface with the water restriction log file for the animal with id {self._animal_id}. "
                f"The following required headers are missing from the water restriction log Google Sheet: "
                f"{missing_headers_str}."
            )
            console.error(message, error=ValueError)

        # Parses the session's date and converts it into the format used in the log files
        dt = datetime.strptime(session_date, "%Y-%m-%d-%H-%M-%S-%f")
        dt = dt.replace(tzinfo=pytz.UTC)  # Marks the datetime as UTC

        # Session timestamps are in UTC, but our log uses eastern time for user convenience. Converts the date to
        # ET
        eastern = pytz.timezone("US/Eastern")
        dt_eastern = dt.astimezone(eastern)

        # Formats the date to appear the same way as used in the log file
        formatted_date = dt_eastern.strftime("%-m/%-d/%y")

        # Formats the session's start time in the same way as used in the log file and saves it to class attribute.
        self._current_time = dt_eastern.strftime("%H:%M")

        # Finds the row inside the water restriction log file with session's date. This assumes that the log file is
        # pre-filled with dates. If not, this method will enter a loop to prompt the user to resolve the date issue.
        self._session_row_index = self._find_date_row(formatted_date)

    def __del__(self) -> None:
        """Terminates the Google Sheets API service when the class is garbage-collected."""
        self._service.close()

    def update_water_log(self, mouse_weight: float, water_ml: float, experimenter_id: str, session_type: str) -> None:
        """Updates the water restriction log for the managed animal's training or experiment data.

        This method is used at the end of each BehaviorTraining or MesoscopeExperiment runtime to update the water
        restriction log with the runtime data. Primarily, this is used to keep a record of behavior interventions and to
        streamline experimenter experience by automatically synchronizing the Google Sheet log with the data logged
        during runtime.

        Notes:
            For this method to work as intended, the target water restriction log tab must be pre-filled with dates
            at least up to today's data. The method searches the 'date' column for today's date and uses it to determine
            which row of the table to update with data.

        Args:
            mouse_weight: The weight of the mouse, in grams, at the beginning of the training or experiment session.
            water_ml: The combined volume of water, in milliliters, given to the animal automatically (during runtime)
                and manually (by the experimenter, after runtime).
            experimenter_id: The ID of the experimenter running the training or experiment session.
            session_type: The type of the training or experiment session. This is written to the 'behavior'
                column to describe the type of activity performed by the animal during runtime.
        """
        # Writes each value to the appropriate column, using the same formatting as used in row 3. Since the sheet
        # is checked for validity and the session row index is discovered at class instantiation, this is a fairly
        # simple writing procedure.
        row_index = self._session_row_index
        self._write_value("weight (g)", row_index, mouse_weight)
        self._write_value("given by:", row_index, experimenter_id)
        self._write_value("water given (ml)", row_index, water_ml)
        self._write_value("behavior", row_index, session_type)
        self._write_value("time", row_index, self._current_time)

    def _find_date_row(self, target_date: str) -> int:
        """Finds the row index inside the manged water restriction log file containing the target date.

        This is used when updating the log with new data to determine which row to write the data to.

        Args:
            target_date: The date to find in 'mm/dd/yyyy' format.

        Returns:
            The row index (1-based), containing the target date.

        Raises:
            ValueError: If the target data is not found inside the managed Google Sheet file.
        """
        # Gets the date column letter
        date_column = self._headers["date"]

        while True:
            # Retrieves all dates from the date column (row 3 and below)
            date_data = (
                self._service.spreadsheets()
                .values()
                .get(spreadsheetId=self._sheet_id, range=f"'{self._animal_id}'!{date_column}3:{date_column}")
                .execute()
            )
            date_values = date_data.get("values", [])

            # Finds the row with the target date
            row_index = -1
            for i, date_cell in enumerate(date_values):
                # Checks if the cell has a value matching the target date
                if date_cell and date_cell[0] == target_date:
                    # Adds 3 to account for 0-indexing and the fact we started from row 3
                    row_index = i + 3
                    break
            else:
                message = (
                    f"Unable to find the row for the target date {target_date} inside the water restriction log "
                    f"sheet. This indicates that the log has not been filled with dates up to the requested date. "
                    f"Modify the sheet to contain the required date and try again."
                )
                console.echo(message=message, level=LogLevel.WARNING)
                response = input("Enter anything to retry. Enter 'a' to abort: ").lower()
                if response == "a":
                    message = (
                        f"No row found for date {target_date} in the water restriction log file for the animal "
                        f"{self._animal_id}. The water restriction log must be pre-filled with dates at least up to "
                        f"the requested date."
                    )
                    console.error(message, error=ValueError)  # Aborts with an error
                    raise ValueError(message)  # Fallback to appease mypy, should not be reachable.
                continue  # Cycles the while loop if the user chooses to retry
            break  # Breaks the while loop if the row is found

        return row_index

    def _write_value(self, column_name: str, row_index: int, value: int | float | str) -> None:
        """Writes the input value to the specific cell based on column name and row index.

        This is the primary method used to write new values to the managed water restriction log Google Sheet.

        Args:
            column_name: The name of the column to write to.
            row_index: The row index (1-based) to write to.
            value: The value to write.
        """
        # Gets the column letter for the specified column name
        column_letter = self._headers[column_name.lower()]

        # Defines the cell range based on the column letter and row index
        cell_range = f"{column_letter}{row_index}"

        # Formats value based on its type and column
        formatted_value = value
        if column_name.lower() == "weight (g)":
            formatted_value = round(float(value), ndigits=1)
        elif column_name.lower() == "water given (ml)":
            formatted_value = round(float(value), ndigits=1)

        # Writes the value to the target cell
        body = {"values": [[formatted_value]]}
        self._service.spreadsheets().values().update(
            spreadsheetId=self._sheet_id,
            range=f"'{self._animal_id}'!{cell_range}",
            valueInputOption="USER_ENTERED",
            body=body,  # type: ignore
        ).execute()

        # Transforms the column letter and the row index to the format necessary to apply formatting to the newly
        # written value.
        col_index = 0
        for char in column_letter.upper():
            col_index = col_index * 26 + (ord(char) - ord("A") + 1)
        col_index -= 1  # Converts to 0-based index
        row_index_zero_based = row_index - 1

        # Applies formatting to the newly written value using the cached sheet ID
        requests = [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": self._sheet_id_numeric,
                        "startRowIndex": row_index_zero_based,
                        "endRowIndex": row_index_zero_based + 1,
                        "startColumnIndex": col_index,
                        "endColumnIndex": col_index + 1,
                    },
                    "cell": {"userEnteredFormat": {"horizontalAlignment": "CENTER", "verticalAlignment": "MIDDLE"}},
                    "fields": "userEnteredFormat.horizontalAlignment,userEnteredFormat.verticalAlignment",
                }
            }
        ]
        self._service.spreadsheets().batchUpdate(
            spreadsheetId=self._sheet_id,
            body={"requests": requests},  # type: ignore
        ).execute()
