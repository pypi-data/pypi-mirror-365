"""
Core functionality for querying Family feasts in Opus Dei.

This module provides functions to search and retrieve feast day information
from a local JSON database.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Union
from datetime import datetime, date
import re


@dataclass
class Feast:
    """Represents a feast day.
    
    Attributes:
        date: The date string (e.g., "January 1")
        title: The feast title
        description: Detailed description of the feast
        color: Liturgical color (White, Red, etc.)
        type: Type of celebration (Solemnity, Memorial, etc.)
        class_: Classification within the Work (A, B, C, D, E). "E" means no feast.
        tags: List of associated tags
    """
    date: str
    title: str
    description: str
    color: str
    type: str
    class_: str
    tags: List[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Feast':
        """Create a Feast instance from dictionary data."""
        return cls(
            date=data.get('date', ''),
            title=data.get('title', ''),
            description=data.get('description', ''),
            color=data.get('color', ''),
            type=data.get('type', ''),
            class_=data.get('class', ''),
            tags=data.get('tags', [])
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Feast instance to dictionary."""
        return {
            'date': self.date,
            'title': self.title,
            'description': self.description,
            'color': self.color,
            'type': self.type,
            'class': self.class_,
            'tags': self.tags
        }


def _load_feast_data() -> Dict[str, List[Dict[str, Any]]]:
    """Load feast day data from JSON file.
    
    Returns:
        Dictionary with date keys and feast data values.
        
    Raises:
        FileNotFoundError: If the JSON file cannot be found.
        json.JSONDecodeError: If the JSON file is malformed.
    """
    data_path = Path(__file__).parent / 'data' / 'feast_days.json'
    
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Feast days data file not found at {data_path}")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in feast days data file: {e}", e.doc, e.pos)


def _parse_date_to_key(date_input: Union[str, date, datetime]) -> str:
    """Parse various date formats to MM-DD format.
    
    Args:
        date_input: Date in various formats:
            - datetime.date or datetime.datetime object
            - "MM-DD" format (e.g., "01-09", "12-25")
            - "Jan 1", "January 1", "January 1st" formats
            - "1 Jan", "1 January" formats
            - "Jan 1 2024", "January 1st 2024", "1 Jan 2024", "1st January 2024" formats
    
    Returns:
        Date string in MM-DD format
        
    Raises:
        ValueError: If date format cannot be parsed
    """
    if isinstance(date_input, (date, datetime)):
        return date_input.strftime("%m-%d")
    
    if not isinstance(date_input, str):
        raise ValueError(f"Date input must be string, date, or datetime object, got {type(date_input)}")
    
    date_str = date_input.strip()
    
    # Handle MM-DD format directly
    if re.match(r'^\d{1,2}-\d{1,2}$', date_str):
        month, day = map(int, date_str.split('-'))
        return f"{month:02d}-{day:02d}"
    
    # Month name mappings
    month_names = {
        'jan': 1, 'january': 1,
        'feb': 2, 'february': 2,
        'mar': 3, 'march': 3,
        'apr': 4, 'april': 4,
        'may': 5,
        'jun': 6, 'june': 6,
        'jul': 7, 'july': 7,
        'aug': 8, 'august': 8,
        'sep': 9, 'september': 9, 'sept': 9,
        'oct': 10, 'october': 10,
        'nov': 11, 'november': 11,
        'dec': 12, 'december': 12
    }
    
    # Normalize the input
    date_str_lower = date_str.lower()

    # Remove commas
    date_str_lower = date_str_lower.replace(',', '')

    # Pattern for "Jan 1", "January 1st", "Jan 1st" etc. (without year)
    pattern1 = r'^([a-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?$'
    match1 = re.match(pattern1, date_str_lower)
    if match1:
        month_str, day_str = match1.groups()
        if month_str in month_names:
            month = month_names[month_str]
            day = int(day_str)
            return f"{month:02d}-{day:02d}"
    
    # Pattern for "1 Jan", "1 January", "1st January" etc. (without year)
    pattern2 = r'^(\d{1,2})(?:st|nd|rd|th)?\s+([a-z]+)$'
    match2 = re.match(pattern2, date_str_lower)
    if match2:
        day_str, month_str = match2.groups()
        if month_str in month_names:
            month = month_names[month_str]
            day = int(day_str)
            return f"{month:02d}-{day:02d}"
    
    # Pattern for "Jan 1 2024", "January 1st 2024", "Jan 1st 2024" etc. (with year)
    pattern3 = r'^([a-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?\s+(\d{4})$'
    match3 = re.match(pattern3, date_str_lower)
    if match3:
        month_str, day_str, year_str = match3.groups()
        if month_str in month_names:
            month = month_names[month_str]
            day = int(day_str)
            return f"{month:02d}-{day:02d}"
    
    # Pattern for "1 Jan 2024", "1 January 2024", "1st January 2024" etc. (with year)
    pattern4 = r'^(\d{1,2})(?:st|nd|rd|th)?\s+([a-z]+)\s+(\d{4})$'
    match4 = re.match(pattern4, date_str_lower)
    if match4:
        day_str, month_str, year_str = match4.groups()
        if month_str in month_names:
            month = month_names[month_str]
            day = int(day_str)
            return f"{month:02d}-{day:02d}"
    
    raise ValueError(f"Unable to parse date format: '{date_input}'. "
                     f"Supported formats: MM-DD, 'Jan 1', 'January 1st', '1 Jan', '1 January', "
                     f"'Jan 1 2024', 'January 1st 2024', '1 Jan 2024', '1st January 2024', or date/datetime objects")


