"""geo_technical tool — Technical SEO and GEO analysis."""

from __future__ import annotations

from ..client import fetch_page, fetch_robots_txt


async def run_technical(url: str) -> str:
    page = await fetch_page(url)
    robots = await fetch_robots_txt(url)

    errors = page.get("errors", [])
    if page["status_code"] is None and errors:
        return f"# Technical Analysis Error\n\nFailed to fetch `{url}`:\n- " + "\n- ".join(errors)

    lines = [
        "# Technical GEO Analysis",
        "",
        f"> **Bofusions GEO MCP** | `{url}`",
        "",
        f"**Status Code**: {page.get('status_code', 'N/A')}",
    ]

    # Redirects
    if page.get("redirect_chain"):
        lines.append(f"**Redirects**: {len(page['redirect_chain'])} redirect(s)")
        for r in page["redirect_chain"]:
            lines.append(f"  - {r['status']} → {r['url']}")
    lines.append("")

    # SSR
    lines.extend([
        "## Server-Side Rendering",
        "",
        f"- **Has SSR Content**: {'Yes' if page.get('has_ssr_content') else 'No'}",
        f"- **Word Count**: {page.get('word_count', 0)}",
    ])
    if not page.get("has_ssr_content"):
        lines.append("- **Issue**: Client-side only rendering detected — AI crawlers may see empty page")
        lines.append("  - Solution: Implement SSR, pre-rendering, or use a service like Prerender.io")
    lines.append("")

    # robots.txt
    lines.extend([
        "## robots.txt",
        "",
        f"- **Exists**: {'Yes' if robots.get('exists') else 'No'}",
    ])
    if robots.get("sitemaps"):
        lines.append(f"- **Sitemaps**: {len(robots['sitemaps'])}")
        for s in robots["sitemaps"]:
            lines.append(f"  - {s}")
    lines.append("")

    # AI Crawler Status
    lines.extend(["## AI Crawler Access", ""])
    crawler_status = robots.get("ai_crawler_status", {})
    blocked = []
    allowed = []
    for crawler, status in sorted(crawler_status.items()):
        if status in ("BLOCKED", "BLOCKED_BY_WILDCARD"):
            blocked.append(f"- **{crawler}**: BLOCKED ({status})")
        elif status in ("ALLOWED", "ALLOWED_BY_DEFAULT", "NOT_MENTIONED"):
            allowed.append(f"- {crawler}: OK ({status})")
        else:
            allowed.append(f"- {crawler}: {status}")

    if blocked:
        lines.append("**Blocked Crawlers**:")
        lines.extend(blocked)
        lines.append("")
    lines.append("**Allowed Crawlers**:")
    lines.extend(allowed)
    lines.append("")

    # Meta Tags
    lines.extend(["## Meta Tags", ""])
    meta = page.get("meta_tags", {})
    important_tags = ["description", "og:title", "og:description", "og:image", "og:type", "twitter:card", "robots"]
    for tag in important_tags:
        val = meta.get(tag)
        status = f"`{val[:60]}{'...' if len(val) > 60 else ''}`" if val else "MISSING"
        lines.append(f"- **{tag}**: {status}")

    other_tags = {k: v for k, v in meta.items() if k not in important_tags}
    if other_tags:
        lines.append(f"- **Other tags**: {len(other_tags)} additional meta tags")
    lines.append("")

    # Heading Structure
    lines.extend(["## Heading Structure", ""])
    headings = page.get("heading_structure", [])
    h1_tags = page.get("h1_tags", [])

    if len(h1_tags) == 0:
        lines.append("- **H1**: MISSING (should have exactly one)")
    elif len(h1_tags) == 1:
        lines.append(f"- **H1**: `{h1_tags[0]}`")
    else:
        lines.append(f"- **H1**: {len(h1_tags)} found (should be exactly one)")
        for h in h1_tags:
            lines.append(f"  - `{h}`")

    for h in headings:
        indent = "  " * (h["level"] - 1)
        lines.append(f"{indent}- H{h['level']}: `{h['text'][:60]}`")
    lines.append("")

    # Security Headers
    lines.extend(["## Security Headers", ""])
    sec = page.get("security_headers", {})
    for header, value in sec.items():
        status = "SET" if value else "MISSING"
        lines.append(f"- **{header}**: {status}")
    lines.append("")

    # Images
    images = page.get("images", [])
    if images:
        with_alt = sum(1 for img in images if img.get("alt"))
        lines.extend([
            "## Images",
            "",
            f"- **Total**: {len(images)} images",
            f"- **With Alt Text**: {with_alt} ({with_alt * 100 // max(len(images), 1)}%)",
            f"- **Lazy Loading**: {sum(1 for img in images if img.get('loading') == 'lazy')}",
            "",
        ])

    # Performance Signals
    lines.extend(["## Performance Signals", ""])
    lines.append(f"- **Internal Links**: {len(page.get('internal_links', []))}")
    lines.append(f"- **External Links**: {len(page.get('external_links', []))}")
    lines.append(f"- **Total Word Count**: {page.get('word_count', 0)}")
    lines.append("")

    # Action Items
    lines.extend(["## Priority Actions", ""])
    actions = []
    if not page.get("has_ssr_content"):
        actions.append("Implement SSR or pre-rendering for AI crawler access")
    if not robots.get("exists"):
        actions.append("Create a robots.txt file with AI crawler directives")
    if blocked:
        actions.append(f"Unblock AI crawlers: {', '.join(c for c, _ in [(c, s) for c, s in crawler_status.items() if 'BLOCKED' in s])}")
    if not meta.get("description"):
        actions.append("Add a meta description")
    if len(h1_tags) != 1:
        actions.append("Fix H1 tags (exactly one required)")
    if images and sum(1 for img in images if img.get("alt")) < len(images) * 0.8:
        actions.append("Add alt text to images (aim for 100%)")

    if actions:
        for i, a in enumerate(actions, 1):
            lines.append(f"{i}. {a}")
    else:
        lines.append("No critical technical issues found.")

    lines.extend(["", "---", "*Powered by [Bofusions](https://github.com/bofusions/bofusions-geo-mcp)*"])
    return "\n".join(lines)
