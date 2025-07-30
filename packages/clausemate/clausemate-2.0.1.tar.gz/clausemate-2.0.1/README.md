# Clause Mates Analyzer

<!-- Badges -->
<p align="left">
  <a href="https://github.com/jobschepens/clausemate/actions">
    <img src="https://github.com/jobschepens/clausemate/actions/workflows/python-app.yml/badge.svg" alt="Build Status">
  </a>
  <a href="https://codecov.io/gh/jobschepens/clausemate">
    <img src="https://codecov.io/gh/jobschepens/clausemate/branch/main/graph/badge.svg" alt="Coverage">
  </a>
  <a href="https://www.python.org/downloads/release/python-3110/">
    <img src="https://img.shields.io/badge/python-3.11%2B-blue.svg" alt="Python 3.11+">
  </a>
  <a href="https://github.com/charliermarsh/ruff">
    <img src="https://img.shields.io/badge/linting-ruff-%23f7ca18" alt="Ruff Linting">
  </a>
  <a href="https://pre-commit.com/">
    <img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit" alt="pre-commit">
  </a>
  <a href="https://github.com/jobschepens/clausemate/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-research-lightgrey.svg" alt="License">
  </a>
  <a href="https://github.com/jobschepens/clausemate/tree/main/docs">
    <img src="https://img.shields.io/badge/docs-available-brightgreen.svg" alt="Docs">
  </a>
</p>

> **⚠️ Disclaimer**: This repository contains experimental research code developed through iterative "vibe coding" sessions. While the functionality is complete and tested, the codebase reflects rapid prototyping, multiple refactoring attempts, and exploratory development. Code quality and organization may vary across different phases of development. Use with appropriate expectations for research/experimental software.

A Python tool for extracting and analyzing clause mate relationships from German pronoun data for linguistic research.

## Project Status

- ✅ **Phase 1 Complete**: Self-contained monolithic version with full functionality
- ✅ **Phase 2 Complete**: Modular architecture with adaptive parsing and 100% file compatibility
- ✅ **Phase 3.1 Complete**: Unified multi-file processing with cross-chapter coreference resolution
- ✅ **Documentation Complete**: Comprehensive format documentation for all supported file types
- ✅ **Deliverable Package Complete**: Professional HTML report with interactive visualizations ready for collaboration
- 📋 **Phase 3.2 Planned**: Advanced analytics and visualization features

> 📦 **Latest Achievement**: Complete deliverable package created with comprehensive HTML report, interactive visualizations, and professional documentation for collaborator delivery.

## Deliverable Package

A complete analysis package is available at [`data/output/deliverable_package_20250729/`](data/output/deliverable_package_20250729/) containing:

- **📊 Comprehensive HTML Report**: Interactive analysis with embedded visualizations
- **📈 Network Visualizations**: Character relationships and cross-chapter connections
- **📋 Complete Dataset**: 1,904 unified relationships in CSV format
- **📖 Documentation**: README and delivery summary for collaborators

> 🎯 **Ready for Delivery**: The package contains everything needed for collaborative analysis and can be shared independently.

## Description

This tool analyzes German pronouns and their clause mates in annotated linguistic data. It identifies critical pronouns (personal, demonstrative, and d-pronouns) and extracts their relationships with other referential expressions in the same sentence.

### Critical Pronouns Analyzed

- **Third person personal**: er, sie, es, ihm, ihr, ihn, ihnen
- **D-pronouns (pronominal)**: der, die, das, dem, den, deren, dessen, derer
- **Demonstrative**: dieser, diese, dieses, diesem, diesen

## Features

- **Unified Multi-File Processing**: Process all 4 chapter files as a single unified dataset
- **Cross-Chapter Coreference Resolution**: Identify and resolve coreference chains spanning multiple files
- **Adaptive TSV Parsing**: Supports multiple WebAnno TSV 3.3 format variations (12-38 columns)
- **Automatic Format Detection**: Preamble-based dynamic column mapping
- **100% File Compatibility**: Works with standard, extended, legacy, and incomplete formats
- **Cross-sentence Analysis**: Antecedent detection with 94.4% success rate
- **Single Unified Output**: One comprehensive file instead of four separate outputs
- **Comprehensive Documentation**: Detailed format specifications for all supported files
- **Robust Error Handling**: Graceful degradation and clear user feedback
- **Type-safe Implementation**: Full type hints and comprehensive testing
- **Timestamped Output**: Automatic organization with date/time-stamped directories

## Supported File Formats

