"""Unified Relationship Data Model for Multi-File Processing.

This module defines the enhanced data model for relationships that span
across multiple chapter files, including cross-chapter metadata and
global sentence numbering.

Author: Kilo Code
Version: 3.0 - Phase 3.1 Implementation
Date: 2025-07-28
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

from ..data.models import ClauseMateRelationship


@dataclass
class UnifiedClauseMateRelationship(ClauseMateRelationship):
    """Extended relationship model with multi-file metadata.

    This class extends the base ClauseMateRelationship with additional
    fields needed for cross-chapter coreference resolution and unified
    multi-file processing.
    """

    # Multi-file metadata (with defaults to avoid dataclass field ordering issues)
    source_file: str = ""
    chapter_number: int = 0
    global_sentence_id: str = ""
    cross_chapter_relationship: bool = False
    chapter_boundary_context: Optional[str] = None

    def __post_init__(self):
        """Post-initialization processing."""
        # Call parent post-init
        super().__post_init__()

        # Ensure global_sentence_id is set
        if not self.global_sentence_id:
            self.global_sentence_id = f"ch{self.chapter_number}_{self.sentence_id}"

    def get_chapter_context(self) -> str:
        """Get chapter context information."""
        return f"Chapter {self.chapter_number} ({self.source_file})"

    def is_cross_chapter(self) -> bool:
        """Check if this is a cross-chapter relationship."""
        return self.cross_chapter_relationship

    def get_unified_id(self) -> str:
        """Get unified identifier for this relationship."""
        return f"{self.chapter_number}_{self.sentence_id}_{self.pronoun.idx}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation with multi-file metadata."""
        # Get base dictionary from parent
        base_dict = super().to_dict()

        # Add multi-file fields
        base_dict.update(
            {
                "source_file": self.source_file,
                "chapter_number": self.chapter_number,
                "global_sentence_id": self.global_sentence_id,
                "cross_chapter_relationship": self.cross_chapter_relationship,
                "chapter_boundary_context": self.chapter_boundary_context,
            }
        )

        return base_dict

    @classmethod
    def from_base_relationship(
        cls,
        base_rel: ClauseMateRelationship,
        source_file: str,
        chapter_number: int,
        global_sentence_id: str,
    ) -> "UnifiedClauseMateRelationship":
        """Create UnifiedClauseMateRelationship from base relationship.

        Args:
            base_rel: Base ClauseMateRelationship instance
            source_file: Source file path
            chapter_number: Chapter number
            global_sentence_id: Global sentence identifier

        Returns:
            UnifiedClauseMateRelationship instance
        """
        return cls(
            # Copy all base fields (matching ClauseMateRelationship structure)
            sentence_id=base_rel.sentence_id,
            sentence_num=base_rel.sentence_num,
            pronoun=base_rel.pronoun,
            clause_mate=base_rel.clause_mate,
            num_clause_mates=base_rel.num_clause_mates,
            antecedent_info=base_rel.antecedent_info,
            first_words=base_rel.first_words,
            pronoun_coref_ids=base_rel.pronoun_coref_ids,
            pronoun_coref_base_num=base_rel.pronoun_coref_base_num,
            pronoun_coref_occurrence_num=base_rel.pronoun_coref_occurrence_num,
            clause_mate_coref_base_num=base_rel.clause_mate_coref_base_num,
            clause_mate_coref_occurrence_num=base_rel.clause_mate_coref_occurrence_num,
            pronoun_coref_link_base_num=base_rel.pronoun_coref_link_base_num,
            pronoun_coref_link_occurrence_num=base_rel.pronoun_coref_link_occurrence_num,
            pronoun_inanimate_coref_link_base_num=base_rel.pronoun_inanimate_coref_link_base_num,  # noqa: E501
            pronoun_inanimate_coref_link_occurrence_num=base_rel.pronoun_inanimate_coref_link_occurrence_num,  # noqa: E501
            # Add multi-file fields
            source_file=source_file,
            chapter_number=chapter_number,
            global_sentence_id=global_sentence_id,
            cross_chapter_relationship=False,
            chapter_boundary_context=None,
        )
