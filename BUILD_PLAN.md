# WAGON WINDOWS — EXHAUSTIVE BUILD PLAN
**Status:** Approved for execution  
**Date:** 2026-05-07  
**Target:** 72 → 210 pages | 80%+ uniqueness | verbose schema | 50 blog posts | 30 GBP posts  
**Execution:** 5 sequential build sessions. Each session is self-contained. Do not begin a session until the prior one passes its verification gate.

---

## GROUND RULES FOR ALL BUILD AGENTS

1. **Always `cd ~/wagonwindows` and run `git fetch origin && git log HEAD..origin/main --oneline` before any edits.**
2. **Never hardcode derived values.** If a field is computed (e.g. price in meta title uses `base_price_small`), use the template expression.
3. **Run `python3 build/build.py --check` after every data file edit to validate before full build.**
4. **Run `python3 build/build.py` (full build) only at session end, after all data/template changes are complete.**
5. **Verify page count and uniqueness warnings in build output before marking session done.**
6. **Business name in site brand/copy = "Wagon Windows". In legal docs only = "Wagon Window Washers". config.json unchanged.**
7. **Never write placeholder content.** Every word written into data files must be final, publish-ready copy.
8. **Internal links:** every page must link to at minimum: homepage, its service hub (if service-location), its location hub (if service-location), and one related blog post or guide once those exist.

---

## SESSION 1 — SCHEMA OVERHAUL + TEMPLATE ENHANCEMENTS + UNIQUENESS UPGRADE
**Goal:** Rebuild all 72 existing pages with 2,800–3,200 words, 80%+ uniqueness, verbose schema, above-fold CTA on all page types, FAQs on all page types, BreadcrumbList JSON-LD everywhere.  
**Files modified:** 5 templates + 3 data files  
**Files created:** 0  
**Expected output:** 72 pages rebuilt (same URLs, richer content)

---

### 1A — base.html: Expand LocalBusiness Schema

**File:** `build/templates/base.html`  
**Location:** Find the existing `LocalBusiness` JSON-LD block (around line 51).  
**Replace the entire JSON-LD block with:**

```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Wagon Windows",
  "legalName": "Wagon Window Washers",
  "description": "Professional window cleaning for homes and businesses across Salmon Arm and the Shuswap region, BC. Residential, commercial, screen, track, gutter, and hard water stain removal services.",
  "url": "{{ config.site_url }}",
  "logo": "{{ config.site_url }}/assets/logo.png",
  "image": "{{ config.site_url }}/assets/og-image.jpg",
  "telephone": "{{ config.phone_raw }}",
  "email": "{{ config.email }}",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "Salmon Arm",
    "addressLocality": "Salmon Arm",
    "addressRegion": "BC",
    "postalCode": "V1E",
    "addressCountry": "CA"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": 50.6991,
    "longitude": -119.2780
  },
  "areaServed": [
    {"@type": "City", "name": "Salmon Arm"},
    {"@type": "City", "name": "Sorrento"},
    {"@type": "City", "name": "Tappen"},
    {"@type": "City", "name": "Blind Bay"},
    {"@type": "City", "name": "Sicamous"},
    {"@type": "City", "name": "Chase"},
    {"@type": "City", "name": "Enderby"},
    {"@type": "City", "name": "Armstrong"},
    {"@type": "City", "name": "Eagle Bay"},
    {"@type": "City", "name": "Celista"},
    {"@type": "City", "name": "Scotch Creek"},
    {"@type": "City", "name": "Grindrod"},
    {"@type": "City", "name": "Spallumcheen"},
    {"@type": "City", "name": "Swansea Point"}
  ],
  "openingHoursSpecification": [
    {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday"], "opens": "08:00", "closes": "18:00"},
    {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Saturday"], "opens": "09:00", "closes": "16:00"}
  ],
  "priceRange": "$$",
  "currenciesAccepted": "CAD",
  "paymentAccepted": "Cash, E-Transfer",
  "hasMap": "https://maps.google.com/?q=Wagon+Windows+Salmon+Arm+BC",
  "sameAs": [
    "https://www.google.com/maps?cid=PLACEHOLDER_REPLACE_WITH_GBP_CID"
  ],
  "serviceType": ["Window Cleaning", "Gutter Cleaning", "Screen Cleaning", "Hard Water Stain Removal"],
  "slogan": "Crystal Clear Windows. Every Time."
}
```

**Also add Open Graph tags inside `<head>` if not already present:**
```html
<meta property="og:title" content="{{ page_title }}">
<meta property="og:description" content="{{ meta_desc }}">
<meta property="og:url" content="{{ canonical }}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Wagon Windows">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{{ page_title }}">
<meta name="twitter:description" content="{{ meta_desc }}">
```

---

### 1B — services.json: Add Process Steps + Service-Specific Content

**File:** `build/data/services.json`  
**Add the following new fields to each service object:**

#### residential-window-cleaning — add:
```json
"process_steps": [
  {"step": 1, "name": "Property Walkthrough", "description": "We walk the full exterior with you (or alone if you prefer), photographing every window and noting any pre-existing chips, seal failures, or difficult-access points before a single tool comes out."},
  {"step": 2, "name": "Screen Removal & Labelling", "description": "All screens are removed and labelled by position so they go back exactly where they came from. We inspect each one for damage before removal and flag anything compromised."},
  {"step": 3, "name": "Dry Debris Clear", "description": "Loose debris, insect nests, and cobwebs are cleared from frames and sills with a dry brush before any water touches the glass — wet debris smears, dry debris removes cleanly."},
  {"step": 4, "name": "Pre-Rinse", "description": "A clean water pre-rinse removes surface grit that would otherwise drag under the squeegee and cause micro-scratches on glass."},
  {"step": 5, "name": "Solution & Scrub", "description": "Eco-friendly, biodegradable cleaning solution applied with a professional-grade T-bar scrubber. Dwell time adjusted for buildup severity."},
  {"step": 6, "name": "Squeegee & Detail", "description": "Professional rubber-blade squeegee technique removes solution in a single pass. All edges are hand-detailed with a lint-free cloth — no drips on frames or sills."},
  {"step": 7, "name": "Interior Cleaning", "description": "Interior panes cleaned with a separate solution and tool set — never the same squeegee that touched the exterior. Sills protected with microfibre during the clean."},
  {"step": 8, "name": "Screen Reinstall & Final Inspection", "description": "Screens reinstalled and checked for proper seating. Final walk with you to confirm every pane is streak-free before we pack up."}
],
"differentiator": "The only service in the Shuswap that includes a pre-job photo walkthrough, screen labelling, and a signed service agreement on every residential job — no surprises, no disputes.",
"common_problems": ["Mineral deposits from Shuswap Lake spray", "Cottonwood pollen buildup in May-June", "Upper-storey access on hillside homes", "Failed window seals discovered during cleaning (not caused by cleaning)", "Screen corrosion on older aluminum frames"],
"result_description": "Every exterior pane streak-free and squeegee-detailed. Interior glass cleaned without disturbing your space. Screens back in place. Tracks cleared. The whole house done in a single visit.",
"booking_urgency": "Spring and fall slots fill within days — book 1-2 weeks ahead during peak season (April-May and September-October)."
```

#### exterior-window-cleaning — add:
```json
"process_steps": [
  {"step": 1, "name": "Access Assessment", "description": "We assess every window for safe ladder access, soft ground, low overhead wires, and proximity to landscaping before setup. Any windows we can't safely reach are flagged before we start."},
  {"step": 2, "name": "Dry Clear", "description": "Frames, sills, and corners brushed dry to remove loose debris, spider webs, and dried insect material before water contact."},
  {"step": 3, "name": "Pre-Rinse", "description": "Clean water rinse to remove surface grit — prevents dragging particles across glass during the scrub phase."},
  {"step": 4, "name": "Solution Application", "description": "Eco-friendly cleaning solution applied with a professional T-bar scrubber. Contact time varies by glass condition and buildup type."},
  {"step": 5, "name": "Squeegee & Edge Detail", "description": "Single-pass squeegee technique followed by edge detailing with a dry lint-free cloth. Zero drips on frames or siding."},
  {"step": 6, "name": "Sill & Frame Wipe", "description": "All exterior window sills and frames wiped down after the glass is done. The surround is part of the result — not just the glass."},
  {"step": 7, "name": "Final Inspection", "description": "We check every pane from multiple angles in natural light. Any streaks are re-done on the spot before moving to the next window."}
],
"differentiator": "Exterior-only cleans are our most popular quick-result service — the most visible improvement with the shortest visit time. Ideal for pre-event, pre-sale, or seasonal refresh without the full interior-access commitment.",
"common_problems": ["Hard water spray from sprinkler systems hitting glass repeatedly", "Oxidized aluminum frames leaving white residue on glass edges", "Bird strike marks requiring extended dwell time", "Paint overspray on older homes", "UV haze on south-facing glass in summer"],
"result_description": "Every accessible exterior pane squeegee-clean and streak-free. Frames and sills wiped. Visible from the street — immediate curb appeal improvement.",
"booking_urgency": "Exterior-only slots are typically available within 3-5 business days. Spring and pre-sale bookings fill faster."
```

#### commercial-window-cleaning — add:
```json
"process_steps": [
  {"step": 1, "name": "Site Assessment & Scheduling", "description": "We assess the storefront or building before quoting — counting panes, noting access constraints, signage, and preferred service windows (early morning before open is standard for most retail)."},
  {"step": 2, "name": "Low-Traffic Scheduling", "description": "Commercial cleans are scheduled for before opening (typically 7:00–9:00 AM) or after close to avoid disrupting customers or staff."},
  {"step": 3, "name": "Debris & Frame Pre-Clean", "description": "Frames, signage surrounds, and door glass pre-cleaned dry before water contact. Food residue, tape adhesive, and sticker removal handled at this stage."},
  {"step": 4, "name": "Solution & Scrubber", "description": "Commercial-grade solution applied with a wide T-bar scrubber. Higher-traffic storefronts with grease or film buildup get a degreaser pre-treatment."},
  {"step": 5, "name": "Squeegee & Detail", "description": "Professional squeegee technique — no drips on door handles, signage, or entry mats. All edges hand-detailed."},
  {"step": 6, "name": "Door Glass", "description": "Entry door glass cleaned last — it gets touched the most and is the first thing customers see when they walk in."},
  {"step": 7, "name": "Walkthrough with Owner/Manager", "description": "Final walkthrough with whoever is on-site to confirm all glass is done to standard before we leave."}
],
"differentiator": "Recurring commercial contracts available — weekly, bi-weekly, or monthly. Locked rate for the season. We schedule automatically so you don't have to remember.",
"common_problems": ["Finger smudges and handprints on entry glass daily", "Adhesive residue from promotional stickers and posters", "Grease film from kitchen exhaust on restaurant windows", "Salt spray on parking lot-facing glass in winter", "Inconsistent results from rotating staff doing it themselves"],
"result_description": "Every storefront pane, entry door, and office window streak-free and customer-ready. Completed before your business opens.",
"booking_urgency": "Recurring contracts are booked by the month — contact us to lock a weekly or bi-weekly slot before your preferred time fills."
```

#### screen-cleaning — add:
```json
"process_steps": [
  {"step": 1, "name": "Removal & Labelling", "description": "Every screen removed and labelled by window position before washing. This prevents the inevitable 'wrong screen on the wrong window' problem that loose-process cleaners create."},
  {"step": 2, "name": "Inspection", "description": "Each screen inspected for tears, bent frames, loose splines, and corrosion. Any issues flagged and photographed before washing — so damage present before we touched it is documented."},
  {"step": 3, "name": "Brush Wash", "description": "Screens laid flat and scrubbed with a soft-bristle brush and mild solution. Pollen, dust, insect debris, and mould spores all release differently — scrub technique adjusted per screen condition."},
  {"step": 4, "name": "Rinse", "description": "Clean water rinse until water runs clear. Soap residue left on screens creates a pollen magnet — full rinse is non-negotiable."},
  {"step": 5, "name": "Air Dry & Reinstall", "description": "Screens stood upright to air dry before reinstallation — never reinstalled wet into frames. Each screen checked for proper seat and corner clip engagement before we move on."}
],
"differentiator": "Screen cleaning is almost always an add-on to window cleaning — bundling it on the same visit saves a second service call and takes only 15-20 minutes for a standard home. $4-$5 per screen.",
"common_problems": ["Pollen permanently embedded in fine mesh (cottonwood is the worst offender in the Shuswap)", "Bent frames from improper DIY removal", "Missing corner clips discovered during removal", "Corrosion on aluminum frames in high-humidity lake areas", "Screens reinstalled in wrong windows after DIY washing"],
"result_description": "Every screen brushed clean, rinsed, dried, and reinstalled in the correct window. Light and airflow restored. No pollen film on glass from dirty screens in rain.",
"booking_urgency": "Best combined with any window clean — no additional trip charge. Book screen cleaning as an add-on when booking your window clean."
```

#### track-cleaning — add:
```json
"process_steps": [
  {"step": 1, "name": "Vacuum", "description": "A hand vacuum removes loose debris from tracks and channels before wet cleaning — dry first prevents wet grime from spreading into corners."},
  {"step": 2, "name": "Brush Scrub", "description": "Stiff detail brush works into track corners and channels to break up compacted dirt, dead insects, and accumulated debris. Tracks are narrower than they look — a proper detail brush is the only tool that clears corners effectively."},
  {"step": 3, "name": "Damp Wipe", "description": "Damp microfibre cloth removes loosened debris. Multiple passes until cloth comes back clean."},
  {"step": 4, "name": "Weep Hole Clear", "description": "Weep holes (the small drainage holes at the bottom of each track) cleared with a thin probe. Blocked weep holes cause water pooling inside frames — a leading cause of sill rot."},
  {"step": 5, "name": "Roller Inspection & Lubrication", "description": "Sliding window rollers inspected for wear and debris. A light dry-lubricant applied to rollers and the track surface — windows glide smoothly after a proper track service."}
],
"differentiator": "Most window cleaners wipe the surface of tracks and call it done. We vacuum, brush-scrub corners, clear weep holes, and lubricate rollers — it takes longer but windows operate properly afterward.",
"common_problems": ["Compacted insect debris and pollen in track corners (especially after summer)", "Blocked weep holes causing interior water pooling during rain", "Seized or worn rollers on sliding windows and patio doors", "Mould growth in damp tracks (common in lake-adjacent properties)", "Tracks on older homes with 10+ years of accumulated grime"],
"result_description": "Tracks vacuumed, scrubbed, and wiped clean. Weep holes open. Rollers lubricated. Windows slide smoothly. The kind of clean that makes a home feel well-maintained.",
"booking_urgency": "Track cleaning is almost always an add-on — bundle it with a window clean for the best value. Starting from $65 for a standard home."
```

#### hard-water-stain-removal — add:
```json
"process_steps": [
  {"step": 1, "name": "Severity Assessment", "description": "We assess each stained pane under direct light to classify stain severity: light (surface mineral haze), moderate (visible white deposits), or severe (etched or pitted glass surface). Severe etching may be permanent — we'll be honest with you before we proceed."},
  {"step": 2, "name": "Test Patch", "description": "A 10cm test patch is treated first on an inconspicuous corner of the most-affected pane. Result assessed after full treatment cycle before committing to the full window."},
  {"step": 3, "name": "Acid-Free Mineral Remover Application", "description": "Professional-grade acid-free mineral deposit remover applied with a microfibre applicator. Dwell time is critical — under-dwelling leaves residue, over-dwelling risks surface damage."},
  {"step": 4, "name": "Agitation", "description": "Gentle agitation with a non-abrasive pad works the treatment into the mineral layer. Circular motion, uniform pressure, no scraping."},
  {"step": 5, "name": "Rinse & Assess", "description": "Thorough rinse and visual assessment in direct light. Second treatment applied if deposits remain. We do not proceed past two treatment cycles without re-quoting — some stains require multiple visits."},
  {"step": 6, "name": "Protective Treatment (Optional)", "description": "A hydrophobic glass sealant can be applied after stain removal to slow future mineral adhesion — particularly recommended for Shuswap Lake spray-affected properties. Quoted separately."}
],
"differentiator": "Hard water stain removal is a specialist service — not every window cleaner offers it and not every cleaner who offers it does it safely. We use acid-free chemistry, test patches, and honest assessments. If the staining is beyond treatment, we'll tell you before charging you.",
"common_problems": ["Calcium and silica deposits from Shuswap Lake spray on waterfront properties", "Sprinkler system hard water etching on south-facing glass", "Multi-year mineral buildup that has begun to etch (pit) the glass surface", "Customers expecting standard cleaning to remove stains (it won't)", "Misidentified staining — some 'stains' are failed seals or internal fogging, not surface deposits"],
"result_description": "Surface mineral deposits removed or significantly reduced. Glass clarity restored. Hydrophobic treatment available to protect against future buildup. Honest assessment if etching has progressed beyond surface treatment.",
"booking_urgency": "Hard water removal is quoted on-site after assessment — contact us to arrange an inspection. Severe deposits are harder to remove and may require multiple treatments."
```

#### seasonal-window-cleaning — add:
```json
"process_steps": [
  {"step": 1, "name": "Pre-Season Assessment", "description": "Each seasonal visit begins with a quick visual assessment of what the previous season left behind — pollen load in spring, UV haze in summer, leaf tannins and frost damage in fall."},
  {"step": 2, "name": "Spring Clean (April-May)", "description": "Spring clean targets cottonwood and tree pollen, winter grime, and mineral buildup from freeze-thaw moisture. The heaviest clean of the year — full exterior + interior + screens recommended."},
  {"step": 3, "name": "Midsummer Clean (July)", "description": "Midsummer clean addresses dust accumulation from Okanagan wind corridors, insect residue on south-facing glass, and UV haze on older panes. Usually exterior-only."},
  {"step": 4, "name": "Fall Clean (September-October)", "description": "Fall clean removes leaf tannin deposits (which stain glass if left to break down over winter), spider egg cases from frames, and early frost residue. Sets the windows up for winter."},
  {"step": 5, "name": "Recurring Booking Setup", "description": "Seasonal package customers are booked automatically for all three visits at the start of the season. We send a reminder text 1 week before each visit — you don't have to remember anything."},
  {"step": 6, "name": "Annual Summary", "description": "At the end of your first full seasonal cycle, we provide a brief condition summary — any panes showing seal failure, screens with corrosion, or tracks with wear — so you can plan any maintenance proactively."}
],
"differentiator": "Seasonal packages are priced below booking each clean individually. One conversation, three cleans, automatic scheduling. Most Shuswap homeowners who start a seasonal package renew every year.",
"common_problems": ["Forgetting to book before peak slots fill", "Pollen from spring left on glass through summer (causes UV bonding)", "Leaf tannins left through winter staining glass permanently", "Paying single-clean rates when a seasonal bundle would save money"],
"result_description": "Windows cleaned three times per year at the optimal points in the Shuswap climate cycle. Automatic scheduling means you never think about it. Bundle pricing saves vs individual bookings.",
"booking_urgency": "Seasonal packages are sold in limited quantities — we cap them to maintain scheduling flexibility. Book before spring slots close (typically by April 15)."
```

**Also add to each service — new field for meta and uniqueness:**
```json
"page_intro_template": "If you're looking for [service.name] in {location}, you're in the right place. Wagon Windows serves {location} residents and businesses with professional results, transparent pricing, and a signed service agreement on every job. Below: exactly what's included, what it costs in {location}, and how to book."
```
*(Note: This field is used by the template to render a conversion-focused summary paragraph unique to each service type, not just location-swapped.)*

---

### 1C — locations.json: Add Service-Location Combination Notes

**File:** `build/data/locations.json`  
**Add a `service_notes` object to EACH location.** This is the uniqueness Layer 2 — ~150 words per service per location. These are genuinely unique combination blocks that make residential/salmon-arm different from exterior/salmon-arm AND from residential/armstrong.

**Schema to add inside each location object:**
```json
"service_notes": {
  "residential-window-cleaning": "150-word paragraph specific to what residential window cleaning looks like in THIS location — property types, access challenges, climate-specific buildup, typical job scope.",
  "exterior-window-cleaning": "150-word paragraph specific to exterior cleaning in this location.",
  "commercial-window-cleaning": "150-word paragraph specific to commercial cleaning in this location.",
  "screen-cleaning": "100-word paragraph — screen-specific issues in this location (pollen types, humidity effects on screens, etc.).",
  "track-cleaning": "100-word paragraph — track-specific issues in this location.",
  "hard-water-stain-removal": "150-word paragraph — water quality, mineral content, common stain sources in this location.",
  "seasonal-window-cleaning": "100-word paragraph — seasonal timing specific to this location's climate cycle."
}
```

**Write the actual content for all 8 existing locations × 7 services = 56 unique prose blocks.** Each block must be written from scratch — no copy-paste between locations. Minimum 100 words each. Tone: factual, local, specific. Reference local geography, property types, specific seasonal conditions.

**Example for salmon-arm / residential:**
> "Salmon Arm residential window cleaning covers a wider range of property types than any other community in our service area — from compact townhomes along the Trans-Canada to expansive lakefront properties on Shuswap Lake with 40+ windows and upper-storey glass requiring 24-foot ladder access. The lake proximity is the dominant factor: calcium and silica from Shuswap Lake spray deposits on exterior glass year-round, requiring a pre-treatment rinse before standard cleaning on most waterfront properties. Hillside homes in the Raven and Hillcrest neighbourhoods face a different challenge — heavy cottonwood pollen in May-June that bonds to glass within 48 hours if not addressed. Interior cleaning in Salmon Arm homes is frequently requested alongside exterior, particularly for lakefront properties where large picture windows face the water. Full residential cleans in Salmon Arm typically take 3-5 hours depending on window count and access."

**Example for armstrong / residential:**
> "Armstrong residential window cleaning is shaped by the Spallumcheen Valley's agricultural character. Properties here range from suburban homes in Armstrong proper to large acreages in the surrounding Spallumcheen municipality — many with 25-40 windows spread across two storeys and outbuildings. The dominant window contamination in Armstrong is agricultural dust: fine clay and organic particulate from surrounding dairy farms and grain operations that accumulates faster here than in any other community we serve. Hot, dry Armstrong summers mean this dust bakes onto south and west-facing glass within days of cleaning if conditions are right. Armstrong homes also tend to be older on average, which means more original aluminum-frame windows with corroded tracks and weakened screen splines. We account for this in our Armstrong quotes — older window hardware requires more careful screen removal and additional track work."

*(Continue this pattern for all 56 combinations — this is the primary content-writing workload of Session 1.)*

---

### 1D — faqs.json: Expand to 12-14 FAQs per Service-Location Combination

**File:** `build/data/faqs.json`  
**Current structure:** global (8), by_service (7 keys), by_location (8 keys)  
**Target structure:** Add `by_service_location` key — a dict with `"service-slug/location-slug"` keys, each containing 4 unique FAQs.

**New structure addition:**
```json
{
  "global": [...existing 8...],
  "by_service": {...existing...},
  "by_location": {...existing...},
  "by_service_location": {
    "residential-window-cleaning/salmon-arm": [
      {"q": "Question unique to residential cleaning specifically in Salmon Arm", "a": "Answer with Salmon Arm-specific detail."},
      {"q": "...", "a": "..."},
      {"q": "...", "a": "..."},
      {"q": "...", "a": "..."}
    ],
    "residential-window-cleaning/armstrong": [...4 unique FAQs...],
    "exterior-window-cleaning/salmon-arm": [...4 unique FAQs...],
    ...all 56 combinations...
  }
}
```

**Writing requirement:** 56 combinations × 4 FAQs = 224 unique FAQ entries. Every Q must be a real question a homeowner in that specific location would ask about that specific service. No repeats. Format: conversational, specific, 40-120 words per answer.

**Also add to `by_service`:** Each service currently has FAQs in the pool. Add 4 more per service (current count likely 4-6 — target 10 per service).

**Also add to `by_location`:** Each location currently has FAQs. Add 2 more per location.

**Update `build.py` — `get_faqs()` function:** Modify to pull from `by_service_location` first (4 FAQs), then `by_service` (4 FAQs), then `by_location` (4 FAQs), then global (2-4 FAQs) = 14-16 total per service-location page.

```python
def get_faqs(service_slug, location_slug, limit=14):
    combo_key = f"{service_slug}/{location_slug}"
    combo_faqs = faqs_db.get('by_service_location', {}).get(combo_key, [])
    svc_faqs = faqs_db.get('by_service', {}).get(service_slug, [])
    loc_faqs = faqs_db.get('by_location', {}).get(location_slug, [])
    global_faqs = faqs_db.get('global', [])
    combined = combo_faqs + svc_faqs + loc_faqs + global_faqs
    seen = set()
    unique = []
    for faq in combined:
        if faq['q'] not in seen:
            seen.add(faq['q'])
            unique.append(faq)
    return unique[:limit]
```

---

### 1E — service-location.html: Template Enhancements

**File:** `build/templates/service-location.html`  
**Current length:** 292 lines  
**Changes required:**

**1. Add BreadcrumbList JSON-LD to `{% block head_extra %}`:**
```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Home", "item": "{{ config.site_url }}/"},
    {"@type": "ListItem", "position": 2, "name": "{{ service.name }}", "item": "{{ config.site_url }}/services/{{ service.slug }}/"},
    {"@type": "ListItem", "position": 3, "name": "{{ location.name }}", "item": "{{ canonical }}"}
  ]
}
```

**2. Expand Service JSON-LD schema (replace existing thin Service block):**
```json
{
  "@context": "https://schema.org",
  "@type": "Service",
  "name": "{{ service.name }} in {{ location.name }}, BC",
  "description": "{{ service.service_description }}",
  "provider": {
    "@type": "LocalBusiness",
    "name": "Wagon Windows",
    "telephone": "{{ config.phone_raw }}",
    "url": "{{ config.site_url }}"
  },
  "areaServed": {
    "@type": "City",
    "name": "{{ location.name }}",
    "addressRegion": "BC",
    "addressCountry": "CA"
  },
  "hasOfferCatalog": {
    "@type": "OfferCatalog",
    "name": "{{ service.name }} Services",
    "itemListElement": [
      {% for bullet in service.what_we_do_bullets %}
      {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "{{ bullet }}"}}{% if not loop.last %},{% endif %}
      {% endfor %}
    ]
  },
  "offers": {
    "@type": "Offer",
    "priceCurrency": "CAD",
    "price": "{{ service.base_price_small | default(service.base_price_commercial) | default(service.price_per_screen_low) | default('varies') }}",
    "description": "Starting price for {{ service.name }} in {{ location.name }}"
  },
  "serviceType": "{{ service.schema_service_type }}"
}
```

**3. Add HowTo JSON-LD (after Service schema, inside `{% block head_extra %}`):**
```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "How {{ service.name }} Works — Wagon Windows Process",
  "description": "Our {{ service.name | lower }} process in {{ location.name }}: step-by-step.",
  "step": [
    {% for step in service.process_steps %}
    {
      "@type": "HowToStep",
      "position": {{ step.step }},
      "name": "{{ step.name }}",
      "text": "{{ step.description }}"
    }{% if not loop.last %},{% endif %}
    {% endfor %}
  ]
}
```

**4. Add "Service Introduction" section — renders immediately after `.key-facts` box, before the "What is..." section:**
```html
<section class="content-section intro-conversion">
  <p class="page-intro">{{ service.page_intro_template | replace('{location}', location.name) }}</p>
  {% if location.service_notes and location.service_notes[service.slug] %}
  <div class="location-service-context">
    <h2>{{ service.name }} in {{ location.name }}: What You're Actually Dealing With</h2>
    <p>{{ location.service_notes[service.slug] }}</p>
  </div>
  {% endif %}
</section>
```

**5. Add "Our Process" section — renders after the "What's Included" section:**
```html
<section class="content-section process-section">
  <h2>How We Do {{ service.name }} in {{ location.name }}: Step by Step</h2>
  <p class="section-intro">We follow the same process on every job. Here's exactly what happens from the moment we arrive at your {{ location.name }} property.</p>
  <ol class="process-steps">
    {% for step in service.process_steps %}
    <li class="process-step">
      <div class="step-header">
        <span class="step-num">{{ step.step }}</span>
        <strong>{{ step.name }}</strong>
      </div>
      <p>{{ step.description }}</p>
    </li>
    {% endfor %}
  </ol>
  <div class="process-callout">
    <p><strong>What makes us different:</strong> {{ service.differentiator }}</p>
  </div>
</section>
```

**6. Add "Common Problems We Solve" section — renders after "When to Book" section:**
```html
<section class="content-section problems-section">
  <h2>Common Window Problems We Fix in {{ location.name }}</h2>
  <ul class="problems-list">
    {% for problem in service.common_problems %}
    <li>{{ problem }}</li>
    {% endfor %}
  </ul>
  <p>{{ service.result_description }}</p>
</section>
```

**7. Add internal links section — renders before the final CTA:**
```html
<section class="content-section related-links">
  <h2>More from Wagon Windows in {{ location.name }}</h2>
  <ul class="related-nav">
    <li><a href="/locations/{{ location.slug }}/">All services in {{ location.name }}</a></li>
    <li><a href="/services/{{ service.slug }}/">{{ service.name }} across the Shuswap</a></li>
    {% for svc in all_services if svc.slug != service.slug %}
    <li><a href="/{{ svc.slug }}/{{ location.slug }}/">{{ svc.name }} in {{ location.name }}</a></li>
    {% endfor %}
  </ul>
</section>
```

---

### 1F — service-hub.html: Add Schema + Above-Fold CTA + FAQ

**File:** `build/templates/service-hub.html`  
**Changes:**

**1. Add to `{% block head_extra %}`:**
- BreadcrumbList JSON-LD: `Home > [Service Name]`
- Service JSON-LD (same structure as service-location but without location specifics)
- FAQPage JSON-LD (using service FAQs)

**2. Add above-fold CTA block immediately after the H1 (currently missing on service hubs):**
```html
<div class="hero-btns">
  <a href="{{ config.calendly_url }}" class="btn-primary" target="_blank" rel="noopener">Book Online — Free Quote</a>
  <a href="tel:{{ config.phone_raw }}" class="btn-outline">Call {{ config.phone }}</a>
</div>
```

**3. Add FAQ section at bottom (currently missing on service hubs):**
```html
<section class="content-section faq-section">
  <h2>Frequently Asked Questions — {{ service.name }}</h2>
  <div class="faq-list">
    {% for faq in faqs %}
    <div class="faq-item">
      <h3>{{ faq.q }}</h3>
      <p>{{ faq.a }}</p>
    </div>
    {% endfor %}
  </div>
</section>
```

**4. Target word count for service hubs after template changes + data rendering:** 1,000–1,200 words.

---

### 1G — location-hub.html: Add Schema + Above-Fold CTA + FAQ

**File:** `build/templates/location-hub.html`  
**Changes (mirror 1F pattern):**

**1. Add to `{% block head_extra %}`:**
- BreadcrumbList JSON-LD: `Home > [Location Name]`
- LocalBusiness JSON-LD with location-specific geo coordinates (add `lat` and `lng` fields to each location in locations.json)
- FAQPage JSON-LD

**2. Add above-fold CTA (currently missing).**

**3. Add FAQ section (currently missing).**

**4. Add `lat` and `lng` to each location in locations.json:**
```
salmon-arm:    50.6991, -119.2780
sorrento:      50.8763, -119.5240
tappen:        50.7856, -119.4190
blind-bay:     50.8428, -119.4610
sicamous:      50.8328, -118.9745
chase:         50.8186, -119.6798
enderby:       50.5497, -119.1396
armstrong:     50.4484, -119.1966
eagle-bay:     50.9176, -119.5840  (new — Session 2)
celista:       50.9890, -119.2820  (new — Session 2)
scotch-creek:  51.0362, -119.3340  (new — Session 2)
grindrod:      50.6140, -119.1200  (new — Session 2)
spallumcheen:  50.4780, -119.2150  (new — Session 2)
swansea-point: 50.8892, -118.9340  (new — Session 2)
```

---

### 1H — Session 1 Verification Gate

Run these checks before marking Session 1 complete:

```bash
cd ~/wagonwindows
python3 build/build.py
```

Expected output:
- `72 pages` (count unchanged — same URLs, enhanced content)
- `0 uniqueness warnings`

Then run the Python similarity check from the analysis phase:
```bash
python3 << 'EOF'
import re, json
from pathlib import Path
dist = Path.home() / "wagonwindows/dist"
def strip_html(h):
    h = re.sub(r'<(script|style)[^>]*>.*?</(script|style)>',' ',h,flags=re.DOTALL|re.IGNORECASE)
    return re.sub(r'<[^>]+>',' ',h)
def shingles(text, n=6):
    words = text.lower().split()
    return set(' '.join(words[i:i+n]) for i in range(len(words)-n+1))
def jaccard(a,b): return len(a&b)/len(a|b)
sa = shingles(strip_html((dist/"residential-window-cleaning/salmon-arm/index.html").read_text()))
arm = shingles(strip_html((dist/"residential-window-cleaning/armstrong/index.html").read_text()))
ext = shingles(strip_html((dist/"exterior-window-cleaning/salmon-arm/index.html").read_text()))
print(f"residential/salmon-arm vs residential/armstrong: {jaccard(sa,arm):.1%}")
print(f"residential/salmon-arm vs exterior/salmon-arm:   {jaccard(sa,ext):.1%}")
EOF
```

**Pass criteria:** Both scores below 20%. If above 20%, the service_notes blocks or process_steps need to be longer/more unique.

Also verify word counts:
```bash
python3 << 'EOF'
import re
from pathlib import Path
dist = Path.home() / "wagonwindows/dist"
def wordcount(f):
    h = f.read_text(errors='ignore')
    h = re.sub(r'<(script|style)[^>]*>.*?</(script|style)>',' ',h,flags=re.DOTALL|re.IGNORECASE)
    h = re.sub(r'<[^>]+>',' ',h)
    return len([w for w in h.split() if re.search(r'[a-zA-Z]',w)])
counts = sorted([(wordcount(f), str(f).replace(str(dist)+'/','').replace('/index.html','')) for f in dist.rglob('index.html')], key=lambda x:x[0])
under = [x for x in counts if x[0] < 1800]
print(f"Pages under 1800 words: {len(under)}")
for w,p in under: print(f"  {w} {p}")
avg = sum(x[0] for x in counts)/len(counts)
print(f"Overall average: {avg:.0f} words")
EOF
```
**Pass criteria:** No service-location pages under 1,800 words. No service/location hubs under 900 words.

---

## SESSION 2 — NEW LOCATIONS + GUTTER SERVICE + NEW PAGES
**Goal:** Add 6 locations + gutter cleaning service. Build new service×location pages and location hubs.  
**Files modified:** `build/data/locations.json`, `build/data/services.json`, `build/data/faqs.json`  
**Files created:** 0 (build.py loops handle it automatically)  
**Expected new pages:** +63 (6 location hubs + 7×6=42 new service-location + 14 gutter-location + 1 gutter hub)

---

### 2A — locations.json: Add 6 New Locations

Add the following 6 location objects to `build/data/locations.json`. Each must be complete — all fields matching the existing location schema. Copy the full field structure from an existing location and populate every field with location-specific content.

**Required fields per location (from existing schema):**
`slug`, `name`, `province`, `region`, `is_primary`, `population`, `postal_prefix`, `geography`, `climate_note`, `lake_proximity`, `lake_note`, `local_landmarks`, `neighborhoods`, `home_style_note`, `drive_time_from_primary_min`, `service_radius_note`, `local_fact_1`, `local_fact_2`, `local_fact_3`, `faq_local_q`, `faq_local_a`, `lat`, `lng`, `service_notes` (all 8 service keys including gutter-cleaning)

**New locations to add:**

```
1. eagle-bay
   name: Eagle Bay
   population: ~600
   drive_time: 25
   lat: 50.9176  lng: -119.5840
   lake_proximity: true
   postal_prefix: V0E
   geography: Waterfront community on the south shore of Shuswap Lake, 25km west of Salmon Arm between Tappen and Sorrento.
   Key facts: Premium vacation and retirement community. High-value lakefront homes. Many seasonal properties requiring pre-arrival cleans. Heavy Shuswap Lake mineral spray.

2. celista
   name: Celista
   population: ~400
   drive_time: 50
   lat: 50.9890  lng: -119.2820
   lake_proximity: true
   postal_prefix: V0E
   geography: North shore of Shuswap Lake, accessible via Squilax-Anglemont Road, ~50 min from Salmon Arm.
   Key facts: Vacation and rural residential community. Underserved market. Lake-view properties with significant mineral spray exposure. Seasonal demand concentrated April-September.

3. scotch-creek
   name: Scotch Creek
   population: ~500
   drive_time: 55
   lat: 51.0362  lng: -119.3340
   lake_proximity: true
   postal_prefix: V0E
   geography: Popular vacation community on the north shore of Shuswap Lake, accessible via Squilax-Anglemont Road.
   Key facts: Summer population spikes dramatically with vacation rental activity. Pre-season cleaning demand is highest in April-May. Many properties sit vacant in winter. Strong vacation rental market creates repeat commercial-adjacent demand.

4. grindrod
   name: Grindrod
   population: ~600
   drive_time: 40
   lat: 50.6140  lng: -119.1200
   lake_proximity: false
   postal_prefix: V0E
   geography: Small agricultural village on the Shuswap River, 10km north of Enderby. Easy to batch with Enderby service days.
   Key facts: Agricultural community. Heavy field dust and pollen. River-adjacent properties have some humidity considerations. Rural residential — larger window counts common on acreages.

5. spallumcheen
   name: Spallumcheen
   population: ~5,000 (rural municipality surrounding Armstrong)
   drive_time: 45
   lat: 50.4780  lng: -119.2150
   lake_proximity: false
   postal_prefix: V0E
   geography: Rural municipality surrounding Armstrong in the Spallumcheen Valley. Agricultural land with rural residential properties.
   Key facts: Large properties with outbuildings. Agricultural dust dominant. Strong dairy farming area — unique contamination profile (fine organic particulate). Batched efficiently with Armstrong service days.

6. swansea-point
   name: Swansea Point
   population: ~800
   drive_time: 45
   lat: 50.8892  lng: -118.9340
   lake_proximity: true
   postal_prefix: V0E
   geography: Lakefront community on Mara Lake near Sicamous. Premium recreational properties.
   Key facts: Adjacent to Sicamous, batched on same service days. Mara Lake mineral spray similar to Shuswap Lake properties. High-value recreational homes. Pre-season demand concentrated in May.
```

**Each new location also requires a full `service_notes` object** (same as 1C above) — 7 keys (existing services) + 1 for gutter-cleaning = 8 × ~130 words each = ~1,040 words of unique content per location × 6 locations = 6,240 words total writing required.

---

### 2B — services.json: Add Gutter Cleaning Service

Add the following complete service object to `build/data/services.json`:

```json
{
  "slug": "gutter-cleaning",
  "name": "Gutter Cleaning",
  "short_name": "Gutter Cleaning",
  "h1_template": "Gutter Cleaning in {location}",
  "meta_title_template": "Gutter Cleaning {location} | Wagon Windows | Prevent Water Damage",
  "meta_desc_template": "Professional gutter cleaning in {location}, BC. Debris removal, downspout flush, and condition report. Wagon Windows — locally owned, insured. Book online.",
  "primary_keyword_template": "gutter cleaning {location}",
  "secondary_keywords": [
    "eavestrough cleaning {location}",
    "gutter cleaning service {location}",
    "gutter clearing {location}",
    "downspout cleaning {location}",
    "eavestroughs cleaned {location} BC"
  ],
  "service_description": "Professional gutter and eavestrough cleaning for homes and businesses across the Shuswap. Debris removal, downspout flushing, and a condition report on every job. Blocked gutters cause water damage — cleaned gutters protect your foundation, fascia, and soffits.",
  "what_we_do_bullets": [
    "Full debris removal from all gutters and eavestroughs",
    "Downspout flush to confirm clear drainage",
    "Visual inspection of gutter joints, hangers, and pitch",
    "Condition report: any sagging, separated joints, or holes flagged",
    "Optional: photo documentation of before/after condition"
  ],
  "process_steps": [
    {"step": 1, "name": "Safety Setup", "description": "Ladder positioned safely at every section. We never lean over — ladder is repositioned along the roofline to maintain safe working position throughout. Ground inspection for soft spots or underground drainage points before setup."},
    {"step": 2, "name": "Debris Removal", "description": "All gutters cleared of leaves, compacted sediment, shingle grit, moss, and debris by hand and scoop. Material collected and removed — not blown onto your garden or driveway."},
    {"step": 3, "name": "Downspout Flush", "description": "Every downspout flushed with water from the top. If water backs up, the blockage is located and cleared. Blocked downspouts are the most common cause of gutter-related water damage — a flush confirms the system is actually draining."},
    {"step": 4, "name": "System Inspection", "description": "Visual inspection of gutter pitch (gutters must slope slightly toward downspouts — flat or reverse-pitched gutters pool), hanger integrity, joint seals, and any holes or separations. All findings reported."},
    {"step": 5, "name": "Fascia & Soffit Check", "description": "Quick check of fascia boards and soffits adjacent to gutters — staining or softness indicates water has already been overflowing. Noted in the condition report if found."},
    {"step": 6, "name": "Photo Documentation", "description": "Before/after photos of gutter condition taken and available on request. Condition report provided verbally on completion with key findings."}
  ],
  "base_price": 149,
  "base_price_large": 229,
  "price_note": "Standard home (single-storey) from $149. Two-storey or larger homes from $229. Quoted on-site for complex rooflines.",
  "schema_service_type": "HomeAndConstructionService",
  "icon": "🍂",
  "faq_count_minimum": 8,
  "min_word_count": 2500,
  "target_word_count": 3500,
  "differentiator": "We don't just scoop debris and leave — every job includes a downspout flush and a condition report. Most homeowners have never had anyone tell them the actual state of their gutters.",
  "common_problems": [
    "Blocked downspouts causing gutter overflow and fascia rot",
    "Compacted leaf sediment that blocks drainage even when gutters look clear from the ground",
    "Sagging gutters that pool water instead of draining",
    "Separated gutter joints leaking behind fascia",
    "Moss growth on shingles depositing into gutters repeatedly"
  ],
  "result_description": "Gutters clear of all debris. Downspouts confirmed draining. Pitch and hanger condition assessed. Any issues flagged with a recommendation. Foundation and fascia protected from water damage going into the next rainy season.",
  "booking_urgency": "Fall is the busiest time for gutter cleaning (after leaf-fall, before freeze). Book in October to secure a slot before freeze. Spring cleans also recommended after cottonwood season (June).",
  "page_intro_template": "If you need gutter cleaning in {location}, Wagon Windows provides full debris removal, downspout flushing, and a condition report on every job. Blocked gutters are one of the leading causes of avoidable water damage to Shuswap homes — below is exactly what's included, what it costs in {location}, and how to book."
}
```

---

### 2C — faqs.json: Add Gutter-Cleaning FAQs

