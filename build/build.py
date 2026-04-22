#!/usr/bin/env python3
"""
Wagon Windows Static Site Generator
Generates all pages from Jinja2 templates + JSON data files.
Output: ~/wagonwindows/dist/

Usage:
  python3 build/build.py           — Full build
  python3 build/build.py --check   — Validate data only, no file writes
"""

import json
import os
import sys
import shutil
import hashlib
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

# ── Paths ───────────────────────────────────────────────────────────────────
BUILD_DIR   = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR    = os.path.dirname(BUILD_DIR)
DATA_DIR    = os.path.join(BUILD_DIR, 'data')
TMPL_DIR    = os.path.join(BUILD_DIR, 'templates')
DIST_DIR    = os.path.join(ROOT_DIR, 'dist')
ASSETS_SRC  = os.path.join(BUILD_DIR, 'assets')
ASSETS_DEST = os.path.join(DIST_DIR, 'assets')

CHECK_ONLY  = '--check' in sys.argv

# ── Load JSON Data ──────────────────────────────────────────────────────────
def load(filename):
    path = os.path.join(DATA_DIR, filename)
    with open(path, encoding='utf-8') as f:
        return json.load(f)

config    = load('config.json')
services  = load('services.json')
locations = load('locations.json')
faqs_db   = load('faqs.json')
guides    = load('guides.json')
seasonal  = load('seasonal.json')

# ── Jinja2 ──────────────────────────────────────────────────────────────────
env = Environment(loader=FileSystemLoader(TMPL_DIR), autoescape=True)
env.globals['config'] = config
env.globals['now']    = datetime.now().strftime('%Y-%m-%d')

# ── Page Registry (for sitemap) ─────────────────────────────────────────────
page_registry = []

def register(url, priority='0.8', changefreq='monthly'):
    page_registry.append({
        'url': url,
        'lastmod': datetime.now().strftime('%Y-%m-%d'),
        'priority': priority,
        'changefreq': changefreq
    })

# ── Uniqueness Tracker ──────────────────────────────────────────────────────
content_hashes = {}
uniqueness_warnings = 0

def check_uniqueness(page_slug, label, text):
    global uniqueness_warnings
    h = hashlib.md5(text.strip().lower().encode()).hexdigest()
    key = f"{label}:{h}"
    if key in content_hashes and content_hashes[key] != page_slug:
        print(f"  ⚠  DUPLICATE: [{label}] on '{page_slug}' matches '{content_hashes[key]}'")
        uniqueness_warnings += 1
    else:
        content_hashes[key] = page_slug

# ── FAQ Assembly ────────────────────────────────────────────────────────────
def get_faqs(service_slug, location_slug, limit=10):
    """Return assembled FAQ list: location FAQs first, then service, then global."""
    loc_faqs = faqs_db.get('by_location', {}).get(location_slug, [])
    svc_faqs = faqs_db.get('by_service', {}).get(service_slug, [])
    global_faqs = faqs_db.get('global', [])
    combined = loc_faqs + svc_faqs + global_faqs
    # Deduplicate by question text
    seen = set()
    unique = []
    for faq in combined:
        if faq['q'] not in seen:
            seen.add(faq['q'])
            unique.append(faq)
    return unique[:limit]

# ── Render Helper ───────────────────────────────────────────────────────────
def render(template_name, output_path, context):
    if CHECK_ONLY:
        return output_path
    template = env.get_template(template_name)
    html = template.render(**context)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    return output_path

def dist_path(*parts):
    return os.path.join(DIST_DIR, *parts, 'index.html')

# ── Copy Assets ─────────────────────────────────────────────────────────────
def copy_assets():
    if CHECK_ONLY:
        return
    if os.path.exists(ASSETS_DEST):
        shutil.rmtree(ASSETS_DEST)
    shutil.copytree(ASSETS_SRC, ASSETS_DEST)
    src_css = os.path.join(ROOT_DIR, 'style.css')
    if os.path.exists(src_css):
        shutil.copy(src_css, os.path.join(DIST_DIR, 'style.css'))
    print("  Assets copied ✓")

