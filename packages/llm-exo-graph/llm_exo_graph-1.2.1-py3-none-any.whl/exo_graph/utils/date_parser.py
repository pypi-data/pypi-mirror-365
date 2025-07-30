"""
Date parsing utilities for Knowledge Graph Engine v2
Uses dateparser library for robust natural language date parsing
"""
from datetime import datetime
from typing import Optional
import dateparser
from neo4j.time import DateTime

def parse_date(date_str: Optional[str | datetime | DateTime]) -> Optional[datetime]:
    """
    Parse various date formats using dateparser library
    
    Args:
        date_str: Date string to parse (can be None)
        
    Returns:
        Parsed datetime object or None if parsing failed
    """
    if not date_str:
        return None


    try:

        if isinstance(date_str, datetime):
            return date_str

        elif date_str and hasattr(date_str, 'to_native'):
            # Handle Neo4j native date objects
            return date_str.to_native()

        # Configure dateparser settings
        parser_settings = {
            'PREFER_DAY_OF_MONTH': 'first',  # When day is ambiguous, prefer first of month
            'PREFER_DATES_FROM': 'past',     # When year is ambiguous, prefer past dates
            'RETURN_AS_TIMEZONE_AWARE': False,  # Return naive datetime objects
            'DATE_ORDER': 'MDY',             # Default to US date order
            'STRICT_PARSING': False,         # Allow fuzzy parsing
        }
        
        # Use dateparser library for robust parsing
        parsed_date = dateparser.parse(
            date_str.strip(), 
            settings=parser_settings
        )
        return parsed_date
    except Exception as e:
        print(f"Warning: Could not parse date '{date_str}': {e}")
        return None