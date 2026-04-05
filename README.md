# Bofusions GEO MCP

**AI Search Engine Optimization (GEO) analysis tools for MCP clients**

by [Bofusions](https://github.com/bofusions)

Optimize your website for AI-powered search engines — ChatGPT, Claude, Perplexity, Gemini, and Google AI Overviews.

## What is GEO?

GEO (Generative Engine Optimization) is the practice of optimizing web content so AI models can find, understand, and cite it. Traditional SEO focuses on Google rankings. GEO focuses on being **the source AI models quote**.

## Tools (7)

| Tool | Description |
|------|-------------|
| `geo_audit` | Full GEO audit with scoring (0-100) and prioritized actions |
| `geo_citability` | Score content passages for AI citation readiness |
| `geo_brand_scan` | Scan brand mentions across YouTube, Reddit, Wikipedia, LinkedIn, etc. |
| `geo_llmstxt` | Validate or generate llms.txt for AI crawler guidance |
| `geo_technical` | Technical SEO/GEO analysis (SSR, robots.txt, meta tags) |
| `geo_schema` | Analyze JSON-LD structured data for AI discoverability |
| `geo_report` | Comprehensive markdown report combining all analyses |

## Installation

```bash
# Run directly (recommended)
uvx bofusions-geo-mcp

# Or install with pip
pip install bofusions-geo-mcp
```

## Configuration

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

### 5ire / Other MCP Clients

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

## Usage Examples

### Full GEO Audit
```
Run a GEO audit on https://example.com
```

### Citability Analysis
```
Check AI citability scores for https://example.com/blog/post
```

### Brand Scan
```
Scan brand mentions for "Bofusions" across AI-cited platforms
```

### Generate llms.txt
```
Generate an llms.txt file for https://example.com
```

### Comprehensive Report
```
Generate a GEO report for https://example.com with brand name "Acme Corp"
```

## GEO Score Components

| Component | Weight | Description |
|-----------|--------|-------------|
| AI Citability | 25% | Passage-level citation readiness |
| Brand Authority | 20% | Mentions on AI-cited platforms |
| Content Quality | 20% | E-E-A-T, readability, originality |
| Technical | 15% | SSR, robots.txt, crawlability |
| Structured Data | 10% | JSON-LD schema completeness |
| Platform Opt. | 10% | llms.txt, platform-specific readiness |

## Key Insights

- **AI-referred traffic** grew +527% year-over-year
- **Brand mentions** correlate 3x more strongly with AI visibility than backlinks
- **Optimal AI-cited passages** are 134-167 words, self-contained
- **YouTube presence** has the highest correlation (0.737) with AI citations

## Development

```bash
# Clone
git clone https://github.com/bofusions/bofusions-geo-mcp.git
cd bofusions-geo-mcp

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -e .

# Run server
python -m bofusions_geo_mcp.server
```

## Requirements

- Python 3.11+
- httpx
- beautifulsoup4
- lxml
- mcp[cli]

## License

MIT License — Copyright (c) 2026 Bofusions

---

**[Bofusions](https://github.com/bofusions)** — Building the future of AI-powered search optimization.
