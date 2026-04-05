"""Interactive CLI demo for the sales team (verbose mode)."""

import asyncio
import logging
import sys
import time
from pathlib import Path

# Ensure leadgen package is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tabulate import tabulate

from leadgen import LeadGenerator, SearchRequest, ScraperSource, LeadGenConfig

# ── Verbose logging setup ────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout,
)
# Quieten noisy libraries but keep our own logs
for noisy in ("httpx", "httpcore", "playwright", "urllib3", "openai"):
    logging.getLogger(noisy).setLevel(logging.WARNING)

logger = logging.getLogger("demo")


def vprint(msg: str):
    """Verbose timestamped print."""
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}]  {msg}")


def print_leads_table(leads, title="Results"):
    """Pretty-print leads in a table."""
    if not leads:
        vprint(f"{title}: No leads found.")
        return

    headers = [
        "Company", "Contact", "Title", "Phone", "Email",
        "Location", "Industry", "Size", "LinkedIn", "Source",
    ]
    rows = []
    for lead in leads:
        rows.append([
            (lead.company_name or "")[:30],
            (lead.contact_name or "")[:20],
            (lead.job_title or "")[:20],
            (lead.phone or "")[:18],
            (lead.email or "")[:25],
            (lead.location or "")[:25],
            (lead.industry or "")[:20],
            (lead.company_size or "")[:15],
            (lead.linkedin_url or "")[:40],
            ", ".join(s.value for s in lead.source),
        ])

    print(f"\n{'='*80}")
    print(f"  {title}  ({len(leads)} leads)")
    print(f"{'='*80}")
    print(tabulate(rows, headers=headers, tablefmt="grid", maxcolwidths=30))
    print()


def print_config(config: LeadGenConfig):
    """Show active configuration."""
    print(f"\n{'─'*60}")
    print("  Active Configuration")
    print(f"{'─'*60}")
    print(f"  NVIDIA NIM Model   : {config.NVIDIA_NIM_MODEL}")
    print(f"  NVIDIA NIM Base URL: {config.NVIDIA_NIM_BASE_URL}")
    print(f"  NVIDIA NIM API Key : {'***' + config.NVIDIA_NIM_API_KEY[-8:] if config.NVIDIA_NIM_API_KEY else 'NOT SET'}")
    print(f"  LinkedIn Session   : {config.LINKEDIN_SESSION_PATH or 'NOT SET'}")
    print(f"  Headless           : {config.HEADLESS}")
    print(f"  Request Delay      : {config.REQUEST_DELAY}s")
    print(f"  Google Max Pages   : {config.GOOGLE_SEARCH_MAX_PAGES}")
    print(f"  Fuzzy Threshold    : {config.FUZZY_MATCH_THRESHOLD}%")
    print(f"{'─'*60}\n")


async def demo_keyword_suggestion(gen: LeadGenerator):
    """Demo 1: AI Keyword Suggestion."""
    print("\n" + "="*60)
    print("  DEMO 1: AI Keyword Suggestion")
    print("="*60)

    prompt = "hospitality industry in South India"
    vprint(f"Prompt: {prompt!r}")
    vprint(f"Calling NVIDIA NIM ({gen.config.NVIDIA_NIM_MODEL}) ...")

    t0 = time.time()
    keywords = await gen.suggest_keywords(prompt)
    elapsed = time.time() - t0

    if keywords:
        vprint(f"Got {len(keywords)} keywords in {elapsed:.1f}s:")
        for i, kw in enumerate(keywords, 1):
            print(f"    {i}. {kw}")
    else:
        vprint(f"No keywords returned (took {elapsed:.1f}s). Check API key / model name.")


async def demo_keyword_search(gen: LeadGenerator):
    """Demo 2: Keyword Search."""
    print("\n" + "="*60)
    print("  DEMO 2: Keyword Search")
    print("="*60)

    query = "hotels in Chennai"
    vprint(f"Query: {query!r}")
    vprint("Starting pipeline: Google Search -> LinkedIn -> Google Maps -> Enricher -> ScrapeGraphAI fallback")

    t0 = time.time()
    result = await gen.search(query)
    elapsed = time.time() - t0

    vprint(f"Pipeline completed in {elapsed:.1f}s")
    vprint(f"Sources used: {[s.value for s in result.sources_used]}")
    vprint(f"Total leads found: {result.total}")
    if result.errors:
        vprint(f"Errors encountered:")
        for err in result.errors:
            print(f"    ! {err}")
    print_leads_table(result.leads, f"Search: {query}")


