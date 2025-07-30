"""Main orchestrator for the clause mates analyzer.

This module provides the primary interface for running the analysis pipeline,
coordinating between parsers, extractors, and analyzers in a clean, modular way.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List

# Import dependencies - handle both module and script execution
try:
    # When run as module (python -m src.main)
    from .config import FilePaths
    from .exceptions import ClauseMateExtractionError
except ImportError:
    # When run as script (python src/main.py)
    import sys

    sys.path.append(str(Path(__file__).parent.parent))
    from src.config import FilePaths
    from src.exceptions import ClauseMateExtractionError

# Import from the modular components
try:
    # Try relative imports first (when run as module)
    from .data.models import ClauseMateRelationship
    from .extractors.coreference_extractor import CoreferenceExtractor
    from .extractors.phrase_extractor import PhraseExtractor
    from .extractors.pronoun_extractor import PronounExtractor
    from .extractors.relationship_extractor import RelationshipExtractor
    from .parsers.adaptive_tsv_parser import AdaptiveTSVParser
    from .parsers.incomplete_format_parser import IncompleteFormatParser
    from .parsers.tsv_parser import DefaultTokenProcessor, TSVParser
    from .utils.format_detector import TSVFormatDetector
except ImportError:
    # Fall back to absolute imports (when run directly)
    import sys

    sys.path.append(str(Path(__file__).parent.parent))

    from src.data.models import ClauseMateRelationship
    from src.extractors.coreference_extractor import CoreferenceExtractor
    from src.extractors.phrase_extractor import PhraseExtractor
    from src.extractors.pronoun_extractor import PronounExtractor
    from src.extractors.relationship_extractor import RelationshipExtractor
    from src.parsers.adaptive_tsv_parser import AdaptiveTSVParser
    from src.parsers.incomplete_format_parser import IncompleteFormatParser
    from src.parsers.tsv_parser import DefaultTokenProcessor, TSVParser
    from src.utils.format_detector import TSVFormatDetector


class ClauseMateAnalyzer:
    """Main analyzer class that orchestrates the complete processing pipeline.

    This class provides a clean, simple interface for clause mate analysis
    while maintaining the modular architecture underneath.
    """

    def __init__(
        self,
        enable_streaming: bool = False,
        log_level: int = logging.INFO,
        enable_adaptive_parsing: bool = True,
    ):
        """Initialize the clause mate analyzer.

        Args:
            enable_streaming: Whether to use streaming parsing for large files
            log_level: Logging level for the analyzer
            enable_adaptive_parsing: Whether to use adaptive parsing for different file formats
        """
        # Set up logging
        logging.basicConfig(
            level=log_level, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.token_processor = DefaultTokenProcessor()
        self.enable_adaptive_parsing = enable_adaptive_parsing

        # Initialize parsers - adaptive parser as primary, incomplete as fallback, legacy as last resort
        if enable_adaptive_parsing:
            self.adaptive_parser = AdaptiveTSVParser(self.token_processor)
            self.incomplete_parser = IncompleteFormatParser(self.token_processor)
            self.format_detector = TSVFormatDetector()
            self.logger.info("Adaptive parsing enabled - will auto-detect file formats")

        self.legacy_parser = TSVParser(self.token_processor)
        self.parser = (
            self.adaptive_parser if enable_adaptive_parsing else self.legacy_parser
        )

        self.coreference_extractor = CoreferenceExtractor()
        self.pronoun_extractor = PronounExtractor()
        self.phrase_extractor = PhraseExtractor()
        self.relationship_extractor = RelationshipExtractor()

        self.enable_streaming = enable_streaming

        # Statistics
        self.stats = {
            "sentences_processed": 0,
            "tokens_processed": 0,
            "relationships_found": 0,
            "coreference_chains_found": 0,
            "critical_pronouns_found": 0,
            "phrases_found": 0,
        }

    def analyze_file(self, file_path: str) -> List[ClauseMateRelationship]:
        """Analyze a TSV file and extract clause mate relationships.

        Args:
            file_path: Path to the TSV file to analyze

        Returns:
            List of clause mate relationships found

        Raises:
            ClauseMateExtractionError: If analysis fails
        """
        self.logger.info(f"Starting analysis of file: {file_path}")

        try:
            # Perform format detection if adaptive parsing is enabled
            if self.enable_adaptive_parsing:
                self._detect_and_configure_format(file_path)

            if self.enable_streaming:
                return self._analyze_streaming(file_path)
            else:
                return self._analyze_complete(file_path)

        except Exception as e:
            self.logger.error(f"Analysis failed: {str(e)}")
            raise ClauseMateExtractionError(
                f"Failed to analyze file {file_path}: {str(e)}"
            ) from e

    def _analyze_complete(self, file_path: str) -> List[ClauseMateRelationship]:
        """Analyze file by loading all sentences into memory.

        This approach prioritizes simplicity and maintainability over memory efficiency.
        """
        self.logger.info("Using complete file analysis (prioritizing maintainability)")

        # Parse all sentences
        contexts = list(self.parser.parse_sentence_streaming(file_path))
        self.stats["sentences_processed"] = len(contexts)
        self.stats["tokens_processed"] = sum(len(ctx.tokens) for ctx in contexts)

        # Create sentence contexts
        for context in contexts:
            # Extract sentence number from ID
            sentence_num = self._extract_sentence_number(context.sentence_id)

            context.sentence_num = sentence_num

        # Extract coreference information
        all_chains = self.coreference_extractor.extract_coreference_chains(contexts)
        self.stats["coreference_chains_found"] = len(all_chains)

        # Extract pronouns and phrases for each context
        total_pronouns = 0
        total_phrases = 0
        all_relationships = []

        for context in contexts:
            # Extract pronouns
            pronoun_result = self.pronoun_extractor.extract(context)
            total_pronouns += len(pronoun_result.pronouns)

            # Extract phrases
            phrase_result = self.phrase_extractor.extract(context)
            total_phrases += len(phrase_result.phrases)

            # Extract relationships (with cross-sentence context)
            if context.has_critical_pronouns and context.has_coreference_phrases:
                relationship_result = self.relationship_extractor.extract(
                    context, all_contexts=contexts
                )
                all_relationships.extend(relationship_result.relationships)

        self.stats["critical_pronouns_found"] = total_pronouns
        self.stats["phrases_found"] = total_phrases
        self.stats["relationships_found"] = len(all_relationships)

        # Return the relationships we found
        relationships = all_relationships

        self.logger.info(f"Analysis complete. Statistics: {self.stats}")
        return relationships

    def _analyze_streaming(self, file_path: str) -> List[ClauseMateRelationship]:
        """Analyze file using streaming for memory efficiency.

        This approach processes sentences one at a time to handle large files.
        """
        self.logger.info("Using streaming analysis (memory efficient)")

        all_relationships = []
        contexts = []

        # Process sentences one by one
        for context in self.parser.parse_sentence_streaming(file_path):
            contexts.append(context)
            self.stats["sentences_processed"] += 1
            self.stats["tokens_processed"] += len(context.tokens)

            # Extract coreference information for this sentence
            self.coreference_extractor.extract(context)

            # Process relationships (placeholder for now)
            # relationships = self._extract_relationships(context)
            # all_relationships.extend(relationships)

        # Extract cross-sentence coreference chains
        all_chains = self.coreference_extractor.extract_coreference_chains(contexts)
        self.stats["coreference_chains_found"] = len(all_chains)

        self.stats["relationships_found"] = len(all_relationships)
        self.logger.info(f"Streaming analysis complete. Statistics: {self.stats}")
        return all_relationships

    def export_results(
        self, relationships: List[ClauseMateRelationship], output_path: str
    ) -> None:
        """Export analysis results to a CSV file.

        Args:
            relationships: List of relationships to export
            output_path: Path to the output CSV file
        """
        import pandas as pd

        if not relationships:
            self.logger.warning("No relationships to export")
            return

        try:
            # Create timestamped output directory if needed
            output_path = self._ensure_timestamped_output_path(output_path)

            # Convert relationships to dictionaries
            data = [rel.to_dict() for rel in relationships]

            # Create DataFrame and export
            df = pd.DataFrame(data)

            # Convert coreference number columns to proper integer type
            # Use pandas nullable integer type to handle NaN values correctly
            integer_columns = [
                "pronoun_coref_base_num",
                "pronoun_coref_occurrence_num",
                "clause_mate_coref_base_num",
                "clause_mate_coref_occurrence_num",
                "pronoun_coref_link_base_num",
                "pronoun_coref_link_occurrence_num",
                "pronoun_inanimate_coref_link_base_num",
                "pronoun_inanimate_coref_link_occurrence_num",
            ]

            for col in integer_columns:
                if col in df.columns:
                    df[col] = df[col].astype("Int64")  # Nullable integer type

            df.to_csv(output_path, index=False)

            self.logger.info(f"Results exported to: {output_path}")
            self.logger.info(f"Exported {len(relationships)} relationships")

        except Exception as e:
            self.logger.error(f"Export failed: {str(e)}")
            raise ClauseMateExtractionError(
                f"Failed to export results: {str(e)}"
            ) from e

    def _ensure_timestamped_output_path(self, output_path: str) -> str:
        """Ensure output path uses timestamped directory structure.

        Args:
            output_path: Original output path

        Returns:
            Modified output path with timestamped directory, or original path if it's a simple filename
        """
        from datetime import datetime
        from pathlib import Path

        output_path_obj = Path(output_path)

        # Check if path already contains a timestamped directory
        import re

        if any(re.match(r"\d{8}_\d{6}", str(part)) for part in output_path_obj.parts):
            # Already has timestamp, return as-is
            return output_path

        # If it's a simple filename (no directory components), respect it for reproducibility tests
        if len(output_path_obj.parts) == 1 and not output_path_obj.is_absolute():
            self.logger.info(f"Using simple filename for output: {output_path}")
            return output_path

        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create timestamped directory under data/output/
        data_output_dir = Path("data/output")
        timestamped_dir = data_output_dir / timestamp

        # Ensure directory exists
        timestamped_dir.mkdir(parents=True, exist_ok=True)

        # Return new path
        new_path = timestamped_dir / output_path_obj.name

        self.logger.info(f"Created timestamped output directory: {timestamped_dir}")
        return str(new_path)

    def get_statistics(self) -> Dict[str, Any]:
        """Get analysis statistics.

        Returns:
            Dictionary containing analysis statistics
        """
        return self.stats.copy()

    def _detect_and_configure_format(self, file_path: str) -> None:
        """Detect file format and configure the appropriate parser.

        Args:
            file_path: Path to the file to analyze
        """
        try:
            # Analyze file format
            format_info = self.format_detector.analyze_file(file_path)

            self.logger.info("File format analysis:")
            self.logger.info(f"  - Columns detected: {format_info.total_columns}")
            self.logger.info(
                f"  - Compatibility score: {format_info.compatibility_score:.2f}"
            )
            self.logger.info(f"  - Format type: {format_info.format_type}")

            # Update statistics with format information (extend stats dict to handle mixed types)
            if not hasattr(self, "_extended_stats"):
                self._extended_stats = {}
            self._extended_stats["file_format_detected"] = format_info.format_type
            self._extended_stats["compatibility_score"] = (
                format_info.compatibility_score
            )
            self._extended_stats["column_count"] = format_info.total_columns

            # Choose parser based on compatibility and format type
            if format_info.compatibility_score >= 0.7:
                self.logger.info("Using adaptive parser for high compatibility file")
                self.parser = self.adaptive_parser
            elif (
                format_info.format_type == "incomplete"
                and format_info.compatibility_score >= 0.5
            ):
                self.logger.info(
                    f"Using incomplete format parser for {format_info.format_type} format "
                    f"(compatibility: {format_info.compatibility_score:.2f})"
                )
                self.parser = self.incomplete_parser
            else:
                self.logger.warning(
                    f"Low compatibility score ({format_info.compatibility_score:.2f}), "
                    f"falling back to legacy parser"
                )
                self.parser = self.legacy_parser

            # Log any issues found
            if format_info.issues:
                self.logger.warning("Format issues detected:")
                for issue in format_info.issues:
                    self.logger.warning(f"  - {issue}")

        except Exception as e:
            self.logger.warning(f"Format detection failed: {e}, using legacy parser")
            self.parser = self.legacy_parser

    def _extract_sentence_number(self, sentence_id: str) -> int:
        """Extract sentence number from sentence ID."""
        import re

        match = re.search(r"(\d+)", sentence_id)
        return int(match.group(1)) if match else 1


def main():
    """Main entry point for the application.

    This function provides a simple command-line interface for the analyzer.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Clause Mate Analyzer - Production Ready v2.1"
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        default=FilePaths.INPUT_FILE,
        help="Input TSV file path",
    )
    parser.add_argument(
        "-o", "--output", default=FilePaths.OUTPUT_FILE, help="Output CSV file path"
    )
    parser.add_argument(
        "--streaming",
        action="store_true",
        help="Use streaming processing for large files",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )
    parser.add_argument(
        "--disable-adaptive",
        action="store_true",
        help="Disable adaptive parsing (use legacy parser only)",
    )

    args = parser.parse_args()

    # Set logging level
    log_level = logging.DEBUG if args.verbose else logging.INFO

    # Create analyzer
    analyzer = ClauseMateAnalyzer(
        enable_streaming=args.streaming,
        log_level=log_level,
        enable_adaptive_parsing=not args.disable_adaptive,
    )

    try:
        # Run analysis
        relationships = analyzer.analyze_file(args.input_file)

        # Export results
        analyzer.export_results(relationships, args.output)

        # Show statistics
        stats = analyzer.get_statistics()
        print("\nAnalysis Summary:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

    except ClauseMateExtractionError as e:
        print(f"Error: {e}")
        return 1
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
