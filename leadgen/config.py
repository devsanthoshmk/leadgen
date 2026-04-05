"""Configuration for lead generation module."""

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class LeadGenConfig(BaseSettings):
    """Configuration loaded from environment variables / .env file."""

    # LinkedIn
    LINKEDIN_SESSION_PATH: Optional[str] = None
    LINKEDIN_EMAIL: Optional[str] = None
    LINKEDIN_PASSWORD: Optional[str] = None
    HEADLESS: bool = True

    # NVIDIA NIM / Kimi K2.5 (for ScrapeGraphAI and keyword AI)
    NVIDIA_NIM_API_KEY: Optional[str] = None
    NVIDIA_NIM_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    NVIDIA_NIM_MODEL: str = "moonshotai/kimi-k2-instruct"

    # Scraping behaviour
    REQUEST_DELAY: float = 3.0
    GOOGLE_SEARCH_MAX_PAGES: int = 3
    FUZZY_MATCH_THRESHOLD: int = 85

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }
