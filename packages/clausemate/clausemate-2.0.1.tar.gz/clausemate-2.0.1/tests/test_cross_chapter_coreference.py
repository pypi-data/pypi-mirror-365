#!/usr/bin/env python3
"""Cross-Chapter Coreference Chain Detection Script.

Tests whether coreference chains span across chapter boundaries
in the sequential book chapters (1.tsv → 2.tsv → 3.tsv → 4.tsv).

Uses production parsers and extractors to ensure data consistency.
"""

import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.data.models import ClauseMateRelationship
from src.main import ClauseMateAnalyzer
from src.utils.format_detector import TSVFormatDetector


@dataclass
class ChapterAnalysis:
    """Analysis results for a single chapter."""

    file_path: str
    chapter_num: int
    relationships: List[ClauseMateRelationship]
    sentence_range: Tuple[int, int]  # (min, max)
    total_sentences: int
    coreference_chains: Dict[str, List[Dict]]  # chain_id -> mentions
    chain_boundaries: Dict[str, Tuple[int, int]]  # chain_id -> (first_sent, last_sent)


class CrossChapterCoreferenceAnalyzer:
    """Analyzes coreference chains across multiple chapter files."""

    def __init__(self):
        """Initializes the analyzer."""
        self.chapter_files = [
            ("data/input/gotofiles/later/1.tsv", 1),  # Chapter 1
            ("data/input/gotofiles/2.tsv", 2),  # Chapter 2
            ("data/input/gotofiles/later/3.tsv", 3),  # Chapter 3
            ("data/input/gotofiles/later/4.tsv", 4),  # Chapter 4
        ]
        self.analyzer = ClauseMateAnalyzer(enable_adaptive_parsing=True)
        self.format_detector = TSVFormatDetector()
        self.chapter_analyses: List[ChapterAnalysis] = []
        self.cross_chapter_evidence: List[Dict] = []

    def run_analysis(self):
        """Main analysis method."""
        print("=" * 70)
        print("CROSS-CHAPTER COREFERENCE ANALYSIS")
        print("Using Production Parsers & Extractors")
        print("=" * 70)
        print()

        # 1. Analyze each chapter using production system
        print("📖 ANALYZING CHAPTERS WITH PRODUCTION SYSTEM...")
        for file_path, chapter_num in self.chapter_files:
            try:
                analysis = self.analyze_chapter(file_path, chapter_num)
                self.chapter_analyses.append(analysis)
                print(
                    f"✅ Chapter {chapter_num}: {len(analysis.relationships)} relationships, "
                    f"sentences {analysis.sentence_range[0]}-{analysis.sentence_range[1]}, "
                    f"{len(analysis.coreference_chains)} chains"
                )
            except Exception as e:
                print(f"❌ Chapter {chapter_num}: Error - {e}")

        print()

        # 2. Analyze sentence continuity
        print("🔢 ANALYZING SENTENCE CONTINUITY...")
        self.analyze_sentence_continuity()
        print()

        # 3. Extract coreference chain information
        print("🔗 EXTRACTING COREFERENCE CHAIN DATA...")
        self.extract_coreference_chains()
        print()

        # 4. Detect cross-chapter evidence
        print("🎯 DETECTING CROSS-CHAPTER EVIDENCE...")
        self.detect_cross_chapter_evidence()
        print()

        # 5. Generate comprehensive report
        print("📊 GENERATING ANALYSIS REPORT...")
        self.generate_report()

    def analyze_chapter(self, file_path: str, chapter_num: int) -> ChapterAnalysis:
        """Analyze a single chapter using production system."""
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Create fresh analyzer instance for each file to avoid parser state contamination
        # This ensures proper format detection and parsing for each file
        fresh_analyzer = ClauseMateAnalyzer(enable_adaptive_parsing=True)
        relationships = fresh_analyzer.analyze_file(file_path)

        # Extract sentence information from relationships
        sentence_numbers = []
        coreference_chains = defaultdict(list)

        for rel in relationships:
            # Extract sentence numbers from the relationship
            sentence_numbers.append(rel.sentence_num)

            # Extract coreference chain information from pronoun
            if (
                rel.pronoun.coreference_link
                and rel.pronoun.coreference_link != "_"
                and "->" in rel.pronoun.coreference_link
            ):
                chain_id = rel.pronoun.coreference_link.split("->")[1].split("-")[0]
                coreference_chains[chain_id].append(
                    {
                        "text": rel.pronoun.text,
                        "sentence": rel.sentence_num,
                        "type": "pronoun",
                        "position": rel.pronoun.idx,
                    }
                )

            # Extract chain ID from pronoun coreference type (e.g., "PersPron[127]")
            if rel.pronoun.coreference_type and rel.pronoun.coreference_type != "_":
                import re

                match = re.search(r"\[(\d+)\]", rel.pronoun.coreference_type)
                if match:
                    chain_id = match.group(1)
                    coreference_chains[chain_id].append(
                        {
                            "text": rel.pronoun.text,
                            "sentence": rel.sentence_num,
                            "type": "pronoun_type",
                            "position": rel.pronoun.idx,
                        }
                    )

            # Extract coreference information from clause mate
            if rel.clause_mate.coreference_id and rel.clause_mate.coreference_id != "_":
                chain_id = rel.clause_mate.coreference_id
                coreference_chains[chain_id].append(
                    {
                        "text": rel.clause_mate.text,
                        "sentence": rel.sentence_num,
                        "type": "clause_mate",
                        "position": rel.clause_mate.start_idx,
                    }
                )

        # Calculate sentence range and chain boundaries
        if sentence_numbers:
            sentence_range = (min(sentence_numbers), max(sentence_numbers))
            total_sentences = len(set(sentence_numbers))
        else:
            sentence_range = (0, 0)
            total_sentences = 0

        # Calculate chain boundaries
        chain_boundaries = {}
        for chain_id, mentions in coreference_chains.items():
            sentences = [m["sentence"] for m in mentions if m["sentence"]]
            if sentences:
                chain_boundaries[chain_id] = (min(sentences), max(sentences))

        return ChapterAnalysis(
            file_path=file_path,
            chapter_num=chapter_num,
            relationships=relationships,
            sentence_range=sentence_range,
            total_sentences=total_sentences,
            coreference_chains=dict(coreference_chains),
            chain_boundaries=chain_boundaries,
        )

    def analyze_sentence_continuity(self):
        """Analyze sentence numbering patterns across chapters."""
        print("Chapter sentence ranges:")

        for analysis in self.chapter_analyses:
            min_sent, max_sent = analysis.sentence_range
            print(
                f"  Chapter {analysis.chapter_num}: sentences {min_sent}-{max_sent} "
                f"({analysis.total_sentences} unique sentences)"
            )

        print("\nSentence continuity analysis:")

        for i in range(len(self.chapter_analyses) - 1):
            current = self.chapter_analyses[i]
            next_chapter = self.chapter_analyses[i + 1]

            current_max = current.sentence_range[1]
            next_min = next_chapter.sentence_range[0]

            if next_min == 1:
                continuity = "INDEPENDENT (restarts from 1)"
            elif next_min == current_max + 1:
                continuity = f"SEQUENTIAL (continues from {current_max})"
            elif next_min > current_max + 1:
                gap = next_min - current_max - 1
                continuity = f"GAP ({gap} sentences missing)"
            else:
                overlap = current_max - next_min + 1
                continuity = f"OVERLAP ({overlap} sentences)"

            print(
                f"  Chapter {current.chapter_num} → {next_chapter.chapter_num}: "
                f"{continuity}"
            )

    def extract_coreference_chains(self):
        """Extract and analyze coreference chain information."""
        print("Coreference chain summary by chapter:")

        for analysis in self.chapter_analyses:
            print(f"\n  Chapter {analysis.chapter_num}:")
            print(f"    Total chains: {len(analysis.coreference_chains)}")

            if analysis.coreference_chains:
                # Show chain statistics
                chain_lengths = [
                    len(mentions) for mentions in analysis.coreference_chains.values()
                ]
                avg_length = (
                    sum(chain_lengths) / len(chain_lengths) if chain_lengths else 0
                )
                print(f"    Average chain length: {avg_length:.1f} mentions")
                longest_chain = max(chain_lengths) if chain_lengths else 0
                print(f"    Longest chain: {longest_chain} mentions")

                # Show some example chains
                print("    Example chains:")
                for chain_id, mentions in list(analysis.coreference_chains.items())[:3]:
                    texts = [m["text"] for m in mentions if m["text"]]
                    sentences = [m["sentence"] for m in mentions if m["sentence"]]
                    if texts and sentences:
                        sent_range = f"{min(sentences)}-{max(sentences)}"
                        print(
                            f"      Chain {chain_id}: {texts} (sentences {sent_range})"
                        )

    def detect_cross_chapter_evidence(self):
        """Detect evidence of cross-chapter coreference chains."""
        cross_chapter_connections = []

        print("Analyzing potential cross-chapter connections...")

        for i in range(len(self.chapter_analyses) - 1):
            current = self.chapter_analyses[i]
            next_chapter = self.chapter_analyses[i + 1]

            print(f"\n🔍 Chapter {current.chapter_num} → {next_chapter.chapter_num}:")

            # Get chains near chapter boundaries
            boundary_threshold = 5  # sentences

            # Chains ending near end of current chapter
            current_max = current.sentence_range[1]
            ending_chains = {}
            for chain_id, (_, last_sent) in current.chain_boundaries.items():
                if last_sent >= current_max - boundary_threshold:
                    ending_chains[chain_id] = {
                        "chain_id": chain_id,
                        "last_sentence": last_sent,
                        "mentions": current.coreference_chains[chain_id],
                    }

            # Chains starting near beginning of next chapter
            next_min = next_chapter.sentence_range[0]
            starting_chains = {}
            for chain_id, (
                first_sent,
                _,
            ) in next_chapter.chain_boundaries.items():
                if first_sent <= next_min + boundary_threshold:
                    starting_chains[chain_id] = {
                        "chain_id": chain_id,
                        "first_sentence": first_sent,
                        "mentions": next_chapter.coreference_chains[chain_id],
                    }

            print(f"  Chains ending near boundary: {len(ending_chains)}")
            print(f"  Chains starting near boundary: {len(starting_chains)}")

            # Check for same chain IDs (strongest evidence)
            common_chain_ids = set(ending_chains.keys()).intersection(
                set(starting_chains.keys())
            )

            if common_chain_ids:
                print(f"  🎯 SAME CHAIN IDs FOUND: {len(common_chain_ids)} chains")
                for chain_id in common_chain_ids:
                    ending_chain = ending_chains[chain_id]
                    starting_chain = starting_chains[chain_id]

                    cross_chapter_connections.append(
                        {
                            "type": "same_chain_id",
                            "chain_id": chain_id,
                            "from_chapter": current.chapter_num,
                            "to_chapter": next_chapter.chapter_num,
                            "ending_sentence": ending_chain["last_sentence"],
                            "starting_sentence": starting_chain["first_sentence"],
                            "ending_mentions": ending_chain["mentions"],
                            "starting_mentions": starting_chain["mentions"],
                        }
                    )

                    print(
                        f"    Chain {chain_id}: ends at {ending_chain['last_sentence']} "
                        f"→ starts at {starting_chain['first_sentence']}"
                    )

            # Check for similar mention texts (supporting evidence)
            similar_connections = 0
            for ending_chain in ending_chains.values():
                ending_texts = {
                    m["text"].lower() for m in ending_chain["mentions"] if m["text"]
                }

                for starting_chain in starting_chains.values():
                    if starting_chain["chain_id"] != ending_chain["chain_id"]:
                        starting_texts = {
                            m["text"].lower()
                            for m in starting_chain["mentions"]
                            if m["text"]
                        }
                        common_texts = ending_texts.intersection(starting_texts)

                        if common_texts:
                            similar_connections += 1
                            cross_chapter_connections.append(
                                {
                                    "type": "similar_mentions",
                                    "from_chain": ending_chain["chain_id"],
                                    "to_chain": starting_chain["chain_id"],
                                    "from_chapter": current.chapter_num,
                                    "to_chapter": next_chapter.chapter_num,
                                    "common_texts": common_texts,
                                }
                            )

            if similar_connections > 0:
                print(f"  🔤 Similar mention connections: {similar_connections}")

        self.cross_chapter_evidence = cross_chapter_connections

        print(
            f"\n📊 TOTAL CROSS-CHAPTER EVIDENCE: {len(cross_chapter_connections)} "
            f"connections"
        )

    def generate_report(self):
        """Generate comprehensive analysis report."""
        print("\n" + "=" * 70)
        print("CROSS-CHAPTER COREFERENCE ANALYSIS REPORT")
        print("=" * 70)

        # System validation
        print("\n🔧 SYSTEM VALIDATION:")
        total_relationships = sum(len(a.relationships) for a in self.chapter_analyses)
        expected_total = 448 + 234 + 527 + 695  # Known totals from production system
        print(f"  Total relationships extracted: {total_relationships}")
        print(f"  Expected total (production): {expected_total}")

        if total_relationships == expected_total:
            print("  ✅ VALIDATION PASSED: Using production parsers correctly")
        else:
            print("  ⚠️  VALIDATION WARNING: Relationship count mismatch")

        # Chapter structure summary
        print("\n📖 CHAPTER STRUCTURE:")
        for analysis in self.chapter_analyses:
            min_sent, max_sent = analysis.sentence_range
            print(
                f"  Chapter {analysis.chapter_num} ({Path(analysis.file_path).name}): "
                f"{len(analysis.relationships)} relationships, "
                f"sentences {min_sent}-{max_sent}, "
                f"{len(analysis.coreference_chains)} coreference chains"
            )

        # Cross-chapter evidence analysis
        print("\n🔗 CROSS-CHAPTER EVIDENCE:")
        same_id_evidence = [
            e for e in self.cross_chapter_evidence if e["type"] == "same_chain_id"
        ]
        similar_mention_evidence = [
            e for e in self.cross_chapter_evidence if e["type"] == "similar_mentions"
        ]

        if self.cross_chapter_evidence:
            print(
                f"  ✅ EVIDENCE FOUND: {len(self.cross_chapter_evidence)} total "
                f"connections"
            )

            if same_id_evidence:
                print(
                    f"    🎯 Same Chain ID Evidence: {len(same_id_evidence)} connections"
                )
                print(
                    "      This is STRONG evidence for cross-chapter coreference chains!"
                )
                for evidence in same_id_evidence[:3]:  # Show first 3
                    print(
                        f"        Chain {evidence['chain_id']}: "
                        f"Chapter {evidence['from_chapter']} → {evidence['to_chapter']}"
                    )

            if similar_mention_evidence:
                print(
                    f"    🔤 Similar Mention Evidence: {len(similar_mention_evidence)} "
                    f"connections"
                )
                print(
                    "      This provides supporting evidence for character continuity."
                )
        else:
            print("  ❌ NO EVIDENCE FOUND: No cross-chapter connections detected.")

        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        if same_id_evidence:
            print("  ✅ UNIFIED PROCESSING STRONGLY RECOMMENDED")
            print("    - Clear evidence of coreference chains spanning chapters")
            print("    - Same chain IDs found across chapter boundaries")
            print("    - Implement cross-chapter coreference resolution")
            print("    - Use unified sentence numbering system")
            print("    - Create single output file with chapter metadata")

            confidence = "VERY HIGH"
        elif similar_mention_evidence:
            print("  ⚠️  UNIFIED PROCESSING RECOMMENDED")
            print("    - Some evidence of character continuity across chapters")
            print("    - Consider unified processing for better coherence")
            print("    - May benefit from cross-chapter entity resolution")

            confidence = "MEDIUM"
        else:
            print("  ℹ️  SEPARATE PROCESSING ACCEPTABLE")
            print("    - No clear evidence of cross-chapter coreference chains")
            print("    - Each chapter appears linguistically independent")
            print("    - Can process files separately if preferred")

            confidence = "HIGH (for independence)"

        print(f"\n🎯 CONFIDENCE LEVEL: {confidence}")

        # Next steps
        print("\n📋 NEXT STEPS:")
        if same_id_evidence:
            print("  1. ✅ PROCEED with unified multi-file processing implementation")
            print("  2. Design cross-chapter coreference resolution system")
            print("  3. Implement global sentence numbering")
            print("  4. Create unified output format with chapter source metadata")
            print("  5. Test with production data to validate cross-chapter chains")
        elif similar_mention_evidence:
            print("  1. Consider implementing unified processing")
            print("  2. Design optional cross-chapter entity linking")
            print("  3. Create combined output with chapter separation")
            print("  4. Allow both unified and separate processing modes")
        else:
            print("  1. Implement batch processing with separate outputs")
            print("  2. Create file aggregation without cross-chain resolution")
            print("  3. Maintain separate chain numbering per chapter")
            print("  4. Consider unified output format for convenience")

        print("\n🏁 ANALYSIS COMPLETE")
        print("=" * 70)


def main():
    """Run the cross-chapter coreference analysis."""
    analyzer = CrossChapterCoreferenceAnalyzer()

    try:
        analyzer.run_analysis()
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Analysis failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
