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
env.globals['faqs']   = faqs_db

_month = datetime.now().month
_ICON_SNOWFLAKE = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="2" x2="12" y2="22"></line><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"></line><line x1="2" y1="12" x2="22" y2="12"></line><line x1="4.93" y1="19.07" x2="19.07" y2="4.93"></line></svg>'
_ICON_BLOSSOM   = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M12 2a3 3 0 0 1 3 3 3 3 0 0 1-3 3 3 3 0 0 1-3-3 3 3 0 0 1 3-3z"></path><path d="M12 16a3 3 0 0 1 3 3 3 3 0 0 1-3 3 3 3 0 0 1-3-3 3 3 0 0 1 3-3z"></path><path d="M22 12a3 3 0 0 1-3 3 3 3 0 0 1-3-3 3 3 0 0 1 3-3 3 3 0 0 1 3 3z"></path><path d="M8 12a3 3 0 0 1-3 3 3 3 0 0 1-3-3 3 3 0 0 1 3-3 3 3 0 0 1 3 3z"></path></svg>'
_ICON_TAG       = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.59 13.41L13.42 20.58a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path><line x1="7" y1="7" x2="7.01" y2="7"></line></svg>'
_ICON_LEAF      = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10z"></path><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"></path></svg>'
_ICON_GIFT      = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="8" width="18" height="4" rx="1"></rect><path d="M12 8v13"></path><path d="M19 12v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-7"></path><path d="M7.5 8a2.5 2.5 0 0 1 0-5C11 3 12 8 12 8"></path><path d="M16.5 8a2.5 2.5 0 0 0 0-5C13 3 12 8 12 8"></path></svg>'

if   _month in (1, 2, 3):
    _season_banner = {'icon': _ICON_SNOWFLAKE, 'strong': 'Beat the spring rush — book now.', 'text': 'Early-season slots fill quickly. Lock in your date before spring demand peaks.'}
elif _month in (4, 5):
    _season_banner = {'icon': _ICON_BLOSSOM, 'strong': 'Spring bookings are filling up fast.', 'text': 'April and May dates are going quick — secure your window clean before the calendar fills.'}
elif _month in (6, 7, 8):
    _season_banner = {'icon': _ICON_TAG, 'strong': 'Save 5% when you book online.', 'text': 'Summer deal — book your clean online today and save 5% off your total. Limited summer slots available.'}
elif _month in (9, 10):
    _season_banner = {'icon': _ICON_LEAF, 'strong': 'Fall is the best time for a pre-winter clean.', 'text': 'Clear out summer buildup before the rain and frost sets in. Book your fall clean now.'}
else:
    _season_banner = {'icon': _ICON_GIFT, 'strong': 'End-of-year bookings going fast.', 'text': 'Lock in your date before the holidays — limited spots remain before year-end.'}
