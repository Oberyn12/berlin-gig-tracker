"""
Festsaal Kreuzberg — Concert venue, Kreuzberg.
Site: festsaal-kreuzberg.de (JS SPA — cannot be scraped with plain httpx)

STATUS: Resident Advisor IDs for this venue are not confirmed.
The RA GraphQL API's venue IDs are not publicly documented.

Until a working data source is found, this scraper returns empty with a warning.

How to fix:
  Option A: Find the correct RA venue ID by inspecting the RA page for
    festsaal-kreuzberg in browser DevTools → Network → look for a GraphQL
    call with the venue ID.
  Option B: Find if festsaal-kreuzberg.de exposes any JSON API endpoints
    (Network tab → XHR filter).
  Option C: Use Playwright in the GitHub Action (adds ~2 min to run).
"""
from __future__ import annotations

import logging

log = logging.getLogger(__name__)


def scrape() -> list[dict]:
    log.warning(
        "Festsaal Kreuzberg: site is a JS SPA (festsaal-kreuzberg.de) that "
        "cannot be scraped with httpx, and the RA venue ID is not confirmed. "
        "See scraper/venues/festsaal.py for how to fix. Returning empty."
    )
    return []
