# GPU Monitor Design System

## 0. Research Log

- Embedded refs: shortlisted `linear.app`, `supabase`, `sentry` → picked `linear.app.md` + `taste-skill.md` because the brief calls for a professional, dark, data-dense dashboard; Linear's near-black canvas, translucent surfaces, and violet accent fit an internal ops tool without looking generic.
- Lazyweb: skipped — no network tool needed; direction is clear from references.
- Imagen drafts: skipped — dashboard UI, no marketing hero imagery required.

## 1. Atmosphere & Identity

A quiet command center for GPU fleet health. The signature is **precision in darkness**: information emerges from a near-black canvas through subtle luminance steps, with a single violet accent reserved for live, healthy states. Offline servers and warnings cut through with deliberate color. The interface feels engineered — tight grids, mono numerals, and generous internal padding inside restrained cards.

## 2. Color

### Palette

| Role | Token | Light | Dark | Usage |
|------|-------|-------|------|-------|
| Surface/page | --surface-page | #FFFFFF | #08090a | Main background |
| Surface/panel | --surface-panel | #F8F8F8 | #0f1011 | Header, sidebar |
| Surface/card | --surface-card | #FFFFFF | rgba(255,255,255,0.03) | Server cards |
| Surface/elevated | --surface-elevated | #FFFFFF | #191a1b | Dropdowns, hover |
| Text/primary | --text-primary | #0A0A0A | #f7f8f8 | Headlines, numbers |
| Text/secondary | --text-secondary | #6B6B6B | #d0d6e0 | Body, labels |
| Text/tertiary | --text-tertiary | #9B9B9B | #8a8f98 | Metadata |
| Text/muted | --text-muted | #9B9B9B | #62666d | Timestamps, disabled |
| Border/default | --border-default | #E5E5E5 | rgba(255,255,255,0.08) | Card borders |
| Border/subtle | --border-subtle | #F0F0F0 | rgba(255,255,255,0.05) | Dividers |
| Accent/primary | --accent-primary | #2563EB | #5e6ad2 | Healthy status, links |
| Accent/bright | --accent-bright | #3B82F6 | #7170ff | Hover, focus |
| Accent/hover | --accent-hover | #1D4ED8 | #828fff | Accent hover |
| Status/success | --status-success | #16A34A | #22c55e | Online, healthy GPU |
| Status/warning | --status-warning | #D97706 | #f59e0b | Disk ≥ 90% |
| Status/error | --status-error | #DC2626 | #ef4444 | Offline / error |
| Status/info | --status-info | #2563EB | #3b82f6 | Info badges |

### Rules
- The page is dark-mode-native. Light mode is not a target for this internal tool.
- Accent violet is used ONLY for online/healthy indicators, focus rings, and primary links.
- Borders are semi-transparent white; never solid gray borders on dark surfaces.

## 3. Typography

### Scale

| Level | Size | Weight | Line Height | Tracking | Usage |
|-------|------|--------|-------------|----------|-------|
| Page title | 28px / 1.75rem | 600 | 1.2 | -0.02em | Header title |
| Card title | 18px / 1.125rem | 590 | 1.3 | -0.01em | Server name |
| Section label | 12px / 0.75rem | 500 | 1.4 | 0.04em | Uppercase group labels |
| Body | 14px / 0.875rem | 400 | 1.5 | 0 | Default text |
| Body/mono | 14px / 0.875rem | 400 | 1.5 | 0 | Metrics, percentages |
| Caption | 12px / 0.75rem | 400 | 1.4 | 0 | Metadata, error text |

### Font Stack
- Primary: `Inter, system-ui, -apple-system, sans-serif`
- Mono: `JetBrains Mono, ui-monospace, SF Mono, monospace`

### Rules
- All numeric metrics use the mono stack.
- Max 2 font families.
- Body text never below 14px.

## 4. Spacing & Layout

### Base Unit

4px base unit.