# ── Build: Homepage ─────────────────────────────────────────────────────────
def build_homepage():
    out = os.path.join(DIST_DIR, 'index.html')
    ctx = {
        'services': services,
        'locations': locations,
        'page_title': 'Wagon Windows | Professional Window Cleaning — Salmon Arm & Shuswap',
        'meta_desc': 'Professional window cleaning for homes and businesses across the Shuswap. Residential, commercial, and seasonal services. Transparent pricing from $169. Locally owned in Salmon Arm, BC.',
        'canonical': config['site_url'] + '/',
        'schema_type': 'homepage'
    }
    render('homepage.html', out, ctx)
    register(config['site_url'] + '/', priority='1.0', changefreq='weekly')
    print("  Homepage ✓")

# ── Build: Service × Location Pages ────────────────────────────────────────
def build_service_location_pages():
    count = 0
    for svc in services:
        for loc in locations:
            price = svc.get('base_price_small',
                    svc.get('base_price_commercial',
                    svc.get('price_per_screen_low',
                    svc.get('base_price', 'varies'))))

            page_slug = f"{svc['slug']}/{loc['slug']}"
            canonical = f"{config['site_url']}/{svc['slug']}/{loc['slug']}/"
            page_faqs = get_faqs(svc['slug'], loc['slug'])

            ctx = {
                'service': svc,
                'location': loc,
                'page_title': svc['meta_title_template']
                    .replace('{location}', loc['name'])
                    .replace('{price}', str(price)),
                'meta_desc': svc['meta_desc_template']
                    .replace('{location}', loc['name'])
                    .replace('{price}', str(price)),
                'h1': svc['h1_template'].replace('{location}', loc['name']),
                'canonical': canonical,
                'faqs': page_faqs,
                'page_slug': page_slug,
                'all_locations': locations,
                'all_services': services
            }

            # Uniqueness checks on key text fields
            check_uniqueness(page_slug, 'meta_desc', ctx['meta_desc'])
            check_uniqueness(page_slug, 'h1', ctx['h1'])

            out = dist_path(svc['slug'], loc['slug'])
            render('service-location.html', out, ctx)
            register(canonical)
            count += 1

    print(f"  Service × Location pages: {count} ✓")

# ── Build: Location Hub Pages ───────────────────────────────────────────────
def build_location_hubs():
    for loc in locations:
        canonical = f"{config['site_url']}/locations/{loc['slug']}/"
        ctx = {
            'location': loc,
            'services': services,
            'page_title': f"Window Cleaning in {loc['name']}, BC | Wagon Windows",
            'meta_desc': f"Professional window cleaning in {loc['name']}, BC. Residential and commercial services by Wagon Windows. Locally owned, streak-free results. Get a free quote.",
            'h1': f"Window Cleaning in {loc['name']}, BC",
            'canonical': canonical,
            'faqs': faqs_db.get('by_location', {}).get(loc['slug'], []) + faqs_db.get('global', [])[:4],
            'all_locations': locations
        }
        out = dist_path('locations', loc['slug'])
        render('location-hub.html', out, ctx)
        register(canonical, priority='0.9')
    print(f"  Location hubs: {len(locations)} ✓")

# ── Build: Service Hub Pages ────────────────────────────────────────────────
def build_service_hubs():
    for svc in services:
        canonical = f"{config['site_url']}/services/{svc['slug']}/"
        ctx = {
            'service': svc,
            'locations': locations,
            'page_title': f"{svc['name']} | Wagon Windows | Shuswap Region, BC",
            'meta_desc': f"{svc['service_description'][:120]} Wagon Windows serves all of the Shuswap. Get a free quote.",
            'h1': f"{svc['name']} — Shuswap Region, BC",
            'canonical': canonical,
            'faqs': faqs_db.get('by_service', {}).get(svc['slug'], []) + faqs_db.get('global', [])[:4],
            'all_services': services
        }
        out = dist_path('services', svc['slug'])
        render('service-hub.html', out, ctx)
        register(canonical, priority='0.9')
    print(f"  Service hubs: {len(services)} ✓")

# ── Build: Guide Pages ──────────────────────────────────────────────────────
def build_guides():
    if not guides:
        print("  Guides: 0 (add entries to data/guides.json to build)")
        return
    count = 0
    for guide in guides:
        canonical = f"{config['site_url']}/guides/{guide['slug']}/"
        ctx = {
            'guide': guide,
            'page_title': guide['meta_title'],
            'meta_desc': guide['meta_desc'],
            'h1': guide['h1'],
            'canonical': canonical,
            'faqs': faqs_db.get('global', [])[:6]
        }
        out = dist_path('guides', guide['slug'])
        render('guide.html', out, ctx)
        register(canonical, priority='0.7', changefreq='yearly')
        count += 1
    print(f"  Guide pages: {count} ✓")

# ── Build: Seasonal Pages ───────────────────────────────────────────────────
def build_seasonal():
    if not seasonal:
        print("  Seasonal: 0 (add entries to data/seasonal.json to build)")
        return
    count = 0
    for page in seasonal:
        canonical = f"{config['site_url']}/seasonal/{page['slug']}/"
        ctx = {
            'page': page,
            'page_title': page['meta_title'],
            'meta_desc': page['meta_desc'],
            'h1': page['h1'],
            'canonical': canonical,
            'faqs': faqs_db.get('global', [])[:6]
        }
        out = dist_path('seasonal', page['slug'])
        render('seasonal.html', out, ctx)
        register(canonical, priority='0.7', changefreq='yearly')
        count += 1
    print(f"  Seasonal pages: {count} ✓")

# ── Generate Sitemap ────────────────────────────────────────────────────────
def generate_sitemap():
    if CHECK_ONLY:
        return
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    for page in page_registry:
        lines.append(
            f'  <url>\n'
            f'    <loc>{page["url"]}</loc>\n'
            f'    <lastmod>{page["lastmod"]}</lastmod>\n'
            f'    <changefreq>{page["changefreq"]}</changefreq>\n'
            f'    <priority>{page["priority"]}</priority>\n'
            f'  </url>'
        )
    lines.append('</urlset>')
    out = os.path.join(DIST_DIR, 'sitemap.xml')
    with open(out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"  Sitemap: {len(page_registry)} URLs ✓")

# ── Generate robots.txt ─────────────────────────────────────────────────────
def generate_robots():
    if CHECK_ONLY:
        return
    content = f"User-agent: *\nAllow: /\n\nSitemap: {config['site_url']}/sitemap.xml\n"
    out = os.path.join(DIST_DIR, 'robots.txt')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(content)
    print("  robots.txt ✓")

# ── Main ────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    mode = "CHECK ONLY" if CHECK_ONLY else "FULL BUILD"
    print(f"\n=== Wagon Windows {mode} — {datetime.now().strftime('%Y-%m-%d %H:%M')} ===\n")

    if not CHECK_ONLY:
        os.makedirs(DIST_DIR, exist_ok=True)
        copy_assets()

    build_homepage()
    build_service_location_pages()
    build_location_hubs()
    build_service_hubs()
    build_guides()
    build_seasonal()

    if not CHECK_ONLY:
        generate_sitemap()
        generate_robots()

    total = len(page_registry)
    print(f"\n{'✓' if uniqueness_warnings == 0 else '⚠'} Complete — {total} pages | {uniqueness_warnings} uniqueness warnings\n")
    if uniqueness_warnings > 0:
        print("  Fix all ⚠ warnings before deploying.\n")
