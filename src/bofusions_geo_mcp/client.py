"""Async HTTP client for Bofusions GEO MCP — fetches pages, robots.txt, llms.txt, sitemaps."""

from __future__ import annotations

import re
import json
from urllib.parse import urljoin, urlparse
from typing import Any

import ssl

import httpx
from bs4 import BeautifulSoup


def _ssl_context() -> ssl.SSLContext:
    """Create SSL context with fallback for environments with missing certs."""
    try:
        ctx = ssl.create_default_context()
        # Test if default certs work
        return ctx
    except Exception:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
}

AI_CRAWLERS = [
    "GPTBot", "OAI-SearchBot", "ChatGPT-User",
    "ClaudeBot", "anthropic-ai", "PerplexityBot",
    "CCBot", "Bytespider", "cohere-ai",
    "Google-Extended", "GoogleOther", "Applebot-Extended",
    "FacebookBot", "Amazonbot",
]

_timeout = httpx.Timeout(30.0, connect=10.0)


async def fetch_page(url: str) -> dict[str, Any]:
    """Fetch a page and return structured analysis data."""
    result: dict[str, Any] = {
        "url": url,
        "status_code": None,
        "redirect_chain": [],
        "headers": {},
        "meta_tags": {},
        "title": None,
        "description": None,
        "canonical": None,
        "h1_tags": [],
        "heading_structure": [],
        "word_count": 0,
        "text_content": "",
        "internal_links": [],
        "external_links": [],
        "images": [],
        "structured_data": [],
        "has_ssr_content": True,
        "security_headers": {},
        "errors": [],
    }

    try:
        async with httpx.AsyncClient(
            headers=DEFAULT_HEADERS, timeout=_timeout, follow_redirects=True,
            verify=_ssl_context(),
        ) as client:
            response = await client.get(url)

            if response.history:
                result["redirect_chain"] = [
                    {"url": str(r.url), "status": r.status_code} for r in response.history
                ]

            result["status_code"] = response.status_code
            result["headers"] = dict(response.headers)

            for hdr in [
                "strict-transport-security", "content-security-policy",
                "x-frame-options", "x-content-type-options",
                "referrer-policy", "permissions-policy",
            ]:
                result["security_headers"][hdr] = response.headers.get(hdr)

            soup = BeautifulSoup(response.text, "lxml")

            title_tag = soup.find("title")
            result["title"] = title_tag.get_text(strip=True) if title_tag else None

            for meta in soup.find_all("meta"):
                name = meta.get("name", meta.get("property", ""))
                content = meta.get("content", "")
                if name and content:
                    result["meta_tags"][name.lower()] = content
                    if name.lower() == "description":
                        result["description"] = content

            canonical = soup.find("link", rel="canonical")
            result["canonical"] = canonical.get("href") if canonical else None

            for level in range(1, 7):
                for heading in soup.find_all(f"h{level}"):
                    text = heading.get_text(strip=True)
                    result["heading_structure"].append({"level": level, "text": text})
                    if level == 1:
                        result["h1_tags"].append(text)

            # JSON-LD (before decompose)
            for script in soup.find_all("script", type="application/ld+json"):
                try:
                    data = json.loads(script.string)
                    result["structured_data"].append(data)
                except (json.JSONDecodeError, TypeError):
                    result["errors"].append("Invalid JSON-LD detected")

            # SSR check (before decompose)
            js_app_roots = soup.find_all(id=re.compile(r"(app|root|__next|__nuxt)", re.I))
            ssr_check_results = []
            for root_el in js_app_roots:
                inner_text = root_el.get_text(strip=True)
                ssr_check_results.append({"id": root_el.get("id", "unknown"), "text_length": len(inner_text)})

            # Decompose non-content
            for el in soup.find_all(["script", "style", "nav", "footer", "header"]):
                el.decompose()
            text = soup.get_text(separator=" ", strip=True)
            result["text_content"] = text
            result["word_count"] = len(text.split())

            # Links
            parsed_url = urlparse(url)
            base_domain = parsed_url.netloc
            for link in soup.find_all("a", href=True):
                href = urljoin(url, link["href"])
                link_text = link.get_text(strip=True)
                parsed_href = urlparse(href)
                if parsed_href.netloc == base_domain:
                    result["internal_links"].append({"url": href, "text": link_text})
                elif parsed_href.scheme in ("http", "https"):
                    result["external_links"].append({"url": href, "text": link_text})

            # Images
            for img in soup.find_all("img"):
                result["images"].append({
                    "src": img.get("src", ""),
                    "alt": img.get("alt", ""),
                    "width": img.get("width"),
                    "height": img.get("height"),
                    "loading": img.get("loading"),
                })

            # SSR assessment
            if js_app_roots:
                for check in ssr_check_results:
                    if check["text_length"] < 50 and result["word_count"] < 200:
                        result["has_ssr_content"] = False
                        result["errors"].append(
                            f"Possible client-side only rendering: #{check['id']} "
                            f"({result['word_count']} words)"
                        )

    except httpx.TimeoutException:
        result["errors"].append("Timeout after 30 seconds")
    except httpx.ConnectError as e:
        result["errors"].append(f"Connection error: {e}")
    except Exception as e:
        result["errors"].append(f"Unexpected error: {e}")

    return result


