"""geo_llmstxt tool — Analyze or generate llms.txt for AI crawler guidance."""

from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from ..client import DEFAULT_HEADERS

BOFUSIONS_NOTE = "\n\n---\n*Powered by [Bofusions](https://github.com/bofusions/bofusions-geo-mcp)*"


async def run_llmstxt(url: str, mode: str = "validate") -> str:
    if mode == "generate":
        return await _generate(url)
    return await _validate(url)


async def _validate(url: str) -> str:
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"

    lines = [
        "# llms.txt Analysis",
        "",
        f"> **Bofusions GEO MCP** | `{url}`",
        "",
    ]

    async with httpx.AsyncClient(headers=DEFAULT_HEADERS, timeout=15.0) as client:
        # Check llms.txt
        llms_result = await _check_file(client, f"{base}/llms.txt", "llms.txt")
        lines.extend(llms_result)

        # Check llms-full.txt
        full_result = await _check_file(client, f"{base}/llms-full.txt", "llms-full.txt")
        lines.extend(full_result)

    # Recommendations
    lines.extend([
        "## Recommendations",
        "",
        "- Place `llms.txt` at the root of your domain (e.g., `example.com/llms.txt`)",
        "- Start with `# Site Name` title",
        "- Add `> Brief description` of your site",
        "- Use `## Section` headings to organize content",
        "- Link key pages with `- [Page Title](url): Description` format",
        "- Include a `## Contact` section",
        "- Create `llms-full.txt` with detailed page descriptions",
        "",
    ])

    # llms.txt format example
    lines.extend([
        "## Example llms.txt Format",
        "",
        "```markdown",
        f"# {parsed.netloc}",
        f"> Your site description here",
        f"",
        f"## Main Pages",
        f"- [Home]({base}/): Welcome page",
        f"- [About]({base}/about): About us",
        f"",
        f"## Products & Services",
        f"- [Products]({base}/products): Our offerings",
        f"",
        f"## Contact",
        f"- Email: info@{parsed.netloc}",
        f"- Website: {base}",
        "```",
    ])

    lines.append(BOFUSIONS_NOTE)
    return "\n".join(lines)


async def _generate(url: str) -> str:
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"

    async with httpx.AsyncClient(headers=DEFAULT_HEADERS, timeout=30.0, follow_redirects=True) as client:
        try:
            resp = await client.get(url)
            soup = BeautifulSoup(resp.text, "lxml")
        except Exception as e:
            return f"# Error\n\nFailed to fetch `{url}`: {e}"

        # Extract site info
        title_tag = soup.find("title")
        site_name = title_tag.get_text(strip=True).split("|")[0].split("-")[0].strip() if title_tag else parsed.netloc
        meta_desc = soup.find("meta", attrs={"name": "description"})
        site_description = meta_desc.get("content", "") if meta_desc else f"Official website of {site_name}"

        # Categorize internal links
        pages: dict[str, list] = {
            "Main Pages": [],
            "Products & Services": [],
            "Resources & Blog": [],
            "Company": [],
            "Support": [],
        }

        seen: set[str] = set()
        for link in soup.find_all("a", href=True):
            href = str(urljoin(base, link["href"]))
            link_text = link.get_text(strip=True)
            if not link_text or len(link_text) < 2:
                continue

            parsed_href = urlparse(href)
            if parsed_href.netloc != parsed.netloc:
                continue
            if href in seen:
                continue
            if any(ext in href for ext in [".pdf", ".jpg", ".png", ".gif", ".css", ".js"]):
                continue

            seen.add(href)
            path = parsed_href.path.lower()
            entry = {"url": href, "title": link_text}

            if any(kw in path for kw in ["/pricing", "/feature", "/product", "/solution", "/demo"]):
                pages["Products & Services"].append(entry)
            elif any(kw in path for kw in ["/blog", "/article", "/resource", "/guide", "/learn", "/docs"]):
                pages["Resources & Blog"].append(entry)
            elif any(kw in path for kw in ["/about", "/team", "/career", "/contact", "/press"]):
                pages["Company"].append(entry)
            elif any(kw in path for kw in ["/help", "/support", "/faq", "/status"]):
                pages["Support"].append(entry)
            else:
                pages["Main Pages"].append(entry)

            if len(seen) >= 50:
                break

    # Generate llms.txt
    llms_lines = [
        f"# {site_name}",
        f"> {site_description}",
        "",
    ]

    for section, section_pages in pages.items():
        if section_pages:
            llms_lines.append(f"## {section}")
            for page in section_pages[:10]:
                llms_lines.append(f"- [{page['title']}]({page['url']})")
            llms_lines.append("")

    llms_lines.extend([
        "## Contact",
        f"- Website: {base}",
        f"- Email: info@{parsed.netloc}",
        "",
    ])

    generated = "\n".join(llms_lines)

    # Output
    lines = [
        "# Generated llms.txt",
        "",
        f"> **Bofusions GEO MCP** | `{url}`",
        "",
        f"Pages discovered: **{len(seen)}**",
        "",
        "## llms.txt Content",
        "",
        "```markdown",
        generated,
        "```",
        "",
        "## Next Steps",
        "",
        "1. Copy the content above to `/llms.txt` on your server",
        "2. Optionally create `/llms-full.txt` with page descriptions",
        "3. Verify both files are accessible (HTTP 200)",
        "4. Reference from `robots.txt` if desired",
        "",
    ]

    lines.append(BOFUSIONS_NOTE)
    return "\n".join(lines)


async def _check_file(client: httpx.AsyncClient, url: str, name: str) -> list[str]:
    """Check a single file and return markdown lines."""
    lines = [f"## {name}", ""]

    try:
        resp = await client.get(url)
        if resp.status_code == 200:
            lines.append(f"**Status**: Found (HTTP 200)")
            content = resp.text

            if name == "llms.txt":
                lns = content.strip().split("\n")
                has_title = lns and lns[0].startswith("# ")
                has_desc = any(l.startswith("> ") for l in lns)
                sections = [l for l in lns if l.startswith("## ")]
                links = re.findall(r"- \[.+\]\(.+\)", content)

                lines.extend([
                    f"- **Title**: {'OK' if has_title else 'MISSING'} (should start with `# Site Name`)",
                    f"- **Description**: {'OK' if has_desc else 'MISSING'} (use `> Description`)",
                    f"- **Sections**: {len(sections)} ({', '.join(s[3:] for s in sections) if sections else 'none'})",
                    f"- **Links**: {len(links)} page links",
                    "",
                ])

                issues = []
                if not has_title:
                    issues.append("Missing title — start with `# Site Name`")
                if not has_desc:
                    issues.append("Missing description — use `> Brief description`")
                if not sections:
                    issues.append("No sections found — add `## Section Name`")
                if not links:
                    issues.append("No page links — add `- [Title](url): Description`")

                if issues:
                    lines.append("**Issues**:")
                    for issue in issues:
                        lines.append(f"- {issue}")
                    lines.append("")
        else:
            lines.append(f"**Status**: Not found (HTTP {resp.status_code})")
            lines.append("")
    except Exception as e:
        lines.append(f"**Status**: Error — {e}")
        lines.append("")

    return lines