**Add to `by_service`:**
```json
"gutter-cleaning": [
  {"q": "How often should gutters be cleaned in the Shuswap?", "a": "Twice per year for most Shuswap homes: once in late spring after cottonwood seed and pollen season (June), and once in late fall after leaf-drop (October–November). Properties with overhanging trees or near-roofline vegetation may need 3 cleanings per year."},
  {"q": "What's the difference between gutter cleaning and eavestrough cleaning?", "a": "Nothing — they're the same service. Gutters and eavestroughs are the same thing. 'Gutter' is the American term, 'eavestrough' is more common in BC and Canada."},
  {"q": "Can you clean gutters on a two-storey home?", "a": "Yes — we clean two-storey homes regularly. Two-storey homes are quoted at $229+ depending on roofline complexity and total linear footage. Safe ladder positioning is assessed on every section."},
  {"q": "Do you repair gutters as well as clean them?", "a": "We don't do gutter repairs — we clean and inspect. If we find damaged joints, sagging sections, or holes, we'll flag them and recommend a gutter repair specialist."},
  {"q": "Will you clean up the debris afterward?", "a": "Yes — all debris is collected and removed. We don't blow it onto your lawn or leave it in a pile. The material is bagged or removed in our vehicle."},
  {"q": "What if my downspout is underground?", "a": "We flush the downspout from the top. If it's blocked underground (a separate issue from the gutter itself), we'll let you know — underground drainage blockages are outside our scope but we'll describe where the blockage appears to be so you can call a plumber."},
  {"q": "How long does gutter cleaning take?", "a": "A standard single-storey home takes 45–90 minutes. Two-storey or larger homes typically 2–3 hours. Add-on to a window clean for the best value — we're already there with the ladders."},
  {"q": "Is it worth cleaning gutters every year?", "a": "In the Shuswap — yes. Cottonwood seeds, pine needles, and deciduous leaf debris accumulate quickly. Blocked gutters can cause fascia rot, soffit damage, and foundation water intrusion that costs thousands to fix. A $149–$229 annual clean is a straightforward investment."}
]
```

**Add to `by_location` for each of the 8 existing locations** — 1 gutter-specific FAQ per location (referencing local tree types, rainfall, or specific property considerations).

**Add gutter-cleaning entries to `by_service_location`** — 4 unique FAQs per location × 14 locations = 56 entries. These must be written as unique combinations.

---

### 2D — Session 2 Verification Gate

```bash
cd ~/wagonwindows && python3 build/build.py
```

**Expected output:**
- `Service × Location pages: 112 ✓` (14 locations × 8 services)
- `Location hubs: 14 ✓`
- `Service hubs: 8 ✓`
- Total pages: approximately 137 (72 prior + 63 new - 2 (build now generates 112 vs 56))

Wait — recalculate: homepage(1) + service-hubs(8) + location-hubs(14) + service-location(112) = 135 pages before seasonal/guides/blog.

Verify new location pages exist:
```bash
ls ~/wagonwindows/dist/gutter-cleaning/
ls ~/wagonwindows/dist/locations/eagle-bay/
ls ~/wagonwindows/dist/residential-window-cleaning/swansea-point/
```

Run uniqueness check on new pages — apply same <20% Jaccard threshold.

---

## SESSION 3 — BLOG INFRASTRUCTURE + 50 POSTS
**Goal:** Build blog template, blog index, and write all 50 blog posts into blog.json.  
**Files created:** `build/templates/blog-post.html`, `build/templates/blog-index.html`, `build/data/blog.json`  
**Files modified:** `build/build.py`  
**Expected new pages:** 51 (50 posts + 1 index)

---

### 3A — build/data/blog.json: Data Structure

Each blog post entry must have exactly these fields:

```json
{
  "slug": "url-safe-slug",
  "meta_title": "≤60 chars — Primary Keyword | Wagon Windows",
  "meta_desc": "140-155 chars — contains action word, benefit, local reference where relevant, no truncation.",
  "h1": "Full article title — can be longer than meta_title",
  "category": "one of: cost-pricing | frequency-timing | hard-water | diy-vs-pro | service-education | local-shuswap | commercial | troubleshooting",
  "tags": ["keyword1", "keyword2"],
  "published_date": "YYYY-MM-DD",
  "intro": "2-3 sentences. Hook. States the problem or question clearly. Does not start with 'In this article...'",
  "sections": [
    {
      "h2": "Section heading — contains keyword or clear benefit",
      "body": "300-500 words of substantive content. No filler. Each paragraph makes a discrete point.",
      "bullets": ["optional", "bullet", "list"]
    }
  ],
  "faqs": [
    {"q": "Question", "a": "Answer — 40-100 words"}
  ],
  "cta_text": "Specific CTA relevant to this post's topic — not generic.",
  "internal_links": [
    {"anchor": "link text", "url": "/relevant-internal-url/"}
  ],
  "word_count_target": 1400
}
```

**Publishing schedule:** 2 posts/day starting 2026-05-09. Set `published_date` in blog.json accordingly.

| Posts | Dates |
|-------|-------|
| Posts 1-2 | 2026-05-09 |
| Posts 3-4 | 2026-05-10 |
| Posts 5-6 | 2026-05-11 |
| ... | ... |
| Posts 49-50 | 2026-06-02 |

**Write ALL 50 posts in full.** Each post must hit 1,200–1,800 words, have 4-5 h2 sections, 3-4 FAQs, and at least 2 internal links to relevant service or location pages. No stubs. Every word final and publishable.

**The 50 posts (with target primary keyword):**

1. `window-cleaning-cost-salmon-arm` — "window cleaning cost Salmon Arm" — target: 1,400w
2. `window-cleaning-price-bc` — "window cleaning prices BC 2026" — target: 1,400w
3. `how-many-windows-does-my-house-have` — "how many windows does my house have" — target: 1,200w
4. `is-professional-window-cleaning-worth-it` — "is professional window cleaning worth it" — target: 1,500w
5. `window-cleaning-cost-per-window` — "window cleaning cost per window" — target: 1,200w
6. `gutter-cleaning-cost-shuswap` — "gutter cleaning cost Shuswap" — target: 1,400w
7. `screen-cleaning-cost-bc` — "screen cleaning cost BC" — target: 1,200w
8. `hard-water-stain-removal-cost` — "hard water stain removal cost" — target: 1,400w
9. `how-often-clean-windows-bc` — "how often clean windows BC" — target: 1,400w
10. `best-time-window-cleaning-shuswap` — "best time window cleaning Shuswap" — target: 1,500w
11. `spring-window-cleaning-guide` — "spring window cleaning guide" — target: 1,600w
12. `fall-window-cleaning-checklist` — "fall window cleaning checklist" — target: 1,500w
13. `before-winter-window-cleaning` — "window cleaning before winter BC" — target: 1,400w
14. `summer-window-cleaning-tips` — "summer window cleaning tips" — target: 1,300w
15. `how-often-clean-gutters-bc` — "how often clean gutters BC" — target: 1,400w
16. `what-causes-hard-water-stains-windows` — "what causes hard water stains windows" — target: 1,500w
17. `lake-spray-window-stains-shuswap` — "lake spray window stains Shuswap" — target: 1,400w
18. `calcium-deposits-glass-removal` — "calcium deposits glass removal" — target: 1,600w
19. `hard-water-stain-prevention-windows` — "prevent hard water stains windows" — target: 1,400w
20. `mineral-deposits-windows-bc` — "mineral deposits windows BC" — target: 1,300w
21. `are-hard-water-stains-permanent` — "are hard water stains on windows permanent" — target: 1,200w
22. `diy-window-cleaning-vs-professional` — "DIY window cleaning vs professional" — target: 1,600w
23. `why-hire-professional-window-cleaner` — "why hire professional window cleaner" — target: 1,500w
24. `window-cleaning-safety-second-story` — "how to clean second story windows safely" — target: 1,400w
25. `professional-window-cleaning-equipment` — "professional window cleaning equipment" — target: 1,300w
26. `squeegee-technique-professional` — "professional squeegee technique windows" — target: 1,200w
27. `what-is-window-track-cleaning` — "what is window track cleaning" — target: 1,400w
28. `window-screen-cleaning-guide` — "window screen cleaning guide" — target: 1,500w
29. `what-is-exterior-window-cleaning` — "exterior vs interior window cleaning" — target: 1,400w
30. `window-cleaning-process-step-by-step` — "professional window cleaning process" — target: 1,500w
31. `gutter-cleaning-what-to-expect` — "what to expect gutter cleaning" — target: 1,400w
32. `eco-friendly-window-cleaning-products` — "eco friendly window cleaning products BC" — target: 1,300w
33. `window-cleaning-insurance-bc` — "window cleaning insurance BC" — target: 1,200w
34. `commercial-window-cleaning-frequency` — "how often clean commercial windows" — target: 1,400w
35. `window-cleaning-salmon-arm-guide` — "window cleaning Salmon Arm guide" — target: 1,800w
36. `shuswap-lake-property-window-care` — "Shuswap Lake property window care" — target: 1,600w
37. `cottonwood-pollen-windows-bc` — "cottonwood pollen windows BC" — target: 1,400w
38. `agricultural-dust-windows-armstrong` — "window cleaning Armstrong BC dust" — target: 1,400w
39. `vacation-rental-window-cleaning-shuswap` — "vacation rental window cleaning Shuswap" — target: 1,500w
40. `lakefront-property-window-maintenance` — "lakefront property window maintenance" — target: 1,600w
41. `window-cleaning-salmon-arm-winter` — "window cleaning winter Salmon Arm" — target: 1,300w
42. `new-home-window-cleaning-shuswap` — "post construction window cleaning Shuswap" — target: 1,400w
43. `storefront-window-cleaning-benefits` — "storefront window cleaning benefits" — target: 1,500w
44. `commercial-window-cleaning-contract-bc` — "commercial window cleaning contract BC" — target: 1,400w
45. `first-impressions-clean-windows-business` — "clean windows business first impressions" — target: 1,500w
46. `restaurant-window-cleaning-guide` — "restaurant window cleaning BC" — target: 1,400w
47. `streaky-windows-after-cleaning` — "why are windows streaky after cleaning" — target: 1,300w
48. `foggy-windows-inside` — "windows foggy inside causes" — target: 1,400w
49. `windows-getting-dirty-too-fast` — "why do windows get dirty so fast" — target: 1,200w
50. `scratched-glass-window-cleaning` — "can window cleaning scratch glass" — target: 1,400w

