# A common auth route handoff

Actual E dependency3c32027b60b01320e4c6d4e90d12da0b66128407 integrated;
M0/MA1 contracts remain. A implements identity_boundary.py/API insertion.

GET /api/auth/config is public and returns E public_config() plus mode local|managed
and anonymous_session_allowed:boolean. F must call this before bootstrap. In local
mode only, existing POST /api/session remains available; local demo isn't real login.
In managed mode F uses configured public ClerkJS and sends current session.getToken()
on each API call. GET /api/auth/session requires verified identity and returns
{authenticated:true,user:{id:server_owner},mode:managed|local}. 401 sign in; 503
unavailable must not fall back to anonymous. All private endpoints use same identity
boundary. API no cookies/CORS; frontend same origin. Origin is server-extracted
HTTP Origin header, never supplied JSON owner. D maps verified identity; A expects
identity_store.resolve_owner(store,VerifiedIdentity)->owner string and will adapt
to D's actual committed signature if necessary. Never claim prior anonymous records.
MINDER_ENV=production OR MINDER_AUTH_PROVIDER=clerk enforces managed boundary.
POST /api/session then401 managed_sign_in_required even when auth not configured.
No SDK/key config means503 on private reads, not anonymous access.

D/F may merge the containing checkpoint without waiting for generation acceptance.
Root recorded Clerk7 dependency for Python3.12 in morning-requirements.txt. E owns
actual deployment requirements/config/worker. Actual live accounts/credentials and
host resource access are unavailable until provisioned; signed software JWT tests
are distinct from live managed login. No deployed URL readiness is claimed.

E hosted factory now product_runtime.build_hosted(database)->Application. Requires
MINDER_ENV=production and explicit existing MINDER_DATA_ROOT outside source checkout;
database must resolve below that root. E wrapper alone verifies actual durable mount,
backups, worker shared-volume access and restart survival; directory existence is
NOT durability proof. Same provider/model/services/migrations/common auth boundary.
Use existing ProductServer+web_app; no second framework/anonymous backend. Hosted
credential server-only environment/secure loader, no local-file requirement.
