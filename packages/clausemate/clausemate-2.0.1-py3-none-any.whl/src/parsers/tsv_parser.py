"""TSV parser implementation for clause mates data.

This module provides a concrete implementation of the BaseParser interface
specifically for parsing TSV files with linguistic annotations.
"""

import csv
import sys
from pathlib import Path
from typing import Dict, Iterator, List

from src.data.models import SentenceContext, Token
from src.parsers.base import BaseParser, BaseTokenProcessor

from ..exceptions import FileProcessingError, ParseError

# Add the parent directory to the path to import from root
sys.path.append(str(Path(__file__).parent.parent.parent))


class TSVParser(BaseParser):
    """Concrete implementation of BaseParser for TSV files.

    Handles parsing of tab-separated value files containing linguistic annotations
    with the expected column structure for clause mate analysis.
    """

    def __init__(self, processor: BaseTokenProcessor):
        """Initialize the TSV parser.

        Args:
            processor: Token processor for validation and enrichment
        """
        self.processor = processor
        self._expected_columns = 14  # Updated based on actual TSV structure

        # Import column mappings from config
        from ..config import TSVColumns

        self.columns = TSVColumns()

    def parse_file(self, file_path: str) -> Dict[str, List[Token]]:
        """Parse a TSV file and return all sentences with their tokens.

        Args:
            file_path: Path to the TSV file to parse

        Returns:
            Dictionary mapping sentence IDs to lists of tokens

        Raises:
            FileProcessingError: If file cannot be read
            ParseError: If file format is invalid
        """
        sentences = {}

        try:
            for sentence_context in self.parse_sentence_streaming(file_path):
                sentences[sentence_context.sentence_id] = sentence_context.tokens
        except FileNotFoundError:
            raise FileProcessingError(f"File not found: {file_path}")
        except PermissionError:
            raise FileProcessingError(f"Permission denied: {file_path}")
        except Exception as e:
            raise FileProcessingError(f"Error reading file {file_path}: {str(e)}")

        return sentences

    def parse_sentence_streaming(self, file_path: str) -> Iterator[SentenceContext]:
        """Parse a TSV file sentence by sentence for memory efficiency.

        Args:
            file_path: Path to the TSV file to parse

        Yields:
            SentenceContext objects for each sentence

        Raises:
            FileProcessingError: If file cannot be processed
            ParseError: If file format is invalid
        """
        current_tokens = []
        current_first_words = None
        current_sentence_num = None
        current_sentence_id = None
        pending_first_words = None
        first_token_texts = []  # Collect first three token texts if needed

        try:
            with open(file_path, encoding="utf-8") as file:
                reader = csv.reader(file, delimiter="\t")
                for line_num, row in enumerate(reader, 1):
                    try:
                        if not row or (len(row) == 1 and not row[0].strip()):
                            continue
                        line_text = "\t".join(row)
                        # Detect sentence boundary and extract first words for
                        # the NEXT sentence
                        if self.is_sentence_boundary(line_text):
                            # If we have tokens, yield the previous sentence
                            # with its first_words
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
                        if line_text.startswith("#"):
                            continue
                        if len(row) < self._expected_columns:
                            raise ParseError(
                                f"Line {line_num}: Expected "
                                f"{self._expected_columns} columns, "
                                f"got {len(row)}"
                            )
                        token = self.parse_token_line(line_text)
                        # On first token, set sentence_num and sentence_id and
                        # first_words
                        if current_sentence_num is None:
                            current_sentence_num = token.sentence_num
                            current_sentence_id = str(token.sentence_num)
                            if pending_first_words is not None:
                                current_first_words = pending_first_words
                                pending_first_words = None
                                # Only reset first_token_texts if not using
                                # pending_first_words
                            else:
                                # Start collecting first three token texts
                                first_token_texts = []
                        # Collect first three token texts if needed
                        if current_first_words is None and len(first_token_texts) < 3:
                            first_token_texts.append(token.text)
                        if self.processor.validate_token(token):
                            current_tokens.append(token)
                    except ParseError:
                        raise
                    except Exception as e:
                        raise ParseError(f"Line {line_num}: {str(e)}")
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
            raise FileProcessingError(f"File not found: {file_path}")
        except PermissionError:
            raise FileProcessingError(f"Permission denied: {file_path}")
        except Exception as e:
            if isinstance(e, (ParseError, FileProcessingError)):
                raise
            raise FileProcessingError(f"Error processing file {file_path}: {str(e)}")

    def parse_token_line(self, line: str) -> Token:
        """Parse a single TSV line into a Token object.

        Args:
            line: TSV line to parse

        Returns:
            Token object with extracted information

        Raises:
            ParseError: If line format is invalid
        """
        try:
            parts = line.strip().split("\t")

            if len(parts) < self._expected_columns:
                raise ParseError(
                    f"Insufficient columns: expected {self._expected_columns}, got {len(parts)}"
                )

            # Extract token information using correct column indices
            token_id_str = parts[self.columns.TOKEN_ID]
            # Parse token ID format "sentence-token" (e.g., "1-1", "2-5")
            if "-" in token_id_str:
                sentence_part, token_part = token_id_str.split("-", 1)
                idx = int(token_part)
                sentence_from_id = int(sentence_part)
            else:
                # Fallback for simple numeric IDs
                idx = int(token_id_str)
                sentence_from_id = 1

            text = parts[self.columns.TOKEN_TEXT]
            grammatical_role = (
                parts[self.columns.GRAMMATICAL_ROLE]
                if len(parts) > self.columns.GRAMMATICAL_ROLE
                else ""
            )
            thematic_role = (
                parts[self.columns.THEMATIC_ROLE]
                if len(parts) > self.columns.THEMATIC_ROLE
                else ""
            )

            # Extract coreference information from correct columns
            coreference_link = None
            coreference_type = None
            inanimate_coreference_link = None
            inanimate_coreference_type = None

            if (
                self.columns.COREFERENCE_LINK is not None
                and len(parts) > self.columns.COREFERENCE_LINK
                and parts[self.columns.COREFERENCE_LINK] != "_"
            ):
                coreference_link = parts[self.columns.COREFERENCE_LINK]

            if (
                self.columns.COREFERENCE_TYPE is not None
                and len(parts) > self.columns.COREFERENCE_TYPE
                and parts[self.columns.COREFERENCE_TYPE] != "_"
            ):
                coreference_type = parts[self.columns.COREFERENCE_TYPE]

            if (
                self.columns.INANIMATE_COREFERENCE_LINK is not None
                and len(parts) > self.columns.INANIMATE_COREFERENCE_LINK
                and parts[self.columns.INANIMATE_COREFERENCE_LINK] != "_"
            ):
                inanimate_coreference_link = parts[
                    self.columns.INANIMATE_COREFERENCE_LINK
                ]

            if (
                self.columns.INANIMATE_COREFERENCE_TYPE is not None
                and len(parts) > self.columns.INANIMATE_COREFERENCE_TYPE
                and parts[self.columns.INANIMATE_COREFERENCE_TYPE] != "_"
            ):
                inanimate_coreference_type = parts[
                    self.columns.INANIMATE_COREFERENCE_TYPE
                ]

            return Token(
                idx=idx,
                text=text,
                # Use actual sentence number from token ID
                sentence_num=sentence_from_id,
                grammatical_role=grammatical_role,
                thematic_role=thematic_role,
                coreference_link=coreference_link,
                coreference_type=coreference_type,
                inanimate_coreference_link=inanimate_coreference_link,
                inanimate_coreference_type=inanimate_coreference_type,
            )

        except (ValueError, IndexError) as e:
            raise ParseError(f"Invalid token line format: {line}. Error: {str(e)}")

    def is_sentence_boundary(self, line: str) -> bool:
        """Check if a line represents a sentence boundary.

        Args:
            line: Line to check

        Returns:
            True if line is a sentence boundary
        """
        # The primary indicator of a new sentence is the '#Text=' marker.
        # This is the only reliable way to identify the start of a new
        # sentence.
        return line.strip().startswith("#Text=")

    def _extract_sentence_id(self, line: str) -> str:
        """Extract sentence ID from a sentence boundary line."""
        line = line.strip()

        # Handle #Text= format
        if line.startswith("#Text="):
            # Use the text content as sentence ID, but clean it up
            text_content = line[6:].strip()  # Remove "#Text="
            # Create a simple ID from the content (first few words)
            words = text_content.split()[:3]  # First 3 words
            return "_".join(words).replace(",", "").replace(".", "")

        # Handle different sentence ID formats
        if "sent_id" in line:
            parts = line.split("=")
            if len(parts) > 1:
                return parts[1].strip()

        # Fallback: use the entire line as ID (cleaned)
        return line.replace("#", "").strip()[:50]  # Limit length

    def _extract_sentence_num(self, line: str) -> int:
        """Extract sentence number from sentence ID."""
        # For this format, we'll track sentences sequentially
        # This is a simple approach - we could make it more sophisticated

        # Try to extract from the sentence content or use a counter
        sentence_id = self._extract_sentence_id(line)

        # Try to extract number from various formats
        import re

        match = re.search(r"(\d+)", sentence_id)
        if match:
            return int(match.group(1))

        # Fallback: use a hash-based approach for consistency
        return hash(sentence_id) % 10000  # Keep it reasonable

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
        self, sentence_id: str, sentence_num: int, tokens: List[Token], first_words: str
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


class DefaultTokenProcessor(BaseTokenProcessor):
    """Default implementation of BaseTokenProcessor.

    Provides basic token validation and enrichment functionality.
    """

    def validate_token(self, token: Token) -> bool:
        """Validate that a token has all required fields.

        Args:
            token: Token to validate

        Returns:
            True if token is valid
        """
        try:
            # Basic validation
            if token.idx < 1:
                return False
            if not token.text or not token.text.strip():
                return False

            # Additional validation can be added here
            return True

        except Exception:
            return False

    def enrich_token(self, token: Token, context: SentenceContext) -> Token:
        """Enrich a token with additional computed information.

        Args:
            token: Token to enrich
            context: Sentence context for enrichment

        Returns:
            Enriched token
        """
        # For now, just return the token as-is
        # Additional enrichment logic can be added here
        return token
