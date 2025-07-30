"""Test Script for Multi-File Processing System.

This script tests the unified multi-file processing capabilities
for cross-chapter coreference analysis.

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


def test_multi_file_processing():
    """Test the multi-file processing system."""
    print("=" * 60)
    print("MULTI-FILE PROCESSING SYSTEM TEST")
    print("=" * 60)

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Initialize the processor
    print("\n1. Initializing MultiFileBatchProcessor...")
    processor = MultiFileBatchProcessor(enable_cross_chapter_resolution=True)

    # Test file discovery
    print("\n2. Testing file discovery...")
    try:
        # Try to discover files in the current directory
        chapter_files = processor.discover_chapter_files(".")
        print(f"   Discovered {len(chapter_files)} chapter files:")
        for i, file_path in enumerate(chapter_files, 1):
            print(f"   {i}. {file_path}")
    except Exception as e:
        print(f"   File discovery failed: {e}")
        print("   This is expected if no chapter files are in the current directory")

    # Test with specific files if they exist
    test_files = [
        "data/input/gotofiles/2.tsv",
        "data/input/gotofiles/later/1.tsv",
        "data/input/gotofiles/later/3.tsv",
        "data/input/gotofiles/later/4.tsv",
    ]

    existing_files = [f for f in test_files if Path(f).exists()]

    if existing_files:
        print(f"\n3. Testing with existing files ({len(existing_files)} found)...")

        # Test processing summary
        print("\n4. Testing processing summary...")
        try:
            summary = processor.get_processing_summary()
            print("   Processing summary:")
            for key, value in summary.items():
                print(f"   - {key}: {value}")
        except Exception as e:
            print(f"   Summary generation failed: {e}")

        # Test actual processing with first available file
        print(f"\n5. Testing actual processing with: {existing_files[0]}")
        try:
            result = processor.process_files(existing_files[0])

            if result.success:
                print("   ✓ Processing completed successfully!")
                print(f"   - Total relationships: {len(result.unified_relationships)}")
                print(f"   - Chapters processed: {len(result.chapter_info)}")
                print(f"   - Cross-chapter chains: {len(result.cross_chapter_chains)}")
                print(f"   - Processing time: {result.processing_time:.2f}s")

                # Show chapter info
                print("\n   Chapter Information:")
                for info in result.chapter_info:
                    print(
                        f"   - Chapter {info.chapter_number}: "
                        f"{info.relationships_count} relationships"
                    )
                    print(
                        f"     Format: {info.format_type}, "
                        f"Compatibility: {info.compatibility_score:.2f}"
                    )

            else:
                print(f"   ✗ Processing failed: {result.error_message}")

        except Exception as e:
            print(f"   Processing failed with exception: {e}")
            import traceback

            traceback.print_exc()

    else:
        print("\n3. No test files found - skipping processing test")
        print("   Expected files:")
        for file_path in test_files:
            print(f"   - {file_path}")

    print("\n" + "=" * 60)
    print("MULTI-FILE PROCESSING TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    test_multi_file_processing()
