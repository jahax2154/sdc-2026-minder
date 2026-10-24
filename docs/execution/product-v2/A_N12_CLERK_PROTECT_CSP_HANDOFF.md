# A-N12 — Clerk Protect CSP repair and E handoff

Parent: e6c61c148cede091e8d171a14e490ffc848fd000 on
session/a-personal-integration. The commit containing this handoff is the new
approved source pin; the coordinator reports its exact immutable SHA after commit.
It includes A-N11's real-browser-verified market-answer refinement and preserves
all prior checkpoint history. Integrate only committed changes missing from E.

## Observed cause and bounded repair

E reports that its real interactive Clerk login loads rotating subdomains below
client.protect.clerk.com and connects on ports 8443, 18443, 2082 and 992. The prior
exact-host configuration hook cannot cover rotation or non-443 ports. This is an
E-reported browser observation, not a new A-hosted login pass.

Clerk's [official CSP requirements](https://clerk.com/docs/guides/secure/best-practices/csp-headers)
explicitly require these minimum service-scoped sources:

| Directive | Added fixed source |
| --- | --- |
| script-src | https://*.protect.clerk.com |
| frame-src | https://*.protect.clerk.com |
| connect-src | https://*.protect.clerk.com:* |

Only successfully configured managed identity receives these additions. Clerk
documents the connection port suffix as required for its abuse-protection service.
Scripts and frames retain the default HTTPS port. There is no generic HTTPS
allowance, arbitrary-domain wildcard, script unsafe-inline or unsafe-eval.

The optional MINDER_CLERK_ADDITIONAL_ORIGINS hook still accepts only exact trusted
HTTPS hosts and rejects wildcard input, explicit ports and unrelated domains.
Anonymous/local runtime policies remain self-only for script/connect/frame/default.
Server identity verification, authorized parties, session revocation, user isolation
and action approval controls are unchanged. No provider/model/search/scorer, frontend,
DB, storage or dependency changes. No credentials or browser session material added.

## Verification

- Five focused identity tests PASS in 0.027s: managed directive scopes, exact-origin
  override rejection cases, local-mode strict policy, existing authenticated/private
  boundaries, and the actual WSGI static response's CSP header.
- Full locked backend suite PASS: 231 tests, 14.031s, no skips. A first sandboxed run
  had three PermissionError failures binding localhost sockets; a permitted socket-
  enabled rerun passed all three concurrency checks and the full suite.
- git diff --check PASS. Reviewed paths are A-owned in product-v2/OWNERSHIP.json.
- These are controlled header/auth/service tests, not live Clerk login evidence.
  Existing A-N11 real-Qwen answer acceptance remains recorded separately.

## E next verification

Load this exact commit or a history-preserving descendant into the existing candidate;
retain the verified complete key, exact authorized parties, private storage and current
single-worker setup. Check the real served CSP and interactive login in fresh browser
sessions, including rotating Protect hosts and its non-443 connection requests. Then
verify authenticated account isolation and the hosted journey. Do not interpret this
source handoff as hosted acceptance or a bypass of the earlier publication review.
E owns deployment and runtime restarts. A has not published or modified E's worktree.

Excluded local state remains untouched: untracked raw/derived source inputs, private
runtime configuration, databases and artifacts. This checkpoint creates no backup
claim for those excluded files.
