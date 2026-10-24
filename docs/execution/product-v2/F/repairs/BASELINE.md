# F-R baseline reproduction (CHAT-01/BOT-01)

Read approved brief from actual original-checkout docs/Minder_Chat_Mindbot_Repair_Brief_v1.md;
it is not yet committed in F. Task source is current user, ownership F frontend only.
UI source29281ec907ef031c1ec07be27c84e25aad69969e, F same-origin9106/API8106,
existing F product runtime/std lib WSGI; preserved Qwen qwen/qwen3.8-27b. Only fictional
owner/empty-evidence profile used. Exact sanitized payload/response and waterfall
are baseline.json. No session token/config/private input captured. Public correlation
ID/response_mode/stage timings absent from current successful response contract.

Unsaved profile: UI refuses locally before sending chat. Saved partial profile with
no evidence: exact screenshot question returns200, provider available/native arguments
validated, but only proposal disclaimer plus three limitations, zero sources. Rendered
verbatim with misleading primary 'Language-assisted answer'. Measured15969ms, repeated
16561ms (provider included, n2). Thus backend returned boilerplate; frontend did not
invent it. A owns routing/grounding diagnosis, no frontend special-cased answer added.

Mindbot initial/repeated navigation ordinary reads:99/111ms (n2, navigation rather
than process-cold measurements). During second chat, profile GET alone waited16519ms;
subsequent agents/proposals/history/settings completed4/7/8/10ms. Mindbot usable
16595ms. Observed request serialization, plus frontend gates frame behind profile
and all4 reads. This is local evidence, not a production latency claim. No model
request from Mindbot opening itself was observed. Backend concurrency belongs to A.

Static findings: Context forced open in every chat update; lacks internal Close;
pending copy says Checking saved evidence; shared client has no request deadlines.
Screenshot /private/tmp/minder-f-repair-before-chat.png (fictional) sent to A.
Raw/derived source inputs preserved/untracked; no new backup of private runtime.
