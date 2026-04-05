"""Google Search results scraper using Playwright with human-like interaction."""

import asyncio
import logging
import random
import re
from pathlib import Path
from typing import Optional

from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from .utils import random_ua
from .config import LeadGenConfig

logger = logging.getLogger(__name__)

_GOOGLE_SESSION_FILE = Path(__file__).resolve().parents[1] / ".google_session.json"


class GoogleSearcher:
    """Scrape organic Google Search results via Playwright with human-like typing."""

    def __init__(self, config: LeadGenConfig):
        self.config = config
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        self._cache: dict[str, list[str]] = {}
        self._initialized = False

    async def _ensure_browser(self) -> Page:
        if self._page is not None:
            return self._page

        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=self.config.HEADLESS
        )

        # Load saved session to reuse cookies (avoids repeated captchas)
        storage_state = str(_GOOGLE_SESSION_FILE) if _GOOGLE_SESSION_FILE.exists() else None
        self._context = await self._browser.new_context(
            user_agent=random_ua(),
            viewport={"width": 1280, "height": 720},
            locale="en-US",
            storage_state=storage_state,
        )
        self._page = await self._context.new_page()
        return self._page

    async def _navigate_and_search(self, query: str) -> None:
        """Navigate to Google and perform a search using human-like interaction."""
        page = await self._ensure_browser()

        if not self._initialized:
            # First time: go to Google homepage
            await page.goto("https://www.google.com", wait_until="domcontentloaded", timeout=15000)
            await asyncio.sleep(random.uniform(1, 2))

            # Accept consent screen
            try:
                await page.locator('button:has-text("Accept all")').click(timeout=3000)
                await asyncio.sleep(1)
            except Exception:
                pass
            try:
                await page.locator('button:has-text("Accept")').click(timeout=2000)
                await asyncio.sleep(1)
            except Exception:
                pass

            self._initialized = True

        # Check for CAPTCHA and wait for user to solve if present
        await self._handle_captcha(page)

        # Use the search box: type like a human
        search_box = page.locator('textarea[name="q"], input[name="q"]')
        try:
            await search_box.wait_for(timeout=10000, state="visible")
        except Exception:
            # If search box not found, navigate to google.com
            await page.goto("https://www.google.com", wait_until="domcontentloaded")
            await asyncio.sleep(2)
            await self._handle_captcha(page)
            search_box = page.locator('textarea[name="q"], input[name="q"]')
            await search_box.wait_for(timeout=10000, state="visible")

        await search_box.click()
        # Clear existing text
        await page.keyboard.press("Control+a")
        await asyncio.sleep(0.2)
        # Type query with human-like delay
        await search_box.type(query, delay=random.randint(50, 120))
        await asyncio.sleep(random.uniform(0.3, 0.8))
        await page.keyboard.press("Enter")

        # Wait for page navigation
        await asyncio.sleep(random.uniform(3, 5))

        # Handle CAPTCHA if Google redirected to /sorry/
        await self._handle_captcha(page)

        # After CAPTCHA solve we may be back on Google homepage — wait for results
        # or re-check we have search results
        for _ in range(3):
            has_results = await page.evaluate(
                "() => !!(document.querySelector('#search') || document.querySelector('#rso') || document.querySelectorAll('h3').length > 0)"
            )
            if has_results:
                break
            await asyncio.sleep(2)

        # Save session for reuse
        try:
            storage = await self._context.storage_state()
            import json
            _GOOGLE_SESSION_FILE.write_text(json.dumps(storage))
        except Exception:
            pass

    async def _handle_captcha(self, page: Page) -> None:
        """Detect CAPTCHA (including /sorry/ redirect) and wait for manual solve."""
        max_wait = 120  # seconds

        # Check URL-based redirect to /sorry/
        if "/sorry/" in page.url:
            logger.warning(
                "Google CAPTCHA redirect detected! Please solve the CAPTCHA "
                "in the browser window. Waiting up to %ds ...", max_wait,
            )
            # Wait until the URL no longer contains /sorry/
            for _ in range(max_wait):
                await asyncio.sleep(1)
                if "/sorry/" not in page.url:
                    logger.info("CAPTCHA solved (URL redirect cleared), continuing...")
                    await asyncio.sleep(2)
                    return
            logger.error("CAPTCHA not solved within %ds", max_wait)
            return

        # Check DOM-based captcha elements
        try:
            captcha = page.locator("#captcha-form, #recaptcha")
            if await captcha.count() > 0 and await captcha.first.is_visible():
                logger.warning(
                    "CAPTCHA detected on page! Please solve it in the browser. "
                    "Waiting up to %ds ...", max_wait,
                )
                await page.wait_for_selector(
                    "#captcha-form, #recaptcha",
                    state="hidden",
                    timeout=max_wait * 1000,
                )
                logger.info("CAPTCHA solved, continuing...")
                await asyncio.sleep(2)
        except Exception:
            pass

    async def search(
        self, query: str, max_pages: int = 0
    ) -> list[dict[str, str]]:
        """Return list of ``{title, url, snippet}`` from Google organic results."""
        if max_pages <= 0:
            max_pages = self.config.GOOGLE_SEARCH_MAX_PAGES

        page = await self._ensure_browser()
        results: list[dict[str, str]] = []

        # First page: human-like search
        await self._navigate_and_search(query)

        for page_idx in range(max_pages):
            if page_idx > 0:
                # Click "Next" or navigate to next page
                try:
                    next_btn = page.locator('a#pnnext, a[aria-label="Next"]')
                    if await next_btn.count() > 0:
                        await next_btn.click()
                        await asyncio.sleep(random.uniform(2, 4))
                        await self._handle_captcha(page)
                    else:
                        logger.info("No next page button found, stopping")
                        break
                except Exception as exc:
                    logger.warning("Failed to navigate to next page: %s", exc)
                    break

            # Extract results — use the most robust approach: find all <a> with <h3>
            items = await page.evaluate("""() => {
                const results = [];
                const seen = new Set();
                // Most reliable: every organic result has an <a> wrapping an <h3>
                document.querySelectorAll('a').forEach(a => {
                    const h3 = a.querySelector('h3');
                    if (!h3) return;
                    const href = a.getAttribute('href');
                    if (!href || !href.startsWith('http') || href.includes('google.com/search')) return;
                    if (seen.has(href)) return;
                    seen.add(href);
                    // Walk up to find snippet sibling
                    let parent = a.closest('.g') || a.closest('[data-hveid]') || a.parentElement;
                    let snippet = '';
                    if (parent) {
                        const sEl = parent.querySelector('.VwiC3b, [data-sncf], .IsZvec, [style*="-webkit-line-clamp"]');
                        if (sEl) snippet = sEl.innerText;
                    }
                    results.push({title: h3.innerText || '', url: href, snippet: snippet});
                });
                return results;
            }""")

            if not items:
                logger.info("No results on page %d, stopping", page_idx + 1)
                break

            results.extend(items)
            logger.info(
                "Google page %d: got %d results (total %d)",
                page_idx + 1, len(items), len(results),
            )

            if page_idx < max_pages - 1:
                await asyncio.sleep(random.uniform(2, 5))

        return results

    async def search_linkedin_urls(self, query: str) -> list[str]:
        """Search Google for LinkedIn company page URLs matching *query*.

        Uses ``site:linkedin.com/company/`` prefix and caches results.
        """
        cache_key = query.lower().strip()
        if cache_key in self._cache:
            return self._cache[cache_key]

        search_query = f'site:linkedin.com/company/ "{query}"'
        raw = await self.search(search_query)

        urls: list[str] = []
        for item in raw:
            url = item["url"]
            if "linkedin.com/company/" in url:
                url = re.sub(r"\?.*$", "", url).rstrip("/")
                if url not in urls:
                    urls.append(url)

        logger.info("Found %d LinkedIn URLs for %r", len(urls), query)
        self._cache[cache_key] = urls
        return urls

    async def close(self) -> None:
        if self._page:
            await self._page.close()
            self._page = None
        if self._context:
            await self._context.close()
            self._context = None
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
