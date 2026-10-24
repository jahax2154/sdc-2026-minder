# Minder Explore — frontend design package

Final navigation revision · 24 October 2026

## Start here

Open **Minder_Explore_Preview.html** for the self-contained interactive preview. It has no CDN, font download, package installation, or server dependency. JavaScript must be enabled. The two destinations are separate page views reached from the expanded Explore sidebar, not a top-of-page Careers/My Path switch.

For the actual multipage source, open **careers.html** or **my-path.html** after extracting the ZIP. Keep the assets folder beside them. The two pages link to one another using real document navigation. `index.html` is an additional Careers entry point.

For reliable cross-page demo storage, serve the extracted folder on one local origin, for example `python3 -m http.server 8000`, then open `http://localhost:8000/careers.html`. Some browsers isolate localStorage between `file://` documents. The standalone preview avoids cross-document state differences; storage still depends on the host/browser allowing it.

## Final navigation

- Explore — expandable sidebar parent, no combined overview page.
- Careers — Matches / Compare / Outlook.
- My Path — Next steps / Roadmap / Skills / Progress.

“Next steps” is retained after the user's final clarification. “My tasks” and “My roadmap” in the sidebar are shortcuts into the same My Path data and routes.

## Included files

| File or directory | Purpose |
| --- | --- |
| Minder_Explore_Preview.html | Portable, self-contained preview with separate hash page routes |
| careers.html | Multipage Careers entry |
| my-path.html | Multipage My Path entry |
| assets/styles.css | Canonical tokens, components, responsive and print styles |
| assets/app.js | Canonical routing, fixtures, interactions, browser-local state |
| docs/DESIGN_CONTEXT.md | Visual rules, layout, components, accessibility, reference precedence |
| docs/FRONTEND_LOGIC.md | Every route, workflow, data ownership, action, state, and integration boundary |
| docs/SCREEN_REFERENCE_INDEX.md | Final image-to-route mapping |
| references/final | Reference images captured from the actual HTML after the navigation revision |
| references/style | User-supplied visual references; styling only, not information architecture |
| qa/VERIFICATION.md | Checks performed, results, and remaining limits |
| tools/build_preview.py | Rebuild the single-file preview after source changes |

## Working demo interactions

Expand/collapse Explore; navigate separate Careers and My Path pages; switch local section tabs; inspect career details; compare roles; choose/restore a career plan; complete/undo tasks; save work notes; inspect all tasks or a milestone; update explicit skill self-reports; add evidence notes; update weekly time preference; filter careers/tasks; download a small CSV; inspect initial/empty states; reset demo.

The default example uses fictional Avery Lim: Machine Learning Engineer plan, 8 tasks, 3 completed; 3 milestones, 1 completed. Milestone counts are 2/2, 1/4, 0/2. A newly selected career begins with unfinished tasks. Previous plans are retained.

## Scope and honesty

This is a frontend reference, not a production backend. Matching results and the 80/100 index are illustrative fixtures. The alternative career plans share a general practice template in this demo; production must use role-specific plans. No live AI calls, authentication, market data, external profile integration, scheduling engine, or autonomous plan changes are implemented. Chat, Profile, Mindbot, and Overview explain their integration boundary when opened.

Progress measures task completion, not skill mastery or employability. Skills change only through explicit self-report actions. Work notes are unverified evidence. The Outlook screen labels its scenarios and the absence of verified market sources.

## Editing and handoff

Edit the separate CSS and JavaScript first, then run `python3 tools/build_preview.py`. Do not separately patch the bundled HTML. There are no build dependencies. Integrate the shared data model and routing with the existing Minder application rather than importing a second backend or scoring function. See the two context documents before integration.

The final screenshots are the authoritative reference for this package. Earlier generated mockups containing a Careers/My Path switch above the content are superseded. Exact font files/design tokens were not supplied; the implementation derives a consistent token set from the screenshots and uses the documented system font stack.
