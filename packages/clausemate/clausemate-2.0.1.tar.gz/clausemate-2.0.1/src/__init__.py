"""Clause Mates Analyzer - Modular Architecture (Phase 2).

A Python package for extracting and analyzing clause mate relationships
from German pronoun data for linguistic research.

This package provides:
- TSV file parsing with linguistic annotations
- Coreference relationship extraction
- Clause mate analysis and export
- Comprehensive type safety and error handling
"""

__version__ = "2.0.0"
__author__ = "Linguistic Research Team"

# Import main classes for convenient access
from .main import ClauseMateAnalyzer

__all__ = [
    "ClauseMateAnalyzer",
]
