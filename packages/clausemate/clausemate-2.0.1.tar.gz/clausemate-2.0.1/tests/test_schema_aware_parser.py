#!/usr/bin/env python3
"""Test script for the schema-aware adaptive parser."""

import logging

from src.parsers.adaptive_tsv_parser import AdaptiveTSVParser
from src.parsers.base import BaseTokenProcessor

# Set up logging
logging.basicConfig(level=logging.INFO)


class TestTokenProcessor(BaseTokenProcessor):
    """Simple test processor."""

    def validate_token(self, token):
        return True

    def enrich_token(self, token, context):
        return token


def test_schema_aware_parsing():
    """Test the schema-aware parsing with different files."""
    files_to_test = [
        "data/input/gotofiles/2.tsv",
        "data/input/gotofiles/later/1.tsv",
        "data/input/gotofiles/later/3.tsv",
        "data/input/gotofiles/later/4.tsv",
    ]

    processor = TestTokenProcessor()
    parser = AdaptiveTSVParser(processor)

    for file_path in files_to_test:
        print(f"\n=== Testing schema-aware parsing: {file_path} ===")

        try:
            # Parse the file
            sentences = parser.parse_file(file_path)

            print(f"Successfully parsed {len(sentences)} sentences")

            # Show format info
            format_info = parser.get_format_info()
            if format_info:
                print(
                    f"Format: {format_info.format_type} ({format_info.total_columns} columns)"
                )
                print(f"Compatibility: {format_info.compatibility_score:.2f}")

            # Show column mapping info
            if parser.current_column_mapping:
                print("Column mapping:")
                print(
                    f"  Coreference link: {parser.current_column_mapping.coreference_link}"
                )
                print(
                    f"  Coreference type: {parser.current_column_mapping.coreference_type}"
                )

            # Show annotation schema info
            if parser.current_annotation_schema:
                print("Annotation schema:")
                print(
                    f"  Total columns: {parser.current_annotation_schema.total_columns}"
                )

                # Check for morphological features
                prontype_col = parser.preamble_parser.get_pronoun_type_column()
                if prontype_col:
                    print(f"  Pronoun type column: {prontype_col}")
                else:
                    print("  No pronoun type column found")

            # Count coreference relationships
            total_coref_links = 0
            for _sentence_id, tokens in sentences.items():
                for token in tokens:
                    if token.coreference_link:
                        total_coref_links += 1

            print(f"Total coreference links found: {total_coref_links}")

        except Exception as e:
            print(f"Error: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    test_schema_aware_parsing()
