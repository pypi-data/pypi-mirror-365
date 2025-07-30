"""Data models for the clause mates analyzer.

This module defines the core data structures used throughout the application,
replacing dictionaries with typed dataclasses for better maintainability and safety.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class AnimacyType(Enum):
    """Enumeration for animacy types in coreference analysis."""

    ANIMATE = "anim"
    INANIMATE = "inanim"


@dataclass
class Token:
    """Represents a single token from the TSV file with all its linguistic annotations.

    This replaces the dictionary-based token representation for better type safety
    and clearer interfaces.
    """

    idx: int
    text: str
    sentence_num: int
    grammatical_role: str
    thematic_role: str
    coreference_link: Optional[str] = None
    coreference_type: Optional[str] = None
    inanimate_coreference_link: Optional[str] = None
    inanimate_coreference_type: Optional[str] = None
    is_critical_pronoun: bool = False

    # Additional fields for phrase extraction
    entity_id: Optional[str] = None
    token_position: int = 0
    columns: Optional[List[str]] = None

    def __post_init__(self) -> None:
        """Validate token data after initialization."""
        if self.idx < 1:
            raise ValueError("Token index must be positive")
        if self.sentence_num < 0:  # Allow 0 as temporary value
            raise ValueError("Sentence number cannot be negative")
        if not self.text.strip():
            raise ValueError("Token text cannot be empty")

        # Initialize columns if not provided
        if self.columns is None:
            self.columns = []


@dataclass
class AntecedentInfo:
    """Information about antecedents for a pronoun.

    Stores both most recent and first antecedent information for comprehensive analysis.
    """

    most_recent_text: str
    most_recent_distance: str
    first_text: str
    first_distance: str
    sentence_id: str
    choice_count: int = 0

    def __post_init__(self) -> None:
        """Validate antecedent information."""
        if self.choice_count < 0:
            raise ValueError("Choice count cannot be negative")


@dataclass
class Phrase:
    """Represents a grouped phrase from consecutive tokens with the same coreference ID.

    This structure captures multi-token expressions that refer to the same entity.
    """

    text: str
    coreference_id: str
    start_idx: int
    end_idx: int
    grammatical_role: str
    thematic_role: str
    coreference_type: str
    animacy: AnimacyType
    givenness: str

    def __post_init__(self) -> None:
        """Validate phrase data."""
        if self.start_idx > self.end_idx:
            raise ValueError("Start index cannot be greater than end index")
        if self.start_idx < 1 or self.end_idx < 1:
            raise ValueError("Phrase indices must be positive")
        if not self.text.strip():
            raise ValueError("Phrase text cannot be empty")
        if not self.coreference_id:
            raise ValueError("Coreference ID cannot be empty")

    @property
    def length(self) -> int:
        """Return the length of the phrase in tokens."""
        return self.end_idx - self.start_idx + 1


@dataclass
class CoreferencePhrase:
    """Represents a coreference phrase extracted from tokens with the same entity ID.

    This class groups tokens that belong to the same coreference entity,
    supporting the phrase extraction pipeline.
    """

    entity_id: str
    tokens: List[Token]
    phrase_text: str
    start_position: int
    end_position: int
    sentence_id: str

    def __post_init__(self) -> None:
        """Validate phrase data."""
        if not self.entity_id:
            raise ValueError("Entity ID cannot be empty")
        if not self.tokens:
            raise ValueError("Phrase must have at least one token")
        if self.start_position > self.end_position:
            raise ValueError("Start position cannot be greater than end position")
        if not self.sentence_id:
            raise ValueError("Sentence ID cannot be empty")

    @property
    def length(self) -> int:
        """Return the number of tokens in this phrase."""
        return len(self.tokens)

    @property
    def is_multi_token(self) -> bool:
        """Check if this phrase contains multiple tokens."""
        return len(self.tokens) > 1

    def get_head_token(self) -> Token:
        """Get the head token of the phrase.

        For now, returns the first token. This could be enhanced
        with linguistic analysis to find the actual head.
        """
        if not self.tokens:
            raise ValueError("Cannot get head of empty phrase")
        return self.tokens[0]


@dataclass
class ClauseMateRelationship:
    """Represents a complete clause mate relationship between a pronoun and a clause mate.

    This is the main output structure that captures all the linguistic features
    and relationships for analysis.
    """

    sentence_id: str
    sentence_num: int
    pronoun: Token
    clause_mate: Phrase
    num_clause_mates: int
    antecedent_info: AntecedentInfo
    first_words: str = ""

    # Pronoun coreference IDs (for compatibility with Phase 1)
    pronoun_coref_ids: Optional[List[str]] = None

    # Derived numeric fields for analysis
    pronoun_coref_base_num: Optional[int] = None
    pronoun_coref_occurrence_num: Optional[int] = None
    clause_mate_coref_base_num: Optional[int] = None
    clause_mate_coref_occurrence_num: Optional[int] = None
    pronoun_coref_link_base_num: Optional[int] = None
    pronoun_coref_link_occurrence_num: Optional[int] = None
    pronoun_inanimate_coref_link_base_num: Optional[int] = None
    pronoun_inanimate_coref_link_occurrence_num: Optional[int] = None

    def __post_init__(self) -> None:
        """Validate relationship data."""
        if self.sentence_num < 1:
            raise ValueError("Sentence number must be positive")
        if self.num_clause_mates < 1:
            raise ValueError("Number of clause mates must be positive")
        if not self.sentence_id:
            raise ValueError("Sentence ID cannot be empty")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the relationship to a dictionary for CSV export.

        This method flattens the nested structure into a flat dictionary
        compatible with pandas DataFrame export. Uses standardized column order.
        """
        # Import here to avoid circular imports
        from ..config import ExportColumns

        # Create the full data dictionary
        data = {
            # Sentence information
            "sentence_id": self.sentence_num,
            "sentence_id_numeric": self.sentence_num,
            "sentence_id_prefixed": f"sent_{self.sentence_num}",
            "sentence_num": self.sentence_num,
            "first_words": self.first_words,
            # Pronoun basic information
            "pronoun_text": self.pronoun.text,
            "pronoun_token_idx": self.pronoun.idx,
            "pronoun_grammatical_role": self.pronoun.grammatical_role,
            "pronoun_thematic_role": self.pronoun.thematic_role,
            "pronoun_givenness": self._determine_pronoun_givenness(),
            # Pronoun coreference information
            "pronoun_coref_ids": self.pronoun_coref_ids,
            "pronoun_coref_base_num": self.pronoun_coref_base_num,
            "pronoun_coref_occurrence_num": self.pronoun_coref_occurrence_num,
            # Pronoun coreference links
            "pronoun_coreference_link": self.pronoun.coreference_link,
            "pronoun_coref_link_base_num": self.pronoun_coref_link_base_num,
            "pronoun_coref_link_occurrence_num": self.pronoun_coref_link_occurrence_num,
            "pronoun_coreference_type": self.pronoun.coreference_type,
            # Pronoun inanimate coreference links
            "pronoun_inanimate_coreference_link": (
                self.pronoun.inanimate_coreference_link
            ),
            "pronoun_inanimate_coref_link_base_num": (
                self.pronoun_inanimate_coref_link_base_num
            ),
            "pronoun_inanimate_coref_link_occurrence_num": (
                self.pronoun_inanimate_coref_link_occurrence_num
            ),
            "pronoun_inanimate_coreference_type": (
                self.pronoun.inanimate_coreference_type
            ),
            # Pronoun antecedent information
            "pronoun_most_recent_antecedent_text": (
                self.antecedent_info.most_recent_text
            ),
            "pronoun_most_recent_antecedent_distance": (
                self.antecedent_info.most_recent_distance
            ),
            "pronoun_first_antecedent_text": self.antecedent_info.first_text,
            "pronoun_first_antecedent_distance": self.antecedent_info.first_distance,
            "pronoun_antecedent_choice": self.antecedent_info.choice_count,
            # Clause mate information
            "num_clause_mates": self.num_clause_mates,
            "clause_mate_text": self.clause_mate.text,
            "clause_mate_coref_id": self.clause_mate.coreference_id,
            "clause_mate_coref_base_num": self.clause_mate_coref_base_num,
            "clause_mate_coref_occurrence_num": self.clause_mate_coref_occurrence_num,
            "clause_mate_start_idx": self.clause_mate.start_idx,
            "clause_mate_end_idx": self.clause_mate.end_idx,
            "clause_mate_grammatical_role": self.clause_mate.grammatical_role,
            "clause_mate_thematic_role": self.clause_mate.thematic_role,
            "clause_mate_coreference_type": self.clause_mate.coreference_type,
            "clause_mate_animacy": self.clause_mate.animacy.value,
            "clause_mate_givenness": self.clause_mate.givenness,
        }

        # Return dictionary in standardized column order
        return {col: data.get(col) for col in ExportColumns.STANDARD_ORDER}

    def _determine_pronoun_givenness(self) -> str:
        """Determine pronoun givenness from its coreference information."""
        from ..utils import determine_givenness

        # Try to determine givenness from coreference links
        # First try animate coreference link
        if self.pronoun.coreference_link and self.pronoun.coreference_link != "_":
            # Extract the full coreference ID from the link
            if "->" in self.pronoun.coreference_link:
                coref_id = self.pronoun.coreference_link.split("->")[-1]
                givenness = determine_givenness(coref_id)
                if givenness != "_":
                    return givenness

        # Try inanimate coreference link if animate didn't work
        if (
            self.pronoun.inanimate_coreference_link
            and self.pronoun.inanimate_coreference_link != "_"
        ) and "->" in self.pronoun.inanimate_coreference_link:
            coref_id = self.pronoun.inanimate_coreference_link.split("->")[-1]
            givenness = determine_givenness(coref_id)
            if givenness != "_":
                return givenness

        # Fallback: try to extract from type fields
        if self.pronoun.coreference_type and self.pronoun.coreference_type != "_":
            # Extract ID from type field like "PersPron[127]"
            import re

            match = re.search(r"\[(\d+)\]", self.pronoun.coreference_type)
            if match:
                # This is the base ID, we don't know the occurrence, so assume
                # it's given
                return "bekannt"

        if (
            self.pronoun.inanimate_coreference_type
            and self.pronoun.inanimate_coreference_type != "_"
        ):
            # Extract ID from type field like "defNP[192]"
            import re

            match = re.search(r"\[(\d+)\]", self.pronoun.inanimate_coreference_type)
            if match:
                # This is the base ID, we don't know the occurrence, so assume
                # it's given
                return "bekannt"

        # If no coreference information available, return missing
        return "_"


