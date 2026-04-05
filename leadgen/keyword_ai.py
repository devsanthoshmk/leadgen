"""AI-powered keyword suggestion via NVIDIA NIM (Kimi K2.5)."""

import json
import logging

from openai import AsyncOpenAI

from .config import LeadGenConfig

logger = logging.getLogger(__name__)


async def suggest_keywords(prompt: str, config: LeadGenConfig) -> list[str]:
    """Generate optimized B2B lead-gen search keywords for *prompt*."""
    if not config.NVIDIA_NIM_API_KEY:
        logger.warning("NVIDIA_NIM_API_KEY not set — returning empty keywords")
        return []

    client = AsyncOpenAI(
        api_key=config.NVIDIA_NIM_API_KEY,
        base_url=config.NVIDIA_NIM_BASE_URL,
    )

    try:
        resp = await client.chat.completions.create(
            model=config.NVIDIA_NIM_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a B2B lead generation expert. Generate 5-8 "
                        "optimized search keywords for finding business leads. "
                        "Include industry terms, location variants, and niche "
                        "terms. Return a JSON array of strings ONLY, no explanation."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )

        text = resp.choices[0].message.content.strip()
        # Strip markdown fences if present
        if text.startswith("```"):
            text = text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        return json.loads(text)

    except Exception as exc:
        logger.error("Keyword suggestion failed: %s", exc)
        return []
