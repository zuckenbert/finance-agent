"""Test the Google Sheets connection."""
import os
from tools.google_sheets import google_sheets_query, SheetsQueryParams
from dotenv import load_dotenv

def test_connection():
    """Test that we can connect to and read from the Google Sheet."""
    load_dotenv()
    
    # Get sheet ID from environment
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    if not sheet_id:
        raise ValueError("GOOGLE_SHEET_ID not set in environment")
    
    try:
        # Try to read the first few rows
        params = SheetsQueryParams(
            spreadsheet_id=sheet_id,
            a1_range="Sheet1!A1:Z10"  # Just read first 10 rows
        )
        
        result = google_sheets_query(params)
        
        # Print the results for debugging
        print("\nColumns found:", result.columns)
        print("\nFirst row of data:", result.data[0] if result.data else "No data")
        
        return True
        
    except Exception as e:
        print(f"Error connecting to spreadsheet: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection() 