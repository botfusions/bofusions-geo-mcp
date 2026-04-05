"""geo_report tool — Comprehensive markdown GEO report combining all analyses."""

from __future__ import annotations

from ..client import fetch_page, fetch_robots_txt, fetch_llms_txt
from ..parser import extract_content_blocks
from ..scoring import score_passage, calculate_geo_score
from .citability import run_citability
from .technical import run_technical


async def run_report(url: str, brand_name: str | None = None) -> str:
    page = await fetch_page(url)
    robots = await fetch_robots_txt(url)
    llms = await fetch_llms_txt(url)

    if page["status_code"] is None:
        return f"# Report Error\n\nFailed to fetch `{url}`:\n- " + "\n- ".join(page.get("errors", []))

    # Calculate scores
    citability_scores = []
    if page["text_content"]:
        blocks = extract_content_blocks(
            _rebuild_html(page["heading_structure"], page["text_content"])
        )
        for block in blocks:
            if block["word_count"] >= 20:
                sc = score_passage(block["content"], block["heading"])
                citability_scores.append(sc["total_score"])

    citability_avg = sum(citability_scores) / len(citability_scores) if citability_scores else 0
    schema_count = len(page.get("structured_data", []))
    schema_score = min(schema_count * 25, 100)

    # Technical
    tech_deductions = 0
    if not page.get("has_ssr_content"):
        tech_deductions += 20
    if not page.get("canonical"):
        tech_deductions += 10
    if not page.get("description"):
        tech_deductions += 10
    if len(page.get("h1_tags", [])) != 1:
        tech_deductions += 10
    if not robots.get("exists"):
        tech_deductions += 15
    tech_score = max(100 - tech_deductions, 0)

    # llms.txt
    llms_score = 50 if llms["llms_txt"]["exists"] else 0
    llms_score += 50 if llms["llms_full_txt"]["exists"] else 0

    # Content
    content_score = citability_avg
    brand_score = 0  # Requires separate brand_scan
    platform_score = llms_score

    geo = calculate_geo_score(citability_avg, brand_score, content_score, tech_score, schema_score, platform_score)

    # Build report
    lines = [
        "# GEO Analysis Report",
        "",
        f"> **Bofusions GEO MCP** | Generated for `{url}`",
        f"> Brand: {brand_name or 'N/A'}",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| **GEO Score** | **{geo['total_score']:.1f}**/100 (Grade {geo['grade']}) |",
        f"| **URL** | `{url}` |",
        f"| **Title** | {page.get('title', 'N/A')[:60]} |",
        f"| **Word Count** | {page.get('word_count', 0)} |",
        f"| **JSON-LD Schemas** | {schema_count} |",
        f"| **llms.txt** | {'Yes' if llms['llms_txt']['exists'] else 'No'} |",
        f"| **robots.txt** | {'Yes' if robots.get('exists') else 'No'} |",
        "",
    ]

    # Score breakdown
    lines.extend([
        "## Score Breakdown",
        "",
        "| Component | Weight | Score |",
        "|-----------|--------|-------|",
    ])
    for name, data in geo["components"].items():
        lines.append(f"| {name.replace('_', ' ').title()} | {data['weight']*100:.0f}% | {data['score']:.1f} |")
    lines.append("")

    # Quick findings
    lines.extend(["## Key Findings", ""])

    findings = []
    if not page.get("has_ssr_content"):
        findings.append("Client-side only rendering — AI crawlers may see empty pages")
    if not page.get("description"):
        findings.append("Missing meta description — critical for AI snippet selection")
    if not page.get("canonical"):
        findings.append("Missing canonical URL")
    if len(page.get("h1_tags", [])) != 1:
        findings.append(f"H1 tag issue: {len(page.get('h1_tags', []))} found (need exactly 1)")
    if not page.get("structured_data"):
        findings.append("No JSON-LD structured data — significant gap for AI discoverability")
    if not llms["llms_txt"]["exists"]:
        findings.append("No llms.txt file — AI crawlers can't discover your content structure")
    if not robots.get("exists"):
        findings.append("No robots.txt file")

    blocked_crawlers = [c for c, s in robots.get("ai_crawler_status", {}).items() if "BLOCKED" in s]
    if blocked_crawlers:
        findings.append(f"AI crawlers blocked: {', '.join(blocked_crawlers)}")

    if citability_avg < 50:
        findings.append(f"Low citability score ({citability_avg:.0f}/100) — content needs restructuring")

    images = page.get("images", [])
    if images:
        alt_pct = sum(1 for img in images if img.get("alt")) * 100 // max(len(images), 1)
        if alt_pct < 80:
            findings.append(f"Image alt text coverage: only {alt_pct}%")

    if findings:
        for i, f in enumerate(findings, 1):
            lines.append(f"{i}. {f}")
    else:
        lines.append("No critical issues detected.")
    lines.append("")

    # Action plan
    lines.extend(["## Priority Action Plan", ""])

    # Sort by impact
    actions = []

    if not page.get("has_ssr_content"):
        actions.append(("HIGH", "Implement SSR or pre-rendering for AI crawler access"))
    if not page.get("structured_data"):
        actions.append(("HIGH", "Add Organization + WebSite JSON-LD schema markup"))
    if not page.get("description"):
        actions.append(("HIGH", "Write a compelling meta description (150-160 chars)"))
    if not llms["llms_txt"]["exists"]:
        actions.append(("HIGH", "Create llms.txt file at domain root"))
    if blocked_crawlers:
        actions.append(("HIGH", f"Allow AI crawlers in robots.txt: {', '.join(blocked_crawlers)}"))
    if citability_avg < 50:
        actions.append(("MEDIUM", "Restructure content into 134-167 word self-contained passages"))
    if not page.get("canonical"):
        actions.append(("MEDIUM", "Add canonical URL tag"))
    if len(page.get("h1_tags", [])) != 1:
        actions.append(("MEDIUM", "Fix H1 tags — exactly one per page"))
    if not robots.get("exists"):
        actions.append(("MEDIUM", "Create robots.txt with AI crawler directives"))

    for priority in ["HIGH", "MEDIUM", "LOW"]:
        priority_actions = [a for p, a in actions if p == priority]
        if priority_actions:
            lines.append(f"### {priority} Priority")
            for a in priority_actions:
                lines.append(f"- {a}")
            lines.append("")

    # Citability summary
    lines.extend([
        "## Citability Summary",
        "",
        f"- **Average Score**: {citability_avg:.1f}/100",
        f"- **Blocks Analyzed**: {len(citability_scores)}",
        f"- **Optimal Length Passages** (134-167 words): {sum(1 for s in citability_scores if 50 <= s <= 80)}",
        "",
    ])

    if citability_scores:
        grade_dist = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
        for s in citability_scores:
            if s >= 80: grade_dist["A"] += 1
            elif s >= 65: grade_dist["B"] += 1
            elif s >= 50: grade_dist["C"] += 1
            elif s >= 35: grade_dist["D"] += 1
            else: grade_dist["F"] += 1

        lines.append("| Grade | Count |")
        lines.append("|-------|-------|")
        for g in ["A", "B", "C", "D", "F"]:
            lines.append(f"| {g} | {grade_dist[g]} |")
        lines.append("")

    lines.extend([
        "---",
        "",
        f"*Report generated by [Bofusions GEO MCP](https://github.com/bofusions/bofusions-geo-mcp)*",
    ])

    return "\n".join(lines)


def _rebuild_html(headings: list, text: str) -> str:
    parts = []
    for h in headings:
        parts.append(f"<h{h['level']}>{h['text']}</h{h['level']}>")
    parts.append(f"<p>{text}</p>")
    return "".join(parts)
