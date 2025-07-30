"""Unified Sentence Manager for Multi-File Processing.

This module manages global sentence numbering across multiple chapter files,
ensuring consistent sentence identification in the unified output.

Author: Kilo Code
Version: 3.0 - Phase 3.1 Implementation
Date: 2025-07-28
"""

import logging
from pathlib import Path
from typing import Dict, Tuple


class UnifiedSentenceManager:
    """Manages global sentence numbering across multiple chapter files.

    This class provides unified sentence identification by mapping local
    sentence IDs from individual chapters to global sentence numbers
    that maintain continuity across the entire book.
    """

    def __init__(self):
        """Initialize the unified sentence manager."""
        self.logger = logging.getLogger(__name__)

        # Mapping from file path to sentence range
        self.chapter_sentence_ranges: Dict[str, Tuple[int, int]] = {}

        # Mapping from (file_path, local_sentence_id) to global_sentence_id
        self.sentence_mapping: Dict[Tuple[str, str], str] = {}

        # Global sentence counter
        self.global_sentence_counter = 0

        self.logger.info("UnifiedSentenceManager initialized")

    def process_chapters(self, chapter_info_list) -> None:
        """Process chapter information to establish global sentence numbering.

        Args:
            chapter_info_list: List of ChapterInfo objects
        """
        self.logger.info(
            "Processing %d chapters for unified sentence management",
            len(chapter_info_list),
        )

        self.global_sentence_counter = 0

        for chapter_info in chapter_info_list:
            file_path = chapter_info.file_path
            chapter_num = chapter_info.chapter_number
            sentence_start, sentence_end = chapter_info.sentence_range

            self.logger.info(
                "Processing chapter %d: %s (sentences %d-%d)",
                chapter_num,
                file_path,
                sentence_start,
                sentence_end,
            )

            # Calculate global sentence range for this chapter
            global_start = self.global_sentence_counter + 1
            sentence_count = sentence_end - sentence_start + 1
            global_end = self.global_sentence_counter + sentence_count

            # Store chapter sentence range
            self.chapter_sentence_ranges[file_path] = (global_start, global_end)

            # Create mappings for each sentence in this chapter
            for local_sentence_num in range(sentence_start, sentence_end + 1):
                local_sentence_id = str(local_sentence_num)
                global_sentence_num = global_start + (
                    local_sentence_num - sentence_start
                )
                global_sentence_id = f"global_{global_sentence_num}"

                # Store mapping
                self.sentence_mapping[(file_path, local_sentence_id)] = (
                    global_sentence_id
                )

            # Update global counter
            self.global_sentence_counter = global_end

            self.logger.info(
                "Chapter %d mapped to global sentences %d-%d",
                chapter_num,
                global_start,
                global_end,
            )

        self.logger.info(
            "Unified sentence management complete: %d total sentences",
            self.global_sentence_counter,
        )

    def get_global_sentence_id(self, file_path: str, local_sentence_id: str) -> str:
        """Get global sentence ID for a local sentence.

        Args:
            file_path: Path to the chapter file
            local_sentence_id: Local sentence identifier

        Returns:
            Global sentence identifier
        """
        mapping_key = (file_path, local_sentence_id)

        if mapping_key in self.sentence_mapping:
            return self.sentence_mapping[mapping_key]
        else:
            # Fallback: create a chapter-prefixed ID
            chapter_num = self._extract_chapter_number(file_path)
            fallback_id = f"ch{chapter_num}_{local_sentence_id}"

            self.logger.warning(
                "No mapping found for %s:%s, using fallback: %s",
                file_path,
                local_sentence_id,
                fallback_id,
            )

            return fallback_id

    def get_chapter_sentence_range(self, file_path: str) -> Tuple[int, int]:
        """Get global sentence range for a chapter.

        Args:
            file_path: Path to the chapter file

        Returns:
            Tuple of (start_sentence, end_sentence) in global numbering
        """
        return self.chapter_sentence_ranges.get(file_path, (0, 0))

    def get_total_sentences(self) -> int:
        """Get total number of sentences across all chapters."""
        return self.global_sentence_counter

    def get_chapter_summary(self) -> Dict[str, Dict[str, int]]:
        """Get summary of sentence ranges for all chapters.

        Returns:
            Dictionary mapping file paths to sentence range information
        """
        summary = {}

        for file_path, (start, end) in self.chapter_sentence_ranges.items():
            chapter_num = self._extract_chapter_number(file_path)
            summary[file_path] = {
                "chapter_number": chapter_num,
                "global_start": start,
                "global_end": end,
                "sentence_count": end - start + 1,
            }

        return summary

    def _extract_chapter_number(self, file_path: str) -> int:
        """Extract chapter number from file path."""
        path = Path(file_path)
        filename = path.stem

        # Try to extract number from filename
        import re

        match = re.search(r"(\d+)", filename)
        return int(match.group(1)) if match else 1
