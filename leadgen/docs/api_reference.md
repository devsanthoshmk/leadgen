# API Reference

## LeadGenerator

Main orchestrator class. Use as an async context manager.

```python
from leadgen import LeadGenerator, SearchRequest, ScraperSource

async with LeadGenerator() as gen:
    result = await gen.search("hotels in Chennai")
```

### Methods

#### `search(query: str | SearchRequest) -> LeadResult`

Run the full pipeline: Google Search → LinkedIn → Google Maps → ScrapeGraphAI fallback.

```python
# Simple string query
result = await gen.search("hotels in Chennai")

# With SearchRequest for more control
request = SearchRequest(
    query="hotels in Chennai",
    location="Tamil Nadu",
    sources=[ScraperSource.LINKEDIN, ScraperSource.GOOGLE_MAPS],
    max_results=20,
)
result = await gen.search(request)
```

**Returns:** `LeadResult` with `.leads`, `.total`, `.sources_used`, `.errors`

#### `lookup(company_name: str, sources: list[ScraperSource] | None) -> Lead | None`

Look up a single company across specified (or all) sources.

```python
# All sources
lead = await gen.lookup("Microsoft")

# Specific sources
lead = await gen.lookup("Microsoft", sources=[ScraperSource.SCRAPEGRAPH])
lead = await gen.lookup("Microsoft", sources=[ScraperSource.LINKEDIN, ScraperSource.GOOGLE_MAPS])
```

#### `suggest_keywords(prompt: str) -> list[str]`

AI-powered keyword suggestion via NVIDIA NIM Kimi K2.5.

```python
keywords = await gen.suggest_keywords("hospitality industry in South India")
# ["hotels in Chennai", "resorts Tamil Nadu", "luxury hospitality Bangalore", ...]
```

## Models

### `Lead`
| Field | Type | Description |
|-------|------|-------------|
| company_name | str \| None | Company name |
| job_title | str \| None | From LinkedIn employees |
| contact_name | str \| None | From LinkedIn employees |
| email | str \| None | Email address |
| phone | str \| None | E.164 phone number |
| linkedin_url | str \| None | LinkedIn company page URL |
| industry | str \| None | Industry classification |
| location | str \| None | Address / headquarters |
| company_size | str \| None | Employee count range |
| website | str \| None | Company website URL |
| revenue_estimate | str \| None | ScrapeGraphAI only |
| source | list[ScraperSource] | Which sources contributed |

### `SearchRequest`
| Field | Type | Default |
|-------|------|---------|
| query | str | required |
| location | str \| None | None |
| sources | list[ScraperSource] | all three |
| max_results | int | 50 |

### `LeadResult`
| Field | Type |
|-------|------|
| leads | list[Lead] |
| total | int |
| sources_used | list[ScraperSource] |
| errors | list[str] |

### `ScraperSource` (enum)
- `LINKEDIN` — LinkedIn company scraper
- `GOOGLE_MAPS` — Google Maps local pack
- `SCRAPEGRAPH` — ScrapeGraphAI fallback

## LeadGenConfig

Loaded from `.env` automatically. See `configuration.md` for all env vars.
