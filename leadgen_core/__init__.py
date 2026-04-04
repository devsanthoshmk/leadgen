"""
Lead Generation Core Module
Unified Python module for CLI and Android integration
"""

__version__ = "1.0.0"
__author__ = "Mergex Lead Gen"

from .scraper import LeadScraper
from .models import Lead, ScrapeSource
from .enricher import LeadEnricher

__all__ = [
    'LeadScraper',
    'Lead',
    'ScrapeSource',
    'LeadEnricher',
]
