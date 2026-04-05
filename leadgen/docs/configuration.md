# Configuration

All settings are loaded from environment variables or a `.env` file in the project root.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LINKEDIN_SESSION_PATH` | No | None | Path to saved LinkedIn browser session JSON |
| `LINKEDIN_EMAIL` | No | None | LinkedIn login email (if no session file) |
| `LINKEDIN_PASSWORD` | No | None | LinkedIn login password |
| `NVIDIA_NIM_API_KEY` | For AI features | None | NVIDIA NIM API key for Kimi K2.5 |
| `NVIDIA_NIM_BASE_URL` | No | `https://integrate.api.nvidia.com/v1` | NIM endpoint |
| `NVIDIA_NIM_MODEL` | No | `moonshotai/kimi-k2-5` | Model name |
| `HEADLESS` | No | `true` | Run Playwright browser headless |
| `REQUEST_DELAY` | No | `3.0` | Base delay between requests (seconds) |
| `GOOGLE_SEARCH_MAX_PAGES` | No | `3` | Max Google Search pages to fetch |
| `FUZZY_MATCH_THRESHOLD` | No | `85` | Minimum fuzzy match score (0-100) |

## LinkedIn Session Setup

1. Run the linkedin_scraper session creation tool or log in manually
2. Save the session JSON to a known path (e.g., `./linkedin_scraper/linkedin_session.json`)
3. Set `LINKEDIN_SESSION_PATH` in your `.env`

## NVIDIA NIM API Key

1. Go to https://build.nvidia.com
2. Create an API key
3. Set `NVIDIA_NIM_API_KEY` in your `.env`

This key is used for:
- ScrapeGraphAI fallback scraping (Kimi K2.5 as the LLM backend)
- AI keyword suggestion (`suggest_keywords()`)