def get_feast_for_date(date_input: Union[str, date, datetime]) -> List[Feast]:
    """Get all feasts for a specific date.
    
    Args:
        date_input: Date in various formats:
            - datetime.date or datetime.datetime object
            - "MM-DD" format (e.g., "01-09", "12-25") 
            - "Jan 1", "January 1", "January 1st" formats
            - "1 Jan", "1 January", "1st January" formats
            - "Jan 1 2024", "January 1st 2024", "1 Jan 2024", "1st January 2024" formats
        
    Returns:
        List of Feast objects for the given date. Empty list if no feasts found.
        
    Raises:
        ValueError: If date format cannot be parsed
        
    Examples:
        >>> from datetime import date
        >>> feasts = get_feast_for_date(date(2024, 1, 9))
        >>> feasts = get_feast_for_date("01-09")
        >>> feasts = get_feast_for_date("Jan 9")
        >>> feasts = get_feast_for_date("January 9th")
        >>> feasts = get_feast_for_date("9 January")
        >>> feasts = get_feast_for_date("Jan 9 2024")
        >>> feasts = get_feast_for_date("9th January 2024")
        >>> print(feasts[0].title)
        Birthday of St. Josemaría (1902)
    """
    date_key = _parse_date_to_key(date_input)
    data = _load_feast_data()
    feast_list = data.get(date_key, [])
    return [Feast.from_dict(feast) for feast in feast_list]


def get_feast_for_today() -> List[Feast]:
    """Get all feasts for today's date.
    
    Returns:
        List of Feast objects for today. Empty list if no feasts found.
        
    Example:
        >>> feasts = get_feast_for_today()
        >>> for feast in feasts:
        ...     print(feast.title)
    """
    today = datetime.now()
    date_key = today.strftime("%m-%d")
    return get_feast_for_date(date_key)


def search_feasts_by_title(keyword: str, case_sensitive: bool = False) -> List[Feast]:
    """Search for feasts by title keyword.
    
    Args:
        keyword: Search term to look for in feast titles
        case_sensitive: Whether to perform case-sensitive search
        
    Returns:
        List of Feast objects matching the search criteria.
        
    Example:
        >>> feasts = search_feasts_by_title("mary")
        >>> print(len(feasts))
        15
    """
    data = _load_feast_data()
    results = []
    
    search_term = keyword if case_sensitive else keyword.lower()
    
    for date_key, feast_list in data.items():
        for feast_data in feast_list:
            title = feast_data.get('title', '')
            title_to_search = title if case_sensitive else title.lower()
            
            if search_term in title_to_search:
                results.append(Feast.from_dict(feast_data))
    
    return results


def search_feasts_by_tag(tag: str, case_sensitive: bool = False) -> List[Feast]:
    """Search for feasts by tag.
    
    Args:
        tag: Tag to search for
        case_sensitive: Whether to perform case-sensitive search
        
    Returns:
        List of Feast objects with the specified tag.
        
    Example:
        >>> feasts = search_feasts_by_tag("opus dei")
        >>> print(len(feasts))
        8
    """
    data = _load_feast_data()
    results = []
    
    search_tag = tag if case_sensitive else tag.lower()
    
    for date_key, feast_list in data.items():
        for feast_data in feast_list:
            tags = feast_data.get('tags', [])
            tags_to_search = tags if case_sensitive else [t.lower() for t in tags]
            
            if search_tag in tags_to_search:
                results.append(Feast.from_dict(feast_data))
    
    return results


def search_feasts_by_type(feast_type: str, case_sensitive: bool = False) -> List[Feast]:
    """Search for feasts by liturgical type.
    
    Args:
        feast_type: Type to search for (e.g., "Solemnity", "Memorial", "Feast")
        case_sensitive: Whether to perform case-sensitive search
        
    Returns:
        List of Feast objects of the specified type.
        
    Example:
        >>> feasts = search_feasts_by_type("Solemnity")
        >>> print(len(feasts))
        7
    """
    data = _load_feast_data()
    results = []
    
    search_type = feast_type if case_sensitive else feast_type.lower()
    
    for date_key, feast_list in data.items():
        for feast_data in feast_list:
            ftype = feast_data.get('type', '')
            ftype_to_search = ftype if case_sensitive else ftype.lower()
            
            if search_type == ftype_to_search:
                results.append(Feast.from_dict(feast_data))
    
    return results


def list_all_feasts() -> List[Feast]:
    """Get all feasts in the calendar.
    
    Returns:
        List of all Feast objects in chronological order.
        
    Example:
        >>> all_feasts = list_all_feasts()
        >>> print(f"Total feasts: {len(all_feasts)}")
    """
    data = _load_feast_data()
    results = []
    
    # Sort by date key to maintain chronological order
    for date_key in sorted(data.keys()):
        feast_list = data[date_key]
        for feast_data in feast_list:
            results.append(Feast.from_dict(feast_data))
    
    return results


def get_dates_with_feasts() -> List[str]:
    """Get all dates that have feast days.
    
    Returns:
        List of date keys (MM-DD format) that have associated feasts.
        
    Example:
        >>> dates = get_dates_with_feasts()
        >>> print(f"Feast days in calendar: {len(dates)}")
    """
    data = _load_feast_data()
    return sorted(data.keys())


def get_feast_count() -> int:
    """Get total number of individual feasts in the calendar.
    
    Returns:
        Total count of feast entries.
        
    Example:
        >>> count = get_feast_count()
        >>> print(f"Total feast entries: {count}")
    """
    data = _load_feast_data()
    total = 0
    for feast_list in data.values():
        total += len(feast_list)
    return total
