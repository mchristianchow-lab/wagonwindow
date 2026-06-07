#!/usr/bin/env python3
"""
IndexNow URL Submitter for wagonwindow.com
Submits new/updated URLs to Bing and Yandex for instant indexing.

Usage:
  python3 tools/indexnow-submit.py               — Submit all sitemap URLs
  python3 tools/indexnow-submit.py --recent N     — Submit the N most recently modified URLs
  python3 tools/indexnow-submit.py --url /path/  — Submit a single URL

Requirements:
  pip install requests
  Set INDEXNOW_KEY environment variable (or edit KEY below).

Setup:
  1. Generate a key at https://www.bing.com/indexnow/getstarted
  2. Create /dist/<your-key>.txt containing just the key on one line
  3. Export INDEXNOW_KEY=<your-key> or set KEY below
  4. Run after every deploy
"""

import os
import sys
import json
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: pip install requests")
    sys.exit(1)

# ── Configuration ────────────────────────────────────────────────────────────
SITE_URL    = "https://wagonwindow.com"
KEY         = os.environ.get("INDEXNOW_KEY", "ffebc380c2229846c623cfd17e8d4685")
KEY_LOCATION = f"{SITE_URL}/{KEY}.txt"
SITEMAP_URL = f"{SITE_URL}/sitemap.xml"
BUILD_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITEMAP_PATH = os.path.join(BUILD_DIR, "dist", "sitemap.xml")

# IndexNow endpoints
ENDPOINTS = [
    "https://api.indexnow.org/indexnow",
    "https://www.bing.com/indexnow",
]

BATCH_SIZE = 100  # IndexNow max per request
DELAY_BETWEEN_BATCHES = 2  # seconds

# ── Parse Sitemap ─────────────────────────────────────────────────────────────
def parse_sitemap(path=None, url=None):
    """Returns list of (loc, lastmod) tuples from sitemap."""
    if path and os.path.exists(path):
        tree = ET.parse(path)
        root = tree.getroot()
    else:
        print(f"Fetching sitemap from {SITEMAP_URL}...")
        resp = requests.get(SITEMAP_URL, timeout=15)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)

    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    entries = []
    for url_el in root.findall("sm:url", ns):
        loc = url_el.findtext("sm:loc", namespaces=ns)
        lastmod = url_el.findtext("sm:lastmod", namespaces=ns)
        if loc:
            entries.append((loc, lastmod))
    return entries

# ── Submit URLs ───────────────────────────────────────────────────────────────
def submit_batch(urls):
    """Submit a batch of URLs to all IndexNow endpoints."""
    if KEY == "PASTE_YOUR_KEY_HERE":
        print("ERROR: Set INDEXNOW_KEY environment variable or edit KEY in script.")
        sys.exit(1)

    payload = {
        "host": "wagonwindow.com",
        "key": KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": urls,
    }

    results = []
    for endpoint in ENDPOINTS:
        try:
            resp = requests.post(
                endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=15,
            )
            results.append((endpoint.split("/")[2], resp.status_code))
            if resp.status_code in (200, 202):
                print(f"  ✓ {endpoint.split('/')[2]}: {resp.status_code} — {len(urls)} URLs accepted")
            else:
                print(f"  ✗ {endpoint.split('/')[2]}: {resp.status_code} — {resp.text[:200]}")
        except requests.RequestException as e:
            print(f"  ✗ {endpoint.split('/')[2]}: connection error — {e}")
            results.append((endpoint.split("/")[2], "error"))
    return results

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    args = sys.argv[1:]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"\n=== IndexNow Submission — {timestamp} ===\n")

    # Single URL mode
    if "--url" in args:
        idx = args.index("--url")
        path = args[idx + 1]
        url = path if path.startswith("http") else f"{SITE_URL}{path}"
        print(f"Submitting single URL: {url}")
        submit_batch([url])
        return

    # Parse sitemap
    entries = parse_sitemap(path=SITEMAP_PATH)
    if not entries:
        print("No URLs found in sitemap. Run build first.")
        sys.exit(1)

    # Recent mode — only URLs modified in last N days
    if "--recent" in args:
        idx = args.index("--recent")
        days = int(args[idx + 1])
        cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        entries = [(loc, mod) for loc, mod in entries if mod and mod >= cutoff]
        print(f"Filtering to URLs modified since {cutoff}: {len(entries)} found")

    urls = [loc for loc, _ in entries]
    print(f"Total URLs to submit: {len(urls)}")

    # Batch submit
    total_batches = (len(urls) + BATCH_SIZE - 1) // BATCH_SIZE
    for i in range(0, len(urls), BATCH_SIZE):
        batch = urls[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        print(f"\nBatch {batch_num}/{total_batches} ({len(batch)} URLs):")
        submit_batch(batch)
        if i + BATCH_SIZE < len(urls):
            time.sleep(DELAY_BETWEEN_BATCHES)

    print(f"\n✓ Submission complete — {len(urls)} URLs across {total_batches} batch(es)\n")
    print("Next steps:")
    print("  1. Verify key file is live: " + KEY_LOCATION)
    print("  2. Check Bing Webmaster Tools for crawl activity in ~24h")
    print("  3. Resubmit after each deploy with: python3 tools/indexnow-submit.py\n")

if __name__ == "__main__":
    main()
