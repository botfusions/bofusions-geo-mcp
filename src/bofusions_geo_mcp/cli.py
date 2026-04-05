"""Bofusions GEO MCP — CLI interface for AI Search Engine Optimization analysis."""

from __future__ import annotations

import argparse
import asyncio
import sys

from . import __version__


def _run(fn, *args, **kwargs):
    """Run an async function and print the result."""
    try:
        result = asyncio.run(fn(*args, **kwargs))
        print(result)
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(130)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_audit(args):
    from .tools.audit import run_audit
    _run(run_audit, args.url)


def cmd_citability(args):
    from .tools.citability import run_citability
    _run(run_citability, args.url)


def cmd_brand_scan(args):
    from .tools.brand_scan import run_brand_scan
    _run(run_brand_scan, args.brand_name, getattr(args, "domain", None))


def cmd_llmstxt(args):
    from .tools.llmstxt import run_llmstxt
    _run(run_llmstxt, args.url, args.mode)


def cmd_technical(args):
    from .tools.technical import run_technical
    _run(run_technical, args.url)


def cmd_schema(args):
    from .tools.schema_tool import run_schema
    _run(run_schema, args.url)


def cmd_report(args):
    from .tools.report import run_report
    _run(run_report, args.url, getattr(args, "brand", None))


def main():
    parser = argparse.ArgumentParser(
        prog="bofusions-geo",
        description="Bofusions GEO — AI Search Engine Optimization CLI",
        epilog="Examples:\n"
        "  bofusions-geo audit https://example.com\n"
        "  bofusions-geo citability https://example.com/blog\n"
        "  bofusions-geo brand-scan 'Acme Corp' --domain acme.com\n"
        "  bofusions-geo llmstxt https://example.com --mode generate\n"
        "  bofusions-geo report https://example.com --brand 'Acme Corp'\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    sub = parser.add_subparsers(dest="command", help="Available commands")

    # audit
    p_audit = sub.add_parser("audit", help="Full GEO audit with scoring (0-100)")
    p_audit.add_argument("url", help="URL to audit")
    p_audit.set_defaults(func=cmd_audit)

    # citability
    p_cit = sub.add_parser("citability", help="Score content passages for AI citation readiness")
    p_cit.add_argument("url", help="URL to analyze")
    p_cit.set_defaults(func=cmd_citability)

    # brand-scan
    p_brand = sub.add_parser("brand-scan", help="Scan brand mentions across AI-cited platforms")
    p_brand.add_argument("brand_name", help="Brand or company name")
    p_brand.add_argument("--domain", "-d", help="Website domain (optional)")
    p_brand.set_defaults(func=cmd_brand_scan)

    # llmstxt
    p_llms = sub.add_parser("llmstxt", help="Validate or generate llms.txt")
    p_llms.add_argument("url", help="Website URL")
    p_llms.add_argument("--mode", "-m", choices=["validate", "generate"], default="validate",
                        help="validate (default) or generate")
    p_llms.set_defaults(func=cmd_llmstxt)

    # technical
    p_tech = sub.add_parser("technical", help="Technical SEO/GEO analysis")
    p_tech.add_argument("url", help="URL to analyze")
    p_tech.set_defaults(func=cmd_technical)

    # schema
    p_schema = sub.add_parser("schema", help="Analyze JSON-LD structured data")
    p_schema.add_argument("url", help="URL to analyze")
    p_schema.set_defaults(func=cmd_schema)

    # report
    p_report = sub.add_parser("report", help="Comprehensive markdown GEO report")
    p_report.add_argument("url", help="URL to report on")
    p_report.add_argument("--brand", "-b", help="Brand name for brand-specific recommendations")
    p_report.set_defaults(func=cmd_report)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
