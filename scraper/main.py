"""
Berlin Gig Tracker — Scraper Orchestrator

Runs all venue scrapers concurrently, merges + deduplicates results,
writes web/events.json relative to the repo root.

Usage:
    python scraper/main.py              # run all scrapers
    python scraper/main.py --dry-run    # print JSON, don't write file
    python scraper/main.py --venue atrane  # single venue (for debugging)
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

# ── Import all venue modules ───────────────────────────────────────────────────

from venues import (
    atrane,
    bflat,
    donau115,
    festsaal,
    gretchen,
    huxley,
    neue_zukunft,
    paloma,
    schokoladen,
    sowieso,
    zigzag,
)

# ── Config ────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

SCRAPERS = {
    "gretchen":    gretchen.scrape,
    "festsaal":    festsaal.scrape,
    "huxley":      huxley.scrape,
    "atrane":      atrane.scrape,
    "bflat":       bflat.scrape,
    "zigzag":      zigzag.scrape,
    "sowieso":     sowieso.scrape,
    "donau115":    donau115.scrape,
    "schokoladen": schokoladen.scrape,
    "paloma":      paloma.scrape,
    "neue_zukunft": neue_zukunft.scrape,
}

REPO_ROOT = Path(__file__).parent.parent
OUTPUT_PATH = REPO_ROOT / "web" / "events.json"

# ── Deduplication ─────────────────────────────────────────────────────────────

def _dedup_key(ev: dict) -> str:
    """Events with same venue + date + title are the same gig."""
    return f"{ev['venue_slug']}|{ev['date']}|{ev['title'].lower().strip()}"


def deduplicate(events: list[dict]) -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []
    for ev in events:
        key = _dedup_key(ev)
        if key not in seen:
            seen.add(key)
            out.append(ev)
    return out

# ── Run ───────────────────────────────────────────────────────────────────────

def run_all(venue_filter: str | None = None) -> list[dict]:
    scrapers = (
        {venue_filter: SCRAPERS[venue_filter]}
        if venue_filter
        else SCRAPERS
    )

    all_events: list[dict] = []
    errors: list[str] = []

    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {
            pool.submit(fn): name
            for name, fn in scrapers.items()
        }
        for future in as_completed(futures):
            name = futures[future]
            try:
                events = future.result()
                log.info("%-14s  →  %d events", name, len(events))
                all_events.extend(events)
            except Exception as exc:
                log.warning("%-14s  ✗  %s", name, exc)
                errors.append(f"{name}: {exc}")

    if errors:
        log.warning("Scrapers with errors: %s", ", ".join(e.split(":")[0] for e in errors))

    # Sort + dedup
    all_events = deduplicate(all_events)
    all_events.sort(key=lambda e: (e["date"], e.get("time") or "99:99"))

    return all_events


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape Berlin venue events")
    parser.add_argument("--dry-run", action="store_true", help="Print JSON, don't write file")
    parser.add_argument("--venue", help="Only run this venue scraper (slug name)")
    args = parser.parse_args()

    if args.venue and args.venue not in SCRAPERS:
        log.error("Unknown venue '%s'. Valid: %s", args.venue, ", ".join(SCRAPERS))
        sys.exit(1)

    log.info("Starting scrape%s…", f" ({args.venue} only)" if args.venue else "")
    events = run_all(venue_filter=args.venue)
    log.info("Total: %d events after dedup", len(events))

    payload = json.dumps(events, ensure_ascii=False, indent=2)

    if args.dry_run:
        print(payload)
    else:
        OUTPUT_PATH.write_text(payload, encoding="utf-8")
        log.info("Written → %s", OUTPUT_PATH)

    # Exit non-zero only if ALL scrapers failed (so GitHub Action fails visibly)
    if len(events) == 0 and not args.dry_run:
        log.error("No events fetched at all — check scraper errors above")
        sys.exit(1)


if __name__ == "__main__":
    main()