env.globals['season_banner'] = _season_banner

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
def get_faqs(service_slug, location_slug, limit=14):
    """Combo FAQs first (unique per service×location), then service, location, global."""
    combo_key = f"{service_slug}/{location_slug}"
    combo_faqs = faqs_db.get('by_service_location', {}).get(combo_key, [])
    svc_faqs   = faqs_db.get('by_service', {}).get(service_slug, [])
    loc_faqs   = faqs_db.get('by_location', {}).get(location_slug, [])
    global_faqs = faqs_db.get('global', [])
    combined = combo_faqs + svc_faqs + loc_faqs + global_faqs
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
        guide_faqs = guide.get('faqs') or faqs_db.get('global', [])[:6]
        ctx = {
            'guide': guide,
            'page_title': guide['meta_title'],
            'meta_desc': guide['meta_desc'],
            'h1': guide['h1'],
            'canonical': canonical,
            'faqs': guide_faqs
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
        page_faqs = page.get('faqs') or faqs_db.get('global', [])[:6]
        ctx = {
            'page': page,
            'page_title': page['meta_title'],
            'meta_desc': page['meta_desc'],
            'h1': page['h1'],
            'canonical': canonical,
            'faqs': page_faqs
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

# ── Build: Blog Posts ───────────────────────────────────────────────────────
def build_blog():
    try:
        blog_data = load('blog.json')
    except FileNotFoundError:
        print("  Blog: 0 posts (blog.json not found)")
        return
    if not blog_data:
        print("  Blog: 0 posts")
        return
    count = 0
    for post in blog_data:
        canonical = f"{config['site_url']}/blog/{post['slug']}/"
        ctx = {
            'post': post,
            'page_title': post['meta_title'],
            'meta_desc': post['meta_desc'],
            'h1': post['h1'],
            'canonical': canonical,
        }
        out = dist_path('blog', post['slug'])
        render('blog-post.html', out, ctx)
        register(canonical, priority='0.6', changefreq='yearly')
        count += 1
    print(f"  Blog posts: {count} ✓")

def build_blog_index():
    try:
        blog_data = load('blog.json')
    except FileNotFoundError:
        return
    if not blog_data:
        return
    canonical = f"{config['site_url']}/blog/"
    ctx = {
        'posts': sorted(blog_data, key=lambda x: x['published_date'], reverse=True),
        'page_title': 'Window Cleaning Tips & Guides | Wagon Windows Blog',
        'meta_desc': 'Window cleaning tips, guides, and advice for Shuswap homeowners and businesses. Hard water stains, seasonal cleaning, gutter care, and more — from Wagon Windows.',
        'h1': 'Window Cleaning Tips & Guides',
        'canonical': canonical,
    }
    out = os.path.join(DIST_DIR, 'blog', 'index.html')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    render('blog-index.html', out, ctx)
    register(canonical, priority='0.7', changefreq='weekly')
    print("  Blog index ✓")

# ── Build: Quote Page ───────────────────────────────────────────────────────
def build_review_page():
    canonical = f"{config['site_url']}/review/"
    ctx = {
        'page_title': 'Leave a Review | Wagon Windows — Salmon Arm',
        'meta_desc': 'Happy with your window cleaning? Leave Wagon Windows a Google review — it takes less than a minute and helps your neighbours find us.',
        'canonical': canonical,
        'noindex': True,
    }
    out = dist_path('review')
    render('review.html', out, ctx)
    print("  Review page ✓")

def build_quote_page():
    canonical = f"{config['site_url']}/quote/"
    ctx = {
        'page_title': 'Get an Instant Quote | Wagon Windows — Salmon Arm',
        'meta_desc': 'Get an instant window cleaning quote in 4 steps. Choose your service, count your panes, and see a same-day estimate. Subject to confirmation on arrival.',
        'canonical': canonical,
    }
    out = dist_path('quote')
    render('quote.html', out, ctx)
    register(canonical, priority='0.9', changefreq='monthly')
    print("  Quote page ✓")

# ── Build: Standalone Pages ─────────────────────────────────────────────────
def build_standalones():
    try:
        standalones = load('standalones.json')
    except FileNotFoundError:
        print("  Standalones: 0 (standalones.json not found)")
        return
    if not standalones:
        print("  Standalones: 0")
        return
    count = 0
    for page in standalones:
        canonical = f"{config['site_url']}/{page['url_path']}/"
        ctx = {
            'page': page,
            'page_title': page['meta_title'],
            'meta_desc': page['meta_desc'],
            'h1': page['h1'],
            'canonical': canonical,
            'locations': locations,
        }
        out = os.path.join(DIST_DIR, page['url_path'], 'index.html')
        os.makedirs(os.path.dirname(out), exist_ok=True)
        render('standalone.html', out, ctx)
        register(canonical, priority='0.8', changefreq='monthly')
        count += 1
    print(f"  Standalone pages: {count} ✓")

# ── Main ────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    mode = "CHECK ONLY" if CHECK_ONLY else "FULL BUILD"
    print(f"\n=== Wagon Windows {mode} — {datetime.now().strftime('%Y-%m-%d %H:%M')} ===\n")

    if not CHECK_ONLY:
        os.makedirs(DIST_DIR, exist_ok=True)
        copy_assets()
        # Copy standalone tools directly into dist/
        for fname in ['field-tool.html', 'waiver-ipad.html', 'estimate.html', 'book.html', 'site-quote.html',
                       'ffebc380c2229846c623cfd17e8d4685.txt']:
            src = os.path.join(ROOT_DIR, fname)
            if os.path.exists(src):
                shutil.copy(src, os.path.join(DIST_DIR, fname))

    build_homepage()
    build_quote_page()
    build_review_page()
    build_service_location_pages()
    build_location_hubs()
    build_service_hubs()
    build_guides()
    build_seasonal()
    build_blog()
    build_blog_index()
    build_standalones()

    if not CHECK_ONLY:
        generate_sitemap()
        generate_robots()

    total = len(page_registry)
    print(f"\n{'✓' if uniqueness_warnings == 0 else '⚠'} Complete — {total} pages | {uniqueness_warnings} uniqueness warnings\n")
    if uniqueness_warnings > 0:
        print("  Fix all ⚠ warnings before deploying.\n")
