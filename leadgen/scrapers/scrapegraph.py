"""ScrapeGraphAI wrapper — used as fallback when primary scrapers fail."""

import logging
from typing import Optional

from ..config import LeadGenConfig
from ..models import Lead, ScraperSource
from .base import BaseLeadScraper

logger = logging.getLogger(__name__)


def _llm_config(config: LeadGenConfig) -> dict:
    return {
        "model": f"openai/{config.NVIDIA_NIM_MODEL}",
        "api_key": config.NVIDIA_NIM_API_KEY,
        "base_url": config.NVIDIA_NIM_BASE_URL,
        "temperature": 0,
    }


def _graph_config(config: LeadGenConfig) -> dict:
    return {
        "llm": _llm_config(config),
        "model_tokens": 32768,
    }


class ScrapegraphScraper(BaseLeadScraper):
    """ScrapeGraphAI-based scraper (fallback)."""

    source = ScraperSource.SCRAPEGRAPH

    def __init__(self, config: LeadGenConfig):
        self.config = config

    async def search(
        self, query: str, location: Optional[str] = None, max_results: int = 20
    ) -> list[Lead]:
        try:
            from scrapegraphai.graphs import SearchGraph
        except ImportError:
            logger.error("scrapegraphai not installed — skipping fallback search")
            return []

        search_query = f"{query} {location}" if location else query
        prompt = (
            f"Find companies matching '{search_query}'. For each, extract: "
            "company_name, email, phone, industry, location, company_size, "
            "revenue_estimate, key_contact_name, key_contact_title, linkedin_url. "
            "Return ONLY verified data visible on pages."
        )

        graph = SearchGraph(prompt=prompt, config=_graph_config(self.config))

        try:
            result = graph.run()
        except Exception as exc:
            logger.error("ScrapeGraphAI search failed: %s", exc)
            return []

        return self._parse_results(result, max_results)

    async def deep_scrape_company(self, website_url: str) -> Optional[Lead]:
        """Multi-page scrape — replaces LinkedIn when it fails."""
        try:
            from scrapegraphai.graphs import SmartScraperMultiGraph
        except ImportError:
            logger.error("scrapegraphai not installed")
            return None

        urls = [
            website_url,
            f"{website_url.rstrip('/')}/about",
            f"{website_url.rstrip('/')}/contact",
            f"{website_url.rstrip('/')}/team",
        ]
        prompt = (
            "Extract: company_name, email, phone, industry, location, "
            "company_size, revenue_estimate, key_contact_name, "
            "key_contact_title, linkedin_url. Return ONLY verified data."
        )

        graph = SmartScraperMultiGraph(
            prompt=prompt,
            source=urls,
            config=_graph_config(self.config),
        )

        try:
            result = graph.run()
        except Exception as exc:
            logger.error("ScrapeGraphAI deep scrape failed: %s", exc)
            return None

        leads = self._parse_results(result, 1)
        return leads[0] if leads else None

    async def quick_enrich(self, company_name: str) -> Optional[Lead]:
        """Single-call enrichment — replaces GMap when it fails."""
        try:
            from scrapegraphai.graphs import SmartScraperGraph
        except ImportError:
            logger.error("scrapegraphai not installed")
            return None

        prompt = (
            f"Find {company_name} phone number, email address, "
            "physical address, and revenue estimate."
        )

        graph = SmartScraperGraph(
            prompt=prompt,
            source=f"https://www.google.com/search?q={company_name}",
            config=_graph_config(self.config),
        )

        try:
            result = graph.run()
        except Exception as exc:
            logger.error("ScrapeGraphAI quick_enrich failed: %s", exc)
            return None

        if isinstance(result, dict):
            return Lead(
                company_name=result.get("company_name") or company_name,
                email=result.get("email"),
                phone=result.get("phone"),
                location=result.get("location") or result.get("address"),
                revenue_estimate=result.get("revenue_estimate"),
                source=[ScraperSource.SCRAPEGRAPH],
            )
        return None

    async def lookup_company(self, company_name: str) -> Optional[Lead]:
        """SearchGraph to find website, then deep_scrape_company on it."""
        try:
            from scrapegraphai.graphs import SearchGraph
        except ImportError:
            return None

        prompt = f"Find the official website URL for the company '{company_name}'."
        graph = SearchGraph(prompt=prompt, config=_graph_config(self.config))

        try:
            result = graph.run()
        except Exception as exc:
            logger.error("ScrapeGraphAI lookup failed: %s", exc)
            return None

        website = None
        if isinstance(result, dict):
            website = result.get("website") or result.get("url")
        elif isinstance(result, str):
            website = result

        if website:
            return await self.deep_scrape_company(website)
        return None

    # ------------------------------------------------------------------

    @staticmethod
    def _parse_results(result, max_results: int) -> list[Lead]:
        items = []
        if isinstance(result, list):
            items = result
        elif isinstance(result, dict):
            items = result.get("companies", result.get("results", [result]))

        leads: list[Lead] = []
        for item in items[:max_results]:
            if not isinstance(item, dict):
                continue
            leads.append(
                Lead(
                    company_name=item.get("company_name"),
                    email=item.get("email"),
                    phone=item.get("phone"),
                    industry=item.get("industry"),
                    location=item.get("location"),
                    company_size=item.get("company_size"),
                    revenue_estimate=item.get("revenue_estimate"),
                    contact_name=item.get("key_contact_name"),
                    job_title=item.get("key_contact_title"),
                    linkedin_url=item.get("linkedin_url"),
                    source=[ScraperSource.SCRAPEGRAPH],
                )
            )
        return leads
