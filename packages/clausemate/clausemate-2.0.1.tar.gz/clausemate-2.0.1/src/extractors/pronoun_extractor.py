"""Pronoun extractor implementation.

This module provides concrete implementations for identifying and classifying
critical pronouns from parsed linguistic data, following the patterns established
in the original script.
"""

import sys
from pathlib import Path
from typing import Dict, List

from src.data.models import ExtractionResult, SentenceContext, Token
from src.extractors.base import BasePronounExtractor

from ..config import PronounSets
from ..pronoun_classifier import is_critical_pronoun

# Add the parent directory to the path to import from root
sys.path.append(str(Path(__file__).parent.parent.parent))


class PronounExtractor(BasePronounExtractor):
    """Concrete implementation for extracting and classifying pronouns.

    This extractor handles the identification of critical pronouns based on
    the criteria established in the original script.
    """

    def __init__(self):
        """Initialize the pronoun extractor."""
        self.critical_pronouns = (
            PronounSets.THIRD_PERSON_PRONOUNS
            | PronounSets.D_PRONOUNS
            | PronounSets.DEMONSTRATIVE_PRONOUNS
        )

    def extract(self, context: SentenceContext) -> ExtractionResult:
        """Extract pronoun features from a sentence context.

        Args:
            context: The sentence context to analyze

        Returns:
            ExtractionResult containing pronoun information
        """
        pronouns = self.extract_pronouns(context)

        # Update the context with identified critical pronouns
        context.critical_pronouns = pronouns

        return ExtractionResult(
            pronouns=pronouns,
            phrases=[],  # Will be filled by phrase extractor
            relationships=[],  # Will be filled by relationship extractor
            coreference_chains=[],  # Already handled by coreference extractor
            features={"critical_pronoun_count": len(pronouns)},
        )

    def can_extract(self, context: SentenceContext) -> bool:
        """Check if this extractor can process the given context.

        Args:
            context: The sentence context to check

        Returns:
            True if extractor can process this context
        """
        # Can extract if any token could potentially be a pronoun
        return len(context.tokens) > 0

    def extract_pronouns(self, context: SentenceContext) -> List[Token]:
        """Extract all critical pronouns from a sentence context.

        Args:
            context: The sentence context to search

        Returns:
            List of pronoun tokens
        """
        critical_pronouns = []

        for token in context.tokens:
            if self.is_pronoun(token) and self._is_critical_pronoun(token):
                # Mark the token as a critical pronoun
                token.is_critical_pronoun = True
                critical_pronouns.append(token)

        return critical_pronouns

    def classify_pronoun(
        self, pronoun: Token, context: SentenceContext
    ) -> Dict[str, str]:
        """Classify a pronoun's linguistic properties.

        Args:
            pronoun: The pronoun token to classify
            context: The sentence context

        Returns:
            Dictionary of pronoun properties
        """
        classification = {
            "text": pronoun.text,
            "type": "unknown",
            "animacy": "unknown",
            "person": "unknown",
            "gender": "unknown",
            "number": "unknown",
        }

        # Determine pronoun type based on sets
        if pronoun.text.lower() in PronounSets.THIRD_PERSON_PRONOUNS:
            classification["type"] = "personal"
            classification["person"] = "3rd"

            # Basic gender/number classification for German
            if pronoun.text.lower() in ["er", "ihm", "ihn"]:
                classification["gender"] = "masculine"
                classification["number"] = "singular"
            elif pronoun.text.lower() in ["sie", "ihr"]:
                # Could be feminine singular or plural - need context
                classification["gender"] = "feminine_or_plural"
                classification["number"] = "singular_or_plural"
            elif pronoun.text.lower() == "es":
                classification["gender"] = "neuter"
                classification["number"] = "singular"
            elif pronoun.text.lower() == "ihnen":
                classification["gender"] = "plural"
                classification["number"] = "plural"

        elif pronoun.text.lower() in PronounSets.D_PRONOUNS:
            classification["type"] = "d_pronoun"
            classification["person"] = "3rd"

        elif pronoun.text.lower() in PronounSets.DEMONSTRATIVE_PRONOUNS:
            classification["type"] = "demonstrative"
            classification["person"] = "3rd"

        # Determine animacy from coreference information
        if pronoun.coreference_link or pronoun.coreference_type:
            classification["animacy"] = "animate"
        elif pronoun.inanimate_coreference_link or pronoun.inanimate_coreference_type:
            classification["animacy"] = "inanimate"

        return classification

    def is_pronoun(self, token: Token) -> bool:
        """Check if a token is a pronoun.

        Args:
            token: Token to check

        Returns:
            True if token is a pronoun
        """
        # Check if token text is in any of our pronoun sets
        token_text_lower = token.text.lower()

        return (
            token_text_lower in self.critical_pronouns
            or self._has_pronoun_coreference_annotation(token)
        )

    def _is_critical_pronoun(self, token: Token) -> bool:
        """Check if a token is a critical pronoun using the original logic.

        Args:
            token: Token to check

        Returns:
            True if token is a critical pronoun
        """
        # Use the original pronoun classification logic
        token_data = {
            "token_text": token.text,
            "coreference_type": token.coreference_type or "",
            "inanimate_coreference_type": token.inanimate_coreference_type or "",
        }

        return is_critical_pronoun(token_data)

    def _has_pronoun_coreference_annotation(self, token: Token) -> bool:
        """Check if a token has pronoun-like coreference annotations.

        Args:
            token: Token to check

        Returns:
            True if token has pronoun coreference annotations
        """
        # Check for pronoun-specific coreference types
        pronoun_types = ["PersPron", "D-Pron", "DemPron"]

        if token.coreference_type:
            for pron_type in pronoun_types:
                if pron_type in token.coreference_type:
                    return True

        if token.inanimate_coreference_type:
            for pron_type in pronoun_types:
                if pron_type in token.inanimate_coreference_type:
                    return True

        return False
