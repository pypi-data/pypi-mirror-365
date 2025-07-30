"""
feastdays - A Python package for querying Catholic feast days celebrated in Opus Dei.

This package provides easy access to Catholic feast day information
including dates, descriptions, liturgical details, and search capabilities.
"""

from .core import (
    Feast,
    get_feast_for_date,
    get_feast_for_today,
    search_feasts_by_title,
    search_feasts_by_tag,
    search_feasts_by_type,
    list_all_feasts,
    get_dates_with_feasts,
    get_feast_count
)

__version__ = "1.1.0"
__author__ = "Daniel Okonma"
__email__ = "danielokonma@yahoo.com"

__all__ = [
    "Feast",
    "get_feast_for_date",
    "get_feast_for_today", 
    "search_feasts_by_title",
    "search_feasts_by_tag",
    "search_feasts_by_type",
    "list_all_feasts",
    "get_dates_with_feasts",
    "get_feast_count"
]
