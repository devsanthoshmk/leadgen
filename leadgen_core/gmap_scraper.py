"""
Google Maps scraper integration
Uses the gmap scraper from your folder with enrichment
"""

import json
from typing import List, Optional, Dict
from .models import Lead, ScrapeSource, LeadStatus


class GMapScraper:
    """Wrapper for Google Maps scraping"""

    def __init__(self):
        """Initialize Google Maps scraper"""
        self.data = None

    def search_business(self, query: str, location: Optional[str] = None) -> List[Dict]:
        """
        Search for businesses on Google Maps

        Args:
            query: Search query (e.g., "Software developers")
            location: Optional location filter

        Returns:
            List of business records
        """
        # This would integrate with your scraper.js
        # For now, return structure
        return [
            {
                "title": "Example Company",
                "address": "123 Main St, City",
                "completePhoneNumber": "+1-555-0100",
                "url": "https://example.com",
                "category": "Software Development",
                "stars": 4.5,
                "reviews": 42
            }
        ]

    def extract_leads_from_results(self, results: List[Dict]) -> List[Lead]:
        """
        Extract leads from Google Maps search results

        Args:
            results: List of business records

        Returns:
            List of Lead objects
        """
        leads = []

        for result in results:
            # Try to extract contact from company website if available
            contact_name = self._extract_contact_from_url(result.get("url", ""))

            lead = Lead(
                company_name=result.get("title", "Unknown"),
                contact_name=contact_name or "Business Owner",
                job_title="Decision Maker",
                email=result.get("email", ""),
                phone=result.get("completePhoneNumber", ""),
                linkedin_url="",
                industry=result.get("category", ""),
                location=result.get("address", ""),
                company_size=self._estimate_size_from_reviews(result.get("reviews", 0)),
                source=ScrapeSource.GMAP,
                status=LeadStatus.NEW,
                notes=f"Rating: {result.get('stars', 0)}/5 ({result.get('reviews', 0)} reviews)"
            )

            leads.append(lead)

        return leads

    def _extract_contact_from_url(self, url: str) -> Optional[str]:
        """Try to extract contact name from company website"""
        # This would involve additional web scraping
        # For now, return None
        return None

    def _estimate_size_from_reviews(self, review_count: int) -> str:
        """Estimate company size from review count"""
        if review_count < 10:
            return "1-10"
        elif review_count < 50:
            return "11-50"
        elif review_count < 200:
            return "51-200"
        elif review_count < 500:
            return "201-500"
        else:
            return "500+"
