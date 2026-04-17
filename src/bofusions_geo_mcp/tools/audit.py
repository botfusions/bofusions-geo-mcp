"""geo_audit tool — Full GEO audit with scoring."""

from __future__ import annotations

from ..client import fetch_page, fetch_robots_txt, fetch_llms_txt
from ..parser import extract_content_blocks, rebuild_minimal_html
from ..scoring import score_passage, calculate_geo_score


async def run_audit(url: str) -> str:
    page = await fetch_page(url)
    robots = await fetch_robots_txt(url)
    llms = await fetch_llms_txt(url)

    errors = page.get("errors", [])
    if page["status_code"] is None and errors:
        return f"# GEO Audit Error\n\nFailed to fetch `{url}`:\n- " + "\n- ".join(errors)

    # Citability scoring
    citability_scores = []
    if page["text_content"]:
        blocks = extract_content_blocks(
            rebuild_minimal_html(page["heading_structure"], page["text_content"])
        )
        for block in blocks:
            if block["word_count"] >= 20:
                result = score_passage(block["content"], block["heading"])
                citability_scores.append(result["total_score"])

    citability_avg = sum(citability_scores) / len(citability_scores) if citability_scores else 0

    # Schema score
    schema_count = len(page.get("structured_data", []))
    schema_score = min(schema_count * 20, 100)

    # Technical score
    tech_items = []
    tech_max = 0
    if page.get("has_ssr_content"):
        tech_items.append(("SSR Content", 20))
    else:
        tech_items.append(("SSR Content", 0))
    tech_max += 20

    if page.get("canonical"):
        tech_items.append(("Canonical URL", 10))
    else:
        tech_items.append(("Canonical URL", 0))
    tech_max += 10

    sec_headers = page.get("security_headers", {})
    sec_present = sum(1 for v in sec_headers.values() if v)
    tech_items.append(("Security Headers", min(sec_present * 3, 15)))
    tech_max += 15

    has_robots = robots.get("exists", False)
    tech_items.append(("robots.txt", 15 if has_robots else 0))
    tech_max += 15

    ai_allowed = sum(
        1 for v in robots.get("ai_crawler_status", {}).values()
        if v in ("ALLOWED", "ALLOWED_BY_DEFAULT", "NOT_MENTIONED")
    )
    ai_total = len(robots.get("ai_crawler_status", {}))
    tech_items.append(("AI Crawler Access", int((ai_allowed / max(ai_total, 1)) * 20)))
    tech_max += 20

    has_description = bool(page.get("description"))
    tech_items.append(("Meta Description", 10 if has_description else 0))
    tech_max += 10

    h1_count = len(page.get("h1_tags", []))
    tech_items.append(("H1 Tag", 10 if h1_count == 1 else 0))
    tech_max += 10

    tech_score = (sum(s for _, s in tech_items) / max(tech_max, 1)) * 100

    # llms.txt score
    llms_score = 50 if llms["llms_txt"]["exists"] else 0
    llms_score += 50 if llms["llms_full_txt"]["exists"] else 0

    # Brand placeholder (needs separate scan)
    brand_score = 0
    content_score = citability_avg
    platform_score = llms_score

    # Overall GEO score
    geo = calculate_geo_score(citability_avg, brand_score, content_score, tech_score, schema_score, platform_score)

    # Build markdown
    lines = [
        f"# GEO Audit Report",
        f"",
        f"> **Bofusions GEO MCP** | `{url}`",
        f"",
        f"## Overall GEO Score: {geo['total_score']}/100 (Grade {geo['grade']})",
        f"",
        f"| Component | Weight | Score | Weighted |",
        f"|-----------|--------|-------|----------|",
    ]
    for name, data in geo["components"].items():
        lines.append(f"| {name.replace('_', ' ').title()} | {data['weight']*100:.0f}% | {data['score']:.1f} | {data['weighted']:.1f} |")
    lines.append(f"| **Total** | **100%** | **{geo['total_score']:.1f}** | — |")

    # Technical breakdown
    lines.extend(["", "## Technical Analysis", ""])
    for name, score in tech_items:
        status = "OK" if score > 0 else "MISSING"
        lines.append(f"- **{name}**: {status} ({score} pts)")

    # AI Crawler Status
    lines.extend(["", "## AI Crawler Access", ""])
    crawler_status = robots.get("ai_crawler_status", {})
    for crawler, status in sorted(crawler_status.items()):
        icon = "ALLOWED" if status in ("ALLOWED", "ALLOWED_BY_DEFAULT", "NOT_MENTIONED") else "BLOCKED"
        lines.append(f"- **{crawler}**: {icon} ({status})")

    # Structured Data
    lines.extend(["", "## Structured Data", ""])
    if page.get("structured_data"):
        for i, sd in enumerate(page["structured_data"], 1):
            sd_type = sd.get("@type", "Unknown")
            lines.append(f"{i}. `{sd_type}`")
    else:
        lines.append("- No JSON-LD structured data found")

    # llms.txt
    lines.extend(["", "## llms.txt Status", ""])
    lines.append(f"- **llms.txt**: {'Found' if llms['llms_txt']['exists'] else 'Not found'}")
    lines.append(f"- **llms-full.txt**: {'Found' if llms['llms_full_txt']['exists'] else 'Not found'}")

    # Page basics
    lines.extend(["", "## Page Basics", ""])
    lines.append(f"- **Title**: {page.get('title', 'N/A')}")
    lines.append(f"- **Description**: {page.get('description', 'N/A')}")
    lines.append(f"- **Canonical**: {page.get('canonical', 'N/A')}")
    lines.append(f"- **Word Count**: {page.get('word_count', 0)}")
    lines.append(f"- **H1 Tags**: {len(page.get('h1_tags', []))}")
    lines.append(f"- **Headings**: {len(page.get('heading_structure', []))}")
    lines.append(f"- **Images**: {len(page.get('images', []))} ({sum(1 for img in page.get('images', []) if img.get('alt'))} with alt text)")
    lines.append(f"- **Internal Links**: {len(page.get('internal_links', []))}")
    lines.append(f"- **External Links**: {len(page.get('external_links', []))}")

    # Action items
    lines.extend(["", "## Priority Action Items", ""])
    actions = []
    if not page.get("description"):
        actions.append("Add a meta description (critical for AI snippet selection)")
    if len(page.get("h1_tags", [])) != 1:
        actions.append("Ensure exactly one H1 tag on the page")
    if not page.get("structured_data"):
        actions.append("Add JSON-LD structured data (Organization, WebSite schema)")
    if not llms["llms_txt"]["exists"]:
        actions.append("Create an llms.txt file at the root of your domain")
    if not page.get("has_ssr_content"):
        actions.append("Implement SSR or pre-rendering for AI crawler access")
    blocked = [c for c, s in crawler_status.items() if "BLOCKED" in s]
    if blocked:
        actions.append(f"Unblock AI crawlers in robots.txt: {', '.join(blocked)}")
    if not page.get("canonical"):
        actions.append("Add a canonical URL tag")
    if citability_avg < 50:
        actions.append("Improve content citability (aim for 134-167 word self-contained passages)")

    if actions:
        for i, action in enumerate(actions, 1):
            lines.append(f"{i}. {action}")
    else:
        lines.append("No critical issues found. Keep monitoring and improving.")

    lines.extend(["", "---", "*Powered by [Bofusions](https://github.com/bofusions/bofusions-geo-mcp)*"])

    return "\n".join(lines)
