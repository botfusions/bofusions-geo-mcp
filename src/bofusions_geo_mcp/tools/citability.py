"""geo_citability tool — Score content blocks for AI citation readiness."""

from __future__ import annotations

from ..client import fetch_page
from ..parser import extract_content_blocks, rebuild_minimal_html
from ..scoring import score_passage


async def run_citability(url: str) -> str:
    """Analyze page content blocks for AI citability."""
    page = await fetch_page(url)

    if page["status_code"] is None:
        return f"# Citability Analysis Error\n\nFailed to fetch `{url}`:\n- " + "\n- ".join(page.get("errors", []))

    # Extract content blocks using unified parser
    blocks = extract_content_blocks(
        rebuild_minimal_html(page["heading_structure"], page["text_content"])
    )

    # Filter out very short blocks
    blocks = [b for b in blocks if b["word_count"] >= 20]

    if not blocks:
        return f"# Citability Analysis: {url}\n\nNo analyzable content blocks found."

    # Score each block
    scored = [score_passage(b["content"], b["heading"]) for b in blocks]

    avg = sum(s["total_score"] for s in scored) / len(scored)
    grade_dist: dict[str, int] = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    for s in scored:
        grade_dist[s["grade"]] += 1

    top5 = sorted(scored, key=lambda x: x["total_score"], reverse=True)[:5]
    optimal = sum(1 for s in scored if 134 <= s["word_count"] <= 167)

    # Build markdown
    lines = [
        f"# AI Citability Analysis",
        f"",
        f"> **Bofusions GEO MCP** | `{url}`",
        f"",
        f"## Overview",
        f"",
        f"- **Blocks Analyzed**: {len(scored)}",
        f"- **Average Score**: {avg:.1f}/100",
        f"- **Optimal Length Passages** (134-167 words): {optimal}",
        f"",
        f"## Grade Distribution",
        f"",
        f"| Grade | Count | Label |",
        f"|-------|-------|-------|",
    ]
    for grade in ["A", "B", "C", "D", "F"]:
        count = grade_dist.get(grade, 0)
        labels = {"A": "Highly Citable", "B": "Good", "C": "Moderate", "D": "Low", "F": "Poor"}
        lines.append(f"| {grade} | {count} | {labels[grade]} |")

    lines.extend(["", "## Top 5 Most Citable Passages", ""])
    for i, block in enumerate(top5, 1):
        lines.append(f"### {i}. Score: {block['total_score']}/100 (Grade {block['grade']}) — {block['label']}")
        lines.append(f"")
        lines.append(f"- **Heading**: {block['heading'] or 'N/A'}")
        lines.append(f"- **Word Count**: {block['word_count']}")
        lines.append(f"- **Answer Block Quality**: {block['breakdown']['answer_block_quality']}/30")
        lines.append(f"- **Self-Containment**: {block['breakdown']['self_containment']}/25")
        lines.append(f"- **Structural Readability**: {block['breakdown']['structural_readability']}/20")
        lines.append(f"- **Statistical Density**: {block['breakdown']['statistical_density']}/15")
        lines.append(f"- **Uniqueness Signals**: {block['breakdown']['uniqueness_signals']}/10")
        lines.append(f"")
        lines.append(f"> {block['preview']}")
        lines.append("")

    # Recommendations
    lines.extend(["## Recommendations", ""])
    if optimal < len(scored) * 0.2:
        lines.append("- Restructure content into 134-167 word self-contained passages")
    if grade_dist.get("F", 0) > len(scored) * 0.3:
        lines.append("- Add more fact-rich, specific content with statistics and data points")
    if grade_dist.get("A", 0) == 0:
        lines.append("- Create definition-style answer blocks ('X is...', 'X refers to...')")
    lines.append("- Add structured data and statistics to support AI citation")
    lines.append("- Use clear heading-question-answer patterns")

    lines.extend(["", "---", "*Powered by [Bofusions](https://github.com/bofusions/bofusions-geo-mcp)*"])

    return "\n".join(lines)
