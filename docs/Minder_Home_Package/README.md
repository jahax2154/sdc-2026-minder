# Minder Home — complete frontend design package

Final terminology: **Mindbot**, Minder's personal agent. 24 October 2026.

## Open the preview

Open `Minder_Home_Preview.html` for the self-contained interactive version. It includes its CSS and JavaScript and needs no install or network. If your file viewer shows source instead of running HTML, open the file in a browser with JavaScript enabled.

Open `home.html` or `index.html` to use the separate source files; keep `assets/` beside them. You can also serve this folder using `python3 -m http.server 8000`. Browser file-origin storage rules vary, so use a local server for reliable cross-file persistence.

Use **Preview states & settings** at the bottom of Home to switch among eight examples, including first visit, profile-only, matches ready, career chosen without a plan, active path with a Mindbot message, quiet Skills, Progress, and Mindbot-only setup. Choosing a sample replaces demo data.

## Package structure

| Path | Contents |
|---|---|
| `Minder_Home_Preview.html` | Portable HTML with styles and behaviour embedded |
| `home.html`, `index.html` | Normal entry pages using separate source assets |
| `assets/styles.css` | Tokens, shell, sections, components, responsive styling |
| `assets/app.js` | Rendering, independent states, interactions, local persistence |
| `docs/DESIGN_CONTEXT.md` | Visual system, layout, components and reference precedence |
| `docs/FRONTEND_LOGIC.md` | Workflows, action mappings, states, ownership and integration requirements |
| `docs/SCREEN_REFERENCE_INDEX.md` | Reference image and state mapping |
| `references/approved/` | Four original approved generated images, preserved unchanged |
| `references/final/` | Final screenshots of the actual HTML with corrected Mindbot naming |
| `references/index.html` | Local reference gallery |
| `qa/VERIFICATION.md` | Checks performed and limitations |
| `tools/build_preview.py` | Rebuild the single-file preview after editing sources |

The approved generated references predate the naming correction and contain the old word Mindboard. Their pixels are preserved as source reference; the final implementation and final screenshots use **Mindbot**. ON appears only when it is enabled. The final screenshots are the authoritative reference for repeatable sizing and terminology.

## Working interactions

Profile setup/edit; career match review; explicit direction selection; sample plan creation; Tasks/Skills/Progress tabs with keyboard navigation; task detail and evidence notes; completion/undo and derived progress; Mindbot setup/pause; suggestion acceptance/dismissal; quiet help prompts; draft saving; sidebar expansion/mobile menu; state picker.

## Integration boundary

This is a Home frontend package, not a deployed or backend-connected application. Other module destinations open clearly labelled preview dialogs. Replace these handlers with existing Minder application routes, shared data services and actual agents. No AI reply is fabricated and no calendar, message, or external service is changed.

The fictional sample path starts with 3 of 8 tasks already complete, explicitly disclosed before loading. Sample career matches are not calculated, skill status is self-reported, and task completion is not a skill assessment. This demo store is separate from the previous Explore demo; share real domain records when integrating.

## Editing

Edit `assets/styles.css`, `assets/app.js`, and `home.html`, then run:

```
python3 tools/build_preview.py
```

The build script regenerates `Minder_Home_Preview.html`, `index.html`, and a local QA `dist/` folder. Do not patch the bundled preview separately. There are no dependency or build-system requirements beyond Python for regenerating the bundle.
