#!/usr/bin/env python3
"""
Session 2 merge: new locations + gutter service_notes + gutter FAQs.
Run after all 4 agents complete.
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

# ── 1. Merge 6 new locations into locations.json ─────────────────────────────
print("\n[1] Merging new locations...")
locations = load('locations.json')
existing_slugs = {loc['slug'] for loc in locations}

new_locs_1_3 = load('_new_locations_1_3.json')
new_locs_4_6 = load('_new_locations_4_6.json')
new_locations = new_locs_1_3 + new_locs_4_6

added = 0
for loc in new_locations:
    if loc['slug'] not in existing_slugs:
        locations.append(loc)
        print(f"  + {loc['slug']}: {len(loc.get('service_notes', {}))} service_notes, lat={loc.get('lat')}")
        added += 1
    else:
        print(f"  SKIP (already exists): {loc['slug']}")

print(f"  Added {added} new locations. Total: {len(locations)}")

# ── 2. Add gutter service_notes to existing 8 locations ─────────────────────
print("\n[2] Adding gutter-cleaning service_notes to existing locations...")
gutter_notes = load('_gutter_notes_existing.json')

updated = 0
for loc in locations:
    slug = loc['slug']
    if slug in gutter_notes:
        if 'service_notes' not in loc:
            loc['service_notes'] = {}
        loc['service_notes']['gutter-cleaning'] = gutter_notes[slug]
        print(f"  + gutter note → {slug}")
        updated += 1

print(f"  Updated {updated} existing locations with gutter service_notes")
save('locations.json', locations)

# ── 3. Add gutter by_service_location FAQs to faqs.json ─────────────────────
print("\n[3] Merging gutter by_service_location FAQs...")
faqs = load('faqs.json')
gutter_faqs = load('_gutter_faqs_by_location.json')

if 'by_service_location' not in faqs:
    faqs['by_service_location'] = {}

added_keys = 0
for key, faq_list in gutter_faqs.items():
    faqs['by_service_location'][key] = faq_list
    added_keys += 1

total_combo = len(faqs['by_service_location'])
total_faqs = sum(len(v) for v in faqs['by_service_location'].values())
print(f"  Added {added_keys} gutter combo keys")
print(f"  by_service_location total: {total_combo} keys, {total_faqs} FAQs")
save('faqs.json', faqs)

# ── 4. Verify new locations have gutter-cleaning service_notes ───────────────
print("\n[4] Verification...")
final_locs = load('locations.json')
for loc in final_locs:
    sn = loc.get('service_notes', {})
    gutter_ok = 'gutter-cleaning' in sn
    svc_count = len(sn)
    marker = "✓" if gutter_ok and svc_count == 8 else "⚠"
    print(f"  {marker} {loc['slug']}: {svc_count} service_notes, gutter={'yes' if gutter_ok else 'MISSING'}")

print(f"\n✓ Session 2 merge complete.")
print(f"  locations.json: {len(final_locs)} locations")
print(f"  faqs.json: {total_combo} by_service_location combos, {total_faqs} total FAQs")
