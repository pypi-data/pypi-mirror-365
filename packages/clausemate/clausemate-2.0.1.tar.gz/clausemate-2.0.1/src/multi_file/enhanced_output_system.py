#!/usr/bin/env python3
"""Enhanced Output System for Multi-File Clause Mates Analysis.

This module provides comprehensive output formatting with advanced metadata,
chapter boundary markers, cross-file relationship indicators, and detailed
summary statistics for multi-file processing.

Task 7: Unified Output System Implementation
- Comprehensive output format with source file metadata
- Chapter/file boundary markers in output
- Cross-file relationship indicators
- Summary statistics for multi-file processing
"""

import csv
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..data.models import ClauseMateRelationship


@dataclass
class ChapterMetadata:
    """Metadata for a single chapter."""

    chapter_number: int
    chapter_id: str
    source_file: str
    file_format: str
    total_relationships: int
    total_sentences: int
    sentence_range: Tuple[int, int]
    global_sentence_range: Tuple[int, int]
    coreference_chains: int
    processing_time: float
    file_size_bytes: int
    encoding: str = "utf-8"


@dataclass
class CrossChapterConnection:
    """Information about cross-chapter coreference connections."""

    chain_id: str
    from_chapter: int
    to_chapter: int
    connection_type: str  # "same_chain_id", "similar_mentions", "unified_chain"
    strength: float  # 0.0 to 1.0
    mentions_count: int
    sentence_span: Tuple[int, int]  # global sentence IDs


@dataclass
class ProcessingStatistics:
    """Comprehensive processing statistics."""

    total_chapters: int
    total_relationships: int
    total_sentences: int
    total_coreference_chains: int
    cross_chapter_chains: int
    cross_chapter_relationships: int
    processing_time_seconds: float
    memory_usage_mb: Optional[float]

    # Per-chapter breakdown
    chapter_breakdown: List[ChapterMetadata]

    # Cross-chapter analysis
    cross_chapter_connections: List[CrossChapterConnection]

    # Quality metrics
    average_relationships_per_sentence: float
    average_chain_length: float
    cross_chapter_percentage: float


