"""
Neue Zukunft — Events venue, Friedrichshain (Alt-Stralau 68).
Site: https://neue-zukunft.org/konzerte.html

Status: NOT SCRAPED — no machine-readable event data available.

The venue publishes events only as:
  1. An image-only PDF (no text layer — pdfplumber returns blank)
  2. An Elfsight calendar widget that requires client-side JavaScript

Without a headless browser, there is no way to extract structured events.
This scraper returns an empty list (with a logged warning) so the full run
continues unaffected. The other 9 venues still scrape normally.

Follow: https://www.instagram.com/neuezukunftstralau/
"""
import logging

log = logging.getLogger(__name__)


def scrape() -> list[dict]:
    log.warning(
        "neue_zukunft: skipped — events are published as an image-only PDF and a "
        "JavaScript-rendered widget. Open https://neue-zukunft.org/konzerte.html manually."
    )
    return []
