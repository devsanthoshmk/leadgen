"""LeadGenerator — main orchestrator for the lead generation pipeline."""

import logging
from typing import Optional

from .config import LeadGenConfig
from .enricher import fuzzy_match_and_merge, identify_gaps
from .google_search import GoogleSearcher
from .keyword_ai import suggest_keywords as _suggest_keywords
from .models import Lead, LeadResult, ScraperSource, SearchRequest
from .scrapers.google_maps import GoogleMapsScraper
from .scrapers.linkedin import LinkedInScraper
from .scrapers.scrapegraph import ScrapegraphScraper

logger = logging.getLogger(__name__)


class LeadGenerator:
    """High-level API that chains Google Search → LinkedIn → GMap → ScrapeGraphAI."""

    def __init__(self, config: Optional[LeadGenConfig] = None):
        self.config = config or LeadGenConfig()
        self._google = GoogleSearcher(self.config)
        self._linkedin = LinkedInScraper(self.config, self._google)
        self._gmap = GoogleMapsScraper(self.config)
        self._gmap.set_google_searcher(self._google)  # Share browser
        self._scrapegraph = ScrapegraphScraper(self.config)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        await self.close()

    async def close(self):
        await self._google.close()
        await self._linkedin.close()
        await self._gmap.close()
        await self._scrapegraph.close()

    # ------------------------------------------------------------------
    # Main search pipeline
    # ------------------------------------------------------------------

    async def search(self, query: str | SearchRequest) -> LeadResult:
        """Run the full lead-gen pipeline for *query*."""
        if isinstance(query, str):
            request = SearchRequest(query=query)
        else:
            request = query

        errors: list[str] = []
        sources_used: list[ScraperSource] = []
        linkedin_leads: list[Lead] = []
        gmap_leads: list[Lead] = []

        # Step 1: LinkedIn (Google search → LinkedIn scrape)
        if ScraperSource.LINKEDIN in request.sources:
            try:
                linkedin_leads = await self._linkedin.search(
                    request.query, request.location, request.max_results
                )
                if linkedin_leads:
                    sources_used.append(ScraperSource.LINKEDIN)
            except Exception as exc:
                errors.append(f"LinkedIn: {exc}")
                logger.error("LinkedIn search failed: %s", exc)

        # Step 2: Google Maps (use company names from LinkedIn, or raw query)
        if ScraperSource.GOOGLE_MAPS in request.sources:
            try:
                gmap_query = request.query
                if request.location:
                    gmap_query = f"{gmap_query} {request.location}"
                gmap_leads = await self._gmap.search(
                    gmap_query, max_results=request.max_results
                )
                if gmap_leads:
                    sources_used.append(ScraperSource.GOOGLE_MAPS)
            except Exception as exc:
                errors.append(f"Google Maps: {exc}")
                logger.error("Google Maps search failed: %s", exc)

        # Step 3: Merge LinkedIn + GMap
        if linkedin_leads and gmap_leads:
            merged = fuzzy_match_and_merge(
                linkedin_leads, gmap_leads, self.config
            )
        elif linkedin_leads:
            merged = linkedin_leads
        elif gmap_leads:
            merged = gmap_leads
        else:
            merged = []

        # Step 4: ScrapeGraphAI fallback for gaps
        if ScraperSource.SCRAPEGRAPH in request.sources and merged:
            sg_used = False
            for i, lead in enumerate(merged):
                gaps = identify_gaps(lead)
                if not gaps:
                    continue

                li_failed = ScraperSource.LINKEDIN not in lead.source
                gmap_failed = ScraperSource.GOOGLE_MAPS not in lead.source

                try:
                    if li_failed and lead.website:
                        enriched = await self._scrapegraph.deep_scrape_company(
                            lead.website
                        )
                        if enriched:
                            merged[i] = _merge_into(lead, enriched)
                            sg_used = True
                    elif gmap_failed and lead.company_name:
                        enriched = await self._scrapegraph.quick_enrich(
                            lead.company_name
                        )
                        if enriched:
                            merged[i] = _merge_into(lead, enriched)
                            sg_used = True
                except Exception as exc:
                    errors.append(f"ScrapeGraphAI fallback: {exc}")

            if sg_used:
                sources_used.append(ScraperSource.SCRAPEGRAPH)

        # If nothing worked, try ScrapeGraphAI as primary search
        if not merged and ScraperSource.SCRAPEGRAPH in request.sources:
            try:
                merged = await self._scrapegraph.search(
                    request.query, request.location, request.max_results
                )
                if merged:
                    sources_used.append(ScraperSource.SCRAPEGRAPH)
            except Exception as exc:
                errors.append(f"ScrapeGraphAI search: {exc}")

        return LeadResult(
            leads=merged[: request.max_results],
            total=len(merged),
            sources_used=list(set(sources_used)),
            errors=errors,
        )

    # ------------------------------------------------------------------
    # Single company lookup
    # ------------------------------------------------------------------

    async def lookup(
        self, company_name: str, sources: Optional[list[ScraperSource]] = None
    ) -> Optional[Lead]:
        """Look up a single company across specified sources."""
        if sources is None:
            sources = [
                ScraperSource.LINKEDIN,
                ScraperSource.GOOGLE_MAPS,
                ScraperSource.SCRAPEGRAPH,
            ]

        result: Optional[Lead] = None

        for src in sources:
            try:
                scraper = {
                    ScraperSource.LINKEDIN: self._linkedin,
                    ScraperSource.GOOGLE_MAPS: self._gmap,
                    ScraperSource.SCRAPEGRAPH: self._scrapegraph,
                }[src]
                lead = await scraper.lookup_company(company_name)
                if lead:
                    if result is None:
                        result = lead
                    else:
                        from .enricher import merge_leads
                        result = merge_leads(result, lead)
            except Exception as exc:
                logger.error("Lookup via %s failed: %s", src, exc)

        return result

    # ------------------------------------------------------------------
    # AI keyword suggestion
    # ------------------------------------------------------------------

    async def suggest_keywords(self, prompt: str) -> list[str]:
        return await _suggest_keywords(prompt, self.config)


def _merge_into(existing: Lead, enrichment: Lead) -> Lead:
    """Overlay non-null fields from enrichment onto existing."""
    from .enricher import merge_leads
    return merge_leads(existing, enrichment)
