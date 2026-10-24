# A-N4 — bounded Qwen turns and shared quota coordination

Continues e066f4bcaf9d0bd3d7fd164324ffef13c18a4598. Keep the verified
qwen/qwen3.8-27b model, original C transport source, owner/day request budget,
canonical D state and assessed scoring. No billing, subscription or GPU change.

## Implementation

A-owned CoordinatedGroq subclasses the existing transport. Local/product/hosted
factories now bind it for chat and the existing worker. One outbound attempt per
logical call, no automatic429/network retries, one same-host flight per quota group.
Private OS-file locks coordinate lane processes using the same directory; no
prompt, answer, owner or credential is stored there. Default directory is
/private/tmp/minder-provider-coordination-<numeric UID>. F/E/C must integrate the
committed factory and restart their own runtime to participate. A never restarts
another lane. Hosted replicas need a shared private coordination volume via
MINDER_PROVIDER_COORDINATION_DIR; local locks cannot coordinate different hosts.
MINDER_PROVIDER_QUOTA_GROUP defaults to minder-team-groq plus the actual model.

Only allowlisted quota headers/status and numeric error limit/used/requested fields
are retained. Never print the upstream error body, organization ID or request headers.
The shared retry-after cooldown prevents queued/background calls from issuing
another request during provider unavailability. Wait at most20seconds; a longer
wait returns an honest retry delay with transport_attempts=0. In-flight actions
are never automatically replayed. Existing exact request receipts remain authority.
GET /api/product/provider-status reports safe observed quota/model/cooldown metadata
without a model call. Status is not a promise that legacy/remote lanes participate.

Measured headers advertise8000TPM and1000RPD. Actual errors also enforce1000tokens/
minute and200000tokens/day. These observations remain distinct. A local completion
reservation budget950/minute leaves50tokens headroom below the measured smaller
limit, refunds unused completion reservation on success, and honors error cooldowns.
This is a conservative engineering budget, not a claim that every upstream token
bucket counts the same way. Real429 still remains possible across legacy processes.

Ordinary conversation uses reply_concisely: bounded saved intake/canonical
constraints and four recent visible excerpts, no full plan/catalogue/CV/history.
It cannot return actions or scored claims. Replies become the existing typed
advice envelope with operation none, preserving actual model explanation.
Scheduling uses propose_schedule with actual relevant tasks/current words/timezone
and constraints; it retains server target/time/version/authority validation.
Roadmap generation stays real structured generation, limited to two small practice
stages, one activity each, proposed estimates up to3hours (unknown remains null).
Capacity is not a universal intake or plan prerequisite; actual scheduling checks it.
Existing canonical availability is reused. Output caps: ordinary256, schedule256,
public explanation384, general typed guidance640. Input envelope at most24000bytes.
No model ranking, invented proficiency, canned success or forecast is introduced.

Rejected generated visible content and exact validation rule are persisted in the
owned grounding/evidence ledger for diagnosis, never exposed as verified answers.
Server quote IDs, passages and URLs remain authoritative. Valid natural-language
explanations and negative limitations are retained; no excerpt-only fallback is
presented as successful model chat. A failed source does not discard retrieved ones.

## Empirical evidence and remaining gate

196backend tests pass (latest log next-gateway-checkpoint-full.log); new checks cover
cross-instance serialization, bounded queue/no outbound call,429no retry, safe headers,
actual rule/rejected claim persistence, compact context, and stricter action rejection.
These are software checks with declared transport/provider fixtures.

Native check check_native_starter_journey.py uses a new owner, normal onboarding
fields only, no CV or anchored evidence, actual catalogue and actual Qwen. It passes:
up to five provisional starter directions; real structured plan; exact duplicate
accept returning one canonical plan; distinct canonical view data; completion and
reconstruction persistence; ordinary consecutive replies; one origin-linked
Mindbot proposal; rejection with byte-equivalent saved plan.

Latest successful consecutive turns:540.264/585.609/593.659ms with only2second
reading gaps,697/807/921total tokens, one outbound call each. Useful follow-up
answers narrowed a Python practice project to add/list/delete and explained what
to record while debugging. No65second artificial pause. Earlier failures stay in
ignored native-candidate-* artifacts and are not replaced by passing claims.

A separate actual no-profile public-source check passed in native-candidate-1792852106:
TalentCorp page content + actual Qwen explanation,188completion/1260prompt tokens,
8809.771ms including DOSM's disclosed8second timeout. The latest combined run's
second approval request was blocked by a real daily quota error:200000tokens/day,
used199549, requested1007, retry-after241seconds. Its following web request was
withheld before network(model) with232.435seconds remaining. No billing change.
Therefore the complete native gate is NOT passed: once-only approval is verified
in canonical software tests but not in that combined real-provider run.

Browser gate remains distinct: F62fb94f still renders assessed matching only after
normal onboarding and does not call the new starter endpoint. F owns its minimal
connection and approval UI (F_STARTER_URGENT_HANDOFF.md/A_MINDBOT_HANDOFF_V1.md).
No new browser/Clerk-account/hosted acceptance claim is made from dispatch checks.
