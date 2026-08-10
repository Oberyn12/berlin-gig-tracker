"""
Huxley Neue Welt — Large concert venue, Neukölln.
Site: huxleys.de

STATUS: huxleys.de blocks datacenter IP ranges with a socket-level connection
reset. GitHub Actions runs on AWS/Azure IPs that are blocked.

How to fix:
  Check huxleys.de in a real browser → DevTools → Network tab.
  The site likely uses an external ticketing/events API (Eventim, Ticketmaster,
  or a custom endpoint). Capture that XHR URL, add it below as EVENTS_API_URL,
  and write a simple httpx + json.loads() scraper. These APIs usually work
  from any IP, unlike the main site which fingerprints the browser.

  Example structure to implement once you have the API URL:
    resp = httpx.get(EVENTS_API_URL)
    data = resp.json()
    for event in data["events"]:
        # map fields → normalised event dict
"""
from __future__ import annotations

import logging

log = logging.getLogger(__name__)

# TODO: Set this to the real API endpoint once discovered
EVENTS_API_URL = None


def scrape() -> list[dict]:
    log.warning(
        "Huxley Neue Welt: huxleys.de blocks datacenter IPs (used by GitHub Actions). "
        "Inspect the site's network requests in your browser to find the events API. "
        "See scraper/venues/huxley.py for instructions. Returning empty."
    )
    return []
