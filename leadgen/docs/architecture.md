# Architecture

## Data Flow

```
User query
    │
    ▼
┌─────────────────┐
│ GoogleSearcher   │── site:linkedin.com/company/ "query"
│ (httpx + parsel) │── Returns LinkedIn company URLs
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ LinkedInScraper  │── CompanyScraper on each URL (Playwright)
│                  │── Returns: name, industry, size, phone, website, HQ,
│                  │   employees (name + title)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ GoogleMapsScraper│── Searches using query (enriches with phone, address, website)
│ (httpx+selectolax)── Parses .VkpGBb items, /maps/dir/ for address
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Enricher         │── Fuzzy-match merge by normalized company name (thefuzz ≥85%)
│                  │── Field priority: LinkedIn wins (industry, size, contacts),
│                  │   GMap wins (phone, location), ScrapeGraphAI wins (email, revenue)
└────────┬────────┘
         │
         ▼  (only where data is missing)
┌─────────────────┐
│ ScrapegraphAI    │── If LinkedIn failed → deep_scrape (multi-page)
│ (FALLBACK)       │── If GMap failed → quick_enrich (single call)
│                  │── Uses Kimi K2.5 via NVIDIA NIM
└─────────────────┘
```

## Module Dependencies

- `core.py` (LeadGenerator) orchestrates all scrapers and enricher
- `google_search.py` is shared by LinkedInScraper (to find LinkedIn URLs)
- `enricher.py` merges results from any two sources
- `keyword_ai.py` is standalone, uses OpenAI-compatible client

## Fallback Logic

1. Primary path: LinkedIn + Google Maps
2. If LinkedIn fails for a lead but we have a website → `deep_scrape_company()`
3. If GMap fails/missing for a lead → `quick_enrich(company_name)`
4. If both primary sources return nothing → ScrapeGraphAI `search()` as primary

## Key Design Decisions

- **httpx for Google Search/Maps**: No browser needed, faster, HTTP/2 support
- **Playwright for LinkedIn**: Required for JavaScript-rendered pages + session auth
- **Fuzzy matching**: `thefuzz.token_sort_ratio` handles word reordering ("Hotel Grand" vs "Grand Hotel")
- **Source priorities in enricher**: Avoids overwriting high-quality data with lower-quality data
