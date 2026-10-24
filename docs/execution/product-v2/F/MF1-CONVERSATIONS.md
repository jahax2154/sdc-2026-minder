# MF1 conversations — real persisted chats and client auth boundary

Dependency A fa1130a86337e13a27d74e28da0200570a2331dd, including D MD1
bbe4e1b1e248fd41a1cc621ac9b30d1860622941 and E3c32027. Existing repair8446ca8,
CV exact-review retry57edea4 and approved page slice02d5b83 remain ancestors.

Minder now creates/lists/opens/deletes/continues server conversations. Conversation ID
in hash preserves explicit open across refresh; tokens/content never enter URLs.
New chat waits for explicit submit to create. Mindbot uses only the server singleton;
no New/list/delete/switch UI. Composer and quick suggestions remain inside Mindbot.
Scheduled messages render from that same persisted history. Reads use browser-safe
POST conversation alias, paginate actual sequence and never generate a turn.

Exact request bodies/keys survive uncertain response for explicit retry; history
refresh does not resend. Pending/failed/uncertain turn outcomes are visible, Working
clears in every terminal branch. Provider unavailable remains explicit. Model/source
text is escaped, with a restricted escaped-text bold formatter; no model HTML/URLs.
Typed phases/tasks render once, source context is secondary, no internal rubric dump.
Action lead/status derives from returned executor result, never generated narrative.
Draft guidance is visibly unsaved. Canonical tasks/plans are not browser storage.

Shared auth reads actual GET auth/config then GET auth/session. Only explicit local
mode may bootstrap anonymous session. Managed mode loads maintained ClerkJS6/UI1
from the validated configured instance domain, fetches fresh session.getToken for
each private request, uses Clerk.signOut, and clears/aborts private state on identity
switch/logout/401. Epoch checks drop prior-identity late replies. Current local runtime
is a demonstration, NOT real managed login. Live managed sign-in remains unverified:
E has no provisioned instance/accounts; A must configure exact allowed Clerk CSP.
Official script source: https://clerk.com/docs/js-frontend/getting-started/quickstart
No React migration or direct provider calls were added.

Actual browser tests:
- tests/morning_conversations.cjs: actual backend/Qwen, unsaved profile capability
  question1046ms, generated_guidance; student Mindbot nextstep1299ms, same mode.
  Persisted refresh, singleton isolation, Minder delete, logout privacy passed.
- tests/morning_action_retry.cjs: actual provider interpreted an explicit owned task
  completion. Browser deliberately lost response AFTER real commit. Exact retry
  repeated identical body/key; one saved action, unchanged canonical version, no
  extra turn on refresh. This fault injection is explicitly distinguished from the
  successful actual provider/action. No successful response mock was used.
- JS syntax and git diff --check passed.

Sanitized request/response-mode/timings are adjacent JSON evidence. A notified of
actual generated introductory text ending mid-sentence and mixed-language fragment;
F preserves actual content and does not alter provider/grounder policy.

Local actual UI: http://127.0.0.1:9106/#minder and /#mindbots; F API8106.
Screenshots: /private/tmp/minder-f-morning-conversations/{minder-real-answer,mindbot-real-answer}.png;
/private/tmp/minder-f-morning-action-retry/mindbot-action-retry.png.
No deployment. CV/onboarding/automation and generated plan acceptance await D next
contracts; real managed two-account acceptance remains external provisioning work.
