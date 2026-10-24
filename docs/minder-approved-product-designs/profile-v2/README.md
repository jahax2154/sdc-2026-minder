# Minder User Profile — Frontend Handoff v2

This package contains the interactive standalone HTML prototype, the design/engineering context, two test scripts, and the approved visual reference images.

## Open the preview

1. Open `minder-user-profile-prototype-v2.html` in a modern browser. For consistent localStorage behavior, serving the directory through a local HTTP server is recommended.
2. Default page starts **first-time onboarding**. Answer three adaptive questions, optionally skip enrichment, review, then create the demo profile.
3. After setup, use the five-section horizontal profile navigation. Click the pencil next to the name to verify the initials update after saving a new name.
4. To inspect a prefilled synthetic persona directly, use `?demo=profile` in the URL. This uses fictional Avery Lim and two clearly self-reported demo skills.
5. To return to onboarding, choose the small account-menu button at the bottom of the sidebar, then confirm **Reset demo**.

## Engineering handoff

- `MINDER_USER_PROFILE_DESIGN_CONTEXT.md` — authoritative module behavior, layout tokens, architecture, data boundaries, routes and acceptance gates.
- `minder-user-profile-prototype-v2.html` — executable HTML/CSS/JavaScript UI reference, entirely self-contained.
- `minder-user-profile-v2-structural-test.mjs` — pure Node runtime/behavior tests, no browser installation required.
- `minder-user-profile-v2-test.mjs` — Playwright interaction and browser-screenshot script, requiring Chromium.
- `design_references/` — approved concept mockups and original visual-style sources. These are **not screenshots of the HTML**.

## Verification

Structural test: `node minder-user-profile-v2-structural-test.mjs` — passed in the creation environment.

Browser screenshots, with Playwright installed: `node minder-user-profile-v2-test.mjs`. Screenshots will be written to `minder-user-profile-v2-screenshots/`. This end-to-end test could not be run in the creation environment because browser installation failed. Do not claim it passed until it does locally.

## Production boundary

This is an interactive prototype, not the production React + TypeScript app. All profile state is stored locally in the browser; Career Match/Explore destinations are honest placeholders. Do not copy this storage or placeholder routing into production without integrating the verified FastAPI profile API and authenticated user identity.
