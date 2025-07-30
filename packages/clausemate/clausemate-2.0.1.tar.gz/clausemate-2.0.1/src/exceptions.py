#!/usr/bin/env python3
"""Custom exceptions for the clause mate extraction script."""

from typing import Optional


class ClauseMateExtractionError(Exception):
    """Base exception for clause mate extraction errors."""


class ParseError(ClauseMateExtractionError):
    """Raised when parsing fails."""

    def __init__(
        self,
        message: str,
        line_number: Optional[int] = None,
        raw_data: Optional[str] = None,
    ):
        self.line_number = line_number
        self.raw_data = raw_data

        if line_number is not None:
            message = f"Line {line_number}: {message}"
        if raw_data is not None:
            message = f"{message} (Raw data: {raw_data[:100]}...)"

        super().__init__(message)


class ValidationError(ClauseMateExtractionError):
    """Raised when validation fails."""


class FileProcessingError(ClauseMateExtractionError):
    """Raised when file processing fails."""


class CoreferenceExtractionError(ClauseMateExtractionError):
    """Raised when coreference extraction fails."""
