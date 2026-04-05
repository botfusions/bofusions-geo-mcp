"""geo_schema tool — Analyze structured data (JSON-LD schema markup)."""

from __future__ import annotations

import json

from ..client import fetch_page

# Recommended schema types for different business categories
RECOMMENDED_SCHEMAS = {
    "organization": {
        "types": ["Organization", "WebSite", "SearchAction"],
        "description": "Essential for all businesses",
    },
    "local_business": {
        "types": ["LocalBusiness", "Organization", "WebSite"],
        "description": "Physical locations and local services",
    },
    "saas": {
        "types": ["Organization", "SoftwareApplication", "WebSite", "SearchAction"],
        "description": "SaaS products and software companies",
    },
    "ecommerce": {
        "types": ["Organization", "Product", "WebSite", "SearchAction"],
        "description": "Online stores and e-commerce",
    },
    "publisher": {
        "types": ["Organization", "WebSite", "Article", "Person"],
        "description": "Content publishers and media",
    },
}


async def run_schema(url: str) -> str:
    page = await fetch_page(url)

    if page["status_code"] is None:
        return f"# Schema Analysis Error\n\nFailed to fetch `{url}`:\n- " + "\n- ".join(page.get("errors", []))

    structured_data = page.get("structured_data", [])

    lines = [
        "# Schema Markup Analysis",
        "",
        f"> **Bofusions GEO MCP** | `{url}`",
        "",
        f"## Summary",
        "",
        f"- **JSON-LD Blocks Found**: {len(structured_data)}",
        "",
    ]

    if not structured_data:
        lines.extend([
            "**No structured data found.** This is a significant gap for AI discoverability.",
            "",
            "JSON-LD schema helps AI models understand your content structure,",
            "which directly impacts how they reference and cite your site.",
            "",
        ])
    else:
        lines.extend(["## Detected Schema Types", ""])
        for i, sd in enumerate(structured_data, 1):
            sd_type = sd.get("@type", "Unknown")
            if isinstance(sd_type, list):
                sd_type = " + ".join(sd_type)
            lines.append(f"### {i}. `{sd_type}`")
            lines.append("")

            # Show key properties
            key_props = ["name", "description", "url", "logo", "image", "sameAs", "author",
                         "datePublished", "dateModified", "headline", "price", "availability",
                         "address", "telephone", "email", "contactPoint"]
            found_props = []
            for prop in key_props:
                if prop in sd:
                    val = sd[prop]
                    if isinstance(val, list):
                        found_props.append(f"- **{prop}**: {len(val)} items")
                    elif isinstance(val, dict):
                        found_props.append(f"- **{prop}**: present")
                    else:
                        val_str = str(val)[:80]
                        found_props.append(f"- **{prop}**: `{val_str}`")

            if found_props:
                lines.extend(found_props)
            else:
                lines.append("- Minimal properties set")
            lines.append("")

    # Validation checks
    lines.extend(["## Validation Checks", ""])
    checks = []

    # Check for Organization schema
    has_org = any(
        sd.get("@type") in ("Organization", "organization")
        or (isinstance(sd.get("@type"), list) and "Organization" in sd["@type"])
        for sd in structured_data
    )
    checks.append(("Organization Schema", has_org, "Essential for AI entity recognition"))

    # Check for WebSite schema
    has_website = any(
        sd.get("@type") in ("WebSite", "website")
        or (isinstance(sd.get("@type"), list) and "WebSite" in sd["@type"])
        for sd in structured_data
    )
    checks.append(("WebSite Schema", has_website, "Helps AI understand site structure"))

    # Check for sameAs
    has_sameas = any("sameAs" in sd for sd in structured_data)
    checks.append(("sameAs Property", has_sameas, "Links to social profiles — boosts brand authority"))

    # Check for author
    has_author = any("author" in sd for sd in structured_data)
    checks.append(("Author Property", has_author, "E-E-A-T signal for AI trust"))

    for name, present, note in checks:
        status = "OK" if present else "MISSING"
        lines.append(f"- **{name}**: {status} — {note}")
    lines.append("")

    # Recommendations
    lines.extend(["## Recommendations", ""])

    if not structured_data:
        lines.extend([
            "1. **Add Organization schema** — the foundation for AI entity recognition:",
            "```json-ld",
            '{',
            '  "@context": "https://schema.org",',
            '  "@type": "Organization",',
            f'  "name": "{page.get("title", "Your Company")}",',
            f'  "url": "{url}",',
            '  "logo": "URL_TO_YOUR_LOGO",',
            '  "sameAs": ["https://twitter.com/...", "https://linkedin.com/...", "https://github.com/..."]',
            '}',
            "```",
            "",
        ])

    if not has_website:
        lines.append("- Add a **WebSite** schema with SearchAction for site search")
    if not has_sameas:
        lines.append("- Add **sameAs** property linking to all social/authority profiles")
    if not has_author:
        lines.append("- Add **author** property for E-E-A-T trust signals")

    # Business-specific recommendations
    lines.extend([
        "",
        "## Business-Specific Schema Recommendations",
        "",
    ])

    for category, info in RECOMMENDED_SCHEMAS.items():
        lines.append(f"**{category.replace('_', ' ').title()}**: {info['description']}")
        lines.append(f"- Recommended types: {', '.join(f'`{t}`' for t in info['types'])}")
        lines.append("")

    lines.extend(["---", "*Powered by [Bofusions](https://github.com/bofusions/bofusions-geo-mcp)*"])
    return "\n".join(lines)