---

### 3B — build/templates/blog-post.html: Template Spec

Create this template from scratch. Must include:

**`{% block head_extra %}`:**
- `Article` / `BlogPosting` JSON-LD schema:
```json
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "{{ post.h1 }}",
  "description": "{{ post.meta_desc }}",
  "datePublished": "{{ post.published_date }}",
  "dateModified": "{{ now }}",
  "author": {"@type": "Person", "name": "David Hanna"},
  "publisher": {"@type": "Organization", "name": "Wagon Windows", "url": "{{ config.site_url }}"},
  "mainEntityOfPage": {"@type": "WebPage", "@id": "{{ canonical }}"},
  "keywords": "{{ post.tags | join(', ') }}"
}
```
- FAQPage JSON-LD (from post.faqs)
- BreadcrumbList JSON-LD: `Home > Blog > [Post Title]`

**`{% block content %}`:**
```
BREADCRUMB nav: Home › Blog › [post title]

POST HERO:
  <h1>{{ post.h1 }}</h1>
  <div class="post-meta">Published {{ post.published_date }} · {{ post.category }}</div>
  <p class="post-intro">{{ post.intro }}</p>
  
  ABOVE-FOLD CTA (after intro, before first section):
  <div class="inline-cta">
    <p>Need professional window cleaning in the Shuswap?</p>
    <a href="{{ config.calendly_url }}" class="btn-primary">Book Online — Free Quote</a>
    <a href="tel:{{ config.phone_raw }}" class="btn-outline">{{ config.phone }}</a>
  </div>

CONTENT SECTIONS:
  {% for section in post.sections %}
  <section>
    <h2>{{ section.h2 }}</h2>
    <p>{{ section.body }}</p>
    {% if section.bullets %}
    <ul>{% for b in section.bullets %}<li>{{ b }}</li>{% endfor %}</ul>
    {% endif %}
  </section>
  {% endfor %}

FAQ SECTION:
  <section class="faq-section">
    <h2>Frequently Asked Questions</h2>
    {% for faq in post.faqs %}
    <div class="faq-item">
      <h3>{{ faq.q }}</h3>
      <p>{{ faq.a }}</p>
    </div>
    {% endfor %}
  </section>

POST CTA:
  <section class="page-cta">
    <h2>{{ post.cta_text }}</h2>
    <a href="{{ config.calendly_url }}" class="btn-primary">Book Online</a>
    <a href="tel:{{ config.phone_raw }}" class="btn-outline">{{ config.phone }}</a>
  </section>

RELATED LINKS:
  Internal links from post.internal_links array.

BACK TO BLOG link.
```

---

### 3C — build/templates/blog-index.html: Template Spec

Simple index page at `/blog/`:
- H1: "Window Cleaning Tips & Guides | Wagon Windows Blog"
- Posts listed in reverse chronological order (latest first)
- Each post: title link, category badge, published date, intro (first 120 chars)
- Schema: `Blog` / `CollectionPage` JSON-LD
- BreadcrumbList: `Home > Blog`
- Above-fold: brief intro paragraph + CTA

---

### 3D — build/build.py: Add Blog Build Functions

```python
def build_blog():
    blog_data = load('blog.json')
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
    blog_data = load('blog.json')
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
```

Add both function calls to `if __name__ == '__main__':` block after `build_seasonal()`.

---

### 3E — Session 3 Verification Gate

```bash
cd ~/wagonwindows && python3 build/build.py
```

Expected: blog posts count = 50, blog index exists at `dist/blog/index.html`.

Verify a sample post:
```bash
ls ~/wagonwindows/dist/blog/window-cleaning-cost-salmon-arm/
python3 -c "
import re; from pathlib import Path
f = Path.home()/'wagonwindows/dist/blog/window-cleaning-cost-salmon-arm/index.html'
h = f.read_text()
h2 = re.sub(r'<(script|style)[^>]*>.*?</(script|style)>','',h,flags=re.DOTALL)
h2 = re.sub(r'<[^>]+>',' ',h2)
print('words:', len([w for w in h2.split() if re.search(r'[a-zA-Z]',w)]))
# Check schema
import json
schemas = re.findall(r'application/ld\+json[^>]*>(.*?)</script>', h, re.DOTALL)
for s in schemas: 
    d = json.loads(s)
    print('schema type:', d.get('@type'))
"
```

**Pass criteria:** 1,200+ words. BlogPosting schema present. FAQPage schema present. BreadcrumbList schema present.

---

## SESSION 4 — SEASONAL + GUIDES + STANDALONE PAGES
**Goal:** Populate seasonal.json (4 entries), guides.json (4 entries), create standalone template, build pricing + service area pages.  
**Files created:** `build/templates/standalone.html`, `build/data/standalones.json`  
**Files modified:** `build/data/seasonal.json`, `build/data/guides.json`, `build/build.py`  
**Expected new pages:** 11 (4 seasonal + 4 guides + 1 pricing + 1 service-area + 1 blog-already-counted)

---

### 4A — seasonal.json: 4 Campaign Pages

Each seasonal entry:
```json
{
  "slug": "spring-window-cleaning-shuswap",
  "meta_title": "Spring Window Cleaning Shuswap | Wagon Windows | Book Now",
  "meta_desc": "Spring window cleaning in the Shuswap — pollen, winter grime, and mineral buildup removed. Book your spring clean with Wagon Windows before slots fill.",
  "h1": "Spring Window Cleaning in the Shuswap — Book Before Slots Fill",
  "season": "spring",
  "timing": "April – May",
  "urgency_note": "Spring slots typically fill by the first week of April. Book early.",
  "intro": "Spring is the most important clean of the year for Shuswap homes...",
  "why_this_season": "Cottonwood pollen, post-winter mineral buildup, lake spray from spring runoff...",
  "what_we_do": [...],
  "pricing_note": "...",
  "booking_cta": "Book Your Spring Clean",
  "faqs": [...]
}
```

Write full entries for:
1. `spring-window-cleaning-shuswap` — April–May — pollen/winter grime angle — 1,600w target
2. `summer-window-cleaning-shuswap` — July — dust/UV haze/vacation rental angle — 1,400w target
3. `fall-window-cleaning-shuswap` — Sept–Oct — leaf tannins/pre-winter angle — 1,600w target
4. `pre-season-vacation-home-clean` — March–April — seasonal property owners — 1,500w target

---

### 4B — guides.json: 4 Comprehensive Reference Guides

Each guide entry:
```json
{
  "slug": "complete-guide-window-cleaning-shuswap",
  "meta_title": "Complete Guide to Window Cleaning in the Shuswap | Wagon Windows",
  "meta_desc": "Everything Shuswap homeowners need to know about window cleaning — frequency, cost, hard water stains, seasonal timing, and when to DIY vs hire a pro.",
  "h1": "The Complete Guide to Window Cleaning in the Shuswap",
  "intro": "...",
  "sections": [...],
  "faqs": [...]
}
```

Write full entries for:
1. `complete-guide-window-cleaning-shuswap` — 3,000w comprehensive reference
2. `hard-water-stain-removal-guide` — 2,800w specialist guide
3. `gutter-cleaning-guide-bc` — 2,500w gutter-focused guide
4. `commercial-window-cleaning-guide` — 2,500w commercial-focused guide

---

### 4C — standalones.json + standalone.html: Pricing + Service Area Pages

