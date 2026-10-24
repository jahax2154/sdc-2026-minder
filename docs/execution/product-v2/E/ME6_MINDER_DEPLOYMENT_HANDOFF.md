# ME6 — current Minder deployment candidate

Target: https://replit.com/@JunhongPhuah/Minder
Project: 0f48cf79-f55a-4b24-ba5c-a03d800e03bd
Official repository: https://github.com/jahax2154/sdc-2026-minder.git
Approved branch: session/a-personal-integration
Approved application pin: 74b9688e124f0e6d5f2eb57943fd2671614dab9a
Approval: ../A_N12_CLERK_PROTECT_CSP_HANDOFF.md

This replaces the earlier 27bc760 candidate. It includes A's managed Python
integration and Clerk Protect CSP repair, D's native PostgreSQL/private storage,
E's existing worker launcher and F's accepted frontend. Replit reports application,
deployment and dependency manifests identical to this pin. Provider configuration
HEAD is a5552048b57d22b9d26d70662acdd89d1585009d. Original configuration checkpoint
4528209dd303a7de1b2961cda0f0331048fe3dbd and Git history are preserved.

## Current evidence

Replit reports a successful frozen Linux build, health HTTP200 at the approved
source pin and exactly one existing worker. Managed development PostgreSQL migrations
and a real private bucket put/get/delete round trip passed; anonymous download403.
The disposable storage probe was removed. These are preview checks, not production
restart or end-user acceptance.

After the user replaced the abbreviated secret, both the local private-file check
and the actual Replit process authenticated to Clerk and matched the public signing
key. Replit injects the running key through its process environment. No dotenv
startup override or duplicate inline launch entry was found. Project-local versus
shared/inherited Secret cannot be distinguished by the connector. No published
runtime or separately verified published secret source exists yet. No key values,
fragments, tokens, private user data or provider exception payloads were printed.

Two fresh preview sessions rendered Clerk without CSP violations after A's repair.
Both documented Protect host and connection-port wildcards were verified present.
Actual end-user signup/signin remains unverified; service-key verification does not
substitute for user-session authentication or two-account isolation. The private
local file remains ignored, untracked and owner-only.

## Publication and remaining acceptance

No public deployment exists. The preview replit.dev URL is not the judge endpoint.
The intended configuration is Reserved VM with one replica and the existing cohosted
worker; actual machine size, quoted price and allowance still require Publishing UI
verification. The connector's first-publish operation defaults to Autoscale and must
not be used for this task. Production PostgreSQL is normally created during first
publication; do not copy the development database DSN as a substitute.

An earlier automatic review rejected publication because startup, the old invalid
key, database/HTTPS/VM configuration and the connector's Autoscale default were
unverified. No bypass publication occurred. Startup/key/CSP are now repaired; the
remaining deployment settings need evidence before a safe fresh publication attempt.

Outstanding: Reserved VM allowance/quote, production database binding, final HTTPS
origin and authorized parties, published-secret verification, real two-user login,
profile/chat/CV journeys, logout/refresh/expiry, actual restart/redeployment durability
and one due hosted event with browsers closed plus pause/cancel/retry checks.
26 focused local identity/deployment/operator checks passed at the approved pin.
No hosted acceptance result is inferred from those tests.

Excluded local raw/derived inputs and private configuration remain uncommitted;
this checkpoint does not claim they are backed up. Career Compass was not modified.
