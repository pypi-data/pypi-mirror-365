"""Utilities package for the clause mates analyzer."""

# Import utility functions from the parent utils.py file
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path to import utils.py
utils_path = Path(__file__).parent.parent / "utils.py"
if utils_path.exists():
    import importlib.util

    spec = importlib.util.spec_from_file_location("utils_module", utils_path)
    if spec and spec.loader:
        utils_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(utils_module)

        extract_coreference_id = utils_module.extract_coreference_id
        extract_full_coreference_id = utils_module.extract_full_coreference_id
        extract_coreference_type = utils_module.extract_coreference_type
        determine_givenness = utils_module.determine_givenness
        extract_coref_base_and_occurrence = (
            utils_module.extract_coref_base_and_occurrence
        )
        extract_coref_link_numbers = utils_module.extract_coref_link_numbers
    else:
        # Fallback if spec creation fails
        def extract_coreference_id(value: str) -> Optional[str]:
            return None

        def extract_full_coreference_id(value: str) -> Optional[str]:
            return None

        def extract_coreference_type(value: str) -> Optional[str]:
            return None

        def determine_givenness(value: str) -> str:
            return "_"

        def extract_coref_base_and_occurrence(value: str):
            return None, None

        def extract_coref_link_numbers(value: str):
            return None, None
else:
    # Fallback if utils.py doesn't exist
    def extract_coreference_id(value: str) -> Optional[str]:
        return None

    def extract_full_coreference_id(value: str) -> Optional[str]:
        return None

    def extract_coreference_type(value: str) -> Optional[str]:
        return None

    def determine_givenness(value: str) -> str:
        return "_"

    def extract_coref_base_and_occurrence(value: str):
        return None, None

    def extract_coref_link_numbers(value: str):
        return None, None


__all__ = [
    "extract_coreference_id",
    "extract_full_coreference_id",
    "extract_coreference_type",
    "determine_givenness",
    "extract_coref_base_and_occurrence",
    "extract_coref_link_numbers",
]
