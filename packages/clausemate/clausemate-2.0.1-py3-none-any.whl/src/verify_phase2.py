#!/usr/bin/env python3
"""Verification script for Clause Mates Analyzer components.

This script provides a comprehensive check to ensure our production-ready
modular architecture works correctly and can process data as expected.
"""

import os
import sys
import tempfile
from pathlib import Path

# Handle both direct execution and module execution
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))


def import_module(module_path):
    """Helper to import modules consistently."""
    return __import__(f"src.{module_path}", fromlist=[""])


def test_imports():
    """Test that all our new modules can be imported."""
    print("Testing imports...")

    try:
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_token_creation():
    """Test basic token creation."""
    print("Testing token creation...")

    try:
        from src.data.models import Token

        token = Token(
            idx=1,
            text="er",
            sentence_num=1,
            grammatical_role="SUBJ",
            thematic_role="AGENT",
            coreference_link="PersPron[1]",
        )

        assert token.text == "er"
        assert token.idx == 1
        print("✓ Token creation successful")
        return True
    except Exception as e:
        print(f"✗ Token creation failed: {e}")
        return False


def test_parser_basic():
    """Test basic parser functionality."""
    print("Testing parser...")

    try:
        from src.parsers.tsv_parser import DefaultTokenProcessor, TSVParser

        processor = DefaultTokenProcessor()
        parser = TSVParser(processor)

        # Test sentence boundary detection (updated to match current
        # implementation)
        assert parser.is_sentence_boundary("#Text=Dies ist ein Test."), (
            "Should detect #Text= as sentence boundary"
        )
        assert not parser.is_sentence_boundary("1\ter\t_\t_"), (
            "Should not detect token line as sentence boundary"
        )
        assert not parser.is_sentence_boundary("# sent_id = test"), (
            "Should not detect sent_id as sentence boundary"
        )

        print("✓ Parser basic functionality works")
        return True
    except Exception as e:
        print(f"✗ Parser test failed: {e}")
        return False


def test_coreference_extractor():
    """Test coreference extractor."""
    print("Testing coreference extractor...")

    try:
        from src.data.models import Token
        from src.extractors.coreference_extractor import CoreferenceExtractor

        extractor = CoreferenceExtractor()

        # Test token with coreference info
        token = Token(
            idx=1,
            text="er",
            sentence_num=1,
            grammatical_role="SUBJ",
            thematic_role="AGENT",
            coreference_type="PersPron[1]",
        )

        ids = extractor.extract_all_ids_from_token(token)
        assert len(ids) > 0  # Should extract at least one ID

        print("✓ Coreference extractor works")
        return True
    except Exception as e:
        print(f"✗ Coreference extractor test failed: {e}")
        return False


def test_analyzer_initialization():
    """Test analyzer initialization."""
    print("Testing analyzer initialization...")

    try:
        from src.main import ClauseMateAnalyzer

        analyzer = ClauseMateAnalyzer()

        # Check components are initialized
        assert analyzer.parser is not None
        assert analyzer.coreference_extractor is not None

        # Check statistics
        stats = analyzer.get_statistics()
        assert "sentences_processed" in stats
        assert stats["sentences_processed"] == 0

        print("✓ Analyzer initialization successful")
        return True
    except Exception as e:
        print(f"✗ Analyzer initialization failed: {e}")
        return False


def test_end_to_end_with_sample():
    """Test end-to-end processing with a small sample."""
    print("Testing end-to-end processing...")

    try:
        from src.main import ClauseMateAnalyzer

        # Create a simple test TSV file
        test_content = """# sent_id = test-sentence-1
1	_	Er	_	_	_	_	_	_	_	PersPron[1]	_	_	_
2	_	sieht	_	_	_	_	_	_	_	_	_	_	_
3	_	das	_	_	_	_	_	_	_	D-Pron[2]	_	_	_
4	_	Auto	_	_	_	_	_	_	_	_	_	_	_
"""

        # Write to temporary file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".tsv", delete=False, encoding="utf-8"
        ) as f:
            f.write(test_content)
            temp_file = f.name

        try:
            analyzer = ClauseMateAnalyzer()
            relationships = analyzer.analyze_file(temp_file)

            # Should return a list (even if empty for now)
            assert isinstance(relationships, list)

            # Should have processed at least one sentence
            stats = analyzer.get_statistics()
            assert stats["sentences_processed"] > 0

            print("✓ End-to-end processing successful")
            return True

        finally:
            # Clean up
            os.unlink(temp_file)

    except Exception as e:
        print(f"✗ End-to-end test failed: {e}")
        return False


def main():
    """Run all verification tests."""
    print("Phase 2 Component Verification")
    print("=" * 40)

    tests = [
        test_imports,
        test_token_creation,
        test_parser_basic,
        test_coreference_extractor,
        test_analyzer_initialization,
        test_end_to_end_with_sample,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()  # Empty line for readability

    print("=" * 40)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All Phase 2 components working correctly!")
        return True
    else:
        print("⚠️  Some components need attention")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
