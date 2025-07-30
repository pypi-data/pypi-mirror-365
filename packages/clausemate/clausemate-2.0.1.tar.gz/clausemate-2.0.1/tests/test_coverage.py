import os
import sys

sys.path.append("src")

try:
    from main import ClauseMateAnalyzer

    analyzer = ClauseMateAnalyzer(enable_adaptive_parsing=True)
    print("✅ Main module imported successfully")

    # Try to run a simple analysis if data exists
    if os.path.exists("data/input/gotofiles/2.tsv"):
        relationships = analyzer.analyze_file("data/input/gotofiles/2.tsv")
        print(f"✅ Analysis completed: {len(relationships)} relationships found")
    else:
        print("⚠️ Test data not found, skipping analysis")

except Exception as e:
    print(f"❌ Test failed: {e}")
    sys.exit(1)
