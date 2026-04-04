"""
Lead enrichment pipeline
Combines data from multiple sources
"""

from typing import List, Optional
from .models import Lead, ScrapeSource
from .linkedin_scraper import LinkedInScraper
from .gmap_scraper import GMapScraper
from .scrapegraph_adapter import ScrapeGraphAdapter


class LeadEnricher:
    """Orchestrates lead enrichment from multiple sources"""

    def __init__(
        self,
        linkedin_session_file: Optional[str] = None,
        scrapegraph_api_key: Optional[str] = None
    ):
        """
        Initialize enricher with data sources

        Args:
            linkedin_session_file: Path to LinkedIn session file
            scrapegraph_api_key: ScrapeGraphAI API key
        """
        self.linkedin = LinkedInScraper(linkedin_session_file)
        self.gmap = GMapScraper()
        self.scrapegraph = ScrapeGraphAdapter(scrapegraph_api_key)

    def enrich_lead(
        self,
        lead: Lead,
        use_linkedin: bool = True,
        use_gmap: bool = True,
        use_scrapegraph: bool = False
    ) -> Lead:
        """
        Enrich a single lead from multiple sources

        Args:
            lead: Lead to enrich
            use_linkedin: Try LinkedIn enrichment
            use_gmap: Try Google Maps enrichment
            use_scrapegraph: Try ScrapeGraphAI enrichment

        Returns:
            Enriched lead
        """
        # Step 1: LinkedIn enrichment (primary for B2B)
        if use_linkedin and lead.source != ScrapeSource.LINKEDIN:
            linkedin_lead = self._enrich_from_linkedin(lead)
            if linkedin_lead:
                lead = self._merge_leads(lead, linkedin_lead)

        # Step 2: Google Maps enrichment (secondary for location/phone)
        if use_gmap and lead.source != ScrapeSource.GMAP:
            if not lead.phone or not lead.email:
                gmap_leads = self._enrich_from_gmap(lead)
                if gmap_leads:
                    lead = self._merge_leads(lead, gmap_leads[0])

        # Step 3: ScrapeGraphAI enrichment (fallback for missing data)
        if use_scrapegraph and not lead.email:
            lead = self.scrapegraph.enrich_lead(lead)

        # Calculate final lead score
        lead.lead_score = lead.calculate_lead_score()

        return lead

    def enrich_leads(
        self,
        leads: List[Lead],
        use_linkedin: bool = True,
        use_gmap: bool = True,
        use_scrapegraph: bool = False,
        batch_size: int = 10
    ) -> List[Lead]:
        """
        Enrich multiple leads with batch processing

        Args:
            leads: List of leads to enrich
            use_linkedin: Try LinkedIn enrichment
            use_gmap: Try Google Maps enrichment
            use_scrapegraph: Try ScrapeGraphAI enrichment
            batch_size: Process in batches

        Returns:
            List of enriched leads
        """
        enriched = []

        for i, lead in enumerate(leads):
            enriched_lead = self.enrich_lead(
                lead,
                use_linkedin=use_linkedin,
                use_gmap=use_gmap,
                use_scrapegraph=use_scrapegraph
            )
            enriched.append(enriched_lead)

            if (i + 1) % batch_size == 0:
                print(f"Enriched {i + 1}/{len(leads)} leads")

        return enriched

    def _enrich_from_linkedin(self, lead: Lead) -> Optional[Lead]:
        """Try to find and enrich from LinkedIn"""
        try:
            results = self.linkedin.search_person(
                lead.contact_name,
                lead.company_name
            )

            if results:
                extracted = self.linkedin.extract_leads_from_search(results)
                if extracted:
                    return extracted[0]
        except Exception as e:
            print(f"LinkedIn enrichment failed: {e}")

        return None

    def _enrich_from_gmap(self, lead: Lead) -> Optional[List[Lead]]:
        """Try to find and enrich from Google Maps"""
        try:
            results = self.gmap.search_business(
                lead.company_name,
                lead.location
            )

            if results:
                return self.gmap.extract_leads_from_results(results)
        except Exception as e:
            print(f"Google Maps enrichment failed: {e}")

        return None

    def _merge_leads(self, primary: Lead, secondary: Lead) -> Lead:
        """Merge secondary lead data into primary (non-destructive)"""

        # Only fill empty fields from secondary
        if not primary.email and secondary.email:
            primary.email = secondary.email

        if not primary.phone and secondary.phone:
            primary.phone = secondary.phone

        if not primary.linkedin_url and secondary.linkedin_url:
            primary.linkedin_url = secondary.linkedin_url

        if primary.industry == "Unknown" and secondary.industry != "Unknown":
            primary.industry = secondary.industry

        if primary.company_size == "Unknown" and secondary.company_size != "Unknown":
            primary.company_size = secondary.company_size

        if not primary.revenue_estimate and secondary.revenue_estimate:
            primary.revenue_estimate = secondary.revenue_estimate

        if not primary.job_title and secondary.job_title:
            primary.job_title = secondary.job_title

        # Update timestamp
        from datetime import datetime
        primary.last_updated = datetime.now().isoformat()

        return primary