| Token | Value | Usage |
|-------|-------|-------|
| --space-1 | 4px | Tight inline |
| --space-2 | 8px | Icon-to-label |
| --space-3 | 12px | Compact card padding |
| --space-4 | 16px | Standard card padding |
| --space-6 | 24px | Section gaps |
| --space-8 | 32px | Page gutters |
| --space-10 | 40px | Major section breaks |

### Grid
- Max content width: 1400px.
- Server cards: responsive grid, `repeat(auto-fit, minmax(min(20rem, 100%), 1fr))`.
- Breakpoints: sm 640px, md 768px, lg 1024px, xl 1280px.

### Rules
- Page shell: fixed header, scrolling body.
- Cards are the primary content container.
- No horizontal scroll of primary content at 375px.

## 5. Components

### ServerCard
- **Structure**: card container > header (name + status badge) > metrics grid (CPU, memory) > GPU list > disk list.
- **Variants**: online, offline, warning.
- **Spacing**: --space-4 padding, --space-3 gap between sections.
- **States**: default, hover (slight bg luminance increase).
- **Accessibility**: role="article", aria-label includes server name and status.

### StatusBadge
- **Structure**: inline flex pill with dot + label.
- **Variants**: online (green dot), offline (red dot), warning (amber dot).
- **Spacing**: --space-1 dot margin, --space-2 horizontal padding.
- **States**: static.

### GpuBar
- **Structure**: label row + horizontal progress bar + value.
- **Variants**: default, warning (≥ 90% turns amber), error (offline).
- **Spacing**: --space-2 between label and bar, --space-1 bar height.
- **Motion**: width transition on value change (150ms ease-out).

### MetricRow
- **Structure**: label + mono value pair.
- **Variants**: default, emphasis.
- **Spacing**: --space-2 between label and value.

### DiskRow
- **Structure**: mountpoint + capacity + usage bar + warning marker.
- **Variants**: default, warning (usage ≥ 90%).

### PageHeader
- **Structure**: logo/title + last-updated timestamp + refresh button.
- **States**: refresh button hover/active, loading spinner during fetch.

## 6. Motion & Interaction

### Timing

| Type | Duration | Easing | Usage |
|------|----------|--------|-------|
| Micro | 150ms | ease-out | Progress bars, badge state |
| Standard | 200ms | ease-in-out | Card hover, button press |
| Emphasis | 300ms | cubic-bezier(0.16, 1, 0.3, 1) | Card mount stagger |

### Rules
- Animate only `transform` and `opacity`.
- Progress bars animate width on data update.
- Cards stagger-in on initial load.
- Respect `prefers-reduced-motion`: disable stagger and width transitions.

## 7. Depth & Surface

### Strategy
Tonal-shift + subtle borders. Cards sit on `rgba(255,255,255,0.03)` with `rgba(255,255,255,0.08)` border. Hover raises luminance to `rgba(255,255,255,0.05)`.

| Level | Treatment | Use |
|-------|-----------|-----|
| Flat | #08090a bg | Page background |
| Surface | rgba(255,255,255,0.03) + 1px rgba(255,255,255,0.08) border | Cards |
| Elevated | rgba(255,255,255,0.05) | Card hover |
| Header | #0f1011 | Top bar |

## 8. Accessibility Constraints & Accepted Debt

### Constraints
- WCAG 2.2 AA: body contrast ≥ 4.5:1, large text ≥ 3:1.
- Visible focus rings on all interactive elements.
- Respect `prefers-reduced-motion`.
- Semantic landmarks: `<header>`, `<main>`, `<article>` for cards.

### Accepted Debt
| Item | Location | Why accepted | Owner / Exit |
|------|----------|--------------|--------------|
| No light mode | entire app | Internal tool, brief targets dark professional look only | Add if user requests |
| Auto-refresh without pause | PageHeader | Ops dashboard expectation; can be added later | Add pause button if requested |
