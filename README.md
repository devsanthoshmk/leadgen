# Lead Generation Module

Reusable Python module that scrapes lead data from Google Search, LinkedIn, and Google Maps, with ScrapeGraphAI as an AI-powered fallback.

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required for full functionality:
- `LINKEDIN_SESSION_PATH` — path to your LinkedIn session JSON
- `NVIDIA_NIM_API_KEY` — for AI keyword suggestion and ScrapeGraphAI fallback

### 3. Run the demo

```bash
python -m leadgen.tests.test_demo
```

## Usage

```python
import asyncio
from leadgen import LeadGenerator, SearchRequest, ScraperSource

async def main():
    async with LeadGenerator() as gen:
        # Search for leads
        result = await gen.search("hotels in Chennai")
        for lead in result.leads:
            print(f"{lead.company_name} | {lead.phone} | {lead.location}")

        # Look up a specific company
        lead = await gen.lookup("Microsoft")

        # AI keyword suggestions
        keywords = await gen.suggest_keywords("hospitality industry in South India")

asyncio.run(main())
```

## Features

- **Multi-source scraping**: LinkedIn + Google Maps + ScrapeGraphAI
- **Intelligent fallback**: ScrapeGraphAI fills gaps when primary sources fail
- **Fuzzy matching**: Merges data from different sources by company name
- **AI keyword suggestion**: Generate optimized search keywords via Kimi K2.5
- **Source selection**: Choose which scrapers to use per request
- **Rate limiting**: Built-in delays and UA rotation

## Documentation

- [API Reference](leadgen/docs/api_reference.md)
- [Architecture](leadgen/docs/architecture.md)
- [Configuration](leadgen/docs/configuration.md)
