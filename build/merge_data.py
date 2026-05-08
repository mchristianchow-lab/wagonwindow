#!/usr/bin/env python3
"""
Merge agent-generated data files into the main data files.
Run once after all 6 agents complete.
"""
import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

def load(filename):
    with open(os.path.join(DATA_DIR, filename), encoding='utf-8') as f:
        return json.load(f)

def save(filename, data):
    path = os.path.join(DATA_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  Saved {filename} ({os.path.getsize(path):,} bytes)")

# ── 1. Merge services additions into services.json ───────────────────────────
print("\n[1] Merging service fields...")
services = load('services.json')
additions = load('_services_additions.json')

for svc in services:
    slug = svc['slug']
    if slug in additions:
        svc.update(additions[slug])
        print(f"    {slug}: +{len(additions[slug])} fields")
    else:
        print(f"    WARN: no additions for {slug}")

save('services.json', services)

# ── 2. Merge location service_notes + add lat/lng into locations.json ────────
print("\n[2] Merging location service_notes + coordinates...")
locations = load('locations.json')
notes_p1  = load('_location_notes_part1.json')
notes_p2  = load('_location_notes_part2.json')
all_notes = {**notes_p1, **notes_p2}

# Lat/lng for each location (WGS84, sourced from Google Maps)
COORDS = {
    'salmon-arm': (50.6991, -119.2780),
    'sorrento':   (50.8699, -119.5100),
    'tappen':     (50.7979, -119.4194),
    'blind-bay':  (50.8525, -119.4461),
    'sicamous':   (50.8314, -118.9766),
    'chase':      (50.8183, -119.6820),
    'enderby':    (50.5530, -119.1356),
    'armstrong':  (50.4487, -119.1956),
}

for loc in locations:
    slug = loc['slug']
    if slug in all_notes:
        loc['service_notes'] = all_notes[slug]['service_notes']
        print(f"    {slug}: +service_notes ({len(loc['service_notes'])} services)")
    else:
        print(f"    WARN: no service_notes for {slug}")
    if slug in COORDS:
        loc['lat'], loc['lng'] = COORDS[slug]
        print(f"    {slug}: +lat/lng ({loc['lat']}, {loc['lng']})")
    else:
        print(f"    WARN: no coordinates for {slug}")

save('locations.json', locations)

# ── 3. Merge by_service_location FAQs into faqs.json ────────────────────────
print("\n[3] Merging by_service_location FAQs...")
faqs = load('faqs.json')
faq_res_ext = load('_faqs_combo_res_ext.json')
faq_com_scr_trk = load('_faqs_combo_com_scr_trk.json')
faq_hwr_sea = load('_faqs_combo_hwr_sea.json')

by_sl = {}
for src in [faq_res_ext, faq_com_scr_trk, faq_hwr_sea]:
    by_sl.update(src)

faqs['by_service_location'] = by_sl
total_faqs = sum(len(v) for v in by_sl.values())
print(f"    {len(by_sl)} keys, {total_faqs} total FAQs")

save('faqs.json', faqs)

# ── Summary ──────────────────────────────────────────────────────────────────
print("\n✓ Merge complete.")
print(f"  services.json  — {len(services)} services, each with process_steps, differentiator, etc.")
print(f"  locations.json — {len(locations)} locations, each with service_notes + lat/lng")
print(f"  faqs.json      — by_service_location: {len(by_sl)} combos, {total_faqs} FAQs")
