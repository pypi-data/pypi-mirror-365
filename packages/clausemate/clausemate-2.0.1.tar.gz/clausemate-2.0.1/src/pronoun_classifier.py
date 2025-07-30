#!/usr/bin/env python3
"""Pronoun identification module for the clause mate extraction script."""

from typing import Any, Dict, Optional

from .config import Constants, PronounSets
from .utils import extract_coreference_type


def is_critical_pronoun(token_data: Dict[str, Any]) -> bool:
    """Determine if a token is a critical pronoun.

    Args:
        token_data: Dictionary containing token information including:
                   - token_text: The actual token text
                   - coreference_type: Animate coreference type annotation
                   - inanimate_coreference_type: Inanimate coreference type annotation

    Returns:
        True if the token is a critical pronoun
    """
    token_text = token_data.get("token_text", "")
    coreference_type = token_data.get("coreference_type", Constants.MISSING_VALUE)
    inanimate_coreference_type = token_data.get(
        "inanimate_coreference_type", Constants.MISSING_VALUE
    )

    # Normalize token text to lowercase for comparison
    token_lower = token_text.lower() if token_text else ""

    # Extract types from coreference annotations
    animate_type = extract_coreference_type(coreference_type)
    inanimate_type = extract_coreference_type(inanimate_coreference_type)

    # Check for critical pronoun types with explicit token text filtering
    return (
        _is_third_person_pronoun(animate_type, token_lower)
        or _is_d_pronoun(animate_type, inanimate_type, token_lower)
        or _is_demonstrative_pronoun(animate_type, token_lower)
    )


def _is_third_person_pronoun(animate_type: Optional[str], token_lower: str) -> bool:
    """Check if token is a third person personal pronoun."""
    return (
        animate_type == Constants.PERSONAL_PRONOUN_TYPE
        and token_lower in PronounSets.THIRD_PERSON_PRONOUNS
    )


def _is_d_pronoun(
    animate_type: Optional[str], inanimate_type: Optional[str], token_lower: str
) -> bool:
    """Check if token is a D-pronoun."""
    return (
        animate_type == Constants.D_PRONOUN_TYPE
        or inanimate_type == Constants.D_PRONOUN_TYPE
    ) and token_lower in PronounSets.D_PRONOUNS


def _is_demonstrative_pronoun(animate_type: Optional[str], token_lower: str) -> bool:
    """Check if token is a demonstrative pronoun."""
    return (
        animate_type == Constants.DEMONSTRATIVE_PRONOUN_TYPE
        and token_lower in PronounSets.DEMONSTRATIVE_PRONOUNS
    )
