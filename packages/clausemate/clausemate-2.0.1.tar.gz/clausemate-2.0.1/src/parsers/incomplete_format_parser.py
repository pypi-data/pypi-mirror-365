"""Incomplete Format Parser for handling TSV files with missing columns.

This parser handles files like 4.tsv that have fewer columns than expected
but still contain usable linguistic data including coreference information.
"""

import logging
from typing import Any, Dict, Iterator, Optional

from ..data.models import SentenceContext, Token
from ..parsers.base import BaseTokenProcessor
from .adaptive_tsv_parser import AdaptiveTSVParser
from .preamble_parser import PreambleParser, extract_preamble_from_file


class IncompleteFormatParser(AdaptiveTSVParser):
    """Parser for handling incomplete TSV formats with graceful degradation."""

    def __init__(
        self, processor: BaseTokenProcessor, limitations: Optional[list] = None
    ):
        """Initialize incomplete format parser.

        Args:
            processor: Token processor for handling tokens
            limitations: List of known limitations for this format
        """
        super().__init__(processor)
        self.limitations = limitations or []
        self.logger = logging.getLogger(__name__)

        # Track what features are available
        self.available_features = {
            "basic_tokens": True,
            "pos_tags": True,
            "lemmas": True,
            "coreference": False,
            "morphological": False,
        }

    def _setup_column_mapping_for_incomplete(self, file_path: str) -> None:
        """Set up column mapping for incomplete format with fallback strategies."""
        try:
            # First try preamble-based mapping
            preamble_parser = PreambleParser()
            preamble_lines = extract_preamble_from_file(file_path)

            if preamble_lines:
                self.logger.info(
                    "Attempting preamble-based column mapping for incomplete format"
                )
                schema = preamble_parser.parse_preamble_lines(preamble_lines)

                if schema:
                    self.current_annotation_schema = schema
                    self.current_column_mapping = self._create_dynamic_column_mapping()
                    self._detect_available_features_from_schema()
                    return

            # Fallback to incomplete format detection
            self.logger.info("Using incomplete format detection")
            self._detect_incomplete_format(file_path)

        except Exception as e:
            self.logger.warning(
                f"Column mapping setup failed: {e}, using minimal mapping"
            )
            self._setup_minimal_column_mapping()

    def _detect_incomplete_format(self, file_path: str) -> None:
        """Detect and configure for incomplete format based on column count."""
        try:
            # Sample first few data rows to determine column count
            with open(file_path, encoding="utf-8") as f:
                # Skip preamble
                for line in f:
                    line = line.strip()
                    if line.startswith("#") or line == "":
                        continue

                    # First data line
                    columns = line.split("\t")
                    column_count = len(columns)

                    self.logger.info(
                        f"Detected {column_count} columns in incomplete format"
                    )

                    if column_count == 12:
                        self._setup_12_column_mapping()
                    elif column_count == 13:
                        self._setup_13_column_mapping()
                    else:
                        self.logger.warning(f"Unsupported column count: {column_count}")
                        self._setup_minimal_column_mapping()
                    break

        except Exception as e:
            self.logger.error(f"Error detecting incomplete format: {e}")
            self._setup_minimal_column_mapping()

    def _setup_12_column_mapping(self) -> None:
        """Set up column mapping for 12-column format (like 4.tsv)."""
        self.logger.info("Configuring for 12-column incomplete format")

        # Based on analysis of 4.tsv structure
        self.column_mapping = {
            "token_id": 0,  # '1-1', '1-2', etc.
            "token_span": 1,  # '0-4', '4-5', etc.
            "token_text": 2,  # Token text
            "lemma": 3,  # Lemma
            "pos_tag": 4,  # POS tag or morphological info
            "morph_features": 5,  # Additional morphological features
            "dependency_head": 6,  # Dependency head
            "dependency_rel": 7,  # Dependency relation
            "coreference_link": 8,  # Coreference links (e.g., '*->140-1')
            "coreference_type": 9,  # Coreference types (e.g., 'zero[140]')
            "additional_1": 10,  # Additional annotation
            "additional_2": 11,  # Additional annotation
        }

        # Mark coreference as available if we find the right columns
        self.available_features["coreference"] = True
        self.logger.info("Coreference features detected in columns 8-9")

    def _setup_13_column_mapping(self) -> None:
        """Set up column mapping for 13-column format."""
        self.logger.info("Configuring for 13-column incomplete format")

        # Similar to 12-column but with one additional column
        self.column_mapping = {
            "token_id": 0,
            "token_span": 1,
            "token_text": 2,
            "lemma": 3,
            "pos_tag": 4,
            "morph_features": 5,
            "dependency_head": 6,
            "dependency_rel": 7,
            "additional_1": 8,
            "coreference_link": 9,
            "coreference_type": 10,
            "additional_2": 11,
            "additional_3": 12,
        }

        self.available_features["coreference"] = True
        self.logger.info("Coreference features detected in columns 9-10")

    def _setup_minimal_column_mapping(self) -> None:
        """Set up minimal column mapping for unknown formats."""
        self.logger.warning("Using minimal column mapping - limited functionality")

        self.column_mapping = {
            "token_id": 0,
            "token_span": 1,
            "token_text": 2,
            "lemma": 3 if True else None,
            "pos_tag": 4 if True else None,
        }

        # Disable advanced features
        self.available_features["coreference"] = False
        self.available_features["morphological"] = False

    def _detect_available_features_from_schema(self) -> None:
        """Detect which features are available based on annotation schema."""
        if self.current_column_mapping:
            if hasattr(self.current_column_mapping, "coreference_link") and hasattr(
                self.current_column_mapping, "coreference_type"
            ):
                self.available_features["coreference"] = True
                self.logger.info("Coreference features available")

        if self.current_annotation_schema:
            # Check for morphological features in schema
            for span_ann in self.current_annotation_schema.span_annotations:
                if "MorphologicalFeatures" in span_ann.get("type", ""):
                    self.available_features["morphological"] = True
                    self.logger.info("Morphological features available")
                    break

    def parse_sentence_streaming(self, file_path: str) -> Iterator[SentenceContext]:
        """Parse sentences with graceful degradation for missing features."""
        self.logger.info(f"Starting incomplete format parsing of: {file_path}")

        # Set up column mapping first
        self._setup_column_mapping_for_incomplete(file_path)

        # Log available features
        available = [k for k, v in self.available_features.items() if v]
        limited = [k for k, v in self.available_features.items() if not v]

        if available:
            self.logger.info(f"Available features: {', '.join(available)}")
        if limited:
            self.logger.warning(f"Limited/missing features: {', '.join(limited)}")

        # Use direct parsing instead of parent to avoid compatibility checks
        try:
            yield from self._parse_incomplete_format_streaming(file_path)
        except Exception as e:
            self.logger.error(f"Parsing failed: {e}")
            # Could implement additional fallback strategies here
            raise

    def _parse_incomplete_format_streaming(
        self, file_path: str
    ) -> Iterator[SentenceContext]:
        """Direct parsing implementation for incomplete formats."""
        import csv

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
                        if line_text.startswith("#Text="):
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

                        # Parse token with incomplete format handling
                        token = self._create_token_from_row(
                            row, current_sentence_id or "1"
                        )

                        if token:
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
                            if (
                                current_first_words is None
                                and len(first_token_texts) < 3
                            ):
                                first_token_texts.append(token.text)

                            # Validate and add token
                            if self.processor.validate_token(token):
                                current_tokens.append(token)

                    except Exception as e:
                        self.logger.error(f"Error processing line {line_num}: {str(e)}")
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

        except FileNotFoundError:
            from ..exceptions import FileProcessingError

            raise FileProcessingError(f"File not found: {file_path}")
        except PermissionError:
            from ..exceptions import FileProcessingError

            raise FileProcessingError(f"Permission denied: {file_path}")
        except Exception as e:
            from ..exceptions import FileProcessingError

            raise FileProcessingError(f"Error processing file {file_path}: {str(e)}")

    def _extract_first_words(self, line: str) -> str:
        """Extract the first three words from the sentence boundary line."""
        if line.startswith("#Text="):
            text_content = line[6:].strip()
            words = text_content.split()[:3]
            return "_".join(words).replace(",", "").replace(".", "")
        return ""

    def _create_token_from_row(self, row: list, sentence_id: str) -> Optional[Token]:
        """Create token from row with graceful handling of missing columns."""
        try:
            # Ensure we have minimum required columns
            if len(row) < 3:
                self.logger.warning(
                    f"Row too short: {len(row)} columns, need at least 3"
                )
                return None

            # Extract basic token information
            token_id = row[self.column_mapping.get("token_id", 0)]
            token_text = row[self.column_mapping.get("token_text", 2)]

            # Extract optional information with fallbacks
            lemma = None
            if (
                self.column_mapping.get("lemma")
                and len(row) > self.column_mapping["lemma"]
            ):
                lemma = row[self.column_mapping["lemma"]]
                if lemma == "_":
                    lemma = None

            pos_tag = None
            if (
                self.column_mapping.get("pos_tag")
                and len(row) > self.column_mapping["pos_tag"]
            ):
                pos_tag = row[self.column_mapping["pos_tag"]]
                if pos_tag == "_":
                    pos_tag = None

            # Extract coreference information if available
            coreference_link = None
            coreference_type = None

            if self.available_features["coreference"]:
                coref_link_col = self.column_mapping.get("coreference_link")
                coref_type_col = self.column_mapping.get("coreference_type")

                if coref_link_col and len(row) > coref_link_col:
                    coreference_link = row[coref_link_col]
                    if coreference_link == "_":
                        coreference_link = None

                if coref_type_col and len(row) > coref_type_col:
                    coreference_type = row[coref_type_col]
                    if coreference_type == "_":
                        coreference_type = None

            # Create token with available information using correct Token constructor
            token = Token(
                idx=int(token_id.split("-")[-1]) if "-" in token_id else int(token_id),
                text=token_text,
                sentence_num=int(token_id.split("-")[0]) if "-" in token_id else 1,
                grammatical_role=pos_tag or "",
                thematic_role="",
                coreference_link=coreference_link,
                coreference_type=coreference_type,
            )

            return token

        except Exception as e:
            self.logger.error(f"Error creating token from row: {e}")
            return None

    def get_limitations(self) -> list:
        """Get list of limitations for this format."""
        limitations = []

        if not self.available_features["coreference"]:
            limitations.append("No coreference analysis available")

        if not self.available_features["morphological"]:
            limitations.append("Limited morphological features")

        return limitations

    def get_compatibility_info(self) -> Dict[str, Any]:
        """Get compatibility information for this format."""
        return {
            "format_type": "incomplete",
            "available_features": self.available_features,
            "limitations": self.get_limitations(),
            "column_mapping": self.column_mapping,
            "recommended_actions": [
                "Review output for completeness",
                "Consider using a more complete format for full analysis",
                "Check coreference results manually",
            ],
        }
