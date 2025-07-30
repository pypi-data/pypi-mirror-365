"""
SpreadsheetLLM: A Python Package for Encoding Spreadsheets for Large Language Models

This package implements the key components from the SpreadsheetLLM research:
- SheetCompressor: Efficient encoding framework with three modules
- Chain of Spreadsheet: Multi-step reasoning approach
- Vanilla encoding methods with cell addresses and formats

Based on the research paper: "SpreadsheetLLM: Encoding Spreadsheets for Large Language Models"
by Microsoft Research Team
"""

from .chain import ChainOfSpreadsheet
from .compressor import SheetCompressor
from .core import SpreadsheetLLM
from .data_types import CellInfo, TableRegion
from .encoders import VanillaEncoder
from .utils import create_realistic_spreadsheet

try:
    from importlib.metadata import version
    __version__ = version("sheetwise")
except ImportError:
    # Fallback for Python < 3.8
    from importlib_metadata import version
    __version__ = version("sheetwise")
except Exception:
    # Fallback if package not installed
    __version__ = "1.1.0"

__author__ = "Based on Microsoft Research SpreadsheetLLM"

__all__ = [
    "SpreadsheetLLM",
    "SheetCompressor",
    "VanillaEncoder",
    "ChainOfSpreadsheet",
    "CellInfo",
    "TableRegion",
    "create_realistic_spreadsheet",
]
