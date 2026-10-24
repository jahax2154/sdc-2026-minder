# A-N6.1-R01 — converge early D/E exports without a lane rewrite

Refines ecee95404d63a818e24f87a08643a40d086c6716. D's early message exported the
explicit PostgresStore(DATABASE_URL,schema=...) constructor with persistence_mode
postgresql. E then reported D alignment to from_environment()/managed-postgresql.
Both name the same required PostgreSQL backend, not a permission for SQLite.
A now prefers D's callable from_environment() export when present; otherwise it
uses the explicit constructor with trusted DATABASE_URL/MINDER_DB_SCHEMA. Require
engine=postgresql and persistence_mode in {postgresql,managed-postgresql}. Unknown
markers and SQLite still fail closed; no credential/DSN is logged or Path-converted.
E's wrapper should accept the same two explicit PostgreSQL markers or use D's final
committed managed marker; the actual committed D handoff determines the final form.

This is backward-compatible composition, not SQL translation or hosting evidence.
205backend tests pass13.699s, including seven declared-adapter wiring/fail-closed
checks. No actual PostgreSQL/provider call is made by these checks. Real native PG,
private bucket, restart and managed-auth acceptance remain required with D/E.
Approved pins remain psycopg[binary]==3.3.6, replit-object-storage==1.0.2; isolated
D test-only pgserver==0.1.4 without extras. No package is installed/upgraded by A.

E e8ae2ca is integrated at88684b2;11deploy checks pass. E's ec0b089 merge only
integrates already-present A7d4073f/c5ea43a plus e8ae2ca; its source integration
history is preserved on E, and A has those file changes. New Replit runtime wrapper/
lock/template work is still awaiting a committed E handoff. D currently integrated
7d4073f but has no committed PG implementation in A. Do not claim either adapter is
already live. Frontend remains62fb94f, first browser failure step2 unchanged.
