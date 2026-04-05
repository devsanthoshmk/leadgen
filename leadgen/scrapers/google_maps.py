"""Google Maps local-pack scraper (Playwright-based, ported from gmap scrapper/scraper.js)."""

import asyncio
import logging
import random
from typing import Optional
from urllib.parse import urlencode

from playwright.async_api import Page

from ..config import LeadGenConfig
from ..models import Lead, ScraperSource
from ..utils import parse_phone
from .base import BaseLeadScraper

logger = logging.getLogger(__name__)

# JS to extract local-pack results — mirrors scraper.js logic exactly
_EXTRACT_JS = """() => {
    function extractPhone(text) {
        if (!text) return '';
        const phoneRegex = /(?:[+]?\\d{1,3}[-.\\s]?)?[(]?\\d{1,4}[)]?[-.\\s]?\\d{1,4}[-.\\s]?\\d{1,9}/g;
        const matches = text.match(phoneRegex);
        if (!matches) return '';
        for (const match of matches) {
            if (match.replace(/\\D/g, '').length >= 8) return match;
        }
        return '';
    }

    const searchEl = document.querySelector('#search');
    if (!searchEl) return [];
    const items = searchEl.querySelectorAll('.VkpGBb');
    if (!items || items.length === 0) return [];

    const data = [];
    items.forEach((item) => {
        const row = {title:'N/A', stars:0, reviews:0, category:'', address:'', phone:'', url:''};

        const titleEl = item.querySelector('[role="heading"]');
        if (titleEl) row.title = titleEl.textContent.replace(/\\s+/g,' ').trim();

        const allLinks = Array.from(item.querySelectorAll('a'));
        const dirLink = allLinks.find(a => (a.getAttribute('href')||'').startsWith('/maps/dir/'));
        if (dirLink) {
            try {
                const href = dirLink.getAttribute('href');
                const dest = href.split('/data=')[0].split('/').pop();
                if (dest) {
                    let addr = decodeURIComponent(dest).replace(/[+]/g,' ').trim();
                    if (row.title !== 'N/A') {
                        if (addr.startsWith(row.title))
                            addr = addr.substring(row.title.length).replace(/^[, -]+/,'').trim();
                        else if (addr.endsWith(row.title))
                            addr = addr.substring(0, addr.length - row.title.length).replace(/[, -]+$/,'').trim();
                    }
                    row.address = addr;
                }
            } catch(e) {}
        }

        const webLink = allLinks.find(a => {
            const t = (a.textContent||'').toLowerCase();
            return t.includes('website') && a.href && a.href.startsWith('http');
        });
        if (webLink) row.url = webLink.href;

        const details = item.querySelector('.rllt__details');
        if (details) {
            Array.from(details.children).forEach(line => {
                if (line.getAttribute('role')==='heading' || line.querySelector('[role="heading"]')) return;
                const text = line.textContent.replace(/\\s+/g,' ').trim();
                if (!text) return;

                if (line.querySelector('[role="img"]') || /^\\d[.]\\d/.test(text)) {
                    const starSpan = line.querySelector('.yi40Hd') || line.querySelector('[aria-hidden="true"]');
                    if (starSpan) row.stars = parseFloat(starSpan.textContent) || 0;
                    const revSpan = line.querySelector('.RDApEe');
                    if (revSpan) row.reviews = parseInt(revSpan.textContent.replace(/\\D/g,'')) || 0;
                    if (text.includes('\\u00b7')) row.category = text.split('\\u00b7').pop().trim();
                    return;
                }

                const skip = ['Opens','Closed','Open 24 hours','Dine-in','Takeout','Delivery'];
                if (skip.some(w => text.includes(w))) return;
                if (line.classList.contains('pJ3Ci')) return;

                text.split('\\u00b7').map(s=>s.trim()).forEach(seg => {
                    if (seg.includes('years in business')) return;
                    const ph = extractPhone(seg);
                    const looksPhone = /^[\\d\\s\\-+()]{8,}$/.test(seg);
                    if (ph) row.phone = ph;
                    else if (!looksPhone && seg.length > 3 && !row.address) row.address = seg;
                });
            });
        }
        data.push(row);
    });
    return data;
}"""


