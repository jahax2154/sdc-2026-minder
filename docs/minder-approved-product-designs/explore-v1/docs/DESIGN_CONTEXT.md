# Minder Explore — final design context

Version 2.0 · 24 October 2026 · approved direction with sidebar page separation

## 1. Binding product decisions

Explore is an expandable sidebar group. Clicking the parent toggles its child links; it does not open a dashboard. Careers and My Path are distinct pages with their own title, breadcrumb, local navigation, and content region. Remove the previous top-level horizontal Careers/My Path selector entirely.

Careers has the rounded horizontal bar: **Matches / Compare / Outlook**.

My Path has the rounded horizontal bar: **Next steps / Roadmap / Skills / Progress**.

The user briefly considered renaming Next steps to Tasks, then explicitly said no change was needed. Retain Next steps. The My tasks sidebar shortcut opens Next steps. The My roadmap shortcut opens Roadmap.

Show one selected feature at a time. Detail routes retain the parent tab's active state and offer a back link. The user should understand both where they are and what they can do next without interpreting a dashboard.

## 2. Visual source and precedence

Use the supplied profile, chat, Mindbot, and overview screenshots for brand and component styling only. Do not copy their module hierarchy, dashboard composition, KPI counts, or market claims.

Precedence: latest user navigation decision → frontend logical context → canonical CSS/HTML → screenshots in references/final → original style references. The earlier generated page images with a top Careers/My Path selector are not current implementation references.

The final reference images are browser renders of this package. Their layout and content therefore correspond to runnable source. For capture only, `?reference=1` applies 85% browser-content scale to fit the desktop composition into the available screenshot viewport; normal browsing is unscaled.

## 3. Design tokens

| Token | Value | Purpose |
| --- | --- | --- |
| --paper | #ffffff | Main background and panels |
| --sidebar | #fafbf9 | Quiet navigation surface |
| --ink | #111815 | Titles and primary content |
| --muted | #727984 | Secondary text |
| --forest | #36584b | Primary actions and intentional emphasis |
| --forest-hover | #284438 | Hovered primary action |
| --sage | #edf2ed | Selected tabs, callouts, current milestone |
| --sage-deep | #dfe8df | Avatar and quiet emphasis |
| --line | #e5e8e6 | Borders and dividers |
| --radius | 12px | Primary panels |
| --sidebar-w | 248px desktop; 220px compact desktop | Shared app sidebar |
| --font | Inter, system UI, Segoe UI, Arial, sans-serif | No required external font download |

Inter is a preference when installed, not a bundled font. No exact source font or official token file was supplied; do not claim these inferred values are extracted official brand tokens.

Desktop sizes: page title 44px, section title 28px, body 15px, local tab 14px, support copy 12–13px. Heading weight 650–750. Page title tracking is slightly tight; small eyebrow labels use tracked uppercase. Maintain readable contrast; do not make essential meaning depend on a faint border or green color alone.

## 4. Shared frame and layout

The sidebar contains the Minder mark, New conversation, YOUR SPACE group, expanded Explore with indented Careers and My Path, remaining app destinations, KEEP MOVING shortcuts, a small encouragement note, and the fictional account.

The selected child link has a pale sage background and forest text; the parent Explore stays visually grouped. The parent uses aria-expanded and aria-controls. Preserve the user's choice to collapse it.

The top bar is 73px high with breadcrumb, contextual local search, Ask Minder, and avatar. Main desktop padding is 31px top and 48px horizontally; maximum content width is 1510px. The page title sits above a single centered horizontal capsule bar, maximum width 930px. That bar remains stable within each page.

Use 1px borders, 12px panels, 8px controls, and fully rounded segmented bars. Minimal shadow is reserved for transient overlays. The normal content uses no decorative gradients, stock imagery, hero illustrations, or ornamental charts.

## 5. Component inventory

| Component | Contract |
| --- | --- |
| Explore group | Toggle parent; two navigable child pages; persist expansion preference |
| Local capsule navigation | Exactly 3 Careers or 4 My Path choices; active page marked with aria-current |
| Page heading | Module name plus one concise purpose statement |
| Primary button | Forest fill, white text, clear verb; one dominant action in focused work areas |
| Secondary button | White with thin outline; supporting choice |
| Inline link | Forest text, optional outline arrow; deeper context or detail |
| Context callout | Soft sage background, one explanation plus relevant action |
| Career recommendation | One leading role, brief rationale, index meaning, View career action |
| Comparison | Consistent criteria across two roles; table may scroll on narrow screens |
| Task focus | Current milestone, one recommended task, effort and linked skill |
| Task row | Explicit complete/undo control, task title, effort, detail link |
| Milestone sequence | Vertical connected steps; completed/current/upcoming text and icons |
| Skill row | Capability, source/status, contextual next action; unknown distinct from missing |
| Progress line | Completed / total tasks; one modest bar; no readiness score |
| Work timeline | Completed tasks with milestone context; evidence area below |
| Dialog | Focus managed native dialog, close button, Escape support, single purpose |
| Feedback | Short status toast after local mutations; honest integration placeholders |

## 6. Screen-specific composition

Matches: leading role panel and three compact alternatives. Career Detail: editorial rows for work, fit, learning needs, explanation, then Build my path. Compare: a two-role table and optional contextual help. Outlook: two illustrative future directions, their assumptions, and a separate evidence status row.

Next steps: current milestone, recommended action, two subsequent actions, and a quiet completion link. Task Detail: instruction, observable completion criteria, resources, notes, and complete/undo. Roadmap: three ordered milestone rows. Skills: contextual list with explicit self-report labels. Progress: one completion line, recent work, evidence records, and return-to-work action.

## 7. Responsive behavior

At 1180px and below, narrow the sidebar and horizontal spacing. At 850px and below, use an off-canvas sidebar opened from the top bar; show a dismissible scrim. Retain all child links and local tabs. At 560px and below, stack the recommendation, task action, callouts, roadmap actions, and skill rows. The comparison table alone can scroll horizontally; the overall page must not overflow.

Controls retain descriptive labels and visible keyboard focus. Tables have headings. Decorative SVG icons are aria-hidden. Native dialog supplies modal focus behavior. Reduced-motion settings disable transitions. Print removes navigation and keeps meaningful content.

## 8. Content rules

Keep facts, assumptions, self-reports, evidence, and demo values distinguishable. The score is an illustrative compatibility index. A completed task is an activity record, not an automatic skill assessment. No live labour-market claims appear without source support. Dates and provenance are required when real sources are integrated.

No generic news feed, all-features overview, skill radar, multi-KPI grid, fabricated readiness measure, or decorative completion ring should be added during engineering. The single career-match index ring is retained from the accepted direction and explicitly labeled.