class EnhancedOutputSystem:
    """Enhanced output system with comprehensive metadata and analysis."""

    def __init__(self, output_dir: str):
        """Initialize the enhanced output system.

        Args:
            output_dir: Directory for output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

    def create_enhanced_csv_output(
        self,
        relationships: List[ClauseMateRelationship],
        chapter_metadata: List[ChapterMetadata],
        cross_chapter_connections: List[CrossChapterConnection],
        output_filename: str = "enhanced_unified_relationships.csv",
    ) -> str:
        """Create enhanced CSV output with comprehensive metadata.

        Args:
            relationships: List of all relationships
            chapter_metadata: Metadata for each chapter
            cross_chapter_connections: Cross-chapter connection information
            output_filename: Name of output CSV file

        Returns:
            Path to created CSV file
        """
        output_path = self.output_dir / output_filename

        # Enhanced column headers with additional metadata
        enhanced_headers = [
            # Chapter and file metadata
            "chapter_file",
            "chapter_number",
            "chapter_id",
            "chapter_title",
            "source_file_path",
            "file_format",
            "file_size_bytes",
            # Global positioning
            "global_sentence_id",
            "global_relationship_id",
            "chapter_boundary_marker",
            "cross_chapter",
            "cross_chapter_chain_id",
            # Original relationship data (existing columns)
            "sentence_id",
            "sentence_id_numeric",
            "sentence_id_prefixed",
            "sentence_num",
            "first_words",
            # Pronoun information
            "pronoun_text",
            "pronoun_token_idx",
            "pronoun_grammatical_role",
            "pronoun_thematic_role",
            "pronoun_givenness",
            "pronoun_coref_ids",
            "pronoun_coref_base_num",
            "pronoun_coref_occurrence_num",
            "pronoun_coreference_link",
            "pronoun_coref_link_base_num",
            "pronoun_coref_link_occurrence_num",
            "pronoun_coreference_type",
            "pronoun_inanimate_coreference_link",
            "pronoun_inanimate_coref_link_base_num",
            "pronoun_inanimate_coref_link_occurrence_num",
            "pronoun_inanimate_coreference_type",
            "pronoun_most_recent_antecedent_text",
            "pronoun_most_recent_antecedent_distance",
            "pronoun_first_antecedent_text",
            "pronoun_first_antecedent_distance",
            "pronoun_antecedent_choice",
            # Clause mate information
            "num_clause_mates",
            "clause_mate_text",
            "clause_mate_coref_id",
            "clause_mate_coref_base_num",
            "clause_mate_coref_occurrence_num",
            "clause_mate_start_idx",
            "clause_mate_end_idx",
            "clause_mate_grammatical_role",
            "clause_mate_thematic_role",
            "clause_mate_coreference_type",
            "clause_mate_animacy",
            "clause_mate_givenness",
            # Enhanced analysis fields
            "narrative_position",
            "character_continuity_score",
            "discourse_coherence_score",
            "cross_chapter_strength",
            "chain_importance_score",
        ]

        # Create chapter lookup for metadata
        chapter_lookup = {meta.chapter_number: meta for meta in chapter_metadata}
        {conn.chain_id: conn for conn in cross_chapter_connections}

        with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(enhanced_headers)

            global_rel_id = 1

            for rel in relationships:
                # Get chapter metadata
                # Handle both UnifiedClauseMateRelationship and base ClauseMateRelationship
                chapter_num = getattr(
                    rel, "chapter_number", 1
                )  # Default to chapter 1 for base relationships
                chapter_meta = chapter_lookup.get(chapter_num)

                # Determine cross-chapter information
                cross_chapter_info = self._analyze_cross_chapter_relationship(
                    rel, cross_chapter_connections
                )

                # Calculate enhanced analysis scores
                analysis_scores = self._calculate_analysis_scores(rel, chapter_meta)

                # Create boundary marker
                boundary_marker = self._create_boundary_marker(rel, chapter_metadata)

                row = [
                    # Chapter and file metadata
                    getattr(rel, "chapter_file", ""),
                    chapter_num,
                    f"Chapter_{chapter_num}",
                    f"Chapter {chapter_num}",  # chapter_title
                    getattr(rel, "source_file_path", ""),
                    chapter_meta.file_format if chapter_meta else "unknown",
                    chapter_meta.file_size_bytes if chapter_meta else 0,
                    # Global positioning
                    getattr(rel, "global_sentence_id", ""),
                    f"global_rel_{global_rel_id}",
                    boundary_marker,
                    getattr(rel, "cross_chapter", False),
                    cross_chapter_info.get("chain_id", ""),
                    # Original relationship data
                    rel.sentence_num,
                    rel.sentence_num,
                    f"sent_{rel.sentence_num}",
                    rel.sentence_num,
                    getattr(rel, "first_words", ""),
                    # Pronoun information
                    rel.pronoun.text,
                    rel.pronoun.idx,
                    getattr(rel.pronoun, "grammatical_role", "*"),
                    getattr(rel.pronoun, "thematic_role", "*"),
                    getattr(rel.pronoun, "givenness", ""),
                    str(getattr(rel, "pronoun_coref_ids", [])),
                    getattr(rel.pronoun, "coref_base_num", ""),
                    getattr(rel.pronoun, "coref_occurrence_num", ""),
                    getattr(rel.pronoun, "coreference_link", ""),
                    getattr(rel.pronoun, "coref_link_base_num", ""),
                    getattr(rel.pronoun, "coref_link_occurrence_num", ""),
                    getattr(rel.pronoun, "coreference_type", ""),
                    getattr(rel.pronoun, "inanimate_coreference_link", ""),
                    getattr(rel.pronoun, "inanimate_coref_link_base_num", ""),
                    getattr(rel.pronoun, "inanimate_coref_link_occurrence_num", ""),
                    getattr(rel.pronoun, "inanimate_coreference_type", ""),
                    getattr(rel.pronoun, "most_recent_antecedent_text", ""),
                    getattr(rel.pronoun, "most_recent_antecedent_distance", ""),
                    getattr(rel.pronoun, "first_antecedent_text", ""),
                    getattr(rel.pronoun, "first_antecedent_distance", ""),
                    getattr(rel.pronoun, "antecedent_choice", ""),
                    # Clause mate information
                    1,  # num_clause_mates (simplified)
                    rel.clause_mate.text,
                    getattr(rel.clause_mate, "coreference_id", ""),
                    getattr(rel.clause_mate, "coref_base_num", ""),
                    getattr(rel.clause_mate, "coref_occurrence_num", ""),
                    rel.clause_mate.start_idx,
                    rel.clause_mate.end_idx,
                    getattr(rel.clause_mate, "grammatical_role", "*"),
                    getattr(rel.clause_mate, "thematic_role", "*"),
                    getattr(rel.clause_mate, "coreference_type", ""),
                    getattr(rel.clause_mate, "animacy", ""),
                    getattr(rel.clause_mate, "givenness", ""),
                    # Enhanced analysis fields
                    analysis_scores["narrative_position"],
                    analysis_scores["character_continuity_score"],
                    analysis_scores["discourse_coherence_score"],
                    cross_chapter_info.get("strength", 0.0),
                    analysis_scores["chain_importance_score"],
                ]

                writer.writerow(row)
                global_rel_id += 1

        self.logger.info(f"Enhanced CSV output created: {output_path}")
        return str(output_path)

    def create_comprehensive_statistics(
        self,
        relationships: List[ClauseMateRelationship],
        chapter_metadata: List[ChapterMetadata],
        cross_chapter_connections: List[CrossChapterConnection],
        processing_time: float,
        output_filename: str = "comprehensive_statistics.json",
    ) -> str:
        """Create comprehensive processing statistics.

        Args:
            relationships: List of all relationships
            chapter_metadata: Metadata for each chapter
            cross_chapter_connections: Cross-chapter connection information
            processing_time: Total processing time in seconds
            output_filename: Name of output JSON file

        Returns:
            Path to created statistics file
        """
        output_path = self.output_dir / output_filename

        # Calculate comprehensive statistics
        total_sentences = sum(meta.total_sentences for meta in chapter_metadata)
        total_chains = sum(meta.coreference_chains for meta in chapter_metadata)
        cross_chapter_rels = sum(
            1 for rel in relationships if getattr(rel, "cross_chapter", False)
        )

        # Calculate quality metrics
        avg_rels_per_sentence = (
            len(relationships) / total_sentences if total_sentences > 0 else 0
        )
        avg_chain_length = len(relationships) / total_chains if total_chains > 0 else 0
        cross_chapter_percentage = (
            (len(cross_chapter_connections) / total_chains * 100)
            if total_chains > 0
            else 0
        )

        # Create processing statistics
        stats = ProcessingStatistics(
            total_chapters=len(chapter_metadata),
            total_relationships=len(relationships),
            total_sentences=total_sentences,
            total_coreference_chains=total_chains,
            cross_chapter_chains=len(cross_chapter_connections),
            cross_chapter_relationships=cross_chapter_rels,
            processing_time_seconds=processing_time,
            memory_usage_mb=None,  # Could be implemented with psutil
            chapter_breakdown=chapter_metadata,
            cross_chapter_connections=cross_chapter_connections,
            average_relationships_per_sentence=avg_rels_per_sentence,
            average_chain_length=avg_chain_length,
            cross_chapter_percentage=cross_chapter_percentage,
        )

        # Convert to JSON-serializable format
        stats_dict = asdict(stats)

        # Add timestamp and version info
        stats_dict["generated_at"] = datetime.now().isoformat()
        stats_dict["system_version"] = "3.1 - Enhanced Output System"
        stats_dict["output_format_version"] = "1.0"

        # Write to file
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(stats_dict, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Comprehensive statistics created: {output_path}")
        return str(output_path)

    def create_chapter_boundary_report(
        self,
        chapter_metadata: List[ChapterMetadata],
        cross_chapter_connections: List[CrossChapterConnection],
        output_filename: str = "chapter_boundary_analysis.json",
    ) -> str:
        """Create detailed chapter boundary analysis report.

        Args:
            chapter_metadata: Metadata for each chapter
            cross_chapter_connections: Cross-chapter connection information
            output_filename: Name of output JSON file

        Returns:
            Path to created report file
        """
        output_path = self.output_dir / output_filename

        # Analyze chapter boundaries
        boundary_analysis = {
            "chapter_transitions": [],
            "boundary_statistics": {},
            "cross_chapter_patterns": {},
        }

        # Analyze transitions between consecutive chapters
        for i in range(len(chapter_metadata) - 1):
            current = chapter_metadata[i]
            next_chapter = chapter_metadata[i + 1]

            # Find connections between these chapters
            connections = [
                conn
                for conn in cross_chapter_connections
                if (
                    conn.from_chapter == current.chapter_number
                    and conn.to_chapter == next_chapter.chapter_number
                )
            ]

            transition = {
                "from_chapter": current.chapter_number,
                "to_chapter": next_chapter.chapter_number,
                "sentence_gap": next_chapter.global_sentence_range[0]
                - current.global_sentence_range[1],
                "connections_count": len(connections),
                "connection_types": [conn.connection_type for conn in connections],
                "average_strength": sum(conn.strength for conn in connections)
                / len(connections)
                if connections
                else 0.0,
                "narrative_continuity_score": self._calculate_narrative_continuity(
                    current, next_chapter, connections
                ),
            }

            boundary_analysis["chapter_transitions"].append(transition)

        # Calculate boundary statistics
        boundary_analysis["boundary_statistics"] = {
            "total_boundaries": len(chapter_metadata) - 1,
            "boundaries_with_connections": sum(
                1
                for t in boundary_analysis["chapter_transitions"]
                if t["connections_count"] > 0
            ),
            "average_connections_per_boundary": sum(
                t["connections_count"] for t in boundary_analysis["chapter_transitions"]
            )
            / len(boundary_analysis["chapter_transitions"])
            if boundary_analysis["chapter_transitions"]
            else 0,
            "strongest_boundary": max(
                boundary_analysis["chapter_transitions"],
                key=lambda x: x["average_strength"],
            )
            if boundary_analysis["chapter_transitions"]
            else None,
            "weakest_boundary": min(
                boundary_analysis["chapter_transitions"],
                key=lambda x: x["average_strength"],
            )
            if boundary_analysis["chapter_transitions"]
            else None,
        }

        # Analyze cross-chapter patterns
        connection_types = {}
        for conn in cross_chapter_connections:
            if conn.connection_type not in connection_types:
                connection_types[conn.connection_type] = []
            connection_types[conn.connection_type].append(conn)

        boundary_analysis["cross_chapter_patterns"] = {
            conn_type: {
                "count": len(connections),
                "average_strength": sum(c.strength for c in connections)
                / len(connections),
                "chapter_span": {
                    "min": min(c.to_chapter - c.from_chapter for c in connections),
                    "max": max(c.to_chapter - c.from_chapter for c in connections),
                    "average": sum(c.to_chapter - c.from_chapter for c in connections)
                    / len(connections),
                },
            }
            for conn_type, connections in connection_types.items()
        }

        # Add metadata
        boundary_analysis["metadata"] = {
            "generated_at": datetime.now().isoformat(),
            "total_chapters": len(chapter_metadata),
            "analysis_version": "1.0",
        }

        # Write to file
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(boundary_analysis, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Chapter boundary analysis created: {output_path}")
        return str(output_path)

    def _analyze_cross_chapter_relationship(
        self,
        relationship: ClauseMateRelationship,
        cross_chapter_connections: List[CrossChapterConnection],
    ) -> Dict[str, Any]:
        """Analyze cross-chapter aspects of a relationship."""
        # Check if this relationship is part of a cross-chapter chain
        pronoun_coref_ids = getattr(relationship, "pronoun_coref_ids", [])

        for conn in cross_chapter_connections:
            if any(chain_id in str(pronoun_coref_ids) for chain_id in [conn.chain_id]):
                return {
                    "chain_id": conn.chain_id,
                    "connection_type": conn.connection_type,
                    "strength": conn.strength,
                    "is_cross_chapter": True,
                }

        return {
            "chain_id": "",
            "connection_type": "within_chapter",
            "strength": 0.0,
            "is_cross_chapter": False,
        }

    def _calculate_analysis_scores(
        self,
        relationship: ClauseMateRelationship,
        chapter_meta: Optional[ChapterMetadata],
    ) -> Dict[str, float]:
        """Calculate enhanced analysis scores for a relationship."""
        # Narrative position (0.0 to 1.0 based on position in chapter)
        narrative_position = 0.0
        if (
            chapter_meta
            and chapter_meta.sentence_range[1] > chapter_meta.sentence_range[0]
        ):
            position_in_chapter = (
                relationship.sentence_num - chapter_meta.sentence_range[0]
            ) / (chapter_meta.sentence_range[1] - chapter_meta.sentence_range[0])
            narrative_position = max(0.0, min(1.0, position_in_chapter))

        # Character continuity score (based on coreference chain length and frequency)
        character_continuity_score = 0.5  # Default baseline
        pronoun_coref_ids = getattr(relationship, "pronoun_coref_ids", [])
        if pronoun_coref_ids:
            # Higher score for longer chain IDs (indicating more references)
            character_continuity_score = min(1.0, len(str(pronoun_coref_ids)) / 20.0)

        # Discourse coherence score (based on distance to antecedents)
        discourse_coherence_score = 0.5  # Default baseline
        recent_distance = getattr(
            relationship.pronoun, "most_recent_antecedent_distance", None
        )
        if recent_distance and isinstance(recent_distance, (int, float)):
            # Closer antecedents indicate better coherence
            discourse_coherence_score = max(
                0.1, min(1.0, 1.0 / (1.0 + recent_distance / 10.0))
            )

        # Chain importance score (based on multiple factors)
        chain_importance_score = 0.5  # Default baseline
        if hasattr(relationship.pronoun, "coreference_type"):
            coref_type = relationship.pronoun.coreference_type
            if "PersPron" in str(coref_type):
                chain_importance_score += 0.3  # Personal pronouns are important
            if "D-Pron" in str(coref_type):
                chain_importance_score += 0.2  # Demonstrative pronouns

        chain_importance_score = min(1.0, chain_importance_score)

        return {
            "narrative_position": round(narrative_position, 3),
            "character_continuity_score": round(character_continuity_score, 3),
            "discourse_coherence_score": round(discourse_coherence_score, 3),
            "chain_importance_score": round(chain_importance_score, 3),
        }

    def _create_boundary_marker(
        self,
        relationship: ClauseMateRelationship,
        chapter_metadata: List[ChapterMetadata],
    ) -> str:
        """Create a boundary marker for the relationship."""
        # Handle both UnifiedClauseMateRelationship and base ClauseMateRelationship
        chapter_num = getattr(
            relationship, "chapter_number", 1
        )  # Default to chapter 1 for base relationships
        chapter_meta = next(
            (meta for meta in chapter_metadata if meta.chapter_number == chapter_num),
            None,
        )

        if not chapter_meta:
            return "unknown"

        # Determine position within chapter
        sentence_num = relationship.sentence_num
        chapter_start, chapter_end = chapter_meta.sentence_range

        if sentence_num <= chapter_start + 5:
            return "chapter_beginning"
        elif sentence_num >= chapter_end - 5:
            return "chapter_end"
        else:
            return "chapter_middle"

    def _calculate_narrative_continuity(
        self,
        current_chapter: ChapterMetadata,
        next_chapter: ChapterMetadata,
        connections: List[CrossChapterConnection],
    ) -> float:
        """Calculate narrative continuity score between chapters."""
        if not connections:
            return 0.0

        # Base score on number and strength of connections
        base_score = len(connections) / 10.0  # Normalize by expected max connections
        strength_bonus = sum(conn.strength for conn in connections) / len(connections)

        # Bonus for different types of connections
        connection_types = {conn.connection_type for conn in connections}
        diversity_bonus = len(connection_types) / 3.0  # Max 3 types expected

        total_score = (base_score + strength_bonus + diversity_bonus) / 3.0
        return min(1.0, total_score)
