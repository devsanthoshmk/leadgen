"""
ScrapeGraphAI integration for advanced web scraping
Fallback enrichment source for missing lead data
"""

import os
from typing import List, Optional, Dict
from .models import Lead, ScrapeSource, LeadStatus

try:
    from scrapegraphai.graphs import SmartScraperGraph
    SCRAPEGRAPH_AVAILABLE = True
except ImportError:
    SCRAPEGRAPH_AVAILABLE = False


class ScrapeGraphAdapter:
    """Wrapper for ScrapeGraphAI integration"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize ScrapeGraphAI adapter

        Args:
            api_key: Optional API key for ScrapeGraphAI
                    Falls back to SCRAPEGRAPH_API_KEY env var
        """
        self.api_key = api_key or os.getenv("SCRAPEGRAPH_API_KEY", "")
        self.available = SCRAPEGRAPH_AVAILABLE and self.api_key

    def scrape_website(self, url: str, schema: Dict) -> Optional[Dict]:
        """
        Scrape website for structured data

        Args:
            url: Website URL to scrape
            schema: Schema defining what data to extract

        Returns:
            Extracted data dict or None
        """
        if not self.available:
            print("ScrapeGraphAI not available or API key not set")
            return None

        try:
            scraper = SmartScraperGraph(
                prompt=f"Extract company information from this website: {url}",
                source=url,
                config={
                    "api_key": self.api_key,
                    "model": "gpt-3.5-turbo"  # Free tier model
                }
            )

            result = scraper.run()
            return result

        except Exception as e:
            print(f"Error scraping with ScrapeGraphAI: {e}")
            return None

    def enrich_lead(self, lead: Lead, website_url: Optional[str] = None) -> Lead:
        """
        Enrich lead data using ScrapeGraphAI

        Args:
            lead: Lead to enrich
            website_url: Optional company website URL to scrape

        Returns:
            Enriched Lead object
        """
        if not website_url:
            # Try to infer from company name
            website_url = f"https://{lead.company_name.lower().replace(' ', '')}.com"

        schema = {
            "email": "company email",
            "phone": "company phone",
            "industry": "company industry",
            "company_size": "employee count or company size",
            "revenue": "annual revenue estimate"
        }

        data = self.scrape_website(website_url, schema)

        if data:
            if data.get("email") and not lead.email:
                lead.email = data["email"]
            if data.get("phone") and not lead.phone:
                lead.phone = data["phone"]
            if data.get("industry") and lead.industry == "Unknown":
                lead.industry = data["industry"]
            if data.get("company_size") and lead.company_size == "Unknown":
                lead.company_size = data["company_size"]
            if data.get("revenue") and not lead.revenue_estimate:
                lead.revenue_estimate = data["revenue"]

            lead.source = ScrapeSource.SCRAPEGRAPH

        return lead

    def bulk_enrich_leads(self, leads: List[Lead], rate_limit: int = 5) -> List[Lead]:
        """
        Enrich multiple leads (with rate limiting)

        Args:
            leads: List of leads to enrich
            rate_limit: Max requests per minute (ScrapeGraphAI free tier limit)

        Returns:
            List of enriched leads
        """
        import time

        enriched = []
        for i, lead in enumerate(leads):
            enriched_lead = self.enrich_lead(lead)
            enriched.append(enriched_lead)

            # Rate limiting
            if (i + 1) % rate_limit == 0 and i < len(leads) - 1:
                print(f"Rate limiting: sleeping 60 seconds ({i+1}/{len(leads)})")
                time.sleep(60)

        return enriched
