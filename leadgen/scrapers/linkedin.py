"""LinkedIn company scraper (wraps linkedin-scraper package)."""

import asyncio
import logging
import random
import sys
from pathlib import Path
from typing import Optional

from ..config import LeadGenConfig
from ..models import Lead, ScraperSource
from .base import BaseLeadScraper

logger = logging.getLogger(__name__)

# Ensure the vendored linkedin_scraper package is importable
_LI_SCRAPER_DIR = Path(__file__).resolve().parents[2] / "linkedin_scraper"
if str(_LI_SCRAPER_DIR) not in sys.path:
    sys.path.insert(0, str(_LI_SCRAPER_DIR))

from linkedin_scraper.core.browser import BrowserManager  # noqa: E402
from linkedin_scraper.scrapers.company import CompanyScraper  # noqa: E402


class LinkedInScraper(BaseLeadScraper):
    """Google-search → LinkedIn company page scraper."""

    source = ScraperSource.LINKEDIN

    def __init__(self, config: LeadGenConfig, google_searcher):
        self.config = config
        self.google = google_searcher
        self._browser: Optional[BrowserManager] = None

    async def _ensure_browser(self) -> BrowserManager:
        if self._browser is None:
            self._browser = BrowserManager(headless=self.config.HEADLESS)
            await self._browser.start()
            # Load saved LinkedIn session if available
            session_path = self.config.LINKEDIN_SESSION_PATH
            if session_path and Path(session_path).exists():
                await self._browser.load_session(session_path)
                logger.info("LinkedIn session loaded from %s", session_path)
        return self._browser

    async def search(
        self, query: str, location: Optional[str] = None, max_results: int = 20
    ) -> list[Lead]:
        search_query = f"{query} {location}" if location else query
        urls = await self.google.search_linkedin_urls(search_query)

        browser = await self._ensure_browser()
        leads: list[Lead] = []

        for url in urls[:max_results]:
            try:
                scraper = CompanyScraper(browser.page)
                company = await scraper.scrape(url)
                leads.append(self._company_to_lead(company, url))
            except Exception as exc:
                logger.warning("LinkedIn scrape failed for %s: %s", url, exc)
            await asyncio.sleep(random.uniform(3, 7))

        return leads

    async def lookup_company(self, company_name: str) -> Optional[Lead]:
        urls = await self.google.search_linkedin_urls(company_name)
        if not urls:
            return None

        browser = await self._ensure_browser()
        try:
            scraper = CompanyScraper(browser.page)
            company = await scraper.scrape(urls[0])
            return self._company_to_lead(company, urls[0])
        except Exception as exc:
            logger.warning("LinkedIn lookup failed for %s: %s", company_name, exc)
            return None

    async def close(self) -> None:
        if self._browser:
            await self._browser.close()
            self._browser = None

    @staticmethod
    def _company_to_lead(company, url: str) -> Lead:
        contact_name = None
        job_title = None
        if company.employees:
            contact_name = company.employees[0].name
            job_title = company.employees[0].designation

        return Lead(
            company_name=company.name,
            industry=company.industry,
            company_size=company.company_size,
            phone=company.phone,
            website=company.website,
            location=company.headquarters,
            linkedin_url=url,
            contact_name=contact_name,
            job_title=job_title,
            source=[ScraperSource.LINKEDIN],
        )
