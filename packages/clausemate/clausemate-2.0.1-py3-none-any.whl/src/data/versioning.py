"""Data management and versioning utilities for clause mate project."""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

# Version constants
VERSION = "1.0.0"
__version__ = VERSION


def get_version() -> str:
    """Get the current version string."""
    return VERSION


class DataVersionManager:
    """Manage data versions and provenance."""

    def __init__(self, data_dir: Path = Path("data")):
        self.data_dir = data_dir
        self.metadata_file = data_dir / "metadata.json"

    def compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA-256 hash of file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    def create_metadata(
        self,
        input_file: Path,
        output_file: Path,
        processing_config: Dict[str, Any],
        phase: str = "phase2",
    ) -> Dict[str, Any]:
        """Create metadata for a processing run."""
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "phase": phase,
            "input": {
                "file": str(input_file),
                "hash": self.compute_file_hash(input_file),
                "size_bytes": input_file.stat().st_size,
            },
            "output": {
                "file": str(output_file),
                "hash": (
                    self.compute_file_hash(output_file)
                    if output_file.exists()
                    else None
                ),
                "size_bytes": (
                    output_file.stat().st_size if output_file.exists() else None
                ),
            },
            "processing": processing_config,
            "environment": {
                "python_version": None,  # Can be filled by calling code
                "dependencies": {},  # Can be filled with version info
            },
        }

        if output_file.exists():
            # Add output statistics
            df = pd.read_csv(output_file)
            metadata["output"]["statistics"] = {
                "rows": len(df),
                "columns": len(df.columns),
                "unique_sentences": (
                    df["sentence_id"].nunique() if "sentence_id" in df.columns else None
                ),
                "unique_pronouns": (
                    df["pronoun_text"].nunique()
                    if "pronoun_text" in df.columns
                    else None
                ),
            }

        return metadata

    def save_metadata(self, metadata: Dict[str, Any]):
        """Save metadata to file."""
        # Load existing metadata
        existing_metadata = []
        if self.metadata_file.exists():
            with open(self.metadata_file) as f:
                existing_metadata = json.load(f)

        # Append new metadata
        existing_metadata.append(metadata)

        # Save updated metadata
        with open(self.metadata_file, "w") as f:
            json.dump(existing_metadata, f, indent=2)

    def validate_reproducibility(
        self, original_hash: str, new_output_file: Path
    ) -> bool:
        """Validate that new output matches original."""
        new_hash = self.compute_file_hash(new_output_file)
        return original_hash == new_hash

    def get_latest_metadata(
        self, phase: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get latest metadata for a specific phase."""
        if not self.metadata_file.exists():
            return None

        with open(self.metadata_file) as f:
            metadata_list = json.load(f)

        if phase:
            metadata_list = [m for m in metadata_list if m.get("phase") == phase]

        return metadata_list[-1] if metadata_list else None


def create_processing_config() -> Dict[str, Any]:
    """Create configuration dictionary for current processing run."""
    import platform
    import sys

    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "timestamp": datetime.now().isoformat(),
        "working_directory": str(Path.cwd()),
    }
