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
