#!/usr/bin/env python3
"""Interactive Visualization System for Multi-File Clause Mates Analysis.

This module provides comprehensive visualization capabilities including:
- Cross-chapter coreference chain visualization
- Interactive relationship network graphs
- Chapter-by-chapter analysis reports
- Comparative analysis dashboards

Author: Kilo Code
Version: 3.1 - Visualization and Reporting Implementation
Date: 2025-07-28
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# For generating HTML visualizations
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <link href="https://unpkg.com/vis-network/styles/vis-network.css" rel="stylesheet" type="text/css" />
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .network-container {{ height: 600px; border: 1px solid #ddd; margin: 20px 0; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #007bff; }}
        .stat-value {{ font-size: 2em; font-weight: bold; color: #007bff; }}
        .stat-label {{ color: #666; margin-top: 5px; }}
        .chapter-section {{ margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 5px; }}
        .controls {{ margin: 20px 0; padding: 15px; background: #e9ecef; border-radius: 5px; }}
        .btn {{ padding: 8px 16px; margin: 5px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }}
        .btn:hover {{ background: #0056b3; }}
        .legend {{ display: flex; flex-wrap: wrap; gap: 15px; margin: 15px 0; }}
        .legend-item {{ display: flex; align-items: center; }}
        .legend-color {{ width: 20px; height: 20px; border-radius: 50%; margin-right: 8px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ padding: 8px 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f8f9fa; font-weight: bold; }}
        .highlight {{ background-color: #fff3cd; }}
    </style>
</head>
<body>
    <div class="container">
        {content}
    </div>
    <script>
        {script}
    </script>
</body>
</html>
"""


