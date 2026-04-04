"""
Data models for lead generation
"""

from dataclasses import dataclass, asdict, field
from typing import Optional, List
from enum import Enum
from datetime import datetime
import json


class ScrapeSource(Enum):
    """Source of lead data"""
    LINKEDIN = "linkedin"
    GMAP = "gmap"
    SCRAPEGRAPH = "scrapegraph"
    MANUAL = "manual"


class LeadStatus(Enum):
    """Sales status of lead"""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"
    ARCHIVED = "archived"


@dataclass
class Lead:
    """Lead data model"""
    # Core fields
    company_name: str
    contact_name: str
    job_title: str
    email: str
    phone: str
    linkedin_url: str

    # Company info
    industry: str
    location: str
    company_size: str
    revenue_estimate: str = ""

    # Lead scoring
    lead_score: int = 0  # 0-100
    status: LeadStatus = LeadStatus.NEW

    # Metadata
    notes: str = ""
    source: ScrapeSource = ScrapeSource.LINKEDIN
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())

    # Internal
    id: str = ""  # UUID or database ID
    tags: List[str] = field(default_factory=list)

    def to_dict(self):
        """Convert to dictionary"""
        data = asdict(self)
        data['status'] = self.status.value
        data['source'] = self.source.value
        return data

    def to_json(self):
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)

    def calculate_lead_score(self) -> int:
        """
        Calculate lead score based on data completeness and quality
        Returns: 0-100 score
        """
        score = 0

        # Email presence (20 points)
        if self.email and '@' in self.email:
            score += 20

        # Phone presence (15 points)
        if self.phone:
            score += 15

        # LinkedIn presence (15 points)
        if self.linkedin_url and 'linkedin.com' in self.linkedin_url:
            score += 15

        # Complete contact info (10 points)
        if self.contact_name and self.job_title:
            score += 10

        # Company info completeness (15 points)
        if self.company_name and self.location and self.industry:
            score += 15

        # Revenue estimate (10 points)
        if self.revenue_estimate:
            score += 10

        return min(score, 100)

    def validate(self) -> tuple[bool, List[str]]:
        """
        Validate lead data
        Returns: (is_valid, list of errors)
        """
        errors = []

        if not self.company_name or not self.company_name.strip():
            errors.append("Company name is required")

        if not self.contact_name or not self.contact_name.strip():
            errors.append("Contact name is required")

        if not self.email or '@' not in self.email:
            errors.append("Valid email is required")

        if not self.location or not self.location.strip():
            errors.append("Location is required")

        return len(errors) == 0, errors
