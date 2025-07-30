#!/usr/bin/env python3
"""Utility functions for the clause mate extraction script."""

import re
from pathlib import Path
from typing import List, Optional, Tuple, Union

try:
    from .config import Constants, RegexPatterns
    from .exceptions import ParseError, ValidationError
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path

    sys.path.append(str(Path(__file__).parent))
    from config import Constants, RegexPatterns
    from exceptions import ParseError, ValidationError


def validate_file_path(file_path: Union[str, Path]) -> Path:
    """Validate that the file path exists and is readable.

    Args:
        file_path: Path to the file

    Returns:
        Validated Path object

    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If file is not readable
        ValidationError: If file is invalid
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if not path.is_file():
        raise ValidationError(f"Path is not a file: {path}")

    if not path.stat().st_size > 0:
        raise ValidationError(f"File is empty: {path}")

    # Test readability
    try:
        with open(path, encoding="utf-8") as f:
            f.read(1)
    except PermissionError as e:
        raise PermissionError(f"Cannot read file: {path}") from e

    return path


def safe_get_column(
    row: List[str], column_index: int, default: str = Constants.MISSING_VALUE
) -> str:
    """Safely extract a column value from a row.

    Args:
        row: List of column values
        column_index: Index of the column to extract
        default: Default value if column doesn't exist

    Returns:
        Column value or default
    """
    try:
        if len(row) > column_index:
            value = str(row[column_index]).strip()
            return value if value else default
        return default
    except (IndexError, AttributeError):
        return default


def parse_token_info(token_info: str) -> Tuple[int, int]:
    """Parse token info string into sentence and token numbers.

    Args:
        token_info: String like "4-1" (sentence-token)

    Returns:
        Tuple of (sentence_num, token_num)

    Raises:
        ParseError: If parsing fails
    """
    if not token_info or "-" not in token_info:
        raise ParseError(f"Invalid token info format: {token_info}")

    try:
        parts = token_info.split("-")
        if len(parts) != 2:
            raise ParseError(f"Expected 2 parts, got {len(parts)}: {token_info}")

        sentence_num = int(parts[0])
        token_num = int(parts[1])
        return sentence_num, token_num

    except ValueError as e:
        raise ParseError(f"Non-numeric values in token info: {token_info}") from e


def extract_coreference_type(coreference_value: str) -> Optional[str]:
    """Extract the type from a coreference annotation.

    Args:
        coreference_value: Value like "PersPron[127-4]"

    Returns:
        Type string like "PersPron" or None if not found
    """
    if not coreference_value or coreference_value == Constants.MISSING_VALUE:
        return None

    match = re.search(RegexPatterns.COREFERENCE_TYPE_PATTERN, coreference_value)
    return match.group(1) if match else None


def extract_coreference_id(coreference_value: str) -> Optional[str]:
    """Extract the full coreference chain ID from a coreference annotation.

    Args:
        coreference_value: Value like "PersPron[127-4]"

    Returns:
        Coreference ID like "127-4" or None if not found
    """
    if not coreference_value or coreference_value == Constants.MISSING_VALUE:
        return None

    # Try full ID pattern first
    match = re.search(RegexPatterns.COREFERENCE_ID_PATTERN, coreference_value)
    if match:
        return match.group(1)

    # Fallback to base number only
    match = re.search(RegexPatterns.COREFERENCE_ID_FALLBACK_PATTERN, coreference_value)
    if match:
        return match.group(1)

    return None


def extract_full_coreference_id(coreference_link: str) -> Optional[str]:
    """Extract the full coreference ID from a coreference link annotation.

    Args:
        coreference_link: Value like "*->115-4"

    Returns:
        Coreference ID like "115-4" or None if not found
    """
    if not coreference_link or coreference_link == Constants.MISSING_VALUE:
        return None

    # Try full ID pattern first
    match = re.search(RegexPatterns.COREFERENCE_LINK_PATTERN, coreference_link)
    if match:
        return match.group(1)

    # Fallback to base number only
    match = re.search(RegexPatterns.COREFERENCE_LINK_FALLBACK_PATTERN, coreference_link)
    if match:
        return match.group(1)

    return None


def determine_givenness(coreference_id: str) -> str:
    """Determine if a referential expression is 'neu' (new) or 'bekannt' (given/known).

    Args:
        coreference_id: String like "115-4" or "225-1"

    Returns:
        'neu' if it's the first mention, 'bekannt' otherwise, or '_' if undetermined
    """
    if not coreference_id or coreference_id == Constants.MISSING_VALUE:
        return Constants.MISSING_VALUE

    if "-" in str(coreference_id):
        try:
            occurrence_num = str(coreference_id).split("-")[-1]
            return (
                Constants.NEW_MENTION
                if occurrence_num == "1"
                else Constants.GIVEN_MENTION
            )
        except (ValueError, IndexError):
            return Constants.MISSING_VALUE

    return Constants.MISSING_VALUE


def extract_sentence_number(sentence_id: str) -> Optional[int]:
    """Extract numeric sentence number from sentence_id string.

    Args:
        sentence_id: String like 'sent_34'

    Returns:
        Sentence number or None if parsing fails
    """
    if not sentence_id or sentence_id == Constants.MISSING_VALUE:
        return None

    try:
        return int(sentence_id.replace(Constants.SENTENCE_PREFIX, ""))
    except (ValueError, AttributeError):
        return None


def extract_coref_base_and_occurrence(
    coref_id: str,
) -> Tuple[Optional[int], Optional[int]]:
    """Extract base chain number and occurrence number from coreference ID.

    Args:
        coref_id: String like "115-4" or just "115"

    Returns:
        Tuple of (base_number, occurrence_number) or (None, None) if parsing fails
    """
    if not coref_id or coref_id == Constants.MISSING_VALUE:
        return None, None

    try:
        coref_str = str(coref_id)
        if "-" in coref_str:
            parts = coref_str.split("-")
            base_num = int(parts[0])
            occurrence_num = int(parts[1])
            return base_num, occurrence_num
        else:
            return int(coref_str), None
    except (ValueError, IndexError, AttributeError):
        return None, None


def extract_coref_link_numbers(coref_link: str) -> Tuple[Optional[int], Optional[int]]:
    """Extract base chain number and occurrence number from coreference link.

    Args:
        coref_link: String like "*->115-4" or "*->115"

    Returns:
        Tuple of (base_number, occurrence_number) or (None, None) if parsing fails
    """
    if not coref_link or coref_link == Constants.MISSING_VALUE:
        return None, None

    try:
        if "->" in coref_link:
            target = coref_link.split("->")[-1]
            return extract_coref_base_and_occurrence(target)
        else:
            return None, None
    except (ValueError, AttributeError):
        return None, None
