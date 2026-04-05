"""Bofusions GEO MCP Server — AI Search Engine Optimization tools for MCP clients."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "Bofusions GEO MCP",
    instructions="AI Search Engine Optimization (GEO) analysis tools by Bofusions. "
    "Use geo_audit for full audits, geo_citability for content scoring, "
    "geo_brand_scan for brand presence, geo_llmstxt for llms.txt analysis, "
    "geo_technical for technical SEO, geo_schema for structured data, "
    "and geo_report for comprehensive reports.",
)


@mcp.tool()
async def geo_audit(url: str) -> str:
    """Full GEO audit with scoring and recommendations.

    Analyzes a URL for AI search engine optimization readiness.
    Returns a markdown report with GEO score (0-100), breakdown by category,
    and prioritized action items.

    Args:
        url: The URL to audit (e.g., https://example.com)
    """
    from .tools.audit import run_audit
    return await run_audit(url)


@mcp.tool()
async def geo_citability(url: str) -> str:
    """Score content blocks for AI citation readiness.

    Analyzes all text passages on a page and scores each one
    on how likely AI models (ChatGPT, Claude, Perplexity) are to cite them.
    Optimal AI-cited passages are 134-167 words.

    Args:
        url: The URL to analyze for citability
    """
    from .tools.citability import run_citability
    return await run_citability(url)


@mcp.tool()
async def geo_brand_scan(brand_name: str, domain: str | None = None) -> str:
    """Scan brand mentions across AI-cited platforms.

    Checks YouTube, Reddit, Wikipedia, LinkedIn, and 7+ other platforms
    for brand presence. Brand mentions correlate 3x more strongly with
    AI visibility than backlinks.

    Args:
        brand_name: Brand or company name to search for
        domain: Optional website domain (e.g., example.com)
    """
    from .tools.brand_scan import run_brand_scan
    return await run_brand_scan(brand_name, domain)


@mcp.tool()
async def geo_llmstxt(url: str, mode: str = "validate") -> str:
    """Analyze or generate llms.txt for AI crawler guidance.

    llms.txt is the emerging standard that helps AI crawlers understand
    your site structure and find your most important content.

    Args:
        url: The website URL to analyze
        mode: 'validate' to check existing llms.txt, 'generate' to create one
    """
    from .tools.llmstxt import run_llmstxt
    return await run_llmstxt(url, mode)


@mcp.tool()
async def geo_technical(url: str) -> str:
    """Technical SEO and GEO analysis.

    Checks SSR rendering, robots.txt AI crawler directives,
    meta tags, heading structure, security headers, and page performance signals.

    Args:
        url: The URL to analyze
    """
    from .tools.technical import run_technical
    return await run_technical(url)


@mcp.tool()
async def geo_schema(url: str) -> str:
    """Analyze structured data (JSON-LD schema markup).

    Detects and validates all JSON-LD structured data on the page.
    Provides recommendations for improving AI discoverability through schema.

    Args:
        url: The URL to analyze for schema markup
    """
    from .tools.schema_tool import run_schema
    return await run_schema(url)


@mcp.tool()
async def geo_report(url: str, brand_name: str | None = None) -> str:
    """Generate a comprehensive markdown GEO report.

    Combines audit, citability, technical, schema, and llms.txt analysis
    into a single executive report with scores, findings, and action plan.

    Args:
        url: The URL to generate a report for
        brand_name: Optional brand name for brand-specific recommendations
    """
    from .tools.report import run_report
    return await run_report(url, brand_name)


def main():
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
