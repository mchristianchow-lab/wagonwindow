# Field Tool — Patterns & Learnings

Project-specific lessons for `field-tool.html` — the iOS PWA field quoting tool.

---

[2026-05-21] ARCH: field-tool.html is a standalone single-file PWA — all state, pricing constants, lead storage, and templates live in one file. No build step. Served from Netlify alongside the main site.

[2026-05-21] MECHANIC!: gutters stored as dollar amount (0 = off, 189+ = on), NOT a boolean — all state reset functions (startQuote, selectPackage ×3, resumeSession) must use `gutters: 0` not `gutters: false`. Wrong type silently breaks gutter pricing.

[2026-05-21] MECHANIC!: addonsContext state variable ('packages'|'custom') controls the dual-purpose add-ons screen — set to 'packages' before goScreen('scr-addons') for the package flow, or 'custom' for the manual quote flow. Determines whether forward nav goes to scr-packages or scr-quote.

[2026-05-21] MECHANIC!: pkgCalcFull(type, screens, tracks) computes grand total including ALL current add-ons (gutters, hardwater, travel, largewindow) — packages show complete grand total, not base price. Add-ons screen appears before packages screen so the displayed total is already final.

[2026-05-21] GOTCHA!: Unicode smart quotes (U+2018/U+2019/U+201C/U+201D) used as JS string delimiters break the entire script silently — browser shows blank screen, no console error until you run node --check. Fix: global replace of all 4 curly quote variants at the top of any string-processing function.

[2026-05-21] GOTCHA!: window.location.href = 'mailto:...' silently fails in iOS PWA mode (apple-mobile-web-app-capable: yes). Must use anchor element click: create <a>, set href, appendChild, click(), removeChild.

[2026-05-21] GOTCHA!: localStorage is wiped when user taps "Clear Website Data" in Safari Settings. All leads gone permanently. Mitigated by Backup/Restore feature (exportLeads/importLeads) using navigator.share for JSON file on iOS, data URI download on desktop.

[2026-05-21] PATTERN: Phone formatting uses (250) 555-0123 style. Apply formatPhone(this) via oninput on any phone input. Strips non-digits, formats progressively as user types.

[2026-05-21] GOTCHA!: lead.panes doesn't exist in the lead object — pane count must be computed from lead.params.breakdown (sum of regular + large + french values).

[2026-05-27] ARCH!: Commercial tool JS uses specific element IDs — cv-std/cv-lrg/cv-spc (counter values), cf-screens/cf-tracks/cf-hardwater (fee counters), pw-toggle/pw-detail (power wash), fee-travel/travel-fee-display (travel), c-biz/c-contact/c-phone/c-email/c-address (info form), cq-total/cq-range/comm-breakdown (quote display). Always read HTML before writing commercial JS.

[2026-05-28] MECHANIC!: Residential pricing — $169 base (ext/int), $219 base (both). Per-pane tiers: T1 (31-50) $2.50/$3.50, T2 (51-70) $3.50/$4.00, T3 (71-99) $4.00/$4.50, overflow $4.00/$7.00. Interior-only priced same as exterior for now. Rate ≈ $4/pane at scale.

[2026-05-28] MECHANIC!: Unit pricing for strata — corner unit (20 reg panes + 4 door panes = 24 total) = $100. Regular unit (16 reg panes + 4 door panes = 20 total) = $80. Rate ≈ $4/pane. All-inclusive: interior glass + screens + tracks.

[2026-05-28] ARCH: Unit multiplier feature added to both residential (scr-count) and commercial (scr-comm-windows) screens. State: resUnitRows[] = [{name, units, reg, lrg, fre}], commUnitRows[] = [{name, units, std, lrg, spc}]. Apply buttons push totals into state.breakdown (res) or commState.std/lrg/spc (comm). Both reset in startQuote() and startCommercial().

[2026-05-28] GOTCHA: Sony ILME-FX30 files appear as .JPG but are TIFF-based RAW — sips and ImageMagick cannot process them. Fix: `exiftool -b -JpgFromRaw "$f" > output.jpg` extracts the full embedded JPEG. Requires `brew install exiftool`.

[2026-06-04] GOTCHA!: calcCommQuote() calls commSaveState() before computing — directly mutating commState.travelKm, commState.fieldDiscount is stomped by commSaveState() reading DOM inputs (#fee-travel, #comm-discount). Must set BOTH commState AND the DOM element. commState.afterHours is safe (set via onchange, not read by commSaveState).

[2026-06-04] GOTCHA!: Playwright strict mode throws if a locator matches >1 element — scope to parent container (#scr-complete .topbar-action) for buttons that appear on multiple screens. Never assume a text selector is unique across screens.

[2026-06-04] PATTERN: In mega-audit scripts (150+ variables), section-prefix all variable names — `commBreakdown` not `breakdown` when a second breakdown appears in a later section. Collisions cause SyntaxError at parse time, not runtime.

[2026-06-04] GOTCHA!: Price string checks like `!str.includes('0')` fail on valid prices containing zero (e.g. $230, $300). Use parseFloat(str.replace(/[^0-9.]/g,'')) > 0 instead.

[2026-06-04] GOTCHA!: Min-job floor ($169) masks commercial pricing feature differences in tests — if base calculation is below $169, stories multiplier / after-hours / travel all produce the same total. Use std=30+ (base $180) for feature comparison tests.

[2026-06-04] MECHANIC!: 7 bugs found and fixed in field tool (2026-06-04): showCommCustomer() overlay wiring, loadLeadQuote() commercial guard, saveCommLead() date_pref persistence, phone display truthiness, revenue bar summing l.total for commercial leads, waiver URLs for all lead types, saveSession() skipping scr-comm-* screens. 242-check mega-audit clean after fixes.
