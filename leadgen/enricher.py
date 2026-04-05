"""Merge leads from multiple sources using fuzzy name matching."""

import logging
from typing import Optional

from thefuzz import fuzz

from .config import LeadGenConfig
from .models import Lead, ScraperSource
from .utils import normalize_company_name

logger = logging.getLogger(__name__)

# Which source wins for each field
_FIELD_PRIORITY: dict[str, list[ScraperSource]] = {
    "linkedin_url": [ScraperSource.LINKEDIN],
    "industry": [ScraperSource.LINKEDIN],
    "company_size": [ScraperSource.LINKEDIN],
    "contact_name": [ScraperSource.LINKEDIN],
    "job_title": [ScraperSource.LINKEDIN],
    "phone": [ScraperSource.GOOGLE_MAPS],
    "location": [ScraperSource.GOOGLE_MAPS],
    "email": [ScraperSource.SCRAPEGRAPH],
    "revenue_estimate": [ScraperSource.SCRAPEGRAPH],
}


def _merge_field(
    field: str, primary: Lead, secondary: Lead
) -> Optional[str | float | int]:
    """Return the best value for *field* considering source priority."""
    pri_val = getattr(primary, field, None)
    sec_val = getattr(secondary, field, None)

    priorities = _FIELD_PRIORITY.get(field)
    if priorities:
        # Check if secondary source is the preferred one
        if sec_val and any(s in secondary.source for s in priorities):
            return sec_val
        if pri_val and any(s in primary.source for s in priorities):
            return pri_val

    # First non-null
    return pri_val or sec_val


def merge_leads(primary: Lead, secondary: Lead) -> Lead:
    """Merge two Lead objects, respecting source priorities."""
    merged = {}
    all_fields = [
        "company_name", "job_title", "contact_name", "email", "phone",
        "linkedin_url", "industry", "location", "company_size", "website",
        "revenue_estimate", "stars", "reviews", "category",
    ]
    for field in all_fields:
        merged[field] = _merge_field(field, primary, secondary)

    # Combine sources
    sources = list(set(primary.source + secondary.source))
    return Lead(**merged, source=sources)


def fuzzy_match_and_merge(
    primary_leads: list[Lead],
    secondary_leads: list[Lead],
    config: LeadGenConfig,
) -> list[Lead]:
    """Merge two lists of leads by fuzzy-matching company names."""
    threshold = config.FUZZY_MATCH_THRESHOLD
    merged: list[Lead] = []
    used_secondary: set[int] = set()

    for plead in primary_leads:
        p_name = normalize_company_name(plead.company_name or "")
        best_match: Optional[tuple[int, Lead]] = None

        for idx, slead in enumerate(secondary_leads):
            if idx in used_secondary:
                continue
            s_name = normalize_company_name(slead.company_name or "")
            if not p_name or not s_name:
                continue
            score = fuzz.token_sort_ratio(p_name, s_name)
            if score >= threshold:
                if best_match is None or score > best_match[0]:
                    best_match = (score, slead)
                    best_idx = idx

        if best_match is not None:
            merged.append(merge_leads(plead, best_match[1]))
            used_secondary.add(best_idx)
        else:
            merged.append(plead)

    # Append unmatched secondary leads
    for idx, slead in enumerate(secondary_leads):
        if idx not in used_secondary:
            merged.append(slead)

    return merged


def identify_gaps(lead: Lead) -> list[str]:
    """Return list of important fields that are missing on *lead*."""
    important = [
        "company_name", "phone", "email", "location",
        "industry", "company_size",
    ]
    return [f for f in important if not getattr(lead, f, None)]
