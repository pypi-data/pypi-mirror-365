"""
DataFrame Loader
================

A versatile Python library to read various file formats into a pandas DataFrame, 
with robust handling of nested data structures.
"""

__version__ = "1.0.4"

from .main import DataFrameReader, DataFrameHealthChecker, HTMLReportGenerator

__all__ = ["DataFrameReader", "DataFrameHealthChecker", "HTMLReportGenerator"]