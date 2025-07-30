"""Adaptive TSV parser that handles multiple column formats dynamically.

This module provides an enhanced TSV parser that can automatically detect
and adapt to different column structures while maintaining compatibility
with the clause mates analysis system.
"""

import csv
import logging
from collections.abc import Iterator
from typing import Any

from src.data.models import SentenceContext, Token
from src.parsers.base import BaseParser, BaseTokenProcessor
from src.parsers.preamble_parser import (
    AnnotationSchema,
    PreambleParser,
    extract_preamble_from_file,
)
from src.utils.format_detector import ColumnMapping, TSVFormatDetector, TSVFormatInfo

from ..exceptions import FileProcessingError, ParseError

logger = logging.getLogger(__name__)


class AdaptiveTSVParser(BaseParser):
    """Enhanced TSV parser that adapts to different column formats.

    This parser automatically detects the format of TSV files and adjusts
    its parsing strategy accordingly, supporting both standard (14-15 columns)
    and extended (30+ columns) formats.
    """

    def __init__(self, processor: BaseTokenProcessor):
        """Initialize the adaptive TSV parser.

        Args:
            processor: Token processor for validation and enrichment
        """
        self.processor = processor
        self.format_detector = TSVFormatDetector()
        self.preamble_parser = PreambleParser()
        self.current_format_info: TSVFormatInfo | None = None
        self.current_column_mapping: ColumnMapping | None = None
        self.current_annotation_schema: AnnotationSchema | None = None

        # Import column mappings from config
        from ..config import TSVColumns

        self.default_columns = TSVColumns()

    def parse_file(self, file_path: str) -> dict[str, list[Token]]:
        """Parse a TSV file with automatic format detection.

        Args:
            file_path: Path to the TSV file to parse

        Returns:
            Dictionary mapping sentence IDs to lists of tokens

        Raises:
            FileProcessingError: If file cannot be read or format is incompatible
            ParseError: If file format is invalid
        """
        logger.info(f"Starting adaptive parsing of: {file_path}")

        # Detect format first
        self.current_format_info = self.format_detector.analyze_file(file_path)

        if self.current_format_info.compatibility_score < 0.5:
            raise FileProcessingError(
                f"File format incompatible: {file_path}\n"
                f"Compatibility score: {self.current_format_info.compatibility_score:.2f}\n"
                f"Issues: {', '.join(self.current_format_info.issues)}"
            )

        # Set up column mapping based on detected format
        self._setup_column_mapping()

        if not self.current_column_mapping:
            raise ParseError("Failed to set up column mapping")

        logger.info(
            f"Format detected: {self.current_format_info.format_type} "
            f"({self.current_format_info.total_columns} columns), "
            f"compatibility: {self.current_format_info.compatibility_score:.2f}"
        )

        sentences = {}

        try:
            for sentence_context in self.parse_sentence_streaming(file_path):
                sentences[sentence_context.sentence_id] = sentence_context.tokens
        except FileNotFoundError as e:
            raise FileProcessingError(f"File not found: {file_path}") from e
        except PermissionError as e:
            raise FileProcessingError(f"Permission denied: {file_path}") from e
        except Exception as e:
            raise FileProcessingError(
                f"Error reading file {file_path}: {str(e)}"
            ) from e

        logger.info(f"Successfully parsed {len(sentences)} sentences from {file_path}")
        return sentences

    def _initialize_for_file(self, file_path: str) -> None:
        """Initialize parser for a specific file (used for backward compatibility).

        Args:
            file_path: Path to the file to initialize for

        Raises:
            FileProcessingError: If format detection fails
            ParseError: If format is incompatible
        """
        try:
            # Detect format
            self.current_format_info = self.format_detector.analyze_file(file_path)

            if self.current_format_info.compatibility_score < 0.5:
                raise FileProcessingError(
                    f"File format incompatible: {file_path}\n"
                    f"Compatibility score: {self.current_format_info.compatibility_score:.2f}\n"
                    f"Issues: {', '.join(self.current_format_info.issues)}"
                )

            # Set up column mapping
            self._setup_column_mapping()

            if not self.current_column_mapping:
                raise ParseError("Failed to set up column mapping")

            logger.info(
                f"Auto-initialized for {self.current_format_info.format_type} format "
                f"({self.current_format_info.total_columns} columns), "
                f"compatibility: {self.current_format_info.compatibility_score:.2f}"
            )

        except Exception as e:
            logger.error(f"Failed to initialize parser for {file_path}: {e}")
            raise

    def _setup_column_mapping(self):
        """Set up column mapping based on detected format and preamble analysis."""
        if not self.current_format_info:
            raise ParseError("No format information available")

        # Try preamble-based parsing first
        try:
            file_path = self.current_format_info.file_path
            if file_path:
                preamble_lines = extract_preamble_from_file(file_path)
                self.current_annotation_schema = (
                    self.preamble_parser.parse_preamble_lines(preamble_lines)
                )

                # Create dynamic column mapping based on preamble
                self.current_column_mapping = self._create_dynamic_column_mapping()

                logger.info("Using preamble-based column mapping:")
                logger.info(
                    f"  Total columns: {self.current_annotation_schema.total_columns}"
                )
                logger.info(
                    f"  Coreference link: {self.current_column_mapping.coreference_link}"
                )
                logger.info(
                    f"  Coreference type: {self.current_column_mapping.coreference_type}"
                )

                # Check for morphological features
                prontype_col = self.preamble_parser.get_pronoun_type_column()
                if prontype_col:
                    logger.info(f"  Pronoun type column: {prontype_col}")

                return

        except Exception as e:
            logger.warning(
                f"Preamble-based parsing failed, falling back to standard mapping: {e}"
            )

        # Fallback to standard column mapping
        self.current_column_mapping = ColumnMapping()

        # Log the mapping being used
        logger.debug(
            f"Using standard column mapping for {self.current_format_info.format_type} format:"
        )
        logger.debug(f"  Token ID: {self.current_column_mapping.token_id}")
        logger.debug(f"  Token Text: {self.current_column_mapping.token_text}")
        logger.debug(
            f"  Coreference Link: {self.current_column_mapping.coreference_link}"
        )
        logger.debug(
            f"  Coreference Type: {self.current_column_mapping.coreference_type}"
        )

    def _create_dynamic_column_mapping(self) -> ColumnMapping:
        """Create column mapping based on preamble analysis."""
        if not self.current_annotation_schema:
            raise ParseError("No annotation schema available")

        # Get coreference column positions from preamble parser
        coref_link_col = self.preamble_parser.get_coreference_link_column()
        coref_type_col = self.preamble_parser.get_coreference_type_column()

        if coref_link_col is None or coref_type_col is None:
            raise ParseError("Could not find coreference columns in preamble")

        # Create mapping with dynamic positions
        # Note: WebAnno uses 1-based indexing in preamble but 0-based in arrays
        mapping = ColumnMapping()
        mapping.coreference_link = coref_link_col - 1  # Convert to 0-based
        mapping.coreference_type = coref_type_col - 1  # Convert to 0-based

        # Find inanimate coreference columns
        coref_columns = self.preamble_parser.get_coreference_columns()
        for annotation, column in coref_columns.items():
            if "CoreferenceInanimateLink" in annotation:
                if "referenceRelation" in annotation:
                    mapping.inanimate_coreference_link = column - 1
                elif "referenceType" in annotation:
                    mapping.inanimate_coreference_type = column - 1

        # Get grammatical and thematic role column positions from preamble parser
        grammatical_role_col = self.preamble_parser.get_grammatical_role_column()
        thematic_role_col = self.preamble_parser.get_thematic_role_column()

        if grammatical_role_col is not None:
            mapping.grammatical_role = grammatical_role_col - 1  # Convert to 0-based
            logger.info(
                f"  Grammatical role column: {grammatical_role_col} (index {mapping.grammatical_role})"
            )
        else:
            logger.warning(
                "Could not find grammatical role column in preamble, using default"
            )

        if thematic_role_col is not None:
            mapping.thematic_role = thematic_role_col - 1  # Convert to 0-based
            logger.info(
                f"  Thematic role column: {thematic_role_col} (index {mapping.thematic_role})"
            )
        else:
            logger.warning(
                "Could not find thematic role column in preamble, using default"
            )

        return mapping

    def parse_sentence_streaming(self, file_path: str) -> Iterator[SentenceContext]:
        """Parse a TSV file sentence by sentence with adaptive column handling.

        Args:
            file_path: Path to the TSV file to parse

        Yields:
            SentenceContext objects for each sentence

        Raises:
            FileProcessingError: If file cannot be processed
            ParseError: If file format is invalid
        """
        # Auto-initialize if not already done (for backward compatibility)
        if not self.current_format_info or not self.current_column_mapping:
            logger.info("Auto-initializing parser for streaming mode")
            self._initialize_for_file(file_path)

        current_tokens = []
        current_first_words = None
        current_sentence_num = None
        current_sentence_id = None
        pending_first_words = None
        first_token_texts = []

        try:
            with open(file_path, encoding="utf-8") as file:
                reader = csv.reader(file, delimiter="\t")
                for line_num, row in enumerate(reader, 1):
                    try:
                        if not row or (len(row) == 1 and not row[0].strip()):
                            continue

                        line_text = "\t".join(row)

                        # Handle sentence boundaries
                        if self.is_sentence_boundary(line_text):
                            # Yield previous sentence if we have tokens
                            if current_tokens and current_sentence_id is not None:
                                if not current_first_words and first_token_texts:
                                    current_first_words = "_".join(first_token_texts)

                                yield self._create_sentence_context(
                                    sentence_id=(
                                        str(current_sentence_num)
                                        if current_sentence_num is not None
                                        else "1"
                                    ),
                                    sentence_num=(
                                        current_sentence_num
                                        if current_sentence_num is not None
                                        else 1
                                    ),
                                    tokens=current_tokens,
                                    first_words=current_first_words or "",
                                )

                            # Prepare for next sentence
                            current_tokens = []
                            current_sentence_num = None
                            current_sentence_id = None
                            pending_first_words = self._extract_first_words(line_text)
                            current_first_words = None
                            first_token_texts = []
                            continue

                        # Skip other comment lines
                        if line_text.startswith("#"):
                            continue

                        # Validate column count with adaptive threshold based on format
                        min_required_columns = (
                            3  # Absolute minimum for basic token parsing
                        )

                        if self.current_format_info:
                            if self.current_format_info.format_type == "incomplete":
                                # For incomplete formats, use a lower threshold
                                min_required_columns = max(
                                    self.current_column_mapping.coreference_type + 1
                                    if self.current_column_mapping
                                    else 10,
                                    min_required_columns,
                                )
                            else:
                                # For complete formats, use standard requirements
                                min_required_columns = max(
                                    self.current_column_mapping.inanimate_coreference_type
                                    + 1
                                    if self.current_column_mapping
                                    else 14,
                                    min_required_columns,
                                )

                        # Only warn if significantly below expected columns for the format
                        if len(row) < min_required_columns:
                            # Suppress warnings for incomplete formats that are working correctly
                            if not (
                                self.current_format_info
                                and self.current_format_info.format_type == "incomplete"
                                and len(row) >= 12
                            ):  # 12+ columns for incomplete is acceptable
                                logger.warning(
                                    f"Line {line_num}: Expected at least "
                                    f"{min_required_columns} columns, got {len(row)}. "
                                    f"Attempting to parse with available columns."
                                )

                        # Parse token with adaptive column handling
                        token = self.parse_token_line_adaptive(line_text, line_num)

                        # Handle first token of sentence
                        if current_sentence_num is None:
                            current_sentence_num = token.sentence_num
                            current_sentence_id = str(token.sentence_num)
                            if pending_first_words is not None:
                                current_first_words = pending_first_words
                                pending_first_words = None
                            else:
                                first_token_texts = []

                        # Collect first three token texts if needed
                        if current_first_words is None and len(first_token_texts) < 3:
                            first_token_texts.append(token.text)

                        # Validate and add token
                        if self.processor.validate_token(token):
                            current_tokens.append(token)

                    except ParseError:
                        raise
                    except Exception as e:
                        logger.error(f"Error processing line {line_num}: {str(e)}")
                        # Continue processing instead of failing completely
                        continue

                # Yield last sentence
                if current_tokens and current_sentence_id is not None:
                    if not current_first_words and first_token_texts:
                        current_first_words = "_".join(first_token_texts)

                    yield self._create_sentence_context(
                        sentence_id=(
                            str(current_sentence_num)
                            if current_sentence_num is not None
                            else "1"
                        ),
                        sentence_num=(
                            current_sentence_num
                            if current_sentence_num is not None
                            else 1
                        ),
                        tokens=current_tokens,
                        first_words=current_first_words or "",
                    )

        except FileNotFoundError as e:
            raise FileProcessingError(f"File not found: {file_path}") from e
        except PermissionError as e:
            raise FileProcessingError(f"Permission denied: {file_path}") from e
        except Exception as e:
            if isinstance(e, ParseError | FileProcessingError):
                raise
            raise FileProcessingError(
                f"Error processing file {file_path}: {str(e)}"
            ) from e

    def parse_token_line_adaptive(self, line: str, line_num: int) -> Token:
        """Parse a token line with adaptive column handling.

        Args:
            line: TSV line to parse
            line_num: Line number for error reporting

        Returns:
            Token object with extracted information

        Raises:
            ParseError: If line format is invalid
        """
        try:
            parts = line.strip().split("\t")
            mapping = self.current_column_mapping

            if not mapping:
                raise ParseError("Column mapping not initialized")

            # Extract basic token information
            token_id_str = self._safe_get_column(parts, mapping.token_id, "")
            text = self._safe_get_column(parts, mapping.token_text, "")

            if not token_id_str or not text:
                raise ParseError("Missing required token ID or text")

            # Parse token ID format "sentence-token" (e.g., "1-1", "2-5")
            if "-" in token_id_str:
                sentence_part, token_part = token_id_str.split("-", 1)
                idx = int(token_part)
                sentence_from_id = int(sentence_part)
            else:
                # Fallback for simple numeric IDs
                idx = int(token_id_str)
                sentence_from_id = 1

            # Extract optional columns with safe access
            grammatical_role = self._safe_get_column(
                parts, mapping.grammatical_role, ""
            )
            thematic_role = self._safe_get_column(parts, mapping.thematic_role, "")

            # Extract coreference information
            coreference_link = self._safe_get_column(
                parts, mapping.coreference_link, "_"
            )
            coreference_type = self._safe_get_column(
                parts, mapping.coreference_type, "_"
            )
            inanimate_coreference_link = self._safe_get_column(
                parts, mapping.inanimate_coreference_link, "_"
            )
            inanimate_coreference_type = self._safe_get_column(
                parts, mapping.inanimate_coreference_type, "_"
            )

            # Convert "_" to None for coreference fields
            coreference_link = None if coreference_link == "_" else coreference_link
            coreference_type = None if coreference_type == "_" else coreference_type
            inanimate_coreference_link = (
                None
                if inanimate_coreference_link == "_"
                else inanimate_coreference_link
            )
            inanimate_coreference_type = (
                None
                if inanimate_coreference_type == "_"
                else inanimate_coreference_type
            )

            return Token(
                idx=idx,
                text=text,
                sentence_num=sentence_from_id,
                grammatical_role=grammatical_role,
                thematic_role=thematic_role,
                coreference_link=coreference_link,
                coreference_type=coreference_type,
                inanimate_coreference_link=inanimate_coreference_link,
                inanimate_coreference_type=inanimate_coreference_type,
            )

        except (ValueError, IndexError) as e:
            raise ParseError(
                f"Invalid token line format at line {line_num}: {line}. Error: {str(e)}"
            ) from e

    def parse_token_line(self, line: str) -> Token:
        """Parse a single TSV line into a Token object (BaseParser interface).

        This method provides compatibility with the BaseParser interface.
        It delegates to parse_token_line_adaptive with a default line number.

        Args:
            line: TSV line to parse

        Returns:
            Token object with extracted information

        Raises:
            ParseError: If line format is invalid
        """
        return self.parse_token_line_adaptive(line, 0)

    def _safe_get_column(
        self, parts: list[str], column_index: int, default: str = ""
    ) -> str:
        """Safely get a column value with fallback to default.

        Args:
            parts: List of column values
            column_index: Index of the column to retrieve
            default: Default value if column doesn't exist

        Returns:
            Column value or default
        """
        if column_index < len(parts):
            return parts[column_index]
        return default

    def is_sentence_boundary(self, line: str) -> bool:
        """Check if a line represents a sentence boundary.

        Args:
            line: Line to check

        Returns:
            True if line is a sentence boundary
        """
        return line.strip().startswith("#Text=")

    def _extract_first_words(self, line: str) -> str:
        """Extract the first three words from the sentence boundary line.

        Args:
            line: Line to extract words from

        Returns:
            String with the first three words joined by underscores
        """
        if line.startswith("#Text="):
            text_content = line[6:].strip()
            words = text_content.split()[:3]
            return "_".join(words).replace(",", "").replace(".", "")
        return ""

    def _create_sentence_context(
        self, sentence_id: str, sentence_num: int, tokens: list[Token], first_words: str
    ) -> SentenceContext:
        """Create a SentenceContext with enriched tokens."""
        for token in tokens:
            token.sentence_num = sentence_num

        # Create basic context (will be enriched by extractors)
        context = SentenceContext(
            sentence_id=sentence_id,
            sentence_num=sentence_num,
            tokens=tokens,
            critical_pronouns=[],  # Will be populated by pronoun extractor
            coreference_phrases=[],  # Will be populated by phrase extractor
            first_words=first_words,
        )

        # Enrich tokens with context
        enriched_tokens = []
        for token in tokens:
            enriched_token = self.processor.enrich_token(token, context)
            enriched_tokens.append(enriched_token)

        context.tokens = enriched_tokens
        return context

    def get_format_info(self) -> TSVFormatInfo | None:
        """Get information about the currently loaded format.

        Returns:
            TSVFormatInfo object or None if no file has been parsed
        """
        return self.current_format_info

    def get_parsing_statistics(self) -> dict[str, Any]:
        """Get statistics about the current parsing session.

        Returns:
            Dictionary with parsing statistics
        """
        if not self.current_format_info:
            return {"error": "No file has been parsed yet"}

        return {
            "format_type": self.current_format_info.format_type,
            "total_columns": self.current_format_info.total_columns,
            "compatibility_score": self.current_format_info.compatibility_score,
            "token_count": self.current_format_info.token_count,
            "sentence_count": self.current_format_info.sentence_count,
            "issues": self.current_format_info.issues,
            "additional_columns": len(self.current_format_info.additional_columns),
        }


# Maintain backward compatibility
class EnhancedTSVParser(AdaptiveTSVParser):
    """Alias for AdaptiveTSVParser to maintain backward compatibility."""
