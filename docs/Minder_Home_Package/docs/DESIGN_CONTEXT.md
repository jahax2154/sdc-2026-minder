# Minder Home — design context

Final Home handoff · 24 October 2026

## Purpose and terminology

Home is a calm starting point: understand where you are, choose a direction, take the next step, and access your personal agent. It is not an analytics dashboard. The correct name is **Mindbot**, the existing Minder personal agent. Do not introduce another module called Mindboard. Home replaces the earlier shell label Overview for this deliverable.

The user approved four generated Home references. Their information architecture, white/sage visual language, compact profile strip, direction panel, and lower two-column layout define this implementation. Original generated images are included unmodified in `references/approved`; their old Mindboard wording and unconditional ON badge are superseded by the user's clarification. The final HTML screenshots in `references/final` show corrected labels and deterministic component sizing.

## Reference precedence

1. User's latest naming correction: Mindbot throughout the product.
2. Canonical HTML/CSS and final screenshots: repeatable implementation, stable components and state-specific content.
3. Approved Home images: composition and styling direction, with generation-related variation normalised.
4. Existing Explore package: shared colour palette, typography stack, shell, rounded navigation, borders and buttons.

No original Figma tokens or proprietary font files were supplied. Tokens are reused from the delivered Explore implementation. These are faithful code-based interpretations of the references, not claims of pixel identity with every generated image.

## Layout contract

- Desktop sidebar: 238px, pale off-white, thin right divider. Brand, New conversation, Home, expandable Explore with Careers/My Path, Minder Chat, Mindbot, My profile, and My roadmap/My tasks shortcuts. Account at bottom.
- Top bar: 73px, Workspace > Home breadcrumb, search shortcut, Ask Minder, avatar.
- Main padding: 35px top and 40px horizontal; maximum main width 1560px.
- Greeting: one H1 plus a single supporting sentence. Fixed morning greeting in the demo; use the user's local time in production.
- Profile strip: minimum 130px; identity/icon left, concise profile content, setup/edit action right.
- Direction panel: minimum 165px; prominent career/setup heading, one short explanation, one primary action and at most one secondary action.
- Lower grid: 1.48fr Next steps / 1fr Mindbot; 18px gap. Both panels at least 365px tall on desktop. Stable content order across states.
- Next steps header: title and a single rounded Tasks / Skills / Progress switch. No automatic rotation or unrelated cards under it.
- Mindbot: setup, paused, message, or quiet assistance view. It has no independent navigation tab in Home.
- Preview footer: sample/data disclosure and state picker; development-only controls to remove in production.

## Canonical tokens

| Token | Value | Use |
|---|---|---|
| Ink | `#111815` | Main text |
| Muted | `#727984` | Supporting copy |
| Forest | `#36584b` | Primary actions and active emphasis |
| Forest hover | `#284438` | Primary hover |
| Sage | `#edf2ed` | Selected tab, feature rows, icon backgrounds |
| Sage deep | `#dfe8df` | Avatar |
| Border | `#e5e8e6` | Dividers and panel outlines |
| Paper | `#ffffff` | Page/panels |
| Sidebar | `#fafbf9` | Global navigation |
| Panel radius | `12px` | Main sections |
| Button radius | `8px` | Actions |
| Capsule radius | `40–50px` | Tabs and status pills |
| Type | Inter, system sans-serif, Segoe UI, Arial | No external font dependency |

H1 40px; section H2 about 21–26px; body 14–15px; secondary labels 11–12px; eyebrow 10px with restrained tracking. Use clear weight and space rather than extra colours. Thin outline icons are inline SVG; the logo mark is a CSS approximation matching the previous package.

## Components and rules

- Keep profile summary compact after setup; never expand Home into the full profile editor.
- Career recommendations remain distinct from the user's chosen direction.
- Tasks show one recommended task and at most one following task. Put the full list in My Path.
- Skills show a focused practice action and a clearly labelled self-report state, not an invented mastery percentage.
- Progress shows actual task/milestone counts and recent work. No employability, aptitude or confidence score.
- Mindbot displays one priority message and its action. A proposal remains unapplied until explicitly accepted.
- ON appears only when the personal agent is enabled. Configuration and enablement are separate.
- Quiet is a successful state: no fake notification, no empty red badge, no pressure to complete every section.
- Setup actions should explain the benefit. Missing prerequisites should explain why an action is disabled.

## Responsive and accessible behaviour

At 1250px the shell becomes slightly narrower and section headers can wrap. At 900px the sidebar becomes an off-canvas menu. At 650px the lower panels stack, profile/actions wrap and typography reduces. Maintain order: profile, direction, Next steps, Mindbot. The three tabs stay visible at mobile sizes. The layout is designed for at least 320px width.

Use landmarks, associated form labels, visible keyboard focus, native dialog focus containment, Escape close, accessible status announcements, and semantic tabs. Arrow keys/Home/End change the selected tab; inactive tabs are removed from the Tab sequence. Colour is supplemented by text labels. Reduced-motion preference is respected. Long user text must wrap without pushing actions off-screen. A formal accessibility audit is not claimed.

## Screenshot conventions

Final screenshots use `?reference=1` to fit the desktop composition at 94% scale; ordinary browsing remains unscaled. This changes scale only, not component structure or state. Images with `?state=` are deterministic examples, not signed-in user data. Names, messages, career matches and progress are fictional fixtures.
