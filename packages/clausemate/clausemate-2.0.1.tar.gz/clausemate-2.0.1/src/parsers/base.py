"""Base interfaces for parser components.

This module defines abstract base classes that establish clear contracts
between different parts of the parsing system.
"""

import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Iterator, List

from src.data.models import SentenceContext, Token

# Add the parent directory to the path to import from root
sys.path.append(str(Path(__file__).parent.parent.parent))


class BaseParser(ABC):
    """Abstract base class for all file parsers.

    This interface ensures consistent behavior across different parser implementations
    and makes the system easily extensible.
    """

    @abstractmethod
    def parse_file(self, file_path: str) -> Dict[str, List[Token]]:
        """Parse a file and return all sentences with their tokens.

        Args:
            file_path: Path to the file to parse

        Returns:
            Dictionary mapping sentence IDs to lists of tokens

        Raises:
            FileProcessingError: If file cannot be processed
            ParseError: If file format is invalid
        """

    @abstractmethod
    def parse_sentence_streaming(self, file_path: str) -> Iterator[SentenceContext]:
        """Parse a file sentence by sentence for memory efficiency.

        Args:
            file_path: Path to the file to parse

        Yields:
            SentenceContext objects for each sentence

        Raises:
            FileProcessingError: If file cannot be processed
            ParseError: If file format is invalid
        """

    @abstractmethod
    def parse_token_line(self, line: str) -> Token:
        """Parse a single TSV line into a Token object.

        Args:
            line: TSV line to parse

        Returns:
            Token object with extracted information

        Raises:
            ParseError: If line format is invalid
        """

    @abstractmethod
    def is_sentence_boundary(self, line: str) -> bool:
        """Check if a line represents a sentence boundary.

        Args:
            line: Line to check

        Returns:
            True if line is a sentence boundary
        """


class BaseTokenProcessor(ABC):
    """Abstract base class for token processing operations.

    This interface handles token-level operations like validation and enrichment.
    """

    @abstractmethod
    def validate_token(self, token: Token) -> bool:
        """Validate that a token has all required fields.

        Args:
            token: Token to validate

        Returns:
            True if token is valid
        """

    @abstractmethod
    def enrich_token(self, token: Token, context: SentenceContext) -> Token:
        """Enrich a token with additional computed information.

        Args:
            token: Token to enrich
            context: Sentence context for enrichment

        Returns:
            Enriched token
        """
