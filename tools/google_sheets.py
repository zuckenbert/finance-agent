"""Google Sheets tools for the finance agent."""

import json
import os
from functools import lru_cache
from typing import Dict, List, Optional, Union

import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pandasql import sqldf
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Environment variables are loaded in app/main.py
DEFAULT_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
DEFAULT_SHEET_NAME = "Sheet1"

# ────────────────────────────────────────────────────────────────────────────────
# Custom Exceptions
# ────────────────────────────────────────────────────────────────────────────────
class SheetsError(Exception):
    """Base exception for Google Sheets operations."""
    pass


class SheetsQueryError(SheetsError):
    """Raised when a query operation fails."""
    pass


class SheetsAppendError(SheetsError):
    """Raised when an append operation fails."""
    pass


class SheetsAuthError(SheetsError):
    """Raised when authentication fails."""
    pass


# ────────────────────────────────────────────────────────────────────────────────
# Pydantic models
# ────────────────────────────────────────────────────────────────────────────────
class SheetsQueryParams(BaseModel):
    spreadsheet_id: str = Field(default=DEFAULT_SHEET_ID, description="Google Sheets file ID")
    a1_range: str = Field(
        default="Sheet1!A1:Z50",
        description="A1 notation range (e.g. 'Sheet1!A1:Z50')"
    )
    sql_query: Optional[str] = None
    sheet_name: Optional[str] = None


class SheetsQueryReturn(BaseModel):
    data: List[Dict] = Field(..., description="Rows returned")
    columns: List[str] = Field(..., description="Column names")


class SheetsAppendParams(BaseModel):
    spreadsheet_id: str = Field(..., description="Google Sheets file ID")
    a1_range: str = Field(..., description="Target range (e.g. 'Sheet1!A1')")
    values: Dict = Field(..., description="Row values keyed by column")


class SheetsAppendReturn(BaseModel):
    updated_range: str = Field(..., description="Range that was updated")
    updated_rows: int = Field(..., description="Number of rows updated")


# ────────────────────────────────────────────────────────────────────────────────
# Authentication
# ────────────────────────────────────────────────────────────────────────────────
@lru_cache()
def get_sheets_service():
    """Get authenticated Google Sheets service (cached)."""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
            scopes=["https://www.googleapis.com/auth/spreadsheets"],
        )
        return build("sheets", "v4", credentials=credentials)
    except Exception as e:
        raise SheetsAuthError(f"Failed to authenticate: {str(e)}")


# ────────────────────────────────────────────────────────────────────────────────
# Function Tools
# ────────────────────────────────────────────────────────────────────────────────
def google_sheets_query(params: SheetsQueryParams) -> SheetsQueryReturn:
    """Query Google Sheets data using either A1 notation or SQL-like syntax."""
    try:
        service = get_sheets_service()
        spreadsheet = service.spreadsheets()

        # Log the request parameters
        print(f"Querying Google Sheets with ID: {params.spreadsheet_id}")
        print(f"Range: {params.a1_range}")

        # Direct A1 range query
        result = spreadsheet.values().get(
            spreadsheetId=params.spreadsheet_id,
            range=params.a1_range
        ).execute()

        # Log the raw API response
        print(f"API Response: {result}")

        values = result.get("values", [])
        if not values:
            print("No values found in the response")
            return SheetsQueryReturn(data=[], columns=[])

        # Get headers from the first non-empty row
        header_row_idx = 0
        for i, row in enumerate(values):
            if row and any(cell.strip() for cell in row):
                header_row_idx = i
                break

        if header_row_idx >= len(values):
            return SheetsQueryReturn(data=[], columns=[])

        # Get headers and ensure they are unique
        headers = values[header_row_idx]
        unique_headers = []
        header_counts = {}
        
        for header in headers:
            header = str(header).strip()
            if not header:  # Skip empty headers
                continue
            if header in header_counts:
                header_counts[header] += 1
                unique_headers.append(f"{header}_{header_counts[header]}")
            else:
                header_counts[header] = 1
                unique_headers.append(header)

        # Get data rows after header
        data = values[header_row_idx + 1:]

        # Create a DataFrame with explicit column names
        clean_data = []
        for row in data:
            # Skip empty rows
            if not row or all(cell == '' for cell in row):
                continue
            # Pad or trim row to match headers length
            padded_row = row[:len(unique_headers)]
            if len(padded_row) < len(unique_headers):
                padded_row.extend([''] * (len(unique_headers) - len(padded_row)))
            clean_data.append(padded_row)

        df = pd.DataFrame(clean_data, columns=unique_headers)
        
        # Convert numeric strings to float where possible
        for col in df.columns:
            try:
                # Remove commas and spaces from numbers and convert
                df[col] = df[col].str.strip().str.replace(',', '').astype(float, errors='ignore')
            except:
                pass

        return SheetsQueryReturn(
            data=df.to_dict("records"),
            columns=df.columns.tolist()
        )

    except HttpError as e:
        raise SheetsQueryError(f"Google Sheets API error: {str(e)}")
    except Exception as e:
        raise SheetsQueryError(f"Query failed: {str(e)}")


def google_sheets_append_row(params: SheetsAppendParams) -> SheetsAppendReturn:
    """Append a row to a Google Sheet."""
    try:
        service = get_sheets_service()
        spreadsheet = service.spreadsheets()

        # Get the header row to match column order
        range_parts = params.a1_range.split("!")
        sheet_name = range_parts[0]
        header_range = f"{sheet_name}!1:1"
        
        header_result = spreadsheet.values().get(
            spreadsheetId=params.spreadsheet_id,
            range=header_range
        ).execute()
        
        headers = header_result.get("values", [[]])[0]
        if not headers:
            raise SheetsAppendError("Could not retrieve sheet headers")

        # Order values according to headers
        ordered_values = [params.values.get(header, "") for header in headers]

        # Append the row
        body = {
            "values": [ordered_values]
        }
        
        result = spreadsheet.values().append(
            spreadsheetId=params.spreadsheet_id,
            range=params.a1_range,
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body=body
        ).execute()

        return SheetsAppendReturn(
            updated_range=result["updates"]["updatedRange"],
            updated_rows=result["updates"]["updatedRows"]
        )

    except HttpError as e:
        raise SheetsAppendError(f"Google Sheets API error: {str(e)}")
    except Exception as e:
        raise SheetsAppendError(f"Append failed: {str(e)}")


# ────────────────────────────────────────────────────