class GoogleMapsScraper(BaseLeadScraper):
    """Scrape Google Maps local results. Shares browser with GoogleSearcher when possible."""

    source = ScraperSource.GOOGLE_MAPS

    def __init__(self, config: LeadGenConfig):
        self.config = config
        self._google_searcher = None  # Will be set by core.py

    def set_google_searcher(self, google_searcher):
        """Share the GoogleSearcher's browser to avoid multiple instances."""
        self._google_searcher = google_searcher

    async def _get_page(self) -> Page:
        """Get a Playwright page — reuse GoogleSearcher's browser."""
        if self._google_searcher:
            return await self._google_searcher._ensure_browser()
        raise RuntimeError("GoogleMapsScraper needs a GoogleSearcher (set_google_searcher)")

    async def _fetch_page(self, query: str, start: int = 0) -> list[dict]:
        page = await self._get_page()
        params = {"q": query, "start": start, "udm": "1"}
        url = f"https://www.google.com/search?{urlencode(params)}"

        # Navigate with human-like typing for first page to avoid captcha
        if start == 0:
            search_box = page.locator('textarea[name="q"], input[name="q"]')
            try:
                await search_box.wait_for(timeout=5000, state="visible")
            except Exception:
                await page.goto("https://www.google.com", wait_until="domcontentloaded")
                await asyncio.sleep(1)
                search_box = page.locator('textarea[name="q"], input[name="q"]')
                await search_box.wait_for(timeout=10000, state="visible")

            await search_box.click()
            await page.keyboard.press("Control+a")
            await asyncio.sleep(0.2)
            # Construct the maps query with udm=1 trigger
            maps_query = query
            await search_box.type(maps_query, delay=random.randint(50, 100))
            await asyncio.sleep(0.3)
            await page.keyboard.press("Enter")
            await asyncio.sleep(random.uniform(2, 4))

            # Now switch to Maps tab by adding udm=1
            current_url = page.url
            if "udm=1" not in current_url:
                await page.goto(url, wait_until="domcontentloaded", timeout=15000)
                await asyncio.sleep(random.uniform(2, 3))
        else:
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            await asyncio.sleep(random.uniform(2, 3))

        # Handle captcha
        if self._google_searcher:
            await self._google_searcher._handle_captcha(page)

        # Wait for results
        try:
            await page.wait_for_selector(".VkpGBb, #search", timeout=8000)
        except Exception:
            pass

        rows = await page.evaluate(_EXTRACT_JS)
        logger.info("GMap page (start=%d): got %d results", start, len(rows))
        return rows

    async def search(
        self, query: str, location: Optional[str] = None, max_results: int = 20
    ) -> list[Lead]:
        search_query = f"{query} {location}" if location else query
        all_rows: list[dict] = []
        start = 0

        while len(all_rows) < max_results:
            page_rows = await self._fetch_page(search_query, start)
            if not page_rows:
                break
            all_rows.extend(page_rows)
            start += 10
            await asyncio.sleep(random.uniform(2, 4))

        # Deduplicate by title+address
        seen: set[str] = set()
        unique: list[dict] = []
        for r in all_rows:
            key = r["title"] + r["address"]
            if key not in seen:
                seen.add(key)
                unique.append(r)

        leads = [self._row_to_lead(r) for r in unique[:max_results]]
        logger.info("GMap search %r: %d unique leads", search_query, len(leads))
        return leads

    async def lookup_company(self, company_name: str) -> Optional[Lead]:
        rows = await self._fetch_page(company_name)
        if rows:
            return self._row_to_lead(rows[0])
        return None

    async def close(self) -> None:
        # Browser is owned by GoogleSearcher, don't close it here
        pass

    @staticmethod
    def _row_to_lead(row: dict) -> Lead:
        phone = row.get("phone") or None
        if phone:
            parsed = parse_phone(phone)
            if parsed:
                phone = parsed

        return Lead(
            company_name=row["title"] if row["title"] != "N/A" else None,
            phone=phone,
            location=row.get("address") or None,
            website=row.get("url") or None,
            stars=row.get("stars") or None,
            reviews=row.get("reviews") or None,
            category=row.get("category") or None,
            source=[ScraperSource.GOOGLE_MAPS],
        )