class InteractiveVisualizer:
    """Interactive visualization system for multi-file clause mates analysis."""

    def __init__(self, output_dir: str):
        """Initialize the interactive visualizer.

        Args:
            output_dir: Directory for output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

    def create_cross_chapter_network_visualization(
        self,
        cross_chapter_chains: Dict[str, List[str]],
        relationships_data: List[Dict[str, Any]],
        output_filename: str = "cross_chapter_network.html",
    ) -> str:
        """Create interactive cross-chapter coreference network visualization.

        Args:
            cross_chapter_chains: Cross-chapter chain data
            relationships_data: Relationship data for context
            output_filename: Name of output HTML file

        Returns:
            Path to created HTML file
        """
        output_path = self.output_dir / output_filename

        # Prepare network data
        nodes = []
        edges = []

        # Extract chapter information from relationships data
        chapters = set()
        for rel in relationships_data:
            chapter_num = rel.get("chapter_number", 1)
            chapters.add(chapter_num)

        # If no chapters found in relationships, assume we have 4 chapters based on the data structure
        if not chapters:
            chapters = {1, 2, 3, 4}

        chapter_colors = {1: "#FF6B6B", 2: "#4ECDC4", 3: "#45B7D1", 4: "#96CEB4"}

        # Create chapter nodes
        for chapter in sorted(chapters):
            nodes.append(
                {
                    "id": f"chapter_{chapter}",
                    "label": f"Chapter {chapter}",
                    "group": "chapter",
                    "color": chapter_colors.get(chapter, "#999999"),
                    "size": 30,
                    "font": {"size": 16, "color": "white"},
                }
            )

        # Create chain nodes and edges
        # Since all chains in cross_chapter_chains are by definition cross-chapter,
        # we'll connect each chain to all chapters (simplified approach)
        chain_count = 0
        for chain_id, entities in cross_chapter_chains.items():
            if len(entities) > 1:  # Only chains with multiple entities
                chain_count += 1
                # Create chain node
                chain_node_id = f"chain_{chain_id}"
                nodes.append(
                    {
                        "id": chain_node_id,
                        "label": f"Chain {chain_id.replace('unified_chain_', '')}",
                        "group": "chain",
                        "color": "#FFA500",
                        "size": max(
                            10, min(20, len(entities) * 2)
                        ),  # Size based on entity count
                        "font": {"size": 12},
                        "title": f"Chain {chain_id}: {len(entities)} entities",
                    }
                )

                # Connect chain to all chapters (simplified approach since we don't have
                # specific chapter information for each entity)
                for chapter in sorted(chapters):
                    edges.append(
                        {
                            "from": chain_node_id,
                            "to": f"chapter_{chapter}",
                            "color": {"color": "#999999", "opacity": 0.4},
                            "width": 1,
                        }
                    )

        # Generate HTML content
        content = f"""
        <div class="header">
            <h1>Cross-Chapter Coreference Network</h1>
            <p>Interactive visualization of coreference chains spanning multiple chapters</p>
            <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{len(chapters)}</div>
                <div class="stat-label">Total Chapters</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(cross_chapter_chains)}</div>
                <div class="stat-label">Cross-Chapter Chains</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{sum(len(entities) for entities in cross_chapter_chains.values())}</div>
                <div class="stat-label">Total Connections</div>
            </div>
        </div>

        <div class="legend">
            <div class="legend-item">
                <div class="legend-color" style="background-color: #FF6B6B;"></div>
                <span>Chapter 1</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #4ECDC4;"></div>
                <span>Chapter 2</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #45B7D1;"></div>
                <span>Chapter 3</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #96CEB4;"></div>
                <span>Chapter 4</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #FFA500;"></div>
                <span>Coreference Chain</span>
            </div>
        </div>

        <div class="controls">
            <button class="btn" onclick="fitNetwork()">Fit to Screen</button>
            <button class="btn" onclick="togglePhysics()">Toggle Physics</button>
            <button class="btn" onclick="exportNetwork()">Export Image</button>
        </div>

        <div id="network" class="network-container"></div>

        <div class="chapter-section">
            <h3>Chain Details</h3>
            <div id="chain-details">
                <p>Click on a chain node to see detailed information.</p>
            </div>
        </div>
        """

        # Generate JavaScript
        script = f"""
        const nodes = new vis.DataSet({json.dumps(nodes)});
        const edges = new vis.DataSet({json.dumps(edges)});
        const data = {{ nodes: nodes, edges: edges }};

        const options = {{
            nodes: {{
                shape: 'dot',
                scaling: {{
                    min: 10,
                    max: 30
                }},
                font: {{
                    size: 12,
                    face: 'Arial'
                }}
            }},
            edges: {{
                width: 2,
                color: {{ inherit: 'from' }},
                smooth: {{
                    type: 'continuous'
                }}
            }},
            physics: {{
                stabilization: {{ iterations: 150 }},
                barnesHut: {{
                    gravitationalConstant: -8000,
                    springConstant: 0.001,
                    springLength: 200
                }}
            }},
            interaction: {{
                hover: true,
                tooltipDelay: 200
            }}
        }};

        const container = document.getElementById('network');
        const network = new vis.Network(container, data, options);

        let physicsEnabled = true;

        function fitNetwork() {{
            network.fit();
        }}

        function togglePhysics() {{
            physicsEnabled = !physicsEnabled;
            network.setOptions({{ physics: {{ enabled: physicsEnabled }} }});
        }}

        function exportNetwork() {{
            // This would require additional libraries for image export
            alert('Export functionality would require additional libraries');
        }}

        network.on('click', function(params) {{
            if (params.nodes.length > 0) {{
                const nodeId = params.nodes[0];
                if (nodeId.startsWith('chain_')) {{
                    const chainId = nodeId.replace('chain_', '');
                    showChainDetails(chainId);
                }}
            }}
        }});

        function showChainDetails(chainId) {{
            const chainData = {json.dumps(cross_chapter_chains)};
            const entities = chainData[chainId] || [];

            let detailsHtml = `<h4>Chain ${{chainId}}</h4>`;
            detailsHtml += `<p><strong>Entities:</strong> ${{entities.length}}</p>`;
            detailsHtml += '<ul>';
            entities.forEach(entity => {{
                detailsHtml += `<li>${{entity}}</li>`;
            }});
            detailsHtml += '</ul>';

            document.getElementById('chain-details').innerHTML = detailsHtml;
        }}
        """

        # Write HTML file
        html_content = HTML_TEMPLATE.format(
            title="Cross-Chapter Coreference Network", content=content, script=script
        )

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        self.logger.info(f"Cross-chapter network visualization created: {output_path}")
        return str(output_path)

    def create_chapter_analysis_reports(
        self,
        relationships_data: List[Dict[str, Any]],
        processing_stats: Dict[str, Any],
        output_filename: str = "chapter_analysis_reports.html",
    ) -> str:
        """Create comprehensive chapter-by-chapter analysis reports.

        Args:
            relationships_data: Relationship data
            processing_stats: Processing statistics
            output_filename: Name of output HTML file

        Returns:
            Path to created HTML file
        """
        output_path = self.output_dir / output_filename

        # Analyze data by chapter
        chapter_stats = {}
        for rel in relationships_data:
            chapter = rel.get("chapter_number", 1)
            if chapter not in chapter_stats:
                chapter_stats[chapter] = {
                    "relationships": 0,
                    "pronouns": set(),
                    "clause_mates": set(),
                    "cross_chapter": 0,
                    "sentences": set(),
                }

            chapter_stats[chapter]["relationships"] += 1
            chapter_stats[chapter]["pronouns"].add(rel.get("pronoun_text", ""))
            chapter_stats[chapter]["clause_mates"].add(rel.get("clause_mate_text", ""))
            chapter_stats[chapter]["sentences"].add(rel.get("sentence_num", 0))

            if rel.get("cross_chapter_relationship", False):
                chapter_stats[chapter]["cross_chapter"] += 1

        # Convert sets to counts
        for chapter in chapter_stats:
            chapter_stats[chapter]["unique_pronouns"] = len(
                chapter_stats[chapter]["pronouns"]
            )
            chapter_stats[chapter]["unique_clause_mates"] = len(
                chapter_stats[chapter]["clause_mates"]
            )
            chapter_stats[chapter]["unique_sentences"] = len(
                chapter_stats[chapter]["sentences"]
            )
            del chapter_stats[chapter]["pronouns"]
            del chapter_stats[chapter]["clause_mates"]
            del chapter_stats[chapter]["sentences"]

        # Generate chapter reports
        chapter_reports = ""
        for chapter in sorted(chapter_stats.keys()):
            stats = chapter_stats[chapter]

            chapter_reports += f"""
            <div class="chapter-section">
                <h3>Chapter {chapter} Analysis</h3>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">{stats["relationships"]}</div>
                        <div class="stat-label">Total Relationships</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{stats["unique_pronouns"]}</div>
                        <div class="stat-label">Unique Pronouns</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{stats["unique_clause_mates"]}</div>
                        <div class="stat-label">Unique Clause Mates</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{stats["cross_chapter"]}</div>
                        <div class="stat-label">Cross-Chapter Links</div>
                    </div>
                </div>

                <div style="margin-top: 15px;">
                    <strong>Density Metrics:</strong>
                    <ul>
                        <li>Relationships per sentence: {stats["relationships"] / max(stats["unique_sentences"], 1):.2f}</li>
                        <li>Cross-chapter percentage: {(stats["cross_chapter"] / max(stats["relationships"], 1) * 100):.1f}%</li>
                        <li>Pronoun diversity: {stats["unique_pronouns"] / max(stats["relationships"], 1):.2f}</li>
                    </ul>
                </div>
            </div>
            """

        # Generate HTML content
        content = f"""
        <div class="header">
            <h1>Chapter-by-Chapter Analysis Reports</h1>
            <p>Comprehensive analysis of each chapter's coreference patterns</p>
            <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{len(chapter_stats)}</div>
                <div class="stat-label">Total Chapters</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{sum(stats["relationships"] for stats in chapter_stats.values())}</div>
                <div class="stat-label">Total Relationships</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{sum(stats["cross_chapter"] for stats in chapter_stats.values())}</div>
                <div class="stat-label">Cross-Chapter Links</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{processing_stats.get("processing_time_seconds", 0):.2f}s</div>
                <div class="stat-label">Processing Time</div>
            </div>
        </div>

        {chapter_reports}

        <div class="chapter-section">
            <h3>Comparative Analysis</h3>
            <canvas id="comparisonChart" width="800" height="400"></canvas>
        </div>
        """

        # Generate JavaScript for charts
        script = f"""
        const chapterData = {json.dumps(chapter_stats)};

        // Simple bar chart using canvas
        const canvas = document.getElementById('comparisonChart');
        const ctx = canvas.getContext('2d');

        const chapters = Object.keys(chapterData).sort();
        const relationships = chapters.map(ch => chapterData[ch].relationships);
        const maxRel = Math.max(...relationships);

        const barWidth = 150;
        const barSpacing = 50;
        const chartHeight = 300;
        const chartTop = 50;

        // Draw bars
        chapters.forEach((chapter, index) => {{
            const x = 50 + index * (barWidth + barSpacing);
            const barHeight = (relationships[index] / maxRel) * chartHeight;
            const y = chartTop + chartHeight - barHeight;

            // Bar
            ctx.fillStyle = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'][index] || '#999';
            ctx.fillRect(x, y, barWidth, barHeight);

            // Label
            ctx.fillStyle = '#333';
            ctx.font = '14px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(`Chapter ${{chapter}}`, x + barWidth/2, chartTop + chartHeight + 20);
            ctx.fillText(relationships[index], x + barWidth/2, y - 10);
        }});

        // Title
        ctx.fillStyle = '#333';
        ctx.font = 'bold 16px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('Relationships per Chapter', canvas.width/2, 30);
        """

        # Write HTML file
        html_content = HTML_TEMPLATE.format(
            title="Chapter Analysis Reports", content=content, script=script
        )

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        self.logger.info(f"Chapter analysis reports created: {output_path}")
        return str(output_path)

    def create_comparative_dashboard(
        self,
        relationships_data: List[Dict[str, Any]],
        cross_chapter_chains: Dict[str, List[str]],
        processing_stats: Dict[str, Any],
        output_filename: str = "comparative_dashboard.html",
    ) -> str:
        """Create comprehensive comparative analysis dashboard.

        Args:
            relationships_data: Relationship data
            cross_chapter_chains: Cross-chapter chain data
            processing_stats: Processing statistics
            output_filename: Name of output HTML file

        Returns:
            Path to created HTML file
        """
        output_path = self.output_dir / output_filename

        # Analyze comparative metrics
        chapter_metrics = {}
        pronoun_types = {}

        for rel in relationships_data:
            chapter = rel.get("chapter_number", 1)
            pronoun_type = rel.get("pronoun_coreference_type", "Unknown")

            if chapter not in chapter_metrics:
                chapter_metrics[chapter] = {
                    "total_relationships": 0,
                    "cross_chapter": 0,
                    "pronoun_types": {},
                    "avg_distance": [],
                    "givenness_types": {},
                }

            chapter_metrics[chapter]["total_relationships"] += 1

            if rel.get("cross_chapter_relationship", False):
                chapter_metrics[chapter]["cross_chapter"] += 1

            # Pronoun type analysis
            if pronoun_type not in chapter_metrics[chapter]["pronoun_types"]:
                chapter_metrics[chapter]["pronoun_types"][pronoun_type] = 0
            chapter_metrics[chapter]["pronoun_types"][pronoun_type] += 1

            # Global pronoun type tracking
            if pronoun_type not in pronoun_types:
                pronoun_types[pronoun_type] = 0
            pronoun_types[pronoun_type] += 1

            # Distance analysis
            distance = rel.get("pronoun_most_recent_antecedent_distance", 0)
            if isinstance(distance, (int, float)) and distance > 0:
                chapter_metrics[chapter]["avg_distance"].append(distance)

            # Givenness analysis
            givenness = rel.get("pronoun_givenness", "unknown")
            if givenness not in chapter_metrics[chapter]["givenness_types"]:
                chapter_metrics[chapter]["givenness_types"][givenness] = 0
            chapter_metrics[chapter]["givenness_types"][givenness] += 1

        # Calculate averages
        for chapter in chapter_metrics:
            distances = chapter_metrics[chapter]["avg_distance"]
            chapter_metrics[chapter]["avg_distance"] = (
                sum(distances) / len(distances) if distances else 0
            )

        # Generate dashboard content
        content = f"""
        <div class="header">
            <h1>Comparative Analysis Dashboard</h1>
            <p>Comprehensive comparison across all chapters</p>
            <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{len(chapter_metrics)}</div>
                <div class="stat-label">Chapters Analyzed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{sum(metrics["total_relationships"] for metrics in chapter_metrics.values())}</div>
                <div class="stat-label">Total Relationships</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(cross_chapter_chains)}</div>
                <div class="stat-label">Cross-Chapter Chains</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(pronoun_types)}</div>
                <div class="stat-label">Pronoun Types</div>
            </div>
        </div>

        <div class="chapter-section">
            <h3>Chapter Comparison Matrix</h3>
            <table>
                <thead>
                    <tr>
                        <th>Chapter</th>
                        <th>Total Relationships</th>
                        <th>Cross-Chapter Links</th>
                        <th>Cross-Chapter %</th>
                        <th>Avg. Distance</th>
                        <th>Dominant Pronoun Type</th>
                    </tr>
                </thead>
                <tbody>
        """

        for chapter in sorted(chapter_metrics.keys()):
            metrics = chapter_metrics[chapter]
            cross_chapter_pct = (
                metrics["cross_chapter"] / max(metrics["total_relationships"], 1)
            ) * 100

            # Find dominant pronoun type
            dominant_pronoun = (
                max(metrics["pronoun_types"].items(), key=lambda x: x[1])[0]
                if metrics["pronoun_types"]
                else "None"
            )

            content += f"""
                    <tr>
                        <td>Chapter {chapter}</td>
                        <td>{metrics["total_relationships"]}</td>
                        <td>{metrics["cross_chapter"]}</td>
                        <td>{cross_chapter_pct:.1f}%</td>
                        <td>{metrics["avg_distance"]:.1f}</td>
                        <td>{dominant_pronoun}</td>
                    </tr>
            """

        content += """
                </tbody>
            </table>
        </div>

        <div class="chapter-section">
            <h3>Pronoun Type Distribution</h3>
            <canvas id="pronounChart" width="800" height="400"></canvas>
        </div>

        <div class="chapter-section">
            <h3>Cross-Chapter Connectivity</h3>
            <canvas id="connectivityChart" width="800" height="400"></canvas>
        </div>

        <div class="chapter-section">
            <h3>Processing Performance</h3>
            <div class="stats-grid">
        """

        # Add performance metrics
        total_time = processing_stats.get("processing_time_seconds", 0)
        total_relationships = sum(
            metrics["total_relationships"] for metrics in chapter_metrics.values()
        )

        content += f"""
                <div class="stat-card">
                    <div class="stat-value">{total_time:.2f}s</div>
                    <div class="stat-label">Total Processing Time</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{(total_relationships / max(total_time, 0.001)):.0f}</div>
                    <div class="stat-label">Relationships/Second</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{(total_time / len(chapter_metrics)):.2f}s</div>
                    <div class="stat-label">Avg Time/Chapter</div>
                </div>
            </div>
        </div>
        """

        # Generate JavaScript for charts
        script = f"""
        const chapterMetrics = {json.dumps(chapter_metrics)};
        const pronounTypes = {json.dumps(pronoun_types)};

        // Pronoun type pie chart
        const pronounCanvas = document.getElementById('pronounChart');
        const pronounCtx = pronounCanvas.getContext('2d');

        const pronounLabels = Object.keys(pronounTypes);
        const pronounCounts = Object.values(pronounTypes);
        const total = pronounCounts.reduce((a, b) => a + b, 0);

        const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFA500', '#FF69B4', '#32CD32', '#FFD700'];

        let currentAngle = 0;
        const centerX = pronounCanvas.width / 2;
        const centerY = pronounCanvas.height / 2;
        const radius = 120;

        pronounLabels.forEach((label, index) => {{
            const sliceAngle = (pronounCounts[index] / total) * 2 * Math.PI;

            // Draw slice
            pronounCtx.beginPath();
            pronounCtx.moveTo(centerX, centerY);
            pronounCtx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
            pronounCtx.closePath();
            pronounCtx.fillStyle = colors[index % colors.length];
            pronounCtx.fill();

            // Draw label
            const labelAngle = currentAngle + sliceAngle / 2;
            const labelX = centerX + Math.cos(labelAngle) * (radius + 30);
            const labelY = centerY + Math.sin(labelAngle) * (radius + 30);

            pronounCtx.fillStyle = '#333';
            pronounCtx.font = '12px Arial';
            pronounCtx.textAlign = 'center';
            pronounCtx.fillText(`${{label}} (${{pronounCounts[index]}})`, labelX, labelY);

            currentAngle += sliceAngle;
        }});

        // Title
        pronounCtx.fillStyle = '#333';
        pronounCtx.font = 'bold 16px Arial';
        pronounCtx.textAlign = 'center';
        pronounCtx.fillText('Pronoun Type Distribution', centerX, 30);

        // Connectivity chart
        const connectivityCanvas = document.getElementById('connectivityChart');
        const connectivityCtx = connectivityCanvas.getContext('2d');

        const chapters = Object.keys(chapterMetrics).sort();
        const crossChapterCounts = chapters.map(ch => chapterMetrics[ch].cross_chapter);
        const maxCount = Math.max(...crossChapterCounts);

        const barWidth = 120;
        const barSpacing = 80;
        const chartHeight = 250;
        const chartTop = 80;

        chapters.forEach((chapter, index) => {{
            const x = 100 + index * (barWidth + barSpacing);
            const barHeight = maxCount > 0 ? (crossChapterCounts[index] / maxCount) * chartHeight : 0;
            const y = chartTop + chartHeight - barHeight;

            // Bar
            connectivityCtx.fillStyle = colors[index % colors.length];
            connectivityCtx.fillRect(x, y, barWidth, barHeight);

            // Label
            connectivityCtx.fillStyle = '#333';
            connectivityCtx.font = '14px Arial';
            connectivityCtx.textAlign = 'center';
            connectivityCtx.fillText(`Chapter ${{chapter}}`, x + barWidth/2, chartTop + chartHeight + 25);
            connectivityCtx.fillText(crossChapterCounts[index], x + barWidth/2, y - 10);
        }});

        // Title
        connectivityCtx.fillStyle = '#333';
        connectivityCtx.font = 'bold 16px Arial';
        connectivityCtx.textAlign = 'center';
        connectivityCtx.fillText('Cross-Chapter Connectivity', connectivityCanvas.width/2, 50);
        """

        # Write HTML file
        html_content = HTML_TEMPLATE.format(
            title="Comparative Analysis Dashboard", content=content, script=script
        )

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        self.logger.info(f"Comparative dashboard created: {output_path}")
        return str(output_path)
