# Webapp Revision Log v0.7 — UI and Network Integration (Refined)

## Actors Explorer (Institutional Actor View)
- **Actor Inventory preserved**: Yes. Filters and search are functional.
- **Relationship Map (SVG Graph)**:
  - Renamed to "Institutional Actor View".
  - Added methodological subtitle and persistent caveats.
  - Implemented edge differentiation (color/dash) and interactive tooltips.
  - Standardized node labels (SSA, WHO/OMS, Aduanas).
  - Added view selector: Actor–Instrument, Provision–IHR Traceability, Gap Exposure.
  - Highlighted "Weak Anchors" in Gap Exposure view.
- **Network Metrics tab**: Displays Top Actors and Top Legal Instruments.
- **Analytical Cards**: Added Most Legally Salient Actor, Most Central Legal Instrument, and Most Frequent Gap Type cards below the graph.

## Capacity Brief (Capacity-Building Entry Points)
- **Strategic Review Priorities**: Renamed and restructured with "Why it matters", "Domestic Layer", "International Layer", and "Suggested Validation" fields.
- **Capacity-Building Entry Points**: Structured with collapsible accordion sections (Purpose, Audience, Evidence Base, etc.).
- **Evidence Basis Card**: Displays specific corpus metrics (18 instruments, 110 provisions, 45 IHR obligations, etc.).
- **Interactive UI**: Added action buttons (Download Brief, Export Table) and target audience chips.
- **Caveats**: Added provisional warnings for PABS and refined global disclaimer text.

## Global Design
- **Visual Language**: Light aesthetic, navy/slate palette, consistent card and table styling.
- **Consistency**: Applied across all core pages.

## Build
- **npm run build result**: Success.
- **Warnings/Errors**: Standard Vite chunk size warnings.
- **Remaining known issues**: None.

**Important Note**: No legal data, mapping tables, or analytical scores were modified during this UI revision.
