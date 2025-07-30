"""Format detection utilities for TSV files.

This module provides functionality to analyze TSV file formats,
detect column structures, and validate compatibility with the
clause mates analysis system.
"""

import csv
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


@dataclass
class TSVFormatInfo:
    """Information about a TSV file format."""

    file_path: str
    total_columns: int
    sample_rows: List[List[str]]
    sentence_boundaries: List[str]
    token_count: int
    sentence_count: int
    has_required_columns: bool
    required_column_positions: Dict[str, int]
    additional_columns: List[str]
    format_type: str  # "standard" or "extended"
    compatibility_score: float  # 0.0 to 1.0
    issues: List[str]


@dataclass
class ColumnMapping:
    """Mapping of logical columns to physical positions."""

    token_id: int = 0
    token_text: int = 2  # Fixed: was 1, should be 2 to match config.py
    grammatical_role: int = 4  # Fixed: was 8, should be 4 to match config.py
    thematic_role: int = 5  # Fixed: was 9, should be 5 to match config.py
    coreference_link: int = 10
    coreference_type: int = 11
    inanimate_coreference_link: int = 12
    inanimate_coreference_type: int = 13


class TSVFormatDetector:
    """Detects and analyzes TSV file formats for compatibility."""

    # Required columns for clause mates analysis
    REQUIRED_COLUMNS = {
        "token_id": "Token ID",
        "token_text": "Token Text",
        "coreference_link": "Coreference Link",
        "coreference_type": "Coreference Type",
        "inanimate_coreference_link": "Inanimate Coreference Link",
        "inanimate_coreference_type": "Inanimate Coreference Type",
    }

    def __init__(self):
        """Initialize the format detector."""
        self.standard_mapping = ColumnMapping()

    def analyze_file(self, file_path: str, max_sample_rows: int = 50) -> TSVFormatInfo:
        """Analyze a TSV file and return format information.

        Args:
            file_path: Path to the TSV file
            max_sample_rows: Maximum number of sample rows to analyze

        Returns:
            TSVFormatInfo object with analysis results
        """
        logger.info(f"Analyzing TSV format for: {file_path}")

        try:
            with open(file_path, encoding="utf-8") as file:
                reader = csv.reader(file, delimiter="\t")

                sample_rows = []
                sentence_boundaries = []
                token_count = 0
                sentence_count = 0
                total_columns = 0

                for line_num, row in enumerate(reader):
                    if line_num >= max_sample_rows * 10:  # Stop after reasonable sample
                        break

                    if not row or (len(row) == 1 and not row[0].strip()):
                        continue

                    line_text = "\t".join(row)

                    # Check for sentence boundaries
                    if line_text.startswith("#Text="):
                        sentence_boundaries.append(line_text)
                        sentence_count += 1
                        continue

                    # Skip other comment lines
                    if line_text.startswith("#"):
                        continue

                    # This is a token line
                    if len(sample_rows) < max_sample_rows:
                        sample_rows.append(row)

                    total_columns = max(total_columns, len(row))
                    token_count += 1

                # Analyze column structure
                format_info = self._analyze_format(
                    file_path=file_path,
                    sample_rows=sample_rows,
                    sentence_boundaries=sentence_boundaries,
                    token_count=token_count,
                    sentence_count=sentence_count,
                    total_columns=total_columns,
                )

                logger.info(
                    f"Format analysis complete: {format_info.format_type} format "
                    f"with {format_info.total_columns} columns, "
                    f"compatibility score: {format_info.compatibility_score:.2f}"
                )

                return format_info

        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {str(e)}")
            return TSVFormatInfo(
                file_path=file_path,
                total_columns=0,
                sample_rows=[],
                sentence_boundaries=[],
                token_count=0,
                sentence_count=0,
                has_required_columns=False,
                required_column_positions={},
                additional_columns=[],
                format_type="unknown",
                compatibility_score=0.0,
                issues=[f"Analysis failed: {str(e)}"],
            )

    def _analyze_format(
        self,
        file_path: str,
        sample_rows: List[List[str]],
        sentence_boundaries: List[str],
        token_count: int,
        sentence_count: int,
        total_columns: int,
    ) -> TSVFormatInfo:
        """Analyze the format based on collected data."""
        issues = []
        required_column_positions = {}

        # Determine format type
        if total_columns == 15:
            format_type = "standard"
            column_mapping = self.standard_mapping
        elif total_columns >= 30:
            format_type = "extended"
            column_mapping = self.standard_mapping  # Same core positions
        elif total_columns == 14:
            format_type = "legacy"  # Older 14-column format
            column_mapping = self.standard_mapping
        elif total_columns == 12:
            format_type = "incomplete"  # 12-column incomplete format (like 4.tsv)
            column_mapping = self.standard_mapping
            issues.append(
                "Incomplete format detected - limited coreference analysis available"
            )
        elif total_columns == 13:
            format_type = "incomplete"  # 13-column incomplete format
            column_mapping = self.standard_mapping
            issues.append(
                "Incomplete format detected - limited coreference analysis available"
            )
        else:
            format_type = "unknown"
            column_mapping = self.standard_mapping
            issues.append(f"Unexpected column count: {total_columns}")

        # Validate required columns exist and are accessible
        has_required_columns = True

        if sample_rows:
            try:
                # Check if we can access the required column positions
                sample_row = sample_rows[0]

                if len(sample_row) > column_mapping.token_id:
                    required_column_positions["token_id"] = column_mapping.token_id
                else:
                    has_required_columns = False
                    issues.append("Token ID column not accessible")

                if len(sample_row) > column_mapping.token_text:
                    required_column_positions["token_text"] = column_mapping.token_text
                else:
                    has_required_columns = False
                    issues.append("Token text column not accessible")

                # For incomplete formats, be more lenient with coreference columns
                if format_type == "incomplete":
                    # Check if basic coreference columns are accessible (more lenient)
                    if len(sample_row) > column_mapping.coreference_link:
                        required_column_positions["coreference_link"] = (
                            column_mapping.coreference_link
                        )
                    else:
                        issues.append("Coreference link column not accessible")

                    if len(sample_row) > column_mapping.coreference_type:
                        required_column_positions["coreference_type"] = (
                            column_mapping.coreference_type
                        )
                    else:
                        issues.append("Coreference type column not accessible")

                    # Don't require inanimate coreference for incomplete formats
                    if len(sample_row) > column_mapping.inanimate_coreference_link:
                        required_column_positions["inanimate_coreference_link"] = (
                            column_mapping.inanimate_coreference_link
                        )
                    else:
                        issues.append(
                            "Inanimate coreference link column not accessible"
                        )

                    if len(sample_row) > column_mapping.inanimate_coreference_type:
                        required_column_positions["inanimate_coreference_type"] = (
                            column_mapping.inanimate_coreference_type
                        )
                    else:
                        issues.append(
                            "Inanimate coreference type column not accessible"
                        )

                    # For incomplete formats, having basic columns is enough
                    has_required_columns = (
                        "token_id" in required_column_positions
                        and "token_text" in required_column_positions
                    )
                else:
                    # Standard validation for complete formats
                    if len(sample_row) > column_mapping.coreference_link:
                        required_column_positions["coreference_link"] = (
                            column_mapping.coreference_link
                        )
                    else:
                        has_required_columns = False
                        issues.append("Coreference link column not accessible")

                    if len(sample_row) > column_mapping.coreference_type:
                        required_column_positions["coreference_type"] = (
                            column_mapping.coreference_type
                        )
                    else:
                        has_required_columns = False
                        issues.append("Coreference type column not accessible")

                    if len(sample_row) > column_mapping.inanimate_coreference_link:
                        required_column_positions["inanimate_coreference_link"] = (
                            column_mapping.inanimate_coreference_link
                        )
                    else:
                        has_required_columns = False
                        issues.append(
                            "Inanimate coreference link column not accessible"
                        )

                    if len(sample_row) > column_mapping.inanimate_coreference_type:
                        required_column_positions["inanimate_coreference_type"] = (
                            column_mapping.inanimate_coreference_type
                        )
                    else:
                        has_required_columns = False
                        issues.append(
                            "Inanimate coreference type column not accessible"
                        )

            except Exception as e:
                has_required_columns = False
                issues.append(f"Error validating columns: {str(e)}")
        else:
            has_required_columns = False
            issues.append("No sample rows available for validation")

        # Calculate compatibility score
        compatibility_score = self._calculate_compatibility_score(
            has_required_columns, format_type, total_columns, issues
        )

        # Identify additional columns
        additional_columns = []
        if total_columns > 14:
            additional_columns = [f"Column_{i}" for i in range(14, total_columns)]

        return TSVFormatInfo(
            file_path=file_path,
            total_columns=total_columns,
            sample_rows=sample_rows[:10],  # Keep only first 10 for memory
            sentence_boundaries=sentence_boundaries[:5],  # Keep only first 5
            token_count=token_count,
            sentence_count=sentence_count,
            has_required_columns=has_required_columns,
            required_column_positions=required_column_positions,
            additional_columns=additional_columns,
            format_type=format_type,
            compatibility_score=compatibility_score,
            issues=issues,
        )

    def _calculate_compatibility_score(
        self,
        has_required_columns: bool,
        format_type: str,
        total_columns: int,
        issues: List[str],
    ) -> float:
        """Calculate a compatibility score from 0.0 to 1.0."""
        score = 0.0

        # Base score for having required columns
        if has_required_columns:
            score += 0.6

        # Format type bonus
        if format_type == "standard":
            score += 0.3
        elif format_type == "legacy":
            score += 0.25  # 14-column legacy format
        elif format_type == "extended":
            score += 0.25  # Slightly lower due to complexity
        elif format_type == "incomplete":
            score += 0.35  # Higher score for incomplete formats to make them usable

        # Column count assessment
        if total_columns >= 14:
            score += 0.1
        elif total_columns >= 12:  # Give some credit for 12-13 column formats
            score += 0.05

        # Penalty for issues (but less severe for incomplete formats)
        penalty_factor = 0.03 if format_type == "incomplete" else 0.05
        score -= len(issues) * penalty_factor

        return max(0.0, min(1.0, score))

    def compare_formats(self, format_infos: List[TSVFormatInfo]) -> Dict[str, Any]:
        """Compare multiple format analyses and provide recommendations.

        Args:
            format_infos: List of format analysis results

        Returns:
            Dictionary with comparison results and recommendations
        """
        if not format_infos:
            return {"error": "No format information provided"}

        # Sort by compatibility score
        sorted_formats = sorted(
            format_infos, key=lambda x: x.compatibility_score, reverse=True
        )

        # Identify format types
        format_types = {info.format_type for info in format_infos}

        # Calculate statistics
        total_files = len(format_infos)
        compatible_files = len(
            [info for info in format_infos if info.compatibility_score >= 0.7]
        )

        recommendations = []

        if compatible_files == total_files:
            recommendations.append("All files are compatible with the current system")
        elif compatible_files > 0:
            recommendations.append(
                f"{compatible_files}/{total_files} files are compatible"
            )
            recommendations.append(
                "Consider implementing adaptive parsing for remaining files"
            )
        else:
            recommendations.append(
                "No files are fully compatible - adaptive parsing required"
            )

        if len(format_types) > 1:
            recommendations.append(
                "Multiple format types detected - implement format detection"
            )

        return {
            "total_files": total_files,
            "compatible_files": compatible_files,
            "format_types": list(format_types),
            "best_format": sorted_formats[0] if sorted_formats else None,
            "worst_format": sorted_formats[-1] if sorted_formats else None,
            "recommendations": recommendations,
            "all_formats": sorted_formats,
        }


