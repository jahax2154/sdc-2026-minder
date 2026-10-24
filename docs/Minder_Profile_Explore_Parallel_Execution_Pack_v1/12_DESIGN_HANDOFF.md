# Design assets and frontend handoff

## 1. What Junhong supplies

Suggested path: `docs/design/product/` with separate `minder/`, `mindbots/` and `profile-explore/` folders where useful. These are proposed destinations, not claims that files already exist.

Supply the actual preferred HTML and its CSS/JS/images/fonts, keeping relative paths intact. Add screenshots for visual comparison, preferably desktop and phone. Include Replit source/exports only for the selected useful elements; a screenshot or published URL is not an editable source tree.

Use fictional content for committed screenshots/fixtures. Do not include keys, private chats/CVs, account details, dependency directories, databases or another repository's `.git`.

## 2. DESIGN_BRIEF.md template

```text
Primary visual source: [relative path to preferred HTML and assets]
Minder reference: [path or pending]
Mindbots reference: [path or pending]
Profile/Explore reference: [path or existing shared design]
Replit elements to reuse: [specific components or none]
Preserve: [important layout, type, color, spacing and navigation choices]
Change: [specific changes or none]
Responsive behavior: preserve readable forms, chat and proposal review on phones.
Behavior authority: new product context plus existing Minder/Mindbots context.
API authority: A's bound contracts and C's actual frontend export, tied to SHAs.
If a visual contains unsupported behavior, preserve its design intent but expose
the real capability/unavailable state. Do not fabricate backend functionality.
```

## 3. Minimal useful UI state coverage

F can derive missing states from the chosen design system; Junhong need not draw every case.

| Feature | States that must work |
| --- | --- |
| Profile | Partial/complete editing, saving/saved/error, evidence unknowns, stale edit, supported document processing/correction |
| Career Match | Missing inputs, supported results, personal-only/partial market explanations, role detail, feedback/reset, selection |
| Tasks | No tasks, list/filter, edit/pending/saved, completion/undo, stale conflict |
| Roadmap & Skills | No direction, actual plan, sourced requirement, unassessed/gap distinction, resource/task relationships |
| Progress | Empty denominator, actual counts/history, selected-plan changes, refreshed undo |
| News & Trends | No source, real items, dated cached content, filters/saved state, unavailable forecast |
| Minder | Empty/history, sending, grounded answer/source detail, insufficient evidence, provider failure |
| Mindbots | No events, real activity, proposal differences, approve/reject/stale, persisted success/failure, actual worker status |

Prefer a clear next action and a short explanation over exposing every internal metric. Keep detailed sources accessible without filling every card with engineering fields. Internal ranking matrices remain hidden.

## 4. Backend and frontend synchronization

Design references control appearance; product context controls behavior; actual contracts control HTTP communication. None replaces the others. A screenshot button is not evidence that an endpoint exists.

F wires actual APIs and reports missing operations to the owning backend lane. Development fixtures are useful for layout while an endpoint is unfinished, but final acceptance must distinguish them from real data/provider behavior.

There is no required Figma conversion. Do not spend this implementation window moving a usable HTML design between tools unless Junhong specifically requests it.
