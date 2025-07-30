"""Base interfaces for analysis components.

This module defines abstract base classes for different types of analysis
operations, ensuring consistent behavior and easy extensibility.
"""

import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Tuple

from src.data.models import (
    ClauseMateRelationship,
    CoreferenceChain,
    ExtractionResult,
    Token,
)

# Add the parent directory to the path to import from root
sys.path.append(str(Path(__file__).parent.parent.parent))


class BaseAnalyzer(ABC):
    """Abstract base class for all analysis operations.

    This interface establishes the contract for analyzing extracted linguistic data.
    """

    @abstractmethod
    def analyze(self, extraction_result: ExtractionResult) -> Dict[str, Any]:
        """Analyze extracted linguistic features.

        Args:
            extraction_result: The extraction result to analyze

        Returns:
            Dictionary containing analysis results

        Raises:
            AnalysisError: If analysis fails
        """

    @abstractmethod
    def can_analyze(self, extraction_result: ExtractionResult) -> bool:
        """Check if this analyzer can process the given extraction result.

        Args:
            extraction_result: The extraction result to check

        Returns:
            True if analyzer can process this result
        """


class BaseStatisticalAnalyzer(BaseAnalyzer):
    """Abstract base class for statistical analysis operations.

    Handles computation of various statistical measures and summaries.
    """

    @abstractmethod
    def compute_descriptive_statistics(
        self, relationships: List[ClauseMateRelationship]
    ) -> Dict[str, float]:
        """Compute descriptive statistics for clause mate relationships.

        Args:
            relationships: List of relationships to analyze

        Returns:
            Dictionary of statistical measures
        """

    @abstractmethod
    def compute_frequency_distributions(
        self, relationships: List[ClauseMateRelationship]
    ) -> Dict[str, Dict[str, int]]:
        """Compute frequency distributions for various features.

        Args:
            relationships: List of relationships to analyze

        Returns:
            Dictionary mapping feature names to frequency distributions
        """

    @abstractmethod
    def compute_correlations(
        self, relationships: List[ClauseMateRelationship]
    ) -> Dict[Tuple[str, str], float]:
        """Compute correlations between different features.

        Args:
            relationships: List of relationships to analyze

        Returns:
            Dictionary mapping feature pairs to correlation coefficients
        """


class BaseCoreferenceAnalyzer(BaseAnalyzer):
    """Abstract base class for coreference analysis operations.

    Handles analysis of coreference patterns and chains.
    """

    @abstractmethod
    def analyze_coreference_patterns(
        self, chains: List[CoreferenceChain]
    ) -> Dict[str, Any]:
        """Analyze patterns in coreference chains.

        Args:
            chains: List of coreference chains to analyze

        Returns:
            Dictionary containing pattern analysis results
        """

    @abstractmethod
    def compute_chain_statistics(
        self, chains: List[CoreferenceChain]
    ) -> Dict[str, float]:
        """Compute statistics about coreference chains.

        Args:
            chains: List of coreference chains to analyze

        Returns:
            Dictionary of chain statistics
        """

    @abstractmethod
    def analyze_animacy_patterns(
        self, chains: List[CoreferenceChain]
    ) -> Dict[str, Any]:
        """Analyze animacy patterns in coreference chains.

        Args:
            chains: List of coreference chains to analyze

        Returns:
            Dictionary containing animacy pattern analysis
        """


class BasePronounAnalyzer(BaseAnalyzer):
    """Abstract base class for pronoun-specific analysis operations.

    Handles analysis of pronoun usage patterns and properties.
    """

    @abstractmethod
    def analyze_pronoun_distribution(self, pronouns: List[Token]) -> Dict[str, int]:
        """Analyze the distribution of different pronoun types.

        Args:
            pronouns: List of pronoun tokens to analyze

        Returns:
            Dictionary mapping pronoun types to frequencies
        """

    @abstractmethod
    def analyze_pronoun_contexts(
        self, relationships: List[ClauseMateRelationship]
    ) -> Dict[str, Any]:
        """Analyze contexts in which pronouns appear.

        Args:
            relationships: List of relationships containing pronouns

        Returns:
            Dictionary containing context analysis results
        """

    @abstractmethod
    def analyze_antecedent_patterns(
        self, relationships: List[ClauseMateRelationship]
    ) -> Dict[str, Any]:
        """Analyze patterns in antecedent relationships.

        Args:
            relationships: List of relationships to analyze

        Returns:
            Dictionary containing antecedent pattern analysis
        """


class BaseClauseMateAnalyzer(BaseAnalyzer):
    """Abstract base class for clause mate relationship analysis.

    Handles analysis of clause mate patterns and properties.
    """

    @abstractmethod
    def analyze_clause_mate_distribution(
        self, relationships: List[ClauseMateRelationship]
    ) -> Dict[str, int]:
        """Analyze the distribution of clause mate types.

        Args:
            relationships: List of relationships to analyze

        Returns:
            Dictionary mapping clause mate types to frequencies
        """

    @abstractmethod
    def analyze_syntactic_patterns(
        self, relationships: List[ClauseMateRelationship]
    ) -> Dict[str, Any]:
        """Analyze syntactic patterns in clause mate relationships.

        Args:
            relationships: List of relationships to analyze

        Returns:
            Dictionary containing syntactic pattern analysis
        """

    @abstractmethod
    def analyze_thematic_role_patterns(
        self, relationships: List[ClauseMateRelationship]
    ) -> Dict[str, Any]:
        """Analyze thematic role patterns in clause mate relationships.

        Args:
            relationships: List of relationships to analyze

        Returns:
            Dictionary containing thematic role pattern analysis
        """


class BaseValidationAnalyzer(BaseAnalyzer):
    """Abstract base class for validation and quality analysis.

    Handles validation of data quality and consistency checks.
    """

    @abstractmethod
    def validate_data_consistency(
        self, extraction_result: ExtractionResult
    ) -> List[str]:
        """Validate consistency of extracted data.

        Args:
            extraction_result: The extraction result to validate

        Returns:
            List of validation error messages (empty if valid)
        """

    @abstractmethod
    def check_completeness(
        self, extraction_result: ExtractionResult
    ) -> Dict[str, float]:
        """Check completeness of extracted data.

        Args:
            extraction_result: The extraction result to check

        Returns:
            Dictionary mapping data types to completeness percentages
        """

    @abstractmethod
    def identify_anomalies(
        self, relationships: List[ClauseMateRelationship]
    ) -> List[Dict[str, Any]]:
        """Identify potential anomalies in the data.

        Args:
            relationships: List of relationships to check

        Returns:
            List of anomaly descriptions
        """
