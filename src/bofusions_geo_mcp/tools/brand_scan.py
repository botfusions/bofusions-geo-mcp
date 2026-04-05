"""geo_brand_scan tool — Scan brand mentions across AI-cited platforms."""

from __future__ import annotations

from urllib.parse import quote_plus

import httpx


async def run_brand_scan(brand_name: str, domain: str | None = None) -> str:
    """Scan brand presence across platforms that influence AI citations."""
    lines = [
        f"# Brand Mention Scan",
        f"",
        f"> **Bofusions GEO MCP** | Brand: **{brand_name}**",
        f"",
        f"## Key Insight",
        f"",
        f"Brand mentions correlate **3x more strongly** with AI visibility than backlinks.",
        f"(Ahrefs Dec 2025, 75K brands study)",
        f"",
    ]

    # Check Wikipedia
    wiki_result = await _check_wikipedia(brand_name)
    lines.extend(wiki_result)

    # Check GitHub
    github_result = await _check_github(brand_name)
    lines.extend(github_result)

    # Platform checklist (search URLs for manual verification)
    lines.extend([
        "## Platform Presence Checklist",
        "",
        "Use these URLs to verify brand presence on key platforms:",
        "",
    ])

    platforms = [
        ("YouTube", f"https://www.youtube.com/results?search_query={quote_plus(brand_name)}", "Highest correlation (0.737) with AI citations"),
        ("Reddit", f"https://www.reddit.com/search/?q={quote_plus(brand_name)}", "High correlation — authentic discussions matter"),
        ("LinkedIn", f"https://www.linkedin.com/search/results/companies/?keywords={quote_plus(brand_name)}", "Thought leadership and company presence"),
        ("Quora", f"https://www.quora.com/search?q={quote_plus(brand_name)}", "Q&A platform — answers often cited by AI"),
        ("Product Hunt", f"https://www.producthunt.com/search?q={quote_plus(brand_name)}", "Product discovery and reviews"),
        ("G2", f"https://www.g2.com/search?query={quote_plus(brand_name)}", "Software reviews — social proof signals"),
        ("Trustpilot", f"https://www.trustpilot.com/search?query={quote_plus(brand_name)}", "Customer review signals"),
        ("Crunchbase", f"https://www.crunchbase.com/textsearch?q={quote_plus(brand_name)}", "B2B authority signals"),
    ]

    for name, url, note in platforms:
        lines.append(f"- **{name}**: [Search]({url}) — {note}")

    # Priority actions
    lines.extend([
        "",
        "## Priority Actions",
        "",
        "1. **YouTube** (0.737 correlation): Create educational content channel",
        "2. **Reddit**: Build authentic presence in industry subreddits",
        "3. **Wikipedia**: Establish notability through press coverage",
        "4. **LinkedIn**: Publish thought leadership from founders",
        "5. **Review Platforms**: Encourage customer reviews on G2, Trustpilot",
        "",
        "## Cross-Platform Tips",
        "",
        "- Ensure consistent NAP (Name, Address, Phone) everywhere",
        "- Add `sameAs` in schema markup linking to all profiles",
        "- Set up brand mention alerts across platforms",
        "- Monitor sentiment on Reddit and review sites",
        "",
        "---",
        "*Powered by [Bofusions](https://github.com/bofusions/bofusions-geo-mcp)*",
    ])

    return "\n".join(lines)


async def _check_wikipedia(brand_name: str) -> list[str]:
    """Check Wikipedia and Wikidata for brand presence."""
    lines = ["## Wikipedia & Wikidata", ""]
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Wikipedia search
            api_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={quote_plus(brand_name)}&format=json"
            resp = await client.get(api_url)
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("query", {}).get("search", [])
                if results:
                    top_title = results[0].get("title", "")
                    lines.append(f"- **Wikipedia Search**: {len(results)} results (top: _{top_title}_)")
                    if brand_name.lower() in top_title.lower():
                        lines.append(f"  - Likely has a Wikipedia article")
                    else:
                        lines.append(f"  - No direct Wikipedia article found")
                else:
                    lines.append(f"- **Wikipedia**: No results found")

            # Wikidata
            wd_url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={quote_plus(brand_name)}&language=en&format=json"
            resp = await client.get(wd_url)
            if resp.status_code == 200:
                data = resp.json()
                entities = data.get("search", [])
                if entities:
                    eid = entities[0].get("id", "")
                    desc = entities[0].get("description", "")
                    lines.append(f"- **Wikidata**: Entry found ({eid}) — _{desc}_")
                else:
                    lines.append(f"- **Wikidata**: No entry found")
    except Exception as e:
        lines.append(f"- **Wikipedia/Wikidata**: Check failed ({e})")

    lines.append("")
    return lines


async def _check_github(brand_name: str) -> list[str]:
    """Check GitHub for brand presence."""
    lines = ["## GitHub", ""]
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            api_url = f"https://api.github.com/search/repositories?q={quote_plus(brand_name)}&per_page=5"
            resp = await client.get(api_url, headers={"Accept": "application/vnd.github.v3+json"})
            if resp.status_code == 200:
                data = resp.json()
                total = data.get("total_count", 0)
                lines.append(f"- **GitHub Repos**: {total} repositories found")
                for repo in data.get("items", [])[:3]:
                    lines.append(f"  - [{repo['full_name']}]({repo['html_url']}) — {repo.get('description', 'No description')} ({repo['stargazers_count']} stars)")
            else:
                lines.append(f"- **GitHub**: Search failed (status {resp.status_code})")
    except Exception as e:
        lines.append(f"- **GitHub**: Check failed ({e})")

    lines.append("")
    return lines
