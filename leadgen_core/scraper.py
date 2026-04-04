"""
Main lead scraper orchestrator
Entry point for scraping operations
"""

from typing import List, Optional, Dict
from .models import Lead, ScrapeSource, LeadStatus
from .linkedin_scraper import LinkedInScraper
from .gmap_scraper import GMapScraper
from .enricher import LeadEnricher


class LeadScraper:
    """Main scraper orchestrator - use this for all scraping operations"""

    def __init__(
        self,
        linkedin_session_file: Optional[str] = None,
        scrapegraph_api_key: Optional[str] = None
    ):
        """
        Initialize lead scraper

        Args:
            linkedin_session_file: Path to LinkedIn session file
            scrapegraph_api_key: ScrapeGraphAI API key
        """
        self.linkedin = LinkedInScraper(linkedin_session_file)
        self.gmap = GMapScraper()
        self.enricher = LeadEnricher(linkedin_session_file, scrapegraph_api_key)

    def search_by_industry(
        self,
        industry: str,
        location: Optional[str] = None,
        limit: int = 50,
        enrich: bool = True
    ) -> List[Lead]:
        """
        Search for leads by industry (LinkedIn first)

        Args:
            industry: Industry name (e.g., "Software Development")
            location: Optional location filter
            limit: Max results
            enrich: Enrich results with additional data

        Returns:
            List of leads
        """
        print(f"Searching for {industry} leads" + (f" in {location}" if location else ""))

        # Step 1: Search LinkedIn for industry professionals
        search_term = f"{industry} professionals" + (f" {location}" if location else "")
        linkedin_people = self.linkedin.search_person(search_term)

        if not linkedin_people:
            linkedin_people = []

        leads = self.linkedin.extract_leads_from_search(linkedin_people[:limit])

        # Step 2: If LinkedIn results insufficient, search Google Maps
        if len(leads) < limit:
            search_term_gmap = industry + (f" {location}" if location else "")
            gmap_results = self.gmap.search_business(search_term_gmap, location)

            gmap_leads = self.gmap.extract_leads_from_results(gmap_results)
            leads.extend(gmap_leads[:limit - len(leads)])

        # Step 3: Enrich leads from multiple sources
        if enrich:
            leads = self.enricher.enrich_leads(leads)

        return leads

    def search_by_company(
        self,
        company_name: str,
        limit: int = 20,
        enrich: bool = True
    ) -> List[Lead]:
        """
        Search for leads by company

        Args:
            company_name: Company name
            limit: Max results
            enrich: Enrich results

        Returns:
            List of leads from that company
        """
        print(f"Searching for leads at {company_name}")

        # Step 1: Search LinkedIn for company employees
        linkedin_people = self.linkedin.search_person("", company_name)
        leads = self.linkedin.extract_leads_from_search(linkedin_people[:limit])

        # Step 2: Get company info and enrich
        company_info = self.linkedin.search_company(company_name)
        if company_info:
            for lead in leads:
                if lead.company_name == company_name:
                    # Merge company data
                    pass

        # Step 3: Enrich leads
        if enrich:
            leads = self.enricher.enrich_leads(leads)

        return leads

    def search_by_location(
        self,
        location: str,
        keywords: Optional[str] = None,
        limit: int = 50,
        use_gmap: bool = True,
        enrich: bool = True
    ) -> List[Lead]:
        """
        Search for leads by location

        Args:
            location: Location (e.g., "San Francisco, CA")
            keywords: Optional industry/skill keywords
            limit: Max results
            use_gmap: Use Google Maps for local business search
            enrich: Enrich results

        Returns:
            List of leads
        """
        print(f"Searching for leads in {location}")

        leads = []

        # Step 1: LinkedIn search in location
        search_term = (keywords or "professionals") + f" in {location}"
        linkedin_people = self.linkedin.search_person(search_term)
        leads = self.linkedin.extract_leads_from_search(linkedin_people[:limit // 2])

        # Step 2: Google Maps search for businesses
        if use_gmap:
            search_term_gmap = keywords or "businesses"
            gmap_results = self.gmap.search_business(search_term_gmap, location)
            gmap_leads = self.gmap.extract_leads_from_results(gmap_results)
            leads.extend(gmap_leads[:limit - len(leads)])

        # Step 3: Enrich leads
        if enrich:
            leads = self.enricher.enrich_leads(leads)

        return leads

    def search_by_keywords(
        self,
        keywords: str,
        location: Optional[str] = None,
        limit: int = 50,
        enrich: bool = True
    ) -> List[Lead]:
        """
        Advanced search by keywords (LinkedIn + Maps)

        Args:
            keywords: Search keywords
            location: Optional location filter
            limit: Max results
            enrich: Enrich results

        Returns:
            List of leads
        """
        print(f"Searching for '{keywords}'" + (f" in {location}" if location else ""))

        # LinkedIn search (primary)
        linkedin_people = self.linkedin.search_person(keywords)
        leads = self.linkedin.extract_leads_from_search(linkedin_people[:limit])

        # Google Maps search (if needed)
        if len(leads) < limit:
            gmap_results = self.gmap.search_business(keywords, location)
            gmap_leads = self.gmap.extract_leads_from_results(gmap_results)
            leads.extend(gmap_leads[:limit - len(leads)])

        # Enrich
        if enrich:
            leads = self.enricher.enrich_leads(leads)

        return leads

    def batch_search(
        self,
        queries: List[str],
        search_type: str = "keywords",
        limit: int = 50,
        enrich: bool = True
    ) -> List[Lead]:
        """
        Batch search multiple queries

        Args:
            queries: List of search queries
            search_type: Type of search (keywords, industry, company)
            limit: Max results per query
            enrich: Enrich results

        Returns:
            Combined list of unique leads
        """
        all_leads = []
        seen = set()

        for query in queries:
            print(f"\nProcessing query: {query}")

            if search_type == "industry":
                results = self.search_by_industry(query, limit=limit, enrich=enrich)
            elif search_type == "company":
                results = self.search_by_company(query, limit=limit, enrich=enrich)
            else:
                results = self.search_by_keywords(query, limit=limit, enrich=enrich)

            for lead in results:
                key = (lead.company_name, lead.contact_name, lead.email)
                if key not in seen:
                    all_leads.append(lead)
                    seen.add(key)

        return all_leads
