"""Relationship extractor implementation.

This module provides concrete implementations for extracting clause mate
relationships between critical pronouns and their clause mates within sentences.
"""

import sys
from pathlib import Path
from typing import Any, List, Optional, Set

from src.data.models import (
    AntecedentInfo,
    ClauseMateRelationship,
    CoreferencePhrase,
    ExtractionResult,
    Phrase,
    SentenceContext,
    Token,
)
from src.extractors.base import BaseRelationshipExtractor

from ..utils import (
    determine_givenness,
    extract_coreference_id,
    extract_full_coreference_id,
)

# Add the parent directory to the path to import from root
sys.path.append(str(Path(__file__).parent.parent.parent))


class RelationshipExtractor(BaseRelationshipExtractor):
    """Concrete implementation for extracting clause mate relationships.

    This extractor identifies relationships between critical pronouns and
    their clause mates within the same sentence.
    """

    def extract(
        self,
        context: SentenceContext,
        all_contexts: Optional[List[SentenceContext]] = None,
    ) -> ExtractionResult:
        """Extract relationship features from a sentence context.

        Args:
            context: The sentence context to analyze
            all_contexts: Optional list of all sentence contexts for cross-sentence
                antecedent analysis

        Returns:
            ExtractionResult containing relationship information
        """
        relationships = self.extract_relationships(context, all_contexts)

        return ExtractionResult(
            pronouns=context.critical_pronouns,
            phrases=context.coreference_phrases,
            relationships=relationships,
            coreference_chains=[],  # Already handled by coreference extractor
            features={
                "relationship_count": len(relationships),
                "pronouns_with_clause_mates": len(
                    {rel.pronoun.idx for rel in relationships}
                ),
            },
        )

    def can_extract(self, context: SentenceContext) -> bool:
        """Check if this extractor can process the given context.

        Args:
            context: The sentence context to check

        Returns:
            True if extractor can process this context
        """
        # Can extract if we have critical pronouns and coreference phrases
        return (
            len(context.critical_pronouns) > 0 and len(context.coreference_phrases) > 0
        )

    def extract_relationships(
        self,
        context: SentenceContext,
        all_contexts: Optional[List[SentenceContext]] = None,
    ) -> List[ClauseMateRelationship]:
        """Extract all clause mate relationships from a sentence context.

        Args:
            context: The sentence context to analyze

        Returns:
            List of clause mate relationships
        """
        relationships = []

        # For each critical pronoun, find its clause mates
        for pronoun in context.critical_pronouns:
            pronoun_coref_ids = self._get_pronoun_coreference_ids(pronoun)

            if not pronoun_coref_ids:
                continue  # Skip pronouns without coreference information

            # Find clause mates (phrases with different coreference IDs)
            clause_mates = []
            for phrase in context.coreference_phrases:
                if phrase.entity_id not in pronoun_coref_ids:
                    clause_mates.append(phrase)

            num_clause_mates = len(clause_mates)

            # Create relationship for each clause mate
            for clause_mate in clause_mates:
                # Convert CoreferencePhrase to Phrase for compatibility
                phrase = self._convert_to_phrase(clause_mate)

                # Create antecedent info with cross-sentence analysis
                antecedent_info = self._analyze_antecedents(
                    pronoun, context, all_contexts
                )
                # Debug
                # print(f"DEBUG: Got antecedent info: {antecedent_info}")

                # Extract coreference numbers for statistical analysis
                coref_numbers = self._extract_coreference_numbers(pronoun, phrase)

                relationship = ClauseMateRelationship(
                    sentence_id=str(context.sentence_num),
                    sentence_num=context.sentence_num,
                    pronoun=pronoun,
                    clause_mate=phrase,
                    num_clause_mates=num_clause_mates,
                    antecedent_info=antecedent_info,
                    first_words=getattr(context, "first_words", ""),
                    pronoun_coref_ids=list(pronoun_coref_ids),
                    # Populate coreference number fields for statistical analysis
                    pronoun_coref_base_num=coref_numbers["pronoun_coref_base_num"],
                    pronoun_coref_occurrence_num=coref_numbers[
                        "pronoun_coref_occurrence_num"
                    ],
                    clause_mate_coref_base_num=coref_numbers[
                        "clause_mate_coref_base_num"
                    ],
                    clause_mate_coref_occurrence_num=coref_numbers[
                        "clause_mate_coref_occurrence_num"
                    ],
                    pronoun_coref_link_base_num=coref_numbers[
                        "pronoun_coref_link_base_num"
                    ],
                    pronoun_coref_link_occurrence_num=coref_numbers[
                        "pronoun_coref_link_occurrence_num"
                    ],
                    pronoun_inanimate_coref_link_base_num=coref_numbers[
                        "pronoun_inanimate_coref_link_base_num"
                    ],
                    pronoun_inanimate_coref_link_occurrence_num=coref_numbers[
                        "pronoun_inanimate_coref_link_occurrence_num"
                    ],
                )

                relationships.append(relationship)

        return relationships

    def find_clause_mates(
        self, pronoun: Token, context: SentenceContext
    ) -> List[CoreferencePhrase]:
        """Find all clause mates for a given pronoun in a sentence.

        Args:
            pronoun: The pronoun to find clause mates for
            context: The sentence context

        Returns:
            List of clause mate phrases
        """
        pronoun_coref_ids = self._get_pronoun_coreference_ids(pronoun)

        clause_mates = []
        for phrase in context.coreference_phrases:
            if phrase.entity_id not in pronoun_coref_ids:
                clause_mates.append(phrase)

        return clause_mates

    def validate_relationship(self, relationship: ClauseMateRelationship) -> bool:
        """Validate that a relationship is well-formed.

        Args:
            relationship: The relationship to validate

        Returns:
            True if the relationship is valid
        """
        # Basic validation checks
        if not relationship.pronoun.is_critical_pronoun:
            return False

        if relationship.num_clause_mates < 1:
            return False

        if not relationship.sentence_id:
            return False

        return not relationship.sentence_num < 1

    def _get_pronoun_coreference_ids(self, pronoun: Token) -> Set[str]:
        """Get all coreference IDs for a pronoun.

        Args:
            pronoun: The pronoun token

        Returns:
            Set of coreference IDs
        """
        ids = set()

        # Try to get full ID from animate coreference link
        if pronoun.coreference_link and pronoun.coreference_link != "_":
            full_id = extract_full_coreference_id(pronoun.coreference_link)
            if full_id:
                ids.add(full_id)

        # Try to get full ID from inanimate coreference link
        if (
            pronoun.inanimate_coreference_link
            and pronoun.inanimate_coreference_link != "_"
        ):
            full_id = extract_full_coreference_id(pronoun.inanimate_coreference_link)
            if full_id:
                ids.add(full_id)

        # Fallback: get base IDs from type columns
        if not ids:
            if pronoun.coreference_type and pronoun.coreference_type != "_":
                base_id = extract_coreference_id(pronoun.coreference_type)
                if base_id:
                    ids.add(base_id)

            if (
                pronoun.inanimate_coreference_type
                and pronoun.inanimate_coreference_type != "_"
            ):
                base_id = extract_coreference_id(pronoun.inanimate_coreference_type)
                if base_id:
                    ids.add(base_id)

        return ids

    def _convert_to_phrase(self, coreference_phrase: CoreferencePhrase) -> Phrase:
        """Convert a CoreferencePhrase to a Phrase for compatibility.

        Args:
            coreference_phrase: The coreference phrase to convert

        Returns:
            Converted Phrase object
        """
        # Determine givenness from entity ID
        givenness = determine_givenness(coreference_phrase.entity_id)

        # Use head token for grammatical/thematic roles
        head_token = coreference_phrase.get_head_token()

        return Phrase(
            text=coreference_phrase.phrase_text,
            coreference_id=coreference_phrase.entity_id,
            start_idx=coreference_phrase.start_position,
            end_idx=coreference_phrase.end_position,
            grammatical_role=head_token.grammatical_role,
            thematic_role=head_token.thematic_role,
            coreference_type=head_token.coreference_type
            or head_token.inanimate_coreference_type
            or "_",
            animacy=self._determine_animacy(head_token),
            givenness=givenness,
        )

    def _determine_animacy(self, token: Token) -> Any:
        """Determine animacy type from token coreference information.

        Args:
            token: The token to examine

        Returns:
            AnimacyType enum value
        """
        from src.data.models import AnimacyType

        # Check if token has animate coreference annotation
        if (token.coreference_link and token.coreference_link != "_") or (
            token.coreference_type and token.coreference_type != "_"
        ):
            return AnimacyType.ANIMATE

        # Check if token has inanimate coreference annotation
        elif (
            token.inanimate_coreference_link and token.inanimate_coreference_link != "_"
        ) or (
            token.inanimate_coreference_type and token.inanimate_coreference_type != "_"
        ):
            return AnimacyType.INANIMATE

        # Default to animate if uncertain
        return AnimacyType.ANIMATE

    def _analyze_antecedents(
        self,
        pronoun: Token,
        context: SentenceContext,
        all_contexts: Optional[List[SentenceContext]] = None,
    ) -> AntecedentInfo:
        """Analyze antecedents for a given pronoun with cross-sentence context.

        Args:
            pronoun: The pronoun to analyze
            context: The current sentence context
            all_contexts: All sentence contexts for cross-sentence analysis

        Returns:
            AntecedentInfo with the analysis results
        """
        # Get pronoun's coreference IDs
        pronoun_coref_ids = self._get_pronoun_coreference_ids(pronoun)

        if not pronoun_coref_ids:
            return AntecedentInfo(
                most_recent_text="_",
                most_recent_distance="_",
                first_text="_",
                first_distance="_",
                sentence_id="_",
                choice_count=0,
            )

        # Get base chain numbers for pronoun
        pronoun_chain_numbers = set()
        for coref_id in pronoun_coref_ids:
            if "-" in str(coref_id):
                base_num = str(coref_id).split("-")[0]
                pronoun_chain_numbers.add(base_num)
            else:
                pronoun_chain_numbers.add(str(coref_id))

        if not pronoun_chain_numbers:
            return AntecedentInfo(
                most_recent_text="_",
                most_recent_distance="_",
                first_text="_",
                first_distance="_",
                sentence_id="_",
                choice_count=0,
            )

        # Calculate absolute position of pronoun
        current_sentence_num = context.sentence_num
        pronoun_absolute_pos = 0

        # If we have cross-sentence context, calculate absolute position
        if all_contexts:
            # Count tokens in all sentences before current sentence
            for ctx in all_contexts:
                if ctx.sentence_num < current_sentence_num:
                    pronoun_absolute_pos += len(ctx.tokens)
                elif ctx.sentence_num == current_sentence_num:
                    # Add tokens before pronoun in current sentence
                    pronoun_absolute_pos += pronoun.idx - 1  # idx is 1-based
                    break
        else:
            # Fallback: just use position within sentence
            pronoun_absolute_pos = pronoun.idx - 1

        # Find all potential antecedent phrases
        potential_antecedent_phrases = []

        # Search through all sentences (or just current if no cross-sentence
        # context)
        contexts_to_search = all_contexts if all_contexts else [context]

        for search_ctx in contexts_to_search:
            # Skip sentences after current sentence
            if search_ctx.sentence_num > current_sentence_num:
                continue

            # For current sentence, only look at phrases before pronoun
            phrases_to_check = search_ctx.coreference_phrases
            if search_ctx.sentence_num == current_sentence_num:
                phrases_to_check = [
                    p for p in phrases_to_check if p.start_position < pronoun.idx
                ]

            for phrase in phrases_to_check:
                # Check if phrase shares base coreference chain with pronoun
                phrase_base = (
                    phrase.entity_id.split("-")[0]
                    if "-" in phrase.entity_id
                    else phrase.entity_id
                )

                if phrase_base in pronoun_chain_numbers:
                    # Calculate absolute position of phrase
                    phrase_absolute_pos = 0

                    if all_contexts:
                        # Count tokens in sentences before phrase's sentence
                        for ctx in all_contexts:
                            if ctx.sentence_num < search_ctx.sentence_num:
                                phrase_absolute_pos += len(ctx.tokens)
                            elif ctx.sentence_num == search_ctx.sentence_num:
                                phrase_absolute_pos += (
                                    phrase.start_position - 1
                                )  # start_position is 1-based
                                break
                    else:
                        # Fallback for single sentence
                        phrase_absolute_pos = phrase.start_position - 1

                    distance = pronoun_absolute_pos - phrase_absolute_pos

                    # Only include antecedents that appear before pronoun
                    if distance > 0:
                        occurrence_num = self._extract_occurrence_number(
                            phrase.entity_id
                        )

                        potential_antecedent_phrases.append(
                            {
                                "phrase": phrase,
                                "absolute_pos": phrase_absolute_pos,
                                "distance": distance,
                                "sentence_id": search_ctx.sentence_num,
                                "occurrence_num": occurrence_num,
                            }
                        )

        if not potential_antecedent_phrases:
            return AntecedentInfo(
                most_recent_text="_",
                most_recent_distance="_",
                first_text="_",
                first_distance="_",
                sentence_id="_",
                choice_count=0,
            )

        # Find most recent antecedent (highest absolute position = most recent)
        most_recent = max(potential_antecedent_phrases, key=lambda x: x["absolute_pos"])

        # Find first antecedent (lowest occurrence number = first mention)
        first_antecedent = min(
            potential_antecedent_phrases, key=lambda x: x["occurrence_num"]
        )

        return AntecedentInfo(
            most_recent_text=most_recent["phrase"].phrase_text,
            most_recent_distance=str(most_recent["distance"]),
            first_text=first_antecedent["phrase"].phrase_text,
            first_distance=str(first_antecedent["distance"]),
            sentence_id=str(most_recent["sentence_id"]),
            choice_count=len(potential_antecedent_phrases),
        )

    def _extract_occurrence_number(self, entity_id: str) -> int:
        """Extract occurrence number from entity ID like '127-3'."""
        if "-" in entity_id:
            try:
                return int(entity_id.split("-")[1])
            except (IndexError, ValueError):
                return 999  # Default high number
        return 999

    def _extract_coreference_numbers(self, pronoun: Token, phrase: Phrase) -> dict:
        """Extract all coreference numbers for statistical analysis.

        Args:
            pronoun: The pronoun token
            phrase: The clause mate phrase

        Returns:
            Dictionary with all extracted coreference numbers
        """
        from typing import Dict, Optional

        from ..utils import (
            extract_coref_base_and_occurrence,
            extract_coref_link_numbers,
        )

        result: Dict[str, Optional[int]] = {
            "pronoun_coref_base_num": None,
            "pronoun_coref_occurrence_num": None,
            "clause_mate_coref_base_num": None,
            "clause_mate_coref_occurrence_num": None,
            "pronoun_coref_link_base_num": None,
            "pronoun_coref_link_occurrence_num": None,
            "pronoun_inanimate_coref_link_base_num": None,
            "pronoun_inanimate_coref_link_occurrence_num": None,
        }

        # Extract pronoun coreference type numbers
        if pronoun.coreference_type and pronoun.coreference_type != "_":
            from ..utils import extract_coreference_id

            coref_id = extract_coreference_id(pronoun.coreference_type)
            if coref_id:
                base_num, occurrence_num = extract_coref_base_and_occurrence(coref_id)
                result["pronoun_coref_base_num"] = base_num
                result["pronoun_coref_occurrence_num"] = occurrence_num

        # Extract pronoun coreference link numbers (animate)
        if pronoun.coreference_link and pronoun.coreference_link != "_":
            base_num, occurrence_num = extract_coref_link_numbers(
                pronoun.coreference_link
            )
            result["pronoun_coref_link_base_num"] = base_num
            result["pronoun_coref_link_occurrence_num"] = occurrence_num

        # Extract pronoun inanimate coreference link numbers
        if (
            pronoun.inanimate_coreference_link
            and pronoun.inanimate_coreference_link != "_"
        ):
            base_num, occurrence_num = extract_coref_link_numbers(
                pronoun.inanimate_coreference_link
            )
            result["pronoun_inanimate_coref_link_base_num"] = base_num
            result["pronoun_inanimate_coref_link_occurrence_num"] = occurrence_num

        # Extract clause mate coreference numbers from phrase.coreference_id
        if phrase.coreference_id and phrase.coreference_id != "_":
            base_num, occurrence_num = extract_coref_base_and_occurrence(
                phrase.coreference_id
            )
            result["clause_mate_coref_base_num"] = base_num
            result["clause_mate_coref_occurrence_num"] = occurrence_num

        return result
