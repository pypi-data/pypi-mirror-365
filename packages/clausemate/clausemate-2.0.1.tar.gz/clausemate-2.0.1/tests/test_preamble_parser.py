#!/usr/bin/env python3
"""Test script for the preamble parser."""

from src.parsers.preamble_parser import PreambleParser, extract_preamble_from_file


def test_preamble_parser():
    """Test the preamble parser with different TSV files."""
    files_to_test = [
        "data/input/gotofiles/2.tsv",
        "data/input/gotofiles/later/1.tsv",
        "data/input/gotofiles/later/3.tsv",
        "data/input/gotofiles/later/4.tsv",
    ]

    parser = PreambleParser()

    for file_path in files_to_test:
        print(f"\n=== Testing {file_path} ===")

        try:
            # Extract preamble
            preamble_lines = extract_preamble_from_file(file_path)
            print(f"Preamble lines: {len(preamble_lines)}")

            # Parse schema
            schema = parser.parse_preamble_lines(preamble_lines)
            print(f"Total columns: {schema.total_columns}")

            # Get coreference columns
            coref_columns = parser.get_coreference_columns()
            print(f"Coreference columns: {coref_columns}")

            # Get morphological columns
            morph_columns = parser.get_morphological_columns()
            print(f"Morphological columns: {len(morph_columns)}")

            # Get specific columns
            prontype_col = parser.get_pronoun_type_column()
            coref_link_col = parser.get_coreference_link_column()
            coref_type_col = parser.get_coreference_type_column()

            print(f"Pronoun type column: {prontype_col}")
            print(f"Coreference link column: {coref_link_col}")
            print(f"Coreference type column: {coref_type_col}")

        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    test_preamble_parser()