@dataclass
class SentenceContext:
    """Context information for a sentence during processing.

    This provides a rich context object that can be passed between
    processing functions instead of multiple separate parameters.
    """

    sentence_id: str
    sentence_num: int
    tokens: List[Token]
    critical_pronouns: List[Token]
    coreference_phrases: List[CoreferencePhrase]
    first_words: str = ""

    def __post_init__(self) -> None:
        """Validate sentence context."""
        if self.sentence_num < 1:
            raise ValueError("Sentence number must be positive")
        if not self.sentence_id:
            raise ValueError("Sentence ID cannot be empty")
        if not self.tokens:
            raise ValueError("Sentence must have at least one token")

    @property
    def has_critical_pronouns(self) -> bool:
        """Check if sentence contains any critical pronouns."""
        return len(self.critical_pronouns) > 0

    @property
    def has_coreference_phrases(self) -> bool:
        """Check if sentence contains any coreference phrases."""
        return len(self.coreference_phrases) > 0


@dataclass
class CoreferenceChain:
    """Represents a chain of coreferential expressions.

    Tracks all mentions that refer to the same entity across the text.
    """

    chain_id: str
    mentions: List[Token]
    animacy: AnimacyType

    def __post_init__(self) -> None:
        """Validate coreference chain."""
        if not self.chain_id:
            raise ValueError("Chain ID cannot be empty")
        if not self.mentions:
            raise ValueError("Chain must have at least one mention")

    def add_mention(self, mention: Token) -> None:
        """Add a new mention to this chain."""
        if mention not in self.mentions:
            self.mentions.append(mention)

    @property
    def length(self) -> int:
        """Return the number of mentions in this chain."""
        return len(self.mentions)


@dataclass
class ExtractionResult:
    """Container for results from various extraction operations.

    Provides a structured way to return multiple types of extracted information.
    """

    pronouns: List[Token]
    phrases: Union[List[Phrase], List[CoreferencePhrase]]
    relationships: List[ClauseMateRelationship]
    coreference_chains: List[CoreferenceChain]
    features: Dict[str, Any]

    def __post_init__(self) -> None:
        """Initialize empty collections if None."""
        self.pronouns = self.pronouns or []
        self.phrases = self.phrases or []
        self.relationships = self.relationships or []
        self.coreference_chains = self.coreference_chains or []
        self.features = self.features or {}

    @property
    def has_results(self) -> bool:
        """Check if any extraction results were found."""
        return (
            len(self.pronouns) > 0
            or len(self.phrases) > 0
            or len(self.relationships) > 0
            or len(self.coreference_chains) > 0
            or len(self.features) > 0
        )
