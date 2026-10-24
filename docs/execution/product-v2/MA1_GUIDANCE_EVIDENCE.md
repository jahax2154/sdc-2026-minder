# MA1 typed guidance implementation checkpoint

Starting base1285670, M0 719c873, contract576330d. Runtime8111/9111, same Qwen
qwen/qwen3.8-27b, synthetic owners only. No scoring change, deployment or main merge.

Exact screenshot request reproduced with unsaved/partial/rich profiles on original
9111 code. All real Qwen calls succeeded via select_grounded_statements, but output
was anchored Reading Comprehension for first two and generic role prompt for rich.
Observed request totals17513.66/17848.18/18666.32ms; context16821.218/17200.189/
17975.696ms, provider661.468/626.519/671.362ms. Unseen bus-delay notebook follow-up
returned generic prompt after18439.241ms. This confirms backend routing/renderer
and unnecessary assessment construction, not a broken credential/model.

New generation.py calls real forced propose_guidance with typed advice, assumptions,
questions/stages/tasks, bounded profile and recent visible thread context. It avoids
assessment construction entirely for guidance. Factual market/scoring queries retain
closed source-backed renderer. D callback installed at Application init, registered
conversation operations remain unavailable until D delivery. No transcript/action
claim is inferred from model prose. Existing direct/proposal executor validates scope;
first operation subset completion/reschedule, wider requested operations still pending.

Initial actual new9111 calls: unsaved1177.98ms, partial1306.84ms, unseen follow-up
985.115ms backend total. Qwen returned three provisional stages and adapted the
bus-delay milestone to chronological held-out evaluation. It did not save profile/
plan. Rich fourth call returned actual provider_rate_limited after1400.66ms and
truthful no-draft fallback. This is 3 real validated responses/4 attempts, NOT full
acceptance or a mocked outage. Initial intro was only 'eML'; tightened schema now
requires useful30-character introduction and no-profile first turn a focused question.
Those refinements require renewed live check; initial output is not final acceptance.

Software checks use explicit AdviceProvider: incomplete profile no-assessment gate,
no implicit saves, bounded prior answer, ownership/version isolation, invented fact/
score/URL/extra-field rejection, missing-key fallback, exact direct completion vs
inferred immutable proposal. Full real browser/generated-renderer acceptance awaits F.
No unsupported forecast or learned accuracy claim. Private synthetic runtime outputs
stay under ml/artifacts/session-a/product/morning; no keys or real CVs recorded.
