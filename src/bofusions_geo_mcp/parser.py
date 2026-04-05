"""HTML content parsing and content block extraction for GEO analysis."""

from __future__ import annotations

import re
from typing import Any

from bs4 import BeautifulSoup


def extract_content_blocks(html: str) -> list[dict[str, Any]]:
    """Extract content blocks (sections between headings) for citability analysis."""
    soup = BeautifulSoup(html, "lxml")

    for el in soup.find_all(["script", "style", "nav", "footer", "header", "aside"]):
        el.decompose()

    blocks: list[dict[str, Any]] = []
    current_heading: str | None = None
    current_content: list[str] = []

    for element in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "ul", "ol", "table", "blockquote"]):
        tag = element.name
        if tag and tag.startswith("h"):
            if current_content:
                text = " ".join(current_content)
                blocks.append({"heading": current_heading, "content": text, "word_count": len(text.split())})
            current_heading = element.get_text(strip=True)
            current_content = []
        else:
            text = element.get_text(strip=True)
            if text:
                current_content.append(text)

    if current_content:
        text = " ".join(current_content)
        blocks.append({"heading": current_heading, "content": text, "word_count": len(text.split())})

    return blocks


def extract_schema_data(html: str) -> list[dict[str, Any]]:
    """Extract all JSON-LD structured data from HTML."""
    import json
    soup = BeautifulSoup(html, "lxml")
    schemas: list[dict[str, Any]] = []

    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            if isinstance(data, list):
                schemas.extend(data)
            else:
                schemas.append(data)
        except (json.JSONDecodeError, TypeError):
            pass

    return schemas


def extract_meta_tags(html: str) -> dict[str, str]:
    """Extract all meta tags as a dict."""
    soup = BeautifulSoup(html, "lxml")
    tags: dict[str, str] = {}

    for meta in soup.find_all("meta"):
        name = meta.get("name", meta.get("property", ""))
        content = meta.get("content", "")
        if name and content:
            tags[name.lower()] = content

    return tags


def check_ssr(html: str) -> dict[str, Any]:
    """Check if page has server-side rendered content."""
    soup = BeautifulSoup(html, "lxml")

    js_app_roots = soup.find_all(id=re.compile(r"(app|root|__next|__nuxt)", re.I))

    result: dict[str, Any] = {
        "framework_indicators": [],
        "has_ssr_content": True,
        "text_length": 0,
    }

    for el in js_app_roots:
        text_len = len(el.get_text(strip=True))
        result["framework_indicators"].append({"id": el.get("id"), "text_length": text_len})

    # Decompose non-content and measure
    for el in soup.find_all(["script", "style", "nav", "footer", "header"]):
        el.decompose()
    text = soup.get_text(separator=" ", strip=True)
    result["text_length"] = len(text)

    if js_app_roots:
        for indicator in result["framework_indicators"]:
            if indicator["text_length"] < 50 and result["text_length"] < 200:
                result["has_ssr_content"] = False

    return result