def analyze_directory(directory_path: str, pattern: str = "*.tsv") -> Dict[str, Any]:
    """Analyze all TSV files in a directory.

    Args:
        directory_path: Path to directory containing TSV files
        pattern: File pattern to match (default: "*.tsv")

    Returns:
        Dictionary with analysis results for all files
    """
    detector = TSVFormatDetector()
    directory = Path(directory_path)

    if not directory.exists():
        return {"error": f"Directory not found: {directory_path}"}

    tsv_files = list(directory.glob(pattern))

    if not tsv_files:
        return {"error": f"No TSV files found in {directory_path}"}

    logger.info(f"Analyzing {len(tsv_files)} TSV files in {directory_path}")

    format_infos = []
    for tsv_file in tsv_files:
        format_info = detector.analyze_file(str(tsv_file))
        format_infos.append(format_info)

    comparison = detector.compare_formats(format_infos)

    return {
        "directory": directory_path,
        "files_analyzed": len(tsv_files),
        "individual_analyses": format_infos,
        "comparison": comparison,
    }


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) > 1:
        path = sys.argv[1]
        if Path(path).is_file():
            detector = TSVFormatDetector()
            result = detector.analyze_file(path)
            print(f"Format: {result.format_type}")
            print(f"Columns: {result.total_columns}")
            print(f"Compatibility: {result.compatibility_score:.2f}")
            print(f"Issues: {result.issues}")
        else:
            result = analyze_directory(path)
            print(f"Analyzed {result.get('files_analyzed', 0)} files")
            comparison = result.get("comparison", {})
            print(f"Compatible files: {comparison.get('compatible_files', 0)}")
            print(f"Recommendations: {comparison.get('recommendations', [])}")
    else:
        print("Usage: python format_detector.py <file_or_directory_path>")
