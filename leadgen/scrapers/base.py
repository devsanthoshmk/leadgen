"""Abstract base class for lead scrapers."""

from abc import ABC, abstractmethod
from typing import Optional

from ..models import Lead, ScraperSource


class BaseLeadScraper(ABC):
    """Interface that every scraper must implement."""

    source: ScraperSource

    @abstractmethod
    async def search(
        self, query: str, location: Optional[str] = None, max_results: int = 20
    ) -> list[Lead]:
        """Search for leads matching *query*."""

    @abstractmethod
    async def lookup_company(self, company_name: str) -> Optional[Lead]:
        """Look up a single company by name."""

    async def close(self) -> None:
        """Release resources (override if needed)."""
