"""Utility functions for the finance agent."""

def format_currency(value: float) -> str:
    """
    Format a number as currency with thousands separator and 2 decimal places.
    
    Args:
        value (float): The number to format
        
    Returns:
        str: Formatted currency string (e.g. "1,234.56")
    """
    return f"{value:,.2f}" 