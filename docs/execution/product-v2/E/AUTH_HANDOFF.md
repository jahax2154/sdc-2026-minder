# ME1 first identity contract — Revision 3

Dependency: A M0 `719c8731ff54c73065f675267556e04d14c17a96`.
Auth adapter is prepared using recommended Clerk; no previously working managed
provider has yet been verified in the connected project. No route/middleware,
frontend, user mapping, schema or migration edits in E.

## Implemented Python boundary

`minder_app.auth_adapter.verify_identity(token, request_context=None)` returns a
frozen `VerifiedIdentity`, a Mapping with issuer, subject, session_id, expires_at,
provider="clerk". It is emitted only after official Clerk SDK session-token
verification, exact issuer, authorized party and expiry checks, plus an online
active-session/subject match. Treat issuer+subject as D's stable mapping key.
No email matching, client-supplied owner, anonymous adoption or default identity.
Request context optionally contains `origin`; it cannot override configuration,
time, issuer, credentials or subject. A extracts Bearer token, calls E, passes the
trusted result to D's owner resolver, and enforces that owner for ALL private reads
and writes. Public/anonymous exceptions are A's explicit local-vs-hosted policy.

Failure: AppError401 sign_in_required, or503 managed_auth_not_configured /
managed_auth_invalid_configuration / managed_auth_sdk_unavailable /
managed_auth_temporarily_unavailable. No raw provider errors escape. A must map503
in its common transport. Never fall back to anonymous login on auth failure.

The adapter uses a public signing key for local SDK signature verification; a
bounded three-second SDK session lookup rejects tokens after provider logout.
There is no session-status cache, no provider retry and no DB transaction during
the call. The common concurrent HTTP runtime must remain enabled so a slow login
check or Groq request does not serialize all requests. An identity provider outage
fails closed. This path trades an API call per private request for immediate
revocation checks; measure rate/latency in hosted acceptance.

`public_config()` returns only:

```json
{"contract_version":"minder-managed-auth-v1","provider":"clerk","status":"configured","publishable_key":"pk_test_…","sign_in_path":"/","after_sign_in_path":"/","after_sign_out_path":"/"}
```

Missing config returns status unavailable and publishable_key null. Configured means
fields pass local validation; it does NOT certify provider provisioning/live login.
A owns the actual public configuration and private login-state routes; no new route
is advertised by E. F must await A's committed path names. Suggested login state
semantics: authenticated with server-mapped user; unauthenticated401; unavailable503.
Do not serialize provider credentials or the whole SDK RequestState (it has a token).

## F integration

Keep vanilla frontend. Use maintained ClerkJS login/sign-up components with the
public publishable key. Acquire the current session JWT with session.getToken()
for each private request; send Authorization: Bearer. Do not persist JWTs, raw CVs
or authoritative histories in localStorage. Do not issue anonymous /api/session in
hosted mode. On logout/account switch/401, abort pending requests, clear all private
UI and caches, discard late responses from the previous identity, then refetch for
the new verified account. Clerk.signOut() handles provider logout. A must permit
only the actual Clerk instance origins/scripts/frames in the CSP; no wildcard CSP.
No React/Express scaffold is needed. New frontend implementation belongs to F.

## Private provisioning requirements

Set in the selected runtime's secret interface, never chat/Git/shell history:

- MINDER_AUTH_PROVIDER=clerk
- CLERK_PUBLISHABLE_KEY (public frontend identifier)
- CLERK_SECRET_KEY (server-only same test/live instance)
- CLERK_JWT_KEY (instance PEM public signing key, pin/rotate deliberately)
- CLERK_ISSUER (exact HTTPS issuer from that instance)
- CLERK_AUTHORIZED_PARTIES (comma-separated exact app origins, no wildcard/path)
- CLERK_AUDIENCE only when the configured session template actually issues it

Local test origin is permitted only with MINDER_ENV=development and localhost/
127.0.0.1. Published runtime requires HTTPS. Configure the chosen hosted URL as a
provider-approved sign-in return origin. Provision two separate test/judge accounts;
do not share one account to claim isolation. Keep development/production instances
distinct. Only provider-maintained login stores passwords; this app does not.

A root dependency request: clerk-backend-api==7.0.0; Python>=3.10 required, E tests
use existing Python3.12.15 in a separate temporary environment. Do not replace or
mutate the team's existing Python3.9 environment. SDK7.0.0 imported and actual SDK
signature/origin/audience/expiry checks exercised. Official SDK docs/source:
https://github.com/clerk/clerk-sdk-python and
https://clerk.com/articles/how-to-add-authentication-to-a-python-backend

## Observed checks and honest gaps

```sh
PYTHONPATH=ml/src:apps/backend-api /private/tmp/minder-e-auth-py312/bin/python -m unittest discover -s apps/backend-api/tests -p test_auth_adapter.py
```

Five tests pass. Signed JWTs are generated locally with ephemeral RSA keys and
verified by the real Clerk SDK. Provider active-session reads are controlled test
doubles. Checks cover distinct subjects, frozen identity, expiry, signature/issuer/
audience/origin tampering, missing tokens, logout/revocation, subject/session mismatch,
provider failure and secret exclusion. This is not two live Clerk accounts or
integrated application ownership acceptance; those require A/D/F and live access.

## Hosting discovery at this checkpoint

Connected account search Minder returned no match; listing all editable apps found
Aiversecity Career Compass (shared project), FOS_bot and Discord Bot. Candidate
career project ID d8e6ee62-0e31-4863-bf19-b457893d558c, editor URL
https://replit.com/@yicheng070612/Aiversecity-Career-Compass . Publishing status
reports success with deployment b92b0227-3c18-4f8c-b494-e97230c8637f and URL
https://aiversecity-career-compass.replit.app . Public read returns a Replit Shield
redirect. Source/runtime inspection through read-only Replit Agent timed out; next
query reported busy. No edit/provision/publish request was issued. User was asked
to confirm intended project. Auth/storage/DB/runtime/current credits not verified.

Replit-first is still being evaluated. A timeout is not proof that PostgreSQL,
storage or Python cannot work there. Railway remains an unimplemented fallback,
not a second host. Selecting a durable host requires project access, actual DB/
bucket or volume, worker access, current plan/credits and acceptance evidence.
No billing upgrades or new services are authorized by this handoff.
