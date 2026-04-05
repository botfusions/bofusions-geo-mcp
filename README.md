<div align="center">

# Bofusions GEO MCP

**AI Search Engine Optimization (GEO) Analysis Tools for MCP Clients**

[![PyPI](https://img.shields.io/pypi/v/bofusions-geo-mcp?color=blue&label=PyPI)](https://pypi.org/project/bofusions-geo-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/bofusions-geo-mcp?label=Python)](https://pypi.org/project/bofusions-geo-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-botfusions%2Fbofusions--geo--mcp-black?logo=github)](https://github.com/botfusions/bofusions-geo-mcp)

Optimize your website for AI-powered search engines — **ChatGPT, Claude, Perplexity, Gemini, Google AI Overviews**.

> GEO (Generative Engine Optimization) focuses on being **the source AI models quote** — not just ranking on Google.

Built by **[Bofusions](https://github.com/botfusions)**

</div>

---

## Why GEO?

| Traditional SEO | GEO (This Tool) |
|-----------------|------------------|
| Optimize for Google crawlers | Optimize for AI model training data |
| Rank #1 on search results | Be the **cited source** in AI answers |
| Keywords & backlinks | Citability, brand authority, structured data |
| Google-focused | ChatGPT, Claude, Perplexity, Gemini, AIO |

**The market is shifting:**
- AI-referred traffic grew **+527%** year-over-year
- GEO services market projected **$7.3B by 2031**
- AI traffic conversion rate **4.4x higher** than organic

---

## Installation

```bash
# Run directly (recommended)
uvx bofusions-geo-mcp

# Or install with pip
pip install bofusions-geo-mcp
```

---

## MCP Client Configuration

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "Bofusions GEO": {
      "command": "uvx",
      "args": ["bofusions-geo-mcp"]
    }
  }
}
```

### Cursor / VS Code / 5ire / Other MCP Clients

```json
{
  "mcpServers": {
    "bofusions-geo": {
      "command": "uvx",
      "args": ["bofusions-geo-mcp"]
    }
  }
}
```

### pip install (alternative)

```json
{
  "mcpServers": {
    "Bofusions GEO": {
      "command": "python",
      "args": ["-m", "bofusions_geo_mcp.server"]
    }
  }
}
```

---

## Tools (7)

| Tool | Input | Description |
|------|-------|-------------|
| `geo_audit` | URL | Full GEO audit with scoring (0-100) and prioritized action items |
| `geo_citability` | URL | Score every content passage for AI citation readiness |
| `geo_brand_scan` | Brand name | Scan brand presence across YouTube, Reddit, Wikipedia, LinkedIn, GitHub + 7 platforms |
| `geo_llmstxt` | URL + mode | Validate existing `llms.txt` or generate a new one |
| `geo_technical` | URL | Technical analysis — SSR detection, robots.txt AI directives, meta tags, security headers |
| `geo_schema` | URL | Detect and validate JSON-LD structured data for AI discoverability |
| `geo_report` | URL + brand | Comprehensive markdown report combining all analyses |

---

## Usage Examples

Once connected to your MCP client, just ask naturally:

### Full GEO Audit
```
Run a GEO audit on https://example.com
```

### AI Citability Scoring
```
Score https://example.com/blog/post for AI citation readiness
```

### Brand Presence Scan
```
Scan brand "Acme Corp" across AI-cited platforms
```

### llms.txt Generation
```
Generate an llms.txt file for https://example.com
```

### Structured Data Check
```
Check JSON-LD schema on https://example.com
```

### Full Report
```
Generate a comprehensive GEO report for https://example.com with brand "Acme Corp"
```

---

## GEO Score Breakdown

Every `geo_audit` and `geo_report` produces a **GEO Score (0-100)**:

| Component | Weight | What It Measures |
|-----------|--------|------------------|
| **AI Citability** | 25% | Passage-level scoring — how likely AI will quote your content |
| **Brand Authority** | 20% | Presence on YouTube, Reddit, Wikipedia, LinkedIn (3x stronger than backlinks) |
| **Content Quality** | 20% | E-E-A-T signals, readability, statistical density |
| **Technical** | 15% | SSR rendering, robots.txt AI crawler access, meta tags |
| **Structured Data** | 10% | JSON-LD schema completeness (Organization, WebSite, etc.) |
| **Platform Optimization** | 10% | llms.txt existence, AI crawler friendliness |

**Grading:** A (80+) / B (65+) / C (50+) / D (35+) / F (<35)

---

## Citability Scoring Engine

Each content passage is scored on 5 dimensions:

| Dimension | Weight | Optimal |
|-----------|--------|---------|
| Answer Block Quality | 30% | Definition patterns, early answers, quotable claims |
| Self-Containment | 25% | 134-167 words, low pronoun density, named entities |
| Structural Readability | 20% | 10-20 word sentences, list patterns, paragraph breaks |
| Statistical Density | 15% | Percentages, dollar amounts, named sources |
| Uniqueness Signals | 10% | Original research, case studies, specific tools |

**Key finding:** Optimal AI-cited passages are **134-167 words**, self-contained, and fact-rich.

---

## AI Crawler Coverage

The technical analysis checks access for **14 AI crawlers**:

GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, anthropic-ai, PerplexityBot, CCBot, Bytespider, cohere-ai, Google-Extended, GoogleOther, Applebot-Extended, FacebookBot, Amazonbot

---

## Brand Scan Platforms

| Platform | Correlation | Why It Matters |
|----------|-------------|----------------|
| **YouTube** | 0.737 (strongest) | Video transcripts are major AI training source |
| **Reddit** | High | Authentic discussions heavily cited by AI |
| **Wikipedia** | High | Structured entity data, knowledge graph |
| **LinkedIn** | Moderate | Thought leadership, company authority |
| **GitHub** | Moderate | Developer brand, open-source authority |
| **+ 7 more** | Varies | Quora, Stack Overflow, G2, Trustpilot, Crunchbase, Product Hunt |

---

## Output Format

All tools return **Markdown** — optimized for LLM consumption and human readability:

```markdown
# GEO Audit Report

> **Bofusions GEO MCP** | `https://example.com`

## Overall GEO Score: 72.5/100 (Grade B)

| Component | Weight | Score |
|-----------|--------|-------|
| Ai Citability | 25% | 68.2 |
| Brand Authority | 20% | 45.0 |
| Content Quality | 20% | 71.3 |
| Technical | 15% | 85.0 |
| Schema | 10% | 75.0 |
| Platform | 10% | 90.0 |

## Priority Action Items
1. Restructure content into 134-167 word self-contained passages
2. Add Organization + WebSite JSON-LD schema
...
```

---

## Development

```bash
git clone https://github.com/botfusions/bofusions-geo-mcp.git
cd bofusions-geo-mcp

python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -e .
python -m bofusions_geo_mcp.server
```

### Run Tests

```bash
python -c "
import asyncio
from bofusions_geo_mcp.tools.technical import run_technical
print(asyncio.run(run_technical('https://example.com')))
"
```

---

## Tech Stack

- **Framework:** [FastMCP](https://github.com/jlowin/fastmcp) — Model Context Protocol server
- **HTTP Client:** [httpx](https://www.python-httpx.org/) — async HTTP with SSL fallback
- **HTML Parsing:** [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) + [lxml](https://lxml.de/)
- **Python:** 3.11+ (3.12, 3.13 supported)

---

## Requirements

- Python >= 3.11
- mcp[cli] >= 1.6.0
- httpx >= 0.27.0
- beautifulsoup4 >= 4.12.0
- lxml >= 5.0.0
- validators >= 0.22.0

---

## License

[MIT License](LICENSE) — Copyright (c) 2026 Bofusions

---

<div align="center">

**[Bofusions](https://github.com/botfusions)** — Building the future of AI-powered search optimization.

[Report Bug](https://github.com/botfusions/bofusions-geo-mcp/issues) · [Request Feature](https://github.com/botfusions/bofusions-geo-mcp/issues) · [PyPI](https://pypi.org/project/bofusions-geo-mcp/)

</div>
