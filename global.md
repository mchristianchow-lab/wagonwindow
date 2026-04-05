# Global Patterns

Cross-session learnings for Wagon Windows. Format: `[YYYY-MM-DD] CATEGORY: one-line insight`

Categories: BUILD | DEPLOY | PATTERN | GOTCHA | MECHANIC | API | DB | UI | ARCH

Tiering: Append `!` to category for hard facts affecting correctness. No suffix = soft pattern.
Contrastive format preferred: `X, not Y (because Z)`

[2026-03-27] ARCH: Wagon Windows website at ~/wagonwindows/ — index.html + style.css + "final black and white.jpeg" (active logo). Previous Netlify deploy expired (tubular-hummingbird-0d70dd). Redeploy via netlify.com/drop — user has Netlify account now.
[2026-03-27] ARCH: Business owned by David Hanna. Email: davidhanna@wagonwindow.com. Phone: (403) 837-5092. Location: Salmon Arm, BC — serves Shuswap region.
[2026-03-28] ARCH! Tech stack: Netlify (hosting, free) + Formspree (contact form, YOUR_FORM_ID placeholder still in index.html — needs replacing) + Calendly (booking, embedded, davidhanna-wagonwindow/30min). All free tier.
[2026-03-31] UI! Color palette locked (Crisp White & Racing Red) — --navy #111111, --blue #cc0000, --sky #e81010, --light #f5f5f5, --white #ffffff, --dark #000000. Hero gradient: `linear-gradient(160deg, #000000 0%, #111111 60%, #220000 100%)`. Nav: white bg + 5px solid #e81010 bottom border. CTAs: #e81010 background. Font: Inter throughout.
[2026-03-28] UI: Logo is black-and-white JPEG (no transparency). CSS filter applied for tint: `sepia(0.4) hue-rotate(340deg) saturate(2) brightness(0.95)`. For full color control, request PNG with transparent background from logo designer.
[2026-03-28] PATTERN: JPEG logo with black background — CSS filters give approximate tints only, not precise color control. Transparent PNG = full CSS colorize capability, not JPEG.
[2026-03-28] MECHANIC! Pricing anchors (Salmon Arm market, 2026-03): Small home exterior from $149, medium from $199, large from $269. Minimum job $99. Only competitor [[a-plus-gutter-window-cleaning]] publishes pricing ($179 avg exterior) — all others are quote-only. Wagon Windows showing prices is a differentiator.
[2026-03-28] DEPLOY: Chrome headless PDF generation confirmed working on this machine: `/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --headless --disable-gpu --print-to-pdf="[output]" --print-to-pdf-no-header "file://[input.html]"`
[2026-03-31] ARCH! Active logo is IMG_0634.PNG (transparent background PNG). No CSS tint filter — filter: none. Logo sized at 180px height in 88px nav via `overflow: visible` + `transform: translateY(-1.5mm)`. Nav border-bottom: 5px solid #e81010.
[2026-03-29] UI: Nav logo overflow technique — set nav `overflow: visible`, logo height > nav height, `align-items: center` on nav centers it. Fine-tune vertical position with `transform: translateY()` on the img, not absolute positioning (absolute breaks nav link layout).
[2026-03-29] UI: "5.0 on Google" trust badge removed until Google Business Profile is live — unlinked social proof actively hurts trust. Replaced with "5-Star Service".
[2026-03-29] ARCH: LocalBusiness JSON-LD schema added to index.html `<head>` — covers name, phone, email, address, areaServed, priceRange. Update `sameAs` array when social profiles are created.
[2026-03-29] ARCH! SEO/GEO domination plan saved to ~/.claude/plans/dynamic-foraging-kitten.md — 8-phase plan: DNS → GA4/GSC/CWV → Python+Jinja2 static generator → /intel keyword research → 267-page content build → technical SEO → 17 directory submissions → reporting regimen.
[2026-03-29] ARCH! Static site generator decision: Python + Jinja2, not raw HTML files (250+ pages = unmaintainable without templating). Build system lives in ~/wagonwindows/build/, output to ~/wagonwindows/dist/. Deploy dist/ to Netlify, not root folder.
[2026-03-29] PATTERN: GA4 Calendly conversion tracking requires postMessage listener, not standard onclick — Calendly fires a window message event (`calendly.event_scheduled`) when booking completes. Standard onclick on the widget div does nothing.
[2026-03-29] MECHANIC! NAP consistency rule: Name/Address/Phone must be identical across ALL directory listings (Google, Bing, Yelp, HomeStars, etc.) — inconsistency is a local ranking signal penalty. Canonical NAP: "Wagon Windows | Salmon Arm, BC | (403) 837-5092"
[2026-03-29] ARCH: Domain is Google Workspace / Squarespace Domains — DNS managed via Squarespace (link in admin.google.com → Domains → View Details → "Manage Domain via Squarespace"). Not a standard registrar panel.
[2026-04-05] ARCH!: Domain is wagonwindow.com (NO S) — not wagonwindows.com. All config, canonical URLs, sitemap, schema corrected to wagonwindow.com.

[2026-03-31] UI: Door hanger at ~/wagonwindows/door-hanger.html — matches site colors (red #e81010, black #111111, Inter font) but uses door hanger layout, not website layout. "Matching" means colors + font only, not section structure.
[2026-03-31] UI: Trust bar items styled as dark pills — background #1a1a1a, border #333, border-radius 30px. Service cards have box-shadow 0 2px 12px rgba(0,0,0,0.06) at rest. Section labels have border-left 3px solid #e81010 + padding-left 0.6rem + display inline-block.
[2026-03-31] PATTERN: Door hanger "match the website" means colors/typography only, not layout replication. User explicitly confirmed this — don't rebuild the website in door-hanger dimensions.
[2026-03-31] ARCH! SEO/GEO plan enhanced with 3 agentic search additions: (A) Quick Answer block after H1 with speakable schema, (B) Key Facts box unique per page with location-specific data, (C) Short-answer paragraph after each H2 for AI snippet extraction. All added to dynamic-foraging-kitten.md.