| Format | Columns | Description | Relationships | Status |
|--------|---------|-------------|---------------|---------|
| **Standard** | 15 | Basic linguistic annotations | 448 | ✅ Fully supported |
| **Extended** | 37 | Rich morphological features | 234 | ✅ Fully supported |
| **Legacy** | 14 | Compact annotation set | 527 | ✅ Fully supported |
| **Incomplete** | 12 | Limited annotations | 695 | ✅ Graceful handling |

> 📊 **Format Documentation**: See [`data/input/FORMAT_OVERVIEW.md`](data/input/FORMAT_OVERVIEW.md) for comprehensive technical specifications.

## Project Structure

```
├── src/                        # Phase 3.1 - Complete unified processing architecture
│   ├── main.py                     # Main orchestrator with adaptive parsing
│   ├── config.py                   # Generalized configuration system
│   ├── multi_file/                 # Multi-file processing components (Phase 3.1)
│   │   ├── multi_file_batch_processor.py   # Unified multi-file coordinator
│   │   ├── unified_sentence_manager.py     # Global sentence numbering
│   │   ├── cross_file_coreference_resolver.py # Cross-chapter chain resolution
│   │   ├── unified_relationship_model.py   # Extended relationship data model
│   │   └── __init__.py                     # Multi-file module exports
│   ├── parsers/                    # Adaptive TSV parsing components
│   │   ├── adaptive_tsv_parser.py      # Preamble-based dynamic parsing
│   │   ├── incomplete_format_parser.py # Specialized incomplete format handler
│   │   ├── preamble_parser.py          # WebAnno schema extraction
│   │   └── tsv_parser.py               # Legacy parser (fallback)
│   ├── extractors/                 # Feature extraction components
│   ├── utils/                      # Format detection and utilities
│   │   └── format_detector.py          # Automatic format analysis
│   └── data/                       # Data models and structures
├── scripts/                    # Executable scripts and utilities
│   ├── run_multi_file_analysis.py     # Production multi-file processing interface
│   ├── enhanced_cross_chapter_analysis.py # Enhanced cross-chapter analysis
│   ├── generate_advanced_analysis_simple.py # Advanced analysis generator
│   └── generate_visualizations.py     # Visualization generation
├── analysis/                   # Analysis scripts and tools
│   ├── analyze_4tsv_detailed.py       # Detailed TSV format analysis
│   ├── analyze_column_mapping.py      # Column mapping analysis
│   └── analyze_preambles.py           # Preamble structure analysis
├── tests/                      # Comprehensive test suite
│   ├── test_multi_file_processing.py  # Multi-file processing tests
│   ├── test_cross_chapter_coreference.py # Cross-chapter tests
│   └── test_4tsv_processing.py        # TSV format tests
├── logs/                       # Log files and execution records
│   ├── multi_file_analysis.log        # Multi-file processing logs
│   └── visualization_generation.log   # Visualization generation logs
├── data/                       # Input and output data
│   ├── input/                      # Source TSV files with documentation
│   │   ├── FORMAT_OVERVIEW.md          # Comprehensive format comparison
│   │   ├── gotofiles/                  # Standard and extended formats
│   │   │   ├── 2.tsv_DOCUMENTATION.md      # Standard format (15 cols)
│   │   │   └── later/                      # Alternative formats
│   │   │       ├── 1.tsv_DOCUMENTATION.md      # Extended format (37 cols)
│   │   │       ├── 3.tsv_DOCUMENTATION.md      # Legacy format (14 cols)
│   │   │       └── 4.tsv_DOCUMENTATION.md      # Incomplete format (12 cols)
│   └── output/                     # Analysis results and deliverables
│       ├── deliverable_package_20250729/   # 📦 COMPLETE DELIVERABLE PACKAGE
│       │   ├── comprehensive_analysis_report.html  # Interactive HTML report
│       │   ├── unified_relationships.csv           # Complete dataset (1,904 relationships)
│       │   ├── visualizations_20250729_123445/     # Interactive network visualizations
│       │   ├── README.md                           # Package documentation
│       │   └── DELIVERY_SUMMARY.md                 # Delivery instructions
│       └── unified_analysis_20250729_123353/       # Latest raw analysis results
├── tools/                      # Development and utility tools
│   └── temp_files/                 # Temporary files and cleanup
├── docs/                       # Project documentation
│   ├── MULTI_FILE_PROCESSING_DOCUMENTATION.md # Multi-file architecture guide
│   ├── unified_multi_file_processing_plan.md # Implementation plan
│   ├── 4tsv_analysis_specification.md # TSV format specifications
│   └── cross_chapter_coreference_analysis_spec.md # Cross-chapter analysis spec
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd clause-mates-analyzer
   ```

