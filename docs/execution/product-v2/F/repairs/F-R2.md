# F-R2 — compact shared navigation

Status: passed real shell/routes browser checks. Depends F-R1/8943ba2.
Shared shell only; Overview/Explore page bodies unchanged (git diff verified).
Default rail72 CSS px retains source colors/icons/shape and releases197px of prior
269px width. Hover/focus labels use a fixed tooltip without expanding rail; every
control has accessible name/active route state. Phone/coarse-touch has labeled
expanded menu, Close/backdrop/Escape and restored focus. Account/new chat and all
existing sidebar routes remain reachable. Source's fictional Review tag removed;
actual pending proposal badge will be supplied only after a successful F-R3 read.

Checks: repair_navigation.cjs uses real API/shell and zero provider calls; rail72px,
hover/focus labels without width expansion, all7 sidebar routes active/reachable,
phone390px and1024px touch labeled menu passed; zero page errors. Evidence JSON
F-R2-evidence.json. Screenshots /private/tmp/minder-f-repair-rail-desktop.png and
/private/tmp/minder-f-repair-menu-mobile.png. No redesign of content page bodies.
