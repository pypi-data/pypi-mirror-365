"""Phrase extractor implementation.

This module provides concrete implementations for grouping tokens into
coreference phrases based on the original clause mate analysis patterns.
"""

import sys
from pathlib import Path
from typing import Dict, List

from src.data.models import CoreferencePhrase, ExtractionResult, SentenceContext, Token
from src.extractors.base import BasePhraseExtractor

from ..utils import extract_coreference_id, extract_full_coreference_id

# Add the parent directory to the path to import from root
sys.path.append(str(Path(__file__).parent.parent.parent))


class PhraseExtractor(BasePhraseExtractor):
    """Concrete implementation for extracting coreference phrases.

    This extractor groups tokens that belong to the same coreference
    entity based on the entity IDs in the original data.
    """

    def __init__(self):
        """Initialize the phrase extractor."""

    def extract(self, context: SentenceContext) -> ExtractionResult:
        """Extract phrase features from a sentence context.

        Args:
            context: The sentence context to analyze

        Returns:
            ExtractionResult containing phrase information
        """
        phrases = self.extract_phrases(context)

        # Update the context with identified phrases
        context.coreference_phrases = phrases

        return ExtractionResult(
            pronouns=context.critical_pronouns,  # Preserve existing pronouns
            phrases=phrases,
            relationships=[],  # Will be filled by relationship extractor
            coreference_chains=[],  # Already handled by coreference extractor
            features={
                "phrase_count": len(phrases),
                "multi_token_phrases": len([p for p in phrases if len(p.tokens) > 1]),
            },
        )

    def can_extract(self, context: SentenceContext) -> bool:
        """Check if this extractor can process the given context.

        Args:
            context: The sentence context to check

        Returns:
            True if extractor can process this context
        """
        # Can extract if we have tokens with coreference information
        return any(
            (token.coreference_link and token.coreference_link != "_")
            or (token.coreference_type and token.coreference_type != "_")
            or (
                token.inanimate_coreference_link
                and token.inanimate_coreference_link != "_"
            )
            or (
                token.inanimate_coreference_type
                and token.inanimate_coreference_type != "_"
            )
            for token in context.tokens
        )

    def extract_phrases(self, context: SentenceContext) -> List[CoreferencePhrase]:
        """Extract all coreference phrases from a sentence context.

        Groups tokens by their coreference IDs to form phrases.

        Args:
            context: The sentence context to search

        Returns:
            List of coreference phrases
        """
        # Collect all tokens with coreference annotations
        coreference_tokens = []

        for token in context.tokens:
            # Get coreference IDs from various sources
            entity_ids = self._get_coreference_ids(token)

            for entity_id in entity_ids:
                coreference_tokens.append((token, entity_id))

        # Group tokens by entity ID
        entity_groups: Dict[str, List[Token]] = {}
        for token, entity_id in coreference_tokens:
            if entity_id not in entity_groups:
                entity_groups[entity_id] = []
            entity_groups[entity_id].append(token)

        # Convert groups to phrases
        phrases = []
        for entity_id, tokens in entity_groups.items():
            if tokens:  # Only create phrases for non-empty groups
                # Sort tokens by position to maintain order
                sorted_tokens = sorted(tokens, key=lambda t: t.idx)

                phrase = CoreferencePhrase(
                    entity_id=entity_id,
                    tokens=sorted_tokens,
                    phrase_text=self._build_phrase_text(sorted_tokens),
                    start_position=min(t.idx for t in sorted_tokens),
                    end_position=max(t.idx for t in sorted_tokens),
                    sentence_id=context.sentence_id,
                )
                phrases.append(phrase)

        return phrases

    def group_tokens_by_entity(self, tokens: List[Token]) -> Dict[str, List[Token]]:
        """Group tokens by their entity ID.

        Args:
            tokens: List of tokens to group

        Returns:
            Dictionary mapping entity IDs to token lists
        """
        groups = {}
        for token in tokens:
            entity_ids = self._get_coreference_ids(token)
            for entity_id in entity_ids:
                if entity_id not in groups:
                    groups[entity_id] = []
                groups[entity_id].append(token)
        return groups

    def is_phrase_boundary(self, token1: Token, token2: Token) -> bool:
        """Check if there's a phrase boundary between two tokens.

        Args:
            token1: First token
            token2: Second token

        Returns:
            True if there's a boundary between the tokens
        """
        entities1 = self._get_coreference_ids(token1)
        entities2 = self._get_coreference_ids(token2)

        # Boundary exists if no entity IDs overlap
        return not bool(set(entities1) & set(entities2))

    def _get_coreference_ids(self, token: Token) -> List[str]:
        """Get all coreference IDs for a token from various sources.

        Args:
            token: The token to examine

        Returns:
            List of coreference IDs (may be empty)
        """
        ids = []

        # Try to get full ID from animate coreference link
        if token.coreference_link and token.coreference_link != "_":
            full_id = extract_full_coreference_id(token.coreference_link)
            if full_id:
                ids.append(full_id)

        # Try to get full ID from inanimate coreference link
        if token.inanimate_coreference_link and token.inanimate_coreference_link != "_":
            full_id = extract_full_coreference_id(token.inanimate_coreference_link)
            if full_id:
                ids.append(full_id)

        # Fallback: get base IDs from type columns
        if not ids:
            if token.coreference_type and token.coreference_type != "_":
                base_id = extract_coreference_id(token.coreference_type)
                if base_id:
                    ids.append(base_id)

            if (
                token.inanimate_coreference_type
                and token.inanimate_coreference_type != "_"
            ):
                base_id = extract_coreference_id(token.inanimate_coreference_type)
                if base_id:
                    ids.append(base_id)

        return ids

    def _build_phrase_text(self, tokens: List[Token]) -> str:
        """Build the text representation of a phrase from its tokens.

        Args:
            tokens: List of tokens in the phrase

        Returns:
            String representation of the phrase
        """
        if not tokens:
            return ""

        # Sort by position and join
        sorted_tokens = sorted(tokens, key=lambda t: t.idx)
        return " ".join(token.text for token in sorted_tokens)

    def validate_phrase(self, phrase: CoreferencePhrase) -> bool:
        """Validate that a phrase is well-formed.

        Args:
            phrase: The phrase to validate

        Returns:
            True if the phrase is valid
        """
        # Basic validation checks
        if not phrase.tokens:
            return False

        if not phrase.entity_id:
            return False

        # Check that all tokens have the same entity ID
        for token in phrase.tokens:
            token_ids = self._get_coreference_ids(token)
            if phrase.entity_id not in token_ids:
                return False

        return True
