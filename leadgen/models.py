"""Data models for lead generation."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ScraperSource(str, Enum):
    LINKEDIN = "linkedin"
    GOOGLE_MAPS = "google_maps"
    SCRAPEGRAPH = "scrapegraph"


class Lead(BaseModel):
    """A single lead with contact and company information."""
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    company_size: Optional[str] = None
    website: Optional[str] = None
    revenue_estimate: Optional[str] = None  # ScrapeGraphAI only
    stars: Optional[float] = None
    reviews: Optional[int] = None
    category: Optional[str] = None
    source: list[ScraperSource] = Field(default_factory=list)


class SearchRequest(BaseModel):
    """Parameters for a lead search."""
    query: str
    location: Optional[str] = None
    sources: list[ScraperSource] = Field(
        default_factory=lambda: [
            ScraperSource.LINKEDIN,
            ScraperSource.GOOGLE_MAPS,
            ScraperSource.SCRAPEGRAPH,
        ]
    )
    max_results: int = 50


class LeadResult(BaseModel):
    """Result of a lead search operation."""
    leads: list[Lead] = Field(default_factory=list)
    total: int = 0
    sources_used: list[ScraperSource] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
