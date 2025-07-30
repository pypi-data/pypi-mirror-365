#!/usr/bin/env python3
"""Test script to regenerate the cross-chapter coreference network visualization."""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.append("src")

from visualization.interactive_visualizer import InteractiveVisualizer


def test_visualization():
    """Test the cross-chapter network visualization."""
    # Load the cross-chapter chains data
    chains_file = Path(
        "data/output/unified_analysis_20250729_123353/cross_chapter_chains.json"
    )
    stats_file = Path(
        "data/output/unified_analysis_20250729_123353/processing_statistics.json"
    )

    if not chains_file.exists():
        print(f"❌ Cross-chapter chains file not found: {chains_file}")
        return False

    if not stats_file.exists():
        print(f"❌ Processing statistics file not found: {stats_file}")
        return False

    # Load data
    with open(chains_file, encoding="utf-8") as f:
        cross_chapter_chains = json.load(f)

    with open(stats_file, encoding="utf-8") as f:
        stats_data = json.load(f)

    print(f"✅ Loaded {len(cross_chapter_chains)} cross-chapter chains")

    # Create mock relationships data from chapter info
    relationships_data = []
    chapter_info = stats_data.get("chapter_info", [])
    for chapter in chapter_info:
        # Create mock relationship entries for each chapter
        for i in range(min(10, chapter.get("relationships_count", 0))):
            relationships_data.append(
                {
                    "chapter_number": chapter["chapter_number"],
                    "pronoun_text": f"mock_pronoun_{i}",
                    "clause_mate_text": f"mock_clause_mate_{i}",
                }
            )

    print(f"✅ Created {len(relationships_data)} mock relationship entries")

    # Create visualizer
    output_dir = "data/output/test_visualization"
    visualizer = InteractiveVisualizer(output_dir)

    # Generate visualization
    try:
        output_file = visualizer.create_cross_chapter_network_visualization(
            cross_chapter_chains=cross_chapter_chains,
            relationships_data=relationships_data,
            output_filename="cross_chapter_network_fixed.html",
        )
        print(f"✅ Visualization created successfully: {output_file}")
        return True

    except Exception as e:
        print(f"❌ Error creating visualization: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_visualization()
    if success:
        print("\n🎉 Cross-chapter network visualization test completed successfully!")
    else:
        print("\n💥 Cross-chapter network visualization test failed!")
        sys.exit(1)
