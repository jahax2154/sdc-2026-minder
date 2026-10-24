# A-N4-R02 — writable provider coordination on Linux/Replit

Refines dd843cedf335e0507441813f068625592d7808fe for the current Replit hosting
handoff. The existing default /private/tmp path is macOS-specific; a non-root Linux
runtime could not create its /private ancestor. Preserve that exact existing macOS
coordination group when present, otherwise use tempfile.gettempdir(), preserving
the same private per-UID/group/model locks. Explicit server coordination directory
still takes precedence. No secret, quota policy, model or retry/action change.

Five focused gateway checks pass0.209s, including mocked Linux/macOS directory
selection, real cross-instance file locking, quota no-call and no429retry. No native
model request, filesystem provisioning or deployment is made by those checks.
This does not turn same-host file locks into a distributed quota service.
