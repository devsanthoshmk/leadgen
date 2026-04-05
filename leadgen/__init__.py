"""Lead Generation Module — reusable Python package for the sales team."""

from .config import LeadGenConfig
from .core import LeadGenerator
from .models import Lead, LeadResult, ScraperSource, SearchRequest

__all__ = [
    "LeadGenerator",
    "Lead",
    "SearchRequest",
    "LeadResult",
    "ScraperSource",
    "LeadGenConfig",
]
