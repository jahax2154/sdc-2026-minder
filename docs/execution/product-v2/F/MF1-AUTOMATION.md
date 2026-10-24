# MF1 canonical daily automation controls

Dependency A e3404103182c58898de5b6519d9dcdd72cc25527 / D3299176. Uses ONLY existing
GET/PUT agent-settings {settings,expected_version}, server next_run/last_result,
existing owned plans, notices/events/action history. No second scheduler/endpoints.
Create/edit with time/IANA timezone and explicit own-plan scope; pause/resume/cancel,
cancelled refresh and explicit create-again. A schedule save never claims a run.
Unknown save outcome locks until actual state reload; no blind write retry. Canonical
schedule version prevents old overwrites. Reads remain independent of model work.

Actual morning_automation.cjs against F local app passed create, edit, scope, separate
UTC Profile vs Asia/Kuala_Lumpur automation timezone, server next_run, pause/resume,
cancel and refresh. Synthetic plan fixture uses existing server pathway-preview,
not a claim of generated content. No provider calls or actual scheduled runs claimed
by this browser control test. Existing notices/results are rendered from server;
E/A own actual Worker due/catch-up/deduplication acceptance. No deployment.

Actual UI http://127.0.0.1:9106/#mindbots, Schedule. Screenshot:
/private/tmp/minder-f-morning-automation/daily-cancelled.png. Adjacent JSON evidence.
Generated-plan preview/accept controls are the next separate F slice, currently
blocked on A's reproduced real supported-role eligibility guard, not bypassed in F.
