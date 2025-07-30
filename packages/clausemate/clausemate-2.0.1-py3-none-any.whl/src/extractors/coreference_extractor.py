"""Coreference extractor implementation.

This module provides concrete implementations for extracting coreference information
from parsed linguistic data, following the patterns established in the original script.
"""

import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import List, Set

from src.data.models import (
    AnimacyType,
    CoreferenceChain,
    ExtractionResult,
    SentenceContext,
    Token,
)
from src.extractors.base import BaseCoreferenceExtractor

from ..config import PronounSets

# Add the parent directory to the path to import from root
sys.path.append(str(Path(__file__).parent.parent.parent))


class CoreferenceExtractor(BaseCoreferenceExtractor):
    """Concrete implementation for extracting coreference information.

    This extractor handles the identification and linking of coreferential expressions,
    centralizing the logic that was previously duplicated throughout the main script.
    """

    def __init__(self):
        """Initialize the coreference extractor."""
        self.coreference_pattern = re.compile(r"(\d+)")
        self.critical_pronouns = (
            PronounSets.THIRD_PERSON_PRONOUNS
            | PronounSets.D_PRONOUNS
            | PronounSets.DEMONSTRATIVE_PRONOUNS
        )

    def extract(self, context: SentenceContext) -> ExtractionResult:
        """Extract coreference features from a sentence context.

        Args:
            context: The sentence context to analyze

        Returns:
            ExtractionResult containing coreference information
        """
        # Find all mentions in the sentence
        mentions = self.find_mentions(context)

        # Extract coreference chains (simplified for single sentence)
        chains = self._build_local_chains(mentions)

        return ExtractionResult(
            pronouns=[],  # Will be filled by pronoun extractor
            phrases=[],  # Will be filled by phrase extractor
            relationships=[],  # Will be filled by relationship extractor
            coreference_chains=chains,
            features={"coreference_ids": self._extract_all_ids_from_context(context)},
        )

    def can_extract(self, context: SentenceContext) -> bool:
        """Check if this extractor can process the given context.

        Args:
            context: The sentence context to check

        Returns:
            True if extractor can process this context
        """
        # Can extract if any token has coreference information
        return any(
            token.coreference_link
            or token.coreference_type
            or token.inanimate_coreference_link
            or token.inanimate_coreference_type
            for token in context.tokens
        )

    def extract_coreference_chains(
        self, contexts: List[SentenceContext]
    ) -> List[CoreferenceChain]:
        """Extract coreference chains from multiple sentences.

        Args:
            contexts: List of sentence contexts to analyze

        Returns:
            List of identified coreference chains
        """
        all_mentions = []
        for context in contexts:
            mentions = self.find_mentions(context)
            all_mentions.extend(mentions)

        # Group mentions by coreference ID
        chains_dict = defaultdict(list)
        for mention in all_mentions:
            coref_ids = self.extract_all_ids_from_token(mention)
            for coref_id in coref_ids:
                chains_dict[coref_id].append(mention)

        # Convert to CoreferenceChain objects
        chains = []
        for chain_id, mentions in chains_dict.items():
            if mentions:  # Only create chains with mentions
                # Determine animacy (simplified logic)
                animacy = self._determine_chain_animacy(mentions)
                chains.append(
                    CoreferenceChain(
                        chain_id=chain_id, mentions=mentions, animacy=animacy
                    )
                )

        return chains

    def find_mentions(self, context: SentenceContext) -> List[Token]:
        """Find all mentions in a sentence that could participate in coreference.

        Args:
            context: The sentence context to search

        Returns:
            List of tokens that are potential mentions
        """
        mentions = []

        for token in context.tokens:
            # Check if token has any coreference information
            if self._has_coreference_info(token):
                mentions.append(token)

        return mentions

    def link_mentions(
        self, mentions: List[Token], existing_chains: List[CoreferenceChain]
    ) -> List[CoreferenceChain]:
        """Link new mentions to existing coreference chains.

        Args:
            mentions: New mentions to link
            existing_chains: Existing coreference chains

        Returns:
            Updated list of coreference chains
        """
        # Create a mapping of chain IDs to chains
        chains_dict = {chain.chain_id: chain for chain in existing_chains}

        # Process each mention
        for mention in mentions:
            coref_ids = self.extract_all_ids_from_token(mention)

            for coref_id in coref_ids:
                if coref_id in chains_dict:
                    # Add to existing chain
                    chains_dict[coref_id].add_mention(mention)
                else:
                    # Create new chain
                    animacy = self._determine_token_animacy(mention)
                    new_chain = CoreferenceChain(
                        chain_id=coref_id, mentions=[mention], animacy=animacy
                    )
                    chains_dict[coref_id] = new_chain

        return list(chains_dict.values())

    def extract_all_ids_from_token(self, token: Token) -> Set[str]:
        """Extract all coreference IDs from a token.

        This is the centralized implementation that replaces the duplicated
        coreference ID extraction logic from the original script.

        Args:
            token: Token to extract IDs from

        Returns:
            Set of coreference IDs found in the token
        """
        ids = set()

        # Extract from animate coreference link
        if token.coreference_link:
            extracted_ids = self._extract_ids_from_string(token.coreference_link)
            ids.update(extracted_ids)

        # Extract from animate coreference type
        if token.coreference_type:
            extracted_ids = self._extract_ids_from_string(token.coreference_type)
            ids.update(extracted_ids)

        # Extract from inanimate coreference link
        if token.inanimate_coreference_link:
            extracted_ids = self._extract_ids_from_string(
                token.inanimate_coreference_link
            )
            ids.update(extracted_ids)

        # Extract from inanimate coreference type
        if token.inanimate_coreference_type:
            extracted_ids = self._extract_ids_from_string(
                token.inanimate_coreference_type
            )
            ids.update(extracted_ids)

        return ids

    def _extract_ids_from_string(self, text: str) -> Set[str]:
        """Extract coreference IDs from a string using regex patterns.

        Args:
            text: String to extract IDs from

        Returns:
            Set of extracted IDs
        """
        if not text or text == "_":
            return set()

        # Find all numeric patterns (original script used various patterns)
        matches = self.coreference_pattern.findall(text)
        return set(matches)

    def _has_coreference_info(self, token: Token) -> bool:
        """Check if a token has any coreference information."""
        return any(
            [
                token.coreference_link and token.coreference_link != "_",
                token.coreference_type and token.coreference_type != "_",
                token.inanimate_coreference_link
                and token.inanimate_coreference_link != "_",
                token.inanimate_coreference_type
                and token.inanimate_coreference_type != "_",
            ]
        )

    def _build_local_chains(self, mentions: List[Token]) -> List[CoreferenceChain]:
        """Build coreference chains from mentions in a single sentence."""
        chains_dict = defaultdict(list)

        for mention in mentions:
            coref_ids = self.extract_all_ids_from_token(mention)
            for coref_id in coref_ids:
                chains_dict[coref_id].append(mention)

        chains = []
        for chain_id, chain_mentions in chains_dict.items():
            if chain_mentions:
                animacy = self._determine_chain_animacy(chain_mentions)
                chains.append(
                    CoreferenceChain(
                        chain_id=chain_id, mentions=chain_mentions, animacy=animacy
                    )
                )

        return chains

    def _determine_chain_animacy(self, mentions: List[Token]) -> AnimacyType:
        """Determine the animacy of a coreference chain based on its mentions.

        Args:
            mentions: List of mentions in the chain

        Returns:
            AnimacyType for the chain
        """
        # Simple heuristic: if any mention is a critical pronoun, consider
        # animate
        for mention in mentions:
            if mention.text.lower() in self.critical_pronouns:
                return AnimacyType.ANIMATE

        # Check for inanimate coreference markers
        for mention in mentions:
            if mention.inanimate_coreference_link or mention.inanimate_coreference_type:
                return AnimacyType.INANIMATE

        # Default to animate if uncertain
        return AnimacyType.ANIMATE

    def _determine_token_animacy(self, token: Token) -> AnimacyType:
        """Determine animacy for a single token."""
        return self._determine_chain_animacy([token])

    def _extract_all_ids_from_context(self, context: SentenceContext) -> Set[str]:
        """Extract all coreference IDs present in a sentence context."""
        all_ids = set()

        for token in context.tokens:
            token_ids = self.extract_all_ids_from_token(token)
            all_ids.update(token_ids)

        return all_ids