async def fetch_robots_txt(url: str) -> dict[str, Any]:
    """Fetch and parse robots.txt for AI crawler directives."""
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    result: dict[str, Any] = {
        "url": robots_url,
        "exists": False,
        "content": "",
        "ai_crawler_status": {},
        "sitemaps": [],
        "errors": [],
    }

    try:
        async with httpx.AsyncClient(headers=DEFAULT_HEADERS, timeout=15.0, verify=_ssl_context()) as client:
            response = await client.get(robots_url)

            if response.status_code == 200:
                result["exists"] = True
                result["content"] = response.text

                lines = response.text.split("\n")
                current_agent = None
                agent_rules: dict[str, list] = {}

                for line in lines:
                    line = line.strip()
                    if line.lower().startswith("user-agent:"):
                        current_agent = line.split(":", 1)[1].strip()
                        if current_agent not in agent_rules:
                            agent_rules[current_agent] = []
                    elif line.lower().startswith("disallow:") and current_agent:
                        path = line.split(":", 1)[1].strip()
                        agent_rules[current_agent].append({"directive": "Disallow", "path": path})
                    elif line.lower().startswith("allow:") and current_agent:
                        path = line.split(":", 1)[1].strip()
                        agent_rules[current_agent].append({"directive": "Allow", "path": path})
                    elif line.lower().startswith("sitemap:"):
                        sitemap_url = line.split(":", 1)[1].strip()
                        if not sitemap_url.startswith("http"):
                            sitemap_url = "http" + sitemap_url
                        result["sitemaps"].append(sitemap_url)

                for crawler in AI_CRAWLERS:
                    if crawler in agent_rules:
                        rules = agent_rules[crawler]
                        if any(r["directive"] == "Disallow" and r["path"] == "/" for r in rules):
                            result["ai_crawler_status"][crawler] = "BLOCKED"
                        elif any(r["directive"] == "Disallow" and r["path"] for r in rules):
                            result["ai_crawler_status"][crawler] = "PARTIALLY_BLOCKED"
                        else:
                            result["ai_crawler_status"][crawler] = "ALLOWED"
                    elif "*" in agent_rules:
                        wildcard_rules = agent_rules["*"]
                        if any(r["directive"] == "Disallow" and r["path"] == "/" for r in wildcard_rules):
                            result["ai_crawler_status"][crawler] = "BLOCKED_BY_WILDCARD"
                        else:
                            result["ai_crawler_status"][crawler] = "ALLOWED_BY_DEFAULT"
                    else:
                        result["ai_crawler_status"][crawler] = "NOT_MENTIONED"

            elif response.status_code == 404:
                result["errors"].append("No robots.txt found (404)")
                for crawler in AI_CRAWLERS:
                    result["ai_crawler_status"][crawler] = "NO_ROBOTS_TXT"

    except Exception as e:
        result["errors"].append(f"Error fetching robots.txt: {e}")

    return result


async def fetch_llms_txt(url: str) -> dict[str, Any]:
    """Check for llms.txt and llms-full.txt files."""
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"

    result: dict[str, Any] = {
        "llms_txt": {"url": f"{base}/llms.txt", "exists": False, "content": ""},
        "llms_full_txt": {"url": f"{base}/llms-full.txt", "exists": False, "content": ""},
        "errors": [],
    }

    try:
        async with httpx.AsyncClient(headers=DEFAULT_HEADERS, timeout=15.0, verify=_ssl_context()) as client:
            for key, check_url in [
                ("llms_txt", f"{base}/llms.txt"),
                ("llms_full_txt", f"{base}/llms-full.txt"),
            ]:
                try:
                    resp = await client.get(check_url)
                    if resp.status_code == 200:
                        result[key]["exists"] = True
                        result[key]["content"] = resp.text
                except Exception as e:
                    result["errors"].append(f"Error checking {check_url}: {e}")
    except Exception as e:
        result["errors"].append(f"Error: {e}")

    return result


async def crawl_sitemap(url: str, max_pages: int = 50) -> list[str]:
    """Crawl sitemap.xml to discover pages."""
    parsed = urlparse(url)
    sitemap_urls = [
        f"{parsed.scheme}://{parsed.netloc}/sitemap.xml",
        f"{parsed.scheme}://{parsed.netloc}/sitemap_index.xml",
    ]

    discovered: set[str] = set()

    async with httpx.AsyncClient(headers=DEFAULT_HEADERS, timeout=15.0, verify=_ssl_context()) as client:
        for sitemap_url in sitemap_urls:
            if len(discovered) >= max_pages:
                break
            try:
                resp = await client.get(sitemap_url)
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, "lxml")

                # Sitemap index
                for sitemap in soup.find_all("sitemap"):
                    loc = sitemap.find("loc")
                    if loc and len(discovered) < max_pages:
                        try:
                            child_resp = await client.get(loc.text.strip())
                            if child_resp.status_code == 200:
                                child_soup = BeautifulSoup(child_resp.text, "lxml")
                                for url_tag in child_soup.find_all("url"):
                                    loc_tag = url_tag.find("loc")
                                    if loc_tag:
                                        discovered.add(loc_tag.text.strip())
                                    if len(discovered) >= max_pages:
                                        break
                        except Exception:
                            pass

                # Direct URLs
                for url_tag in soup.find_all("url"):
                    loc = url_tag.find("loc")
                    if loc:
                        discovered.add(loc.text.strip())
                    if len(discovered) >= max_pages:
                        break

                if discovered:
                    break
            except Exception:
                continue

    return list(discovered)[:max_pages]
