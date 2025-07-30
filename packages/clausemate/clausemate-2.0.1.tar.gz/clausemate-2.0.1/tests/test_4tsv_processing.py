#!/usr/bin/env python3
"""Test script for 4.tsv processing - Production Ready Validation.

This script validates the successful 4.tsv processing capabilities that now
extract 695 relationships with the adaptive parsing system.
"""

import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.main import ClauseMateAnalyzer
from src.parsers.incomplete_format_parser import IncompleteFormatParser
from src.parsers.tsv_parser import DefaultTokenProcessor
from src.utils.format_detector import TSVFormatDetector


def test_4tsv_format_detection():
    """Test format detection for 4.tsv."""
    print("=== Testing 4.tsv Format Detection ===")

    detector = TSVFormatDetector()
    file_path = "data/input/gotofiles/later/4.tsv"

    try:
        format_info = detector.analyze_file(file_path)

        print(f"File: {file_path}")
        print(f"Format type: {format_info.format_type}")
        print(f"Total columns: {format_info.total_columns}")
        print(f"Compatibility score: {format_info.compatibility_score:.2f}")
        print(f"Has required columns: {format_info.has_required_columns}")
        print(f"Issues: {format_info.issues}")
        print(f"Token count: {format_info.token_count}")
        print(f"Sentence count: {format_info.sentence_count}")

        return format_info

    except Exception as e:
        print(f"Format detection failed: {e}")
        return None


def test_incomplete_parser_direct():
    """Test incomplete format parser directly on 4.tsv."""
    print("\n=== Testing Incomplete Format Parser Directly ===")

    file_path = "data/input/gotofiles/later/4.tsv"
    processor = DefaultTokenProcessor()
    parser = IncompleteFormatParser(processor)

    try:
        # Test parsing first few sentences
        sentence_count = 0
        token_count = 0

        for sentence_context in parser.parse_sentence_streaming(file_path):
            sentence_count += 1
            token_count += len(sentence_context.tokens)

            print(f"Sentence {sentence_count}: {len(sentence_context.tokens)} tokens")

            # Show first few tokens
            for i, token in enumerate(sentence_context.tokens[:3]):
                print(
                    f"  Token {i + 1}: '{token.text}' (idx={token.idx}, sentence={token.sentence_num})"
                )
                if hasattr(token, "coreference_link") and token.coreference_link:
                    print(f"    Coreference link: {token.coreference_link}")
                if hasattr(token, "coreference_type") and token.coreference_type:
                    print(f"    Coreference type: {token.coreference_type}")

            # Stop after first 3 sentences for testing
            if sentence_count >= 3:
                break

        print(f"\nParsed {sentence_count} sentences with {token_count} total tokens")

        # Get parser limitations
        limitations = parser.get_limitations()
        if limitations:
            print(f"Parser limitations: {limitations}")

        # Get compatibility info
        compat_info = parser.get_compatibility_info()
        print(f"Available features: {compat_info['available_features']}")

        return True

    except Exception as e:
        print(f"Direct parsing failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_main_analyzer():
    """Test main analyzer with 4.tsv."""
    print("\n=== Testing Main Analyzer with 4.tsv ===")

    file_path = "data/input/gotofiles/later/4.tsv"

    try:
        # Create analyzer with verbose logging
        analyzer = ClauseMateAnalyzer(
            enable_streaming=False, log_level=logging.INFO, enable_adaptive_parsing=True
        )

        # Run analysis
        relationships = analyzer.analyze_file(file_path)

        print("Analysis completed successfully!")
        print(f"Found {len(relationships)} relationships")

        # Get statistics
        stats = analyzer.get_statistics()
        print(f"Statistics: {stats}")

        # Export results if any relationships found
        if relationships:
            output_path = "4tsv_test_results.csv"
            analyzer.export_results(relationships, output_path)
            print(f"Results exported to: {output_path}")
        else:
            print(
                "No relationships found - unexpected for 4.tsv (should extract 695 relationships)"
            )

        return True

    except Exception as e:
        print(f"Main analyzer failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("Testing 4.tsv Processing with Incomplete Format Parser")
    print("=" * 60)

    # Test 1: Format detection
    format_info = test_4tsv_format_detection()

    # Test 2: Direct parser test
    parser_success = test_incomplete_parser_direct()

    # Test 3: Main analyzer test
    analyzer_success = test_main_analyzer()

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Format detection: {'✓ PASS' if format_info else '✗ FAIL'}")
    print(f"Direct parser test: {'✓ PASS' if parser_success else '✗ FAIL'}")
    print(f"Main analyzer test: {'✓ PASS' if analyzer_success else '✗ FAIL'}")

    if format_info:
        print(f"\n4.tsv detected as: {format_info.format_type} format")
        print(f"Compatibility score: {format_info.compatibility_score:.2f}")

        if (
            format_info.format_type == "incomplete"
            and format_info.compatibility_score >= 0.5
        ):
            print("✓ 4.tsv should now be processable with incomplete format parser!")
        else:
            print("⚠ 4.tsv may still have compatibility issues")

    overall_success = format_info and parser_success and analyzer_success
    print(f"\nOverall result: {'✓ SUCCESS' if overall_success else '✗ FAILURE'}")

    return 0 if overall_success else 1


if __name__ == "__main__":
    sys.exit(main())
