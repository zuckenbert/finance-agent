"""Tests for Google Sheets functionality."""

import pytest
from tools.google_sheets import SheetsQueryParams, SheetsQueryReturn

def test_sql_query_returns_columns(fake_sheets_query):
    """Test that SQL query returns expected columns."""
    params = SheetsQueryParams(
        sql_query="SELECT * FROM transactions",
        spreadsheet_id="test-sheet-id",
        sheet_name="Transactions"
    )
    result = fake_sheets_query(params)
    
    assert result.columns == ["date", "amount", "category"]
    assert len(result.data) == 3
    assert all(key in result.data[0] for key in result.columns)

def test_a1_range_returns_data(fake_sheets_query):
    """Test that A1 range query returns expected data."""
    params = SheetsQueryParams(
        sql_query="SELECT SUM(amount) FROM transactions",
        spreadsheet_id="test-sheet-id",
        sheet_name="Transactions"
    )
    result = fake_sheets_query(params)
    
    assert result.columns == ["SUM(amount)"]
    assert len(result.data) == 1
    assert result.data[0]["SUM(amount)"] == 425.75 