# A-N2 — actual public retrieval and no-profile cited Qwen answer

Policies: public-career-retrieval-v1 / public-web-answer-v1. Application composition
binds a real backend PublicRetrieval tool in local/product/hosted factories. This
does not depend on the assistant's browsing tool, a stored dataset URL or a paid
search API. `/api/product/retrieval-capabilities` reports configuration. Existing
canonical conversation-turn and chat routes use the tool for current market/job/
skill questions. No complete or saved Profile is required.

The tool makes actual bounded HTTPS requests to allowlisted public Malaysian
official pages, validates destination/redirect/DNS, extracts page text, title,
publication date when supplied, retrieval time, geography, measurement scope and
content hashes. No CV/history/private text goes into any public URL, query/header
or search request. Topic selection uses a fixed public vocabulary and fixed public
source URLs. This is a bounded official-source set, **not exhaustive web search**.
Missing pages and unknown publication dates stay explicit. Verified page content
has a300second labelled cache; source failures have a60second circuit break to
avoid repeatedly blocking chat on the same unavailable site.

LLM input uses the actual extracted passages, metadata and exact server-extracted
quote choices. Native tool explain_public_sources selects quote IDs and explains
the findings; no arbitrary model URL or quote is trusted. The backend validates
IDs, bounded per-source quotes, quantities and unsupported score/prediction claims,
then attaches the actual source URL. Web text is evidence, never action authority.
The web path has no task/profile/plan mutation operation.

## F response contract

Standard saved conversation response, grounded_evidence or limited_fallback.
`answer` is the LLM explanation with [1] citation markers. `statements[]` contains
external_fact exact quotes, standard sources and additive `citation` with id/url/
title/published_at(nullable)/retrieved_at/geography/scope/sha256/cache_status.
`diagnostics.retrieval` reports policy/tool, source metadata, bounded failures and
limitation. These fields fit D's existing visible-response contract; no D module
or migration was edited. F should show clickable citation title/URL/date/geography
and source failures, rather than collapse all useful evidence behind raw IDs.
Source titles/dates must come from these DTOs, not the model. Do not require normal
onboarding or assessed skill input merely to ask general factual questions.

## Actual empirical evidence

`check_native_web.py` exercised the real canonical conversation dispatch in an
isolated A database, actual official-page HTTP and qwen/qwen3.8-27b. Question asked
what MyCOL inclusion says about demand and what it does not show. PASS: provider
available/native tool validated, cited retrieved TalentCorp MyCOL content,0Profiles,
0plans, no target mutation. Application elapsed8907.626ms, primarily the8second
DOSM timeout;1536tokens (1311input/225output). TalentCorp returned200 with actual
text, title and hash. Its publication date was not supplied and staysnull. DOSM's
release page timed out and remains unavailable; no current national vacancy count
is fabricated. Current process cache/circuit break avoids repeating that delay.

Allowlisted real response headers: limit-tokens8000(TPM), limit-requests1000(RPD),
remaining/reset values retained privately. Their meanings match official Groq
rate-limit documentation: https://console.groq.com/docs/rate-limits . No key,
cookie, full upstream headers or error body is printed. No quota/billing/model
change. Shared call coordination and ordinary-pace tests are A-N4, not inferred
from this one successful call.

Three original native verification failures were preserved. The first free-quote
candidate was not retained, so its fine-grained cause is unknown; protocol now uses
exact quote choices. Subsequent captured failure was a legitimate negative list
('does not show ... guaranteed individual employment'), caught by an overbroad
word guard. Bounded negative-disclaimer handling now accepts it while affirmative
unsupported guarantee/quantity/URL claims still fail. No unverified candidate is
shown as an answer. Four logical native application invocations total in this
phase, with one final successful native result; not four individual HTTP attempts.

184backend tests pass10.694s;7focused network/provider-fixture checks cover real
page extraction vs snippets, cache, private-query exclusion, SSRF/redirect bounds,
quote IDs/quantities/disclaimers, owner-scoped no-profile persistence and routing.
These software fixtures are separate from actual native evidence. Private
`next-web-native-v2-summary.json` SHA256:
659050278f108d994918eedb513da39e1d872223033f9b1df6696c233c61d220.
Original failure reports/candidates and fetched public text remain in ignored A
artifacts, never Git. No public judge deployment or browser UI acceptance is
claimed yet. F/E must integrate the committed handoff before final journeys.
