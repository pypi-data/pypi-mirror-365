"""Multi-File Processing Module for Cross-Chapter Analysis.

This module provides unified processing capabilities for multiple related TSV files
representing sequential book chapters, with cross-chapter coreference resolution.

Author: Kilo Code
Version: 3.0 - Phase 3.1 Implementation
Date: 2025-07-28
"""

from .cross_file_coreference_resolver import CrossFileCoreferenceResolver
from .multi_file_batch_processor import (
    ChapterInfo,
    MultiFileBatchProcessor,
    MultiFileProcessingResult,
)
from .unified_relationship_model import UnifiedClauseMateRelationship
from .unified_sentence_manager import UnifiedSentenceManager

__all__ = [
    "MultiFileBatchProcessor",
    "ChapterInfo",
    "MultiFileProcessingResult",
    "UnifiedSentenceManager",
    "CrossFileCoreferenceResolver",
    "UnifiedClauseMateRelationship",
]