async def demo_company_lookup_default(gen: LeadGenerator):
    """Demo 3: Company Lookup — all sources."""
    print("\n" + "="*60)
    print("  DEMO 3: Company Lookup (all sources)")
    print("="*60)

    name = "Microsoft"
    vprint(f"Looking up: {name!r} via LinkedIn -> Google Maps -> ScrapeGraphAI")

    t0 = time.time()
    lead = await gen.lookup(name)
    elapsed = time.time() - t0

    vprint(f"Lookup completed in {elapsed:.1f}s")
    if lead:
        vprint(f"Sources that contributed: {[s.value for s in lead.source]}")
        print_leads_table([lead], f"Lookup: {name}")
    else:
        vprint("No result found from any source.")


async def demo_company_lookup_scrapegraph(gen: LeadGenerator):
    """Demo 4: Company Lookup — ScrapeGraphAI only."""
    print("\n" + "="*60)
    print("  DEMO 4: Company Lookup (ScrapeGraphAI only)")
    print("="*60)

    name = "Microsoft"
    vprint(f"Looking up: {name!r} via ScrapeGraphAI only")

    t0 = time.time()
    lead = await gen.lookup(name, sources=[ScraperSource.SCRAPEGRAPH])
    elapsed = time.time() - t0

    vprint(f"Lookup completed in {elapsed:.1f}s")
    if lead:
        print_leads_table([lead], f"Lookup: {name} (scrapegraph)")
    else:
        vprint("No result found.")


async def demo_company_lookup_li_gmap(gen: LeadGenerator):
    """Demo 5: Company Lookup — LinkedIn + Google Maps only."""
    print("\n" + "="*60)
    print("  DEMO 5: Company Lookup (LinkedIn + Google Maps)")
    print("="*60)

    name = "Microsoft"
    vprint(f"Looking up: {name!r} via LinkedIn + Google Maps")

    t0 = time.time()
    lead = await gen.lookup(
        name, sources=[ScraperSource.LINKEDIN, ScraperSource.GOOGLE_MAPS]
    )
    elapsed = time.time() - t0

    vprint(f"Lookup completed in {elapsed:.1f}s")
    if lead:
        vprint(f"Sources that contributed: {[s.value for s in lead.source]}")
        print_leads_table([lead], f"Lookup: {name} (li+gmap)")
    else:
        vprint("No result found.")


async def demo_full_pipeline(gen: LeadGenerator):
    """Demo 6: Full Pipeline — AI suggests → search → display."""
    print("\n" + "="*60)
    print("  DEMO 6: Full Pipeline")
    print("="*60)

    prompt = "luxury hotels in Tamil Nadu"
    vprint(f"Step 1 — AI Keyword Suggestion for: {prompt!r}")

    t0 = time.time()
    keywords = await gen.suggest_keywords(prompt)
    elapsed = time.time() - t0

    if keywords:
        vprint(f"Got {len(keywords)} keywords in {elapsed:.1f}s:")
        for i, kw in enumerate(keywords, 1):
            print(f"    {i}. {kw}")
        query = keywords[0]
    else:
        vprint(f"No keywords returned ({elapsed:.1f}s) — falling back to raw prompt")
        query = prompt

    vprint(f"\nStep 2 — Searching: {query!r}")
    vprint("Running full pipeline ...")

    t0 = time.time()
    request = SearchRequest(query=query, max_results=10)
    result = await gen.search(request)
    elapsed = time.time() - t0

    vprint(f"Pipeline completed in {elapsed:.1f}s")
    vprint(f"Sources used: {[s.value for s in result.sources_used]}")
    vprint(f"Total leads: {result.total}")
    if result.errors:
        vprint("Errors:")
        for err in result.errors:
            print(f"    ! {err}")
    print_leads_table(result.leads, f"Full Pipeline: {query}")


async def main():
    print("=" * 60)
    print("  Lead Generation Module — Sales Team Demo (VERBOSE)")
    print("=" * 60)

    config = LeadGenConfig()
    print_config(config)

    async with LeadGenerator(config) as gen:
        demos = [
            ("1", "AI Keyword Suggestion", demo_keyword_suggestion),
            ("2", "Keyword Search", demo_keyword_search),
            ("3", "Company Lookup (all sources)", demo_company_lookup_default),
            ("4", "Company Lookup (ScrapeGraphAI only)", demo_company_lookup_scrapegraph),
            ("5", "Company Lookup (LinkedIn + GMaps)", demo_company_lookup_li_gmap),
            ("6", "Full Pipeline", demo_full_pipeline),
            ("a", "Run ALL demos", None),
        ]

        print("Available demos:")
        for key, desc, _ in demos:
            print(f"  [{key}] {desc}")
        print(f"  [q] Quit\n")

        choice = input("Select demo (1-6, a, q): ").strip().lower()

        if choice == "q":
            return

        if choice == "a":
            for key, _, func in demos:
                if func:
                    await func(gen)
        else:
            for key, _, func in demos:
                if key == choice and func:
                    await func(gen)
                    break
            else:
                print(f"Unknown choice: {choice}")


if __name__ == "__main__":
    asyncio.run(main())
