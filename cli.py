#!/usr/bin/env python3
"""
Lead Generation CLI Tool
Standalone tool for testing and batch lead generation

Usage:
    python cli.py search-industry --industry "Software Development" --location "San Francisco"
    python cli.py search-company --company "Google"
    python cli.py search-location --location "New York" --keywords "Sales"
    python cli.py batch --file queries.txt
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional
from leadgen_core import LeadScraper
from leadgen_core.models import Lead, LeadStatus


class LeadGenCLI:
    """Command line interface for lead generation"""

    def __init__(
        self,
        linkedin_session: Optional[str] = None,
        scrapegraph_key: Optional[str] = None
    ):
        """Initialize CLI with optional credentials"""
        self.scraper = LeadScraper(linkedin_session, scrapegraph_key)
        self.output_format = "json"

    def search_industry(
        self,
        industry: str,
        location: Optional[str] = None,
        limit: int = 50,
        enrich: bool = True,
        output_file: Optional[str] = None
    ):
        """Search for leads by industry"""
        print(f"\n🔍 Searching for {industry} leads...")

        leads = self.scraper.search_by_industry(
            industry,
            location=location,
            limit=limit,
            enrich=enrich
        )

        self._output_results(leads, output_file)
        return leads

    def search_company(
        self,
        company_name: str,
        limit: int = 20,
        enrich: bool = True,
        output_file: Optional[str] = None
    ):
        """Search for leads by company"""
        print(f"\n🔍 Searching for leads at {company_name}...")

        leads = self.scraper.search_by_company(
            company_name,
            limit=limit,
            enrich=enrich
        )

        self._output_results(leads, output_file)
        return leads

    def search_location(
        self,
        location: str,
        keywords: Optional[str] = None,
        limit: int = 50,
        output_file: Optional[str] = None
    ):
        """Search for leads by location"""
        print(f"\n🔍 Searching for leads in {location}...")

        leads = self.scraper.search_by_location(
            location,
            keywords=keywords,
            limit=limit,
            enrich=True
        )

        self._output_results(leads, output_file)
        return leads

    def search_keywords(
        self,
        keywords: str,
        location: Optional[str] = None,
        limit: int = 50,
        output_file: Optional[str] = None
    ):
        """Advanced search by keywords"""
        print(f"\n🔍 Searching for '{keywords}'...")

        leads = self.scraper.search_by_keywords(
            keywords,
            location=location,
            limit=limit,
            enrich=True
        )

        self._output_results(leads, output_file)
        return leads

    def batch_search(
        self,
        query_file: str,
        search_type: str = "keywords",
        limit: int = 50,
        output_file: Optional[str] = None
    ):
        """Batch search from file"""
        query_file_path = Path(query_file)

        if not query_file_path.exists():
            print(f"❌ Query file not found: {query_file}")
            return []

        with open(query_file_path, 'r') as f:
            queries = [line.strip() for line in f if line.strip()]

        print(f"\n🔍 Batch searching {len(queries)} queries...")

        leads = self.scraper.batch_search(
            queries,
            search_type=search_type,
            limit=limit,
            enrich=True
        )

        self._output_results(leads, output_file)
        return leads

    def _output_results(self, leads: list[Lead], output_file: Optional[str] = None):
        """Output results to console and/or file"""
        print(f"\n✅ Found {len(leads)} leads\n")

        # Console output
        for i, lead in enumerate(leads, 1):
            self._print_lead(i, lead)

        # File output
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if output_file.endswith('.json'):
                self._save_json(leads, output_file)
            elif output_file.endswith('.csv'):
                self._save_csv(leads, output_file)
            else:
                self._save_json(leads, output_file)

            print(f"💾 Results saved to {output_file}")

    def _print_lead(self, index: int, lead: Lead):
        """Pretty print a single lead"""
        print(f"Lead #{index}")
        print(f"  Company: {lead.company_name}")
        print(f"  Contact: {lead.contact_name} ({lead.job_title})")
        print(f"  Email: {lead.email}")
        print(f"  Phone: {lead.phone}")
        print(f"  LinkedIn: {lead.linkedin_url}")
        print(f"  Location: {lead.location}")
        print(f"  Industry: {lead.industry}")
        print(f"  Company Size: {lead.company_size}")
        print(f"  Score: {lead.lead_score}/100")
        print(f"  Status: {lead.status.value}")
        if lead.notes:
            print(f"  Notes: {lead.notes}")
        print()

    def _save_json(self, leads: list[Lead], filename: str):
        """Save leads as JSON"""
        data = [lead.to_dict() for lead in leads]
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

    def _save_csv(self, leads: list[Lead], filename: str):
        """Save leads as CSV"""
        import csv

        if not leads:
            return

        headers = [
            "company_name", "contact_name", "job_title", "email", "phone",
            "linkedin_url", "industry", "location", "company_size",
            "revenue_estimate", "lead_score", "status", "notes"
        ]

        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for lead in leads:
                row = {k: lead.__dict__.get(k, '') for k in headers}
                writer.writerow(row)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Lead Generation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search by industry
  python cli.py search-industry --industry "Software Development" --location "San Francisco"

  # Search by company
  python cli.py search-company --company "Google" --limit 20

  # Search by location
  python cli.py search-location --location "New York" --keywords "Sales"

  # Batch search from file
  python cli.py batch --file queries.txt --output results.json
        """
    )

    parser.add_argument(
        "--linkedin-session",
        help="Path to LinkedIn session file",
        default=None
    )
    parser.add_argument(
        "--scrapegraph-key",
        help="ScrapeGraphAI API key",
        default=None
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Search by industry
    industry_parser = subparsers.add_parser(
        "search-industry",
        help="Search leads by industry"
    )
    industry_parser.add_argument("--industry", required=True, help="Industry name")
    industry_parser.add_argument("--location", help="Location filter")
    industry_parser.add_argument("--limit", type=int, default=50, help="Max results")
    industry_parser.add_argument("--output", help="Output file (json/csv)")
    industry_parser.add_argument("--skip-enrich", action="store_true", help="Skip enrichment")

    # Search by company
    company_parser = subparsers.add_parser(
        "search-company",
        help="Search leads by company"
    )
    company_parser.add_argument("--company", required=True, help="Company name")
    company_parser.add_argument("--limit", type=int, default=20, help="Max results")
    company_parser.add_argument("--output", help="Output file (json/csv)")
    company_parser.add_argument("--skip-enrich", action="store_true", help="Skip enrichment")

    # Search by location
    location_parser = subparsers.add_parser(
        "search-location",
        help="Search leads by location"
    )
    location_parser.add_argument("--location", required=True, help="Location")
    location_parser.add_argument("--keywords", help="Keywords/industry")
    location_parser.add_argument("--limit", type=int, default=50, help="Max results")
    location_parser.add_argument("--output", help="Output file (json/csv)")

    # Search by keywords
    keywords_parser = subparsers.add_parser(
        "search-keywords",
        help="Advanced search by keywords"
    )
    keywords_parser.add_argument("--keywords", required=True, help="Search keywords")
    keywords_parser.add_argument("--location", help="Location filter")
    keywords_parser.add_argument("--limit", type=int, default=50, help="Max results")
    keywords_parser.add_argument("--output", help="Output file (json/csv)")

    # Batch search
    batch_parser = subparsers.add_parser(
        "batch",
        help="Batch search from file"
    )
    batch_parser.add_argument("--file", required=True, help="Query file (one per line)")
    batch_parser.add_argument("--type", default="keywords", help="Search type")
    batch_parser.add_argument("--limit", type=int, default=50, help="Max results per query")
    batch_parser.add_argument("--output", help="Output file (json/csv)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize CLI
    cli = LeadGenCLI(args.linkedin_session, args.scrapegraph_key)

    try:
        if args.command == "search-industry":
            cli.search_industry(
                args.industry,
                location=args.location,
                limit=args.limit,
                enrich=not args.skip_enrich,
                output_file=args.output
            )
        elif args.command == "search-company":
            cli.search_company(
                args.company,
                limit=args.limit,
                enrich=not args.skip_enrich,
                output_file=args.output
            )
        elif args.command == "search-location":
            cli.search_location(
                args.location,
                keywords=args.keywords,
                limit=args.limit,
                output_file=args.output
            )
        elif args.command == "search-keywords":
            cli.search_keywords(
                args.keywords,
                location=args.location,
                limit=args.limit,
                output_file=args.output
            )
        elif args.command == "batch":
            cli.batch_search(
                args.file,
                search_type=args.type,
                limit=args.limit,
                output_file=args.output
            )
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
