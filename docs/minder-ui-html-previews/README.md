# Minder UI · HTML preview package

This package contains **two standalone interactive HTML mockups**, built using the same minimal light design system shown in the approved Minder reference images. They use embedded CSS, JavaScript, and character assets; **neither HTML page requires a server or build step**.

## Open the preview

Open `minder-chat.html` or `mindbot.html` in a desktop browser. Keep both HTML files in the same folder to navigate between the two modules. The default view is a brand-new conversation.

| Module | Direct view examples |
|---|---|
| Minder Chat | `minder-chat.html` (welcome), `minder-chat.html?state=active` (conversation), `minder-chat.html?state=thinking` (animated thinking indicator) |
| MindBot | `mindbot.html` (welcome), `mindbot.html?state=profile` (agent conversation + profile), `mindbot.html?state=customize` (customize dialog), `mindbot.html?state=schedule` (schedule dialog) |

These state URLs are conveniences for visual review; all states can also be reached using the interface controls.

## Included interactions

**Minder Chat:** Start a new conversation, use suggestion cards, type and send a message (Enter to send, Shift+Enter for a new line), see an animated thinking state, receive one of three illustrative structured answers, copy an answer, use follow-up prompts, and show/hide the contextual rail. Neither user messages nor LLM responses display avatars.

**MindBot:** Chat with a simulated personal agent, see a structured proposed worklog, open a profile popover, access Schedule, toggle demo schedules, add a local schedule, customize the agent's name, character, color, personality, and language, then save local preferences. The selected character and name update in the interface.

## Important limitations

These are **UI/UX engineering mockups, not deployed AI systems**. LLM replies and agent worklogs are local demonstration content. There is **no live LLM, FastAPI backend, database, actual scheduling/automations, calendar updates, Slack access, remote computer, or external integration**. MindBot's personalization is saved to the browser's local storage when available; schedules are session-only. Links to other Minder modules are placeholders and show an explanatory message. Do not treat sample role scores, user profiles, or activity as actual user data.

## Exact colors used in the HTML

| Token | Value |
|---|---|
| App background | `#F7F8F4` |
| Surface | `#FFFFFF` |
| Surface alternative | `#F1F4EF` |
| Border | `#E4E8E0` |
| Primary text | `#111315` |
| Secondary text | `#656E69` |
| Muted text | `#949C96` |
| Sage accent | `#5E7D69` |
| Deep sage | `#355642` |
| Soft sage | `#DDE8DE` |
| Success/progress | `#6C8E79` |
| Neutral chip | `#EEF1EC` |

Typography: system sans-serif stack beginning with Inter where available. Default desktop shell uses a 269px sidebar and 75px top bar, 12–20px radii, and subtle rather than saturated surfaces. All tokens are available in `assets/minder.css`.

## Screenshot provenance

Screenshots in `screenshots/` were captured directly from the **delivered HTML files in Chromium at 1672 × 941**. They are not separate AI-generated depictions of what the HTML might show. Additional mobile viewport screenshots are included as layout checks. Some screenshots deliberately show different scroll positions of a longer conversation.

## Frontend engineering handoff

The self-contained HTML files are convenient as visual and interaction references. The editable source files are in `assets/minder.css` and `assets/minder.js`, and the small character illustrations are also there. For your existing React + TypeScript + Vite Minder application, implement the layouts as components rather than inserting these complete pages into its `index.html`:

- `AppShell`: sidebar, header, navigation and account
- `ChatWelcome`, `MessageThread`, `MessageComposer`, `MinderChatPage`
- `MindBotPage`, `AgentIdentity`, `AgentProfilePopover`, `CustomizeAgentDialog`, `ScheduleDialog`
- A typed API layer replacing the canned response functions and the in-memory actions

This package's initial markup and demos should not be confused with production-ready frontend code. Add application routing, validated data contracts, loading and error states, accessibility testing, and backend integration before deployment.
