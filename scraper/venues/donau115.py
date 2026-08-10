"""
Donau115 — Bar / events venue, Neukölln.
Site: donau115.de (donau115.com is NXDOMAIN)

NOTE: The site is JS-rendered. The static HTML only contains "Loading events…".
GitHub Actions runs on ubuntu/debian with no Playwright, so this scraper
currently returns empty until one of these workarounds is applied:

Option A (recommended): Inspect the real browser's Network tab on donau115.de,
  find the XHR/fetch call that loads events, and add an httpx call to that
  endpoint directly here. Update EVENTS_API_URL below.

Option B: Add Playwright to the GitHub Actions workflow. This works but is
  slower (adds ~2 min to the run).

Until resolved, this venue will be absent from the weekly digest.
The orchestrator logs a warning but continues with all other venues.
"""
from __future__ import annotations

import logging

log = logging.getLogger(__name__)

EVENTS_API_URL = None  # TODO: discover via browser DevTools and fill in


def scrape() -> list[dict]:
    log.warning(
        "Donau115: scraper not yet implemented. "
        "The site is JS-rendered and requires a known API endpoint. "
        "See the comment in scraper/venues/donau115.py for instructions."
    )
    return []
