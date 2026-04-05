"""Utility functions for lead generation."""

import re
import random

import phonenumbers


# User-Agent rotation pool
USER_AGENTS = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
]


def random_ua() -> str:
    """Return a random User-Agent string."""
    return random.choice(USER_AGENTS)


def parse_phone(text: str, region: str = "IN") -> str:
    """Parse and validate a phone number from free-form text.

    Returns the E.164 formatted number or empty string.
    """
    if not text:
        return ""

    # Try regex extraction first
    phone_re = re.compile(
        r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}"
    )
    matches = phone_re.findall(text)
    if not matches:
        return ""

    for match in matches:
        digits = re.sub(r"\D", "", match)
        if len(digits) < 8:
            continue
        try:
            number = phonenumbers.parse(match, region)
            if phonenumbers.is_valid_number(number):
                return phonenumbers.format_number(
                    number, phonenumbers.PhoneNumberFormat.E164
                )
        except phonenumbers.NumberParseException:
            continue
    return ""


_STRIP_SUFFIXES = re.compile(
    r"\b(inc|llc|ltd|limited|corp|corporation|pvt|private|plc|co|company|group|holdings)\b\.?",
    re.IGNORECASE,
)


def normalize_company_name(name: str) -> str:
    """Normalize a company name for fuzzy matching."""
    if not name:
        return ""
    name = name.lower().strip()
    name = _STRIP_SUFFIXES.sub("", name)
    name = re.sub(r"[^\w\s]", "", name)
    return re.sub(r"\s+", " ", name).strip()