2. **Set up environment** (choose one):

   **Option A: pip (recommended)**
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate

   pip install -e .[dev,benchmark]
   ```

   **Option B: conda**
   ```bash
   conda env create -f environment.yml
   conda activate clausemate
   ```

## Usage

### Multi-File Processing (Phase 3.1) - **RECOMMENDED**

Process all 4 chapter files as a unified dataset with cross-chapter coreference resolution:

```bash
# Unified multi-file processing (all chapters as single dataset)
python scripts/run_multi_file_analysis.py

# With verbose logging
python scripts/run_multi_file_analysis.py --verbose

# Custom output directory
python scripts/run_multi_file_analysis.py --output-dir custom_output
```

**Output**: Single unified file with all 1,904 relationships + 36 cross-chapter chains
- Creates timestamped directory: `data/output/unified_analysis_YYYYMMDD_HHMMSS/`
- **unified_relationships.csv**: Main CSV output with source file metadata
- **unified_relationships.json**: JSON format with complete relationship data
- **cross_chapter_statistics.json**: Cross-chapter chain resolution statistics

### Single File Processing (Phase 2)

Process individual files with automatic format detection:

```bash
# Individual file processing with adaptive parsing
python src/main.py data/input/gotofiles/2.tsv                    # Standard format
python src/main.py data/input/gotofiles/later/1.tsv              # Extended format
python src/main.py data/input/gotofiles/later/3.tsv              # Legacy format
python src/main.py data/input/gotofiles/later/4.tsv              # Incomplete format

# Force legacy parser (disable adaptive features)
python src/main.py --disable-adaptive data/input/gotofiles/2.tsv

# Verbose output with format detection details
python src/main.py --verbose data/input/gotofiles/later/1.tsv
```

**Output**: Individual timestamped directories in `data/output/YYYYMMDD_HHMMSS/`

### Analysis Results Comparison

#### Unified Multi-File Processing (Recommended)

| **Unified Output** | **Total** | **Cross-Chapter Chains** | **Processing Time** |
|-------------------|-----------|--------------------------|-------------------|
| **All 4 Chapters** | **1,904 relationships** | **36 unified chains** | **~12 seconds** |

#### Individual File Processing

| File | Format | Sentences | Tokens | Relationships | Coreference Chains |
|------|--------|-----------|--------|---------------|-------------------|
| **2.tsv** | Standard | 222 | 3,665 | **448** | 235 |
| **1.tsv** | Extended | 127 | 2,267 | **234** | 195 |
| **3.tsv** | Legacy | 207 | 3,786 | **527** | 244 |
| **4.tsv** | Incomplete | 243 | 4,412 | **695** | 245 |

> 💡 **Recommendation**: Use multi-file processing for complete narrative analysis with cross-chapter relationships. Individual processing is available for specific chapter analysis or debugging.

### Analysis Tools

```bash
# Generate comprehensive analysis reports
python analysis/analyze_4tsv_detailed.py

# Analyze column mappings and format compatibility
python analysis/analyze_column_mapping.py

# Analyze preamble structures
python analysis/analyze_preambles.py

# Generate advanced analysis with visualizations
python scripts/generate_advanced_analysis_simple.py

# Create interactive visualizations
python scripts/generate_visualizations.py
```

### Testing

```bash
# Run all tests
python -m pytest

# Run specific test categories
python -m pytest tests/test_4tsv_processing.py
python -m pytest tests/test_multi_file_processing.py
python -m pytest tests/test_cross_chapter_coreference.py

# Run with verbose output
python -m pytest -v

# Run with coverage
python -m pytest --cov=src
```

## Development

### Quick Start

```bash
# Install development dependencies
pip install -e .[dev,benchmark]

# Run quality checks
nox                      # Run default sessions (lint, test)
nox -s lint              # Fast ruff linting
nox -s format            # Code formatting
nox -s test              # Run tests
nox -s ci                # Full CI pipeline

# Run tests directly
pytest
```

### Code Quality

This project uses **ruff** for fast, comprehensive code quality checking and formatting:

- **ruff**: Fast linting and formatting (replaces black, isort, flake8)
- **mypy**: Type checking
- **pytest**: Testing framework
- **pre-commit**: Git hooks for quality assurance

## Requirements

- **Python**: 3.8+
- **Core Dependencies**: pandas, standard library modules
- **Development**: ruff, mypy, pytest, pre-commit

## Contributing

This is a research project. For contributions:

1. Follow the established code style and type hints
2. Add tests for new functionality
3. Update documentation as needed
4. Ensure backward compatibility with existing data

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for detailed setup instructions.

## Reproducibility

For exact result reproduction, see [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) for step-by-step instructions using locked dependencies and reference outputs.

## License

Research project - please contact maintainers for usage permissions.

## Contact

For questions about the linguistic methodology or data format, please refer to the project documentation or contact the research team.
