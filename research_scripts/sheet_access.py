import gspread
import numpy as np
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import project_config



def url_to_id(url: str) -> str:
    """
    Extract spreadsheet ID from full Google Sheets URL.

    Parameters
    ----------
    url : str
        Full URL to the Google Sheet.

    Returns
    -------
    str
        Extracted spreadsheet ID.
    """
    last_slash_index = url.rfind("/")
    second_last_slash_index = url.rfind("/", 0, last_slash_index)
    return url[second_last_slash_index + 1 : last_slash_index]


def read_sheet(url: str, worksheet_name: str, path_to_json: str = None) -> pd.DataFrame:
    """
    Reads data from a Google Sheet worksheet into a pandas DataFrame.

    Parameters
    ----------
    url : str
        URL of the Google Sheet.
    worksheet_name : str
        Name of the worksheet to read from.
    path_to_json : str, optional
        Path to the Google service account JSON key.

    Returns
    -------
    pd.DataFrame
        DataFrame with sheet content.
    """
    if path_to_json is None:
        path_to_json = project_config.SERVICE_ACCOUNT_FILE

    credentials = ServiceAccountCredentials.from_json_keyfile_name(path_to_json)
    gc = gspread.authorize(credentials)
    sc_id = url_to_id(url)
    wsc = gc.open_by_key(sc_id).worksheet(worksheet_name)

    data = wsc.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])
    df.replace(["", " "], np.nan, inplace=True)
    df.dropna(how="all", inplace=True)
    return df


def write_sheet(url: str, worksheet_name: str, df: pd.DataFrame, path_to_json: str = None, index: bool = True) -> None:
    """
    Writes a pandas DataFrame to a worksheet in a Google Sheet.

    Parameters
    ----------
    url : str
        URL of the Google Sheet.
    worksheet_name : str
        Name of the worksheet to write to.
    df : pd.DataFrame
        DataFrame to upload.
    path_to_json : str, optional
        Path to the Google service account JSON key.
    index : bool, default True
        Whether to include the index as a column in the sheet.

    Returns
    -------
    None
    """
    from gspread.exceptions import WorksheetNotFound

    if path_to_json is None:
        path_to_json = project_config.SERVICE_ACCOUNT_FILE

    credentials = ServiceAccountCredentials.from_json_keyfile_name(path_to_json)
    gc = gspread.authorize(credentials)
    sc_id = url_to_id(url)
    spreadsheet = gc.open_by_key(sc_id)

    try:
        wsc = spreadsheet.worksheet(worksheet_name)
    except WorksheetNotFound:
        wsc = spreadsheet.add_worksheet(title=worksheet_name, rows="100", cols="20")

    df_to_export = df.reset_index() if index else df.copy()
    data = [df_to_export.columns.tolist()] + df_to_export.replace({np.nan: ""}).values.tolist()

    wsc.clear()
    wsc.update("A1", data)
