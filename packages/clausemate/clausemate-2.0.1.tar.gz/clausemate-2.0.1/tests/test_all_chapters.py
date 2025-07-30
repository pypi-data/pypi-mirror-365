"""Test Script for All 4 Chapters Multi-File Processing.

This script tests the unified processing of all 4 chapter files together
to validate cross-chapter coreference resolution.

Author: Kilo Code
Version: 3.0 - Phase 3.1 Implementation
Date: 2025-07-28
"""

import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.multi_file import MultiFileBatchProcessor


def test_all_chapters():
    """Test processing all 4 chapters together."""
    print("=" * 70)
    print("ALL 4 CHAPTERS UNIFIED PROCESSING TEST")
    print("=" * 70)

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Initialize the processor
    print("\n1. Initializing MultiFileBatchProcessor for all chapters...")
    processor = MultiFileBatchProcessor(enable_cross_chapter_resolution=True)

    # Test with directory to process all files
    print("\n2. Processing all chapters from data/input/gotofiles directory...")
    try:
        result = processor.process_files("data/input/gotofiles")

        if result.success:
            print("   ✓ ALL CHAPTERS PROCESSING COMPLETED SUCCESSFULLY!")
            print(
                f"   - Total unified relationships: {len(result.unified_relationships)}"
            )
            print(f"   - Chapters processed: {len(result.chapter_info)}")
            print(
                f"   - Cross-chapter chains resolved: {len(result.cross_chapter_chains)}"
            )
            print(f"   - Total processing time: {result.processing_time:.2f}s")

            print("\n   DETAILED CHAPTER BREAKDOWN:")
            total_relationships = 0
            for info in result.chapter_info:
                print(
                    f"   - Chapter {info.chapter_number}: {info.relationships_count} relationships"
                )
                print(f"     File: {info.file_path}")
                print(f"     Format: {info.format_type} ({info.columns} columns)")
                print(f"     Compatibility: {info.compatibility_score:.2f}")
                sentence_range = f"{info.sentence_range[0]}-{info.sentence_range[1]}"
                print(f"     Sentence range: {sentence_range}")
                total_relationships += info.relationships_count
                print()

            print("   SUMMARY STATISTICS:")
            print(f"   - Individual chapter relationships: {total_relationships}")
            print(
                "   - Unified relationships created: "
                f"{len(result.unified_relationships)}"
            )
            print(f"   - Cross-chapter chains: {len(result.cross_chapter_chains)}")

            if result.cross_chapter_chains:
                print("\n   CROSS-CHAPTER CHAINS FOUND:")
                for chain_id, entities in result.cross_chapter_chains.items():
                    print(f"   - {chain_id}: {len(entities)} entities")
                    entity_list = ", ".join(entities[:5])
                    if len(entities) > 5:
                        entity_list += "..."
                    print(f"     Entities: {entity_list}")

            # Test unified relationship metadata
            if result.unified_relationships:
                sample_rel = result.unified_relationships[0]
                print("\n   SAMPLE UNIFIED RELATIONSHIP:")
                print(f"   - Source file: {sample_rel.source_file}")
                print(f"   - Chapter number: {sample_rel.chapter_number}")
                print(f"   - Global sentence ID: {sample_rel.global_sentence_id}")
                print(f"   - Cross-chapter: {sample_rel.cross_chapter_relationship}")
                print(f"   - Pronoun: {sample_rel.pronoun.text}")
                print(f"   - Clause mate: {sample_rel.clause_mate.text}")

        else:
            print(f"   ✗ Processing failed: {result.error_message}")

    except Exception as e:
        print(f"   ✗ Processing failed with exception: {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 70)
    print("ALL CHAPTERS PROCESSING TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    test_all_chapters()
