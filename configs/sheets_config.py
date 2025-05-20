"""Google Sheets configuration and helper functions."""

from typing import Dict, Tuple

SHEETS: Dict[str, Dict[str, str]] = {
    "balance_sheet": {
        "id": "PLACEHOLDER_ID",
        "sheet": "Main"
    },
    "income_statement": {
        "id": "PLACEHOLDER_ID",
        "sheet": "Main"
    }
}

def get_sheet(alias: str) -> Tuple[str, str]:
    """
    Get the spreadsheet ID and sheet name for a given alias.
    
    Args:
        alias: The alias of the sheet (e.g., 'balance_sheet', 'income_statement')
        
    Returns:
        Tuple containing (spreadsheet_id, sheet_name)
        
    Raises:
        KeyError: If the alias is not found in the configuration
    """
    if alias not in SHEETS:
        raise KeyError(f"Sheet alias '{alias}' not found in configuration")
    
    sheet_config = SHEETS[alias]
    return sheet_config["id"], sheet_config["sheet"] 