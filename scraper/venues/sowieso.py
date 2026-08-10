"""
Sowieso — Improvised and experimental music, Neukölln.

STATUS: Domain name squatted (confirmed August 2026).
The domain sowieso.berlin was grabbed by a casino affiliate and now serves
a mirrored copy of an unrelated children's site. The real venue
(Weichselstraße 67, 12045 Berlin) likely uses a different domain.

Action needed:
  1. Search "Sowieso Berlin Weichselstr" or "Sowieso Berlin improvised music"
  2. Check their Bandcamp, Facebook, or RA page for a current URL
  3. Update PROGRAMME_URL and implement a scraper here

Possible alternative URL (not verified): https://sowieso.de
"""
from __future__ import annotations

import logging

log = logging.getLogger(__name__)


def scrape() -> list[dict]:
    log.warning(
        "Sowieso: domain sowieso.berlin is squatted by an unrelated site. "
        "Find the venue's actual website and update this scraper. "
        "Returning empty."
    )
    return []