**build/data/standalones.json:**
```json
[
  {
    "slug": "pricing",
    "url_path": "pricing",
    "meta_title": "Window Cleaning Prices | Wagon Windows | Salmon Arm & Shuswap",
    "meta_desc": "Transparent window cleaning prices for the Shuswap. Residential from $169, commercial from $119, gutter cleaning from $149. No hidden fees. Get a free quote.",
    "h1": "Window Cleaning Pricing — Shuswap Region",
    "template_key": "pricing",
    "intro": "...",
    "pricing_tables": [
      {
        "service": "Residential Window Cleaning",
        "tiers": [
          {"label": "Small home (up to 15 windows, exterior only)", "price": "$169"},
          {"label": "Medium home (15-25 windows, exterior only)", "price": "$229"},
          {"label": "Large home (25+ windows, exterior only)", "price": "$299+"},
          {"label": "Add interior cleaning", "price": "+$60–$90"},
          {"label": "Add screen cleaning", "price": "$4–$5 per screen"},
          {"label": "Add track cleaning", "price": "From $65"}
        ]
      },
      {
        "service": "Commercial Window Cleaning",
        "tiers": [
          {"label": "Small storefront (up to 5 panes)", "price": "From $119"},
          {"label": "Medium commercial (6-15 panes)", "price": "From $189"},
          {"label": "Recurring weekly/bi-weekly", "price": "Contracted rate — contact for quote"}
        ]
      },
      {
        "service": "Gutter Cleaning",
        "tiers": [
          {"label": "Single-storey home", "price": "From $149"},
          {"label": "Two-storey home", "price": "From $229"}
        ]
      },
      {
        "service": "Hard Water Stain Removal",
        "tiers": [
          {"label": "All sizes", "price": "Quoted on-site after assessment"}
        ]
      }
    ],
    "faqs": [...pricing-specific FAQs...]
  },
  {
    "slug": "service-area",
    "url_path": "service-area",
    "meta_title": "Window Cleaning Service Area | Wagon Windows | Salmon Arm & Shuswap",
    "meta_desc": "Wagon Windows serves Salmon Arm, Sorrento, Blind Bay, Sicamous, Chase, Enderby, Armstrong, and surrounding Shuswap communities. See all service areas.",
    "h1": "Our Window Cleaning Service Area — Salmon Arm & the Shuswap",
    "template_key": "service-area",
    "intro": "...",
    "locations_context": "full description of coverage area, drive times, batching logic",
    "faqs": [...]
  }
]
```

**build/templates/standalone.html:** Flexible template with `{% if page.template_key == 'pricing' %}` conditional blocks for the pricing table layout vs service-area layout. Both include: breadcrumb, h1, intro, above-fold CTA, relevant content, FAQ, final CTA. Schema: WebPage + FAQPage.

**build/build.py:** Add `build_standalones()` function similar to `build_guides()`.

---

### 4D — Session 4 Verification Gate

```bash
cd ~/wagonwindows && python3 build/build.py
```

Expected page count: ~197 (135 from S2 + 51 from S3 + 11 from S4 = 197).

Verify:
```bash
ls ~/wagonwindows/dist/pricing/
ls ~/wagonwindows/dist/service-area/
ls ~/wagonwindows/dist/seasonal/spring-window-cleaning-shuswap/
ls ~/wagonwindows/dist/guides/complete-guide-window-cleaning-shuswap/
```

---

## SESSION 5 — GBP POST LIBRARY + INDEXNOW + GSC PREP
**Goal:** Deliver 30 GBP posts + 30-day calendar. Build IndexNow submission script. Produce GSC priority list.  
**Files created:** `~/Desktop/gbp-30-day-library.md`, `~/wagonwindows/tools/indexnow-submit.py`, `~/Desktop/gsc-priority-submit.md`  
**No build.py changes.**

---

### 5A — GBP Post Library (30 posts)

**File:** `~/Desktop/gbp-30-day-library.md`

Write 30 complete GBP posts. Each post: title (for reference), body copy (150-300 words — GBP optimal), call to action, and optional photo note.

**Post types and distribution:**
- 8 × Before/After (descriptive — no actual photo needed, describes the result)
- 5 × Seasonal tip (month-specific)
- 4 × Service spotlight (one per: residential, gutter, hard water, commercial)
- 3 × Social proof (anonymous — "A homeowner in [location] recently..." format)
- 3 × Local community (reference Salmon Arm Wharf, IPE Armstrong, Sicamous marina, etc.)
- 3 × Education (tempered glass, cottonwood pollen, weep holes, etc.)
- 2 × Promotion (neighbourhood block pricing, referral reward)
- 2 × Behind the scenes (equipment, process, morning routine)

**30-day calendar:**
```
Day 1:  Before/After post #1
Day 2:  Seasonal tip — current month
Day 3:  Service spotlight — Residential
Day 4:  Before/After post #2
Day 5:  Education — cottonwood pollen
Day 6:  Before/After post #3
Day 7:  Local community — Salmon Arm Wharf
...
```
*(Full 30-day sequence included in the file)*

---

### 5B — IndexNow Submission Script

**File:** `~/wagonwindows/tools/indexnow-submit.py`

```python
#!/usr/bin/env python3
"""
IndexNow bulk URL submission — Wagon Windows
Usage: python3 tools/indexnow-submit.py
Submits all sitemap URLs to Bing/Yandex via IndexNow API.
Requires: INDEXNOW_KEY env var or key in tools/indexnow.key
"""
import json, urllib.request, xml.etree.ElementTree as ET
from pathlib import Path

KEY_FILE = Path(__file__).parent / "indexnow.key"
SITEMAP  = Path(__file__).parent.parent / "dist/sitemap.xml"
HOST     = "wagonwindow.com"
API_URL  = "https://api.indexnow.org/indexnow"

def get_key():
    if KEY_FILE.exists():
        return KEY_FILE.read_text().strip()
    raise FileNotFoundError("Create tools/indexnow.key with your IndexNow key")

def parse_sitemap(path):
    tree = ET.parse(path)
    ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    return [loc.text for loc in tree.findall('.//sm:loc', ns)]

def submit(urls, key):
    payload = json.dumps({
        "host": HOST,
        "key": key,
        "keyLocation": f"https://{HOST}/{key}.txt",
        "urlList": urls
    }).encode()
    req = urllib.request.Request(API_URL, data=payload,
          headers={"Content-Type": "application/json; charset=utf-8"}, method="POST")
    with urllib.request.urlopen(req) as r:
        print(f"Status: {r.status} | Submitted: {len(urls)} URLs")

if __name__ == '__main__':
    key  = get_key()
    urls = parse_sitemap(SITEMAP)
    # IndexNow max 10,000 per request — batch if needed
    for i in range(0, len(urls), 1000):
        submit(urls[i:i+1000], key)
```

**Also create `~/wagonwindows/dist/[KEY].txt`** — the key verification file IndexNow requires. The key value comes from registering at https://www.bing.com/indexnow. The agent building this session should note: the actual API submission requires the key to be live on the domain first. The script is built and ready — user runs it after deployment.

---

### 5C — GSC Priority Submit List

**File:** `~/Desktop/gsc-priority-submit.md`

List the top ~30 URLs to manually request indexing in GSC (in order of priority). These are the highest-conversion pages that should be indexed fastest.

Format:
```
PRIORITY 1 (submit immediately after deploy):
1. https://wagonwindow.com/
2. https://wagonwindow.com/services/residential-window-cleaning/
3. https://wagonwindow.com/services/gutter-cleaning/
4. https://wagonwindow.com/residential-window-cleaning/salmon-arm/
5. https://wagonwindow.com/gutter-cleaning/salmon-arm/
...all 8 Salmon Arm service pages...
...all 8 service hubs...
...pricing page...
...service area page...

PRIORITY 2 (submit within 48 hours):
...all 14 location hubs...
...top 10 blog posts by keyword volume...

PRIORITY 3 (submit within 1 week):
...remaining service-location pages by location size...
...remaining blog posts...
```

---

### 5D — Session 5 Verification Gate

- `~/Desktop/gbp-30-day-library.md` exists and contains 30 complete posts
- `~/wagonwindows/tools/indexnow-submit.py` exists and is syntactically valid (`python3 -m py_compile tools/indexnow-submit.py`)
- `~/Desktop/gsc-priority-submit.md` exists with ~30 URLs in priority order

---

## FINAL VERIFICATION — ALL SESSIONS COMPLETE

```bash
cd ~/wagonwindows && python3 build/build.py
```

**Expected final output:**
```
✓ Complete — ~197 pages | 0 uniqueness warnings
```

Run full similarity check across all service-location pages. All pairs must score below 20% Jaccard.

Run word count check. No service-location page below 1,800 words. Blog posts average 1,300+ words.

Confirm sitemap has ~197 URLs. Confirm robots.txt points to sitemap.

**Deploy:** `git add -A && git commit -m "Site overhaul: 197 pages, schema, blog, gutter service" && git push`

After deploy confirm live at wagonwindow.com, then run IndexNow script and execute GSC manual requests per priority list.

---

## SUMMARY TABLE

| Session | Primary Work | New Pages | Key Output Files |
|---------|-------------|-----------|-----------------|
| S1 | Template + schema overhaul, uniqueness upgrade | 0 new (72 rebuilt) | base.html, service-location.html, service-hub.html, location-hub.html, services.json, locations.json, faqs.json |
| S2 | 6 new locations + gutter service | +63 | locations.json (6 entries), services.json (1 entry), faqs.json (gutter FAQs) |
| S3 | Blog infrastructure + 50 posts | +51 | blog-post.html, blog-index.html, blog.json, build.py |
| S4 | Seasonal, guides, pricing, service-area | +11 | seasonal.json, guides.json, standalones.json, standalone.html, build.py |
| S5 | GBP library, IndexNow, GSC prep | 0 | gbp-30-day-library.md, indexnow-submit.py, gsc-priority-submit.md |
| **Total** | | **~125 new pages** | |
