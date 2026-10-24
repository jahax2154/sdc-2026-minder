# MA1-R08 — typed daily automation tools and failure trace

Typed real-model operation configure_automation now executes through the SAME
ActionExecutor authority/proposal/idempotency/audit as task/profile changes. Its
allowlist covers state/time and an explicit owned plan scope. Current observed
schedule version is captured before provider, exact current-user command required
for direct write, inferred improvements create immutable reviewable proposals.
Creating a check without an essential time asks rather than guessing. Pausing,
resuming and cancelling preserve settings/history and invoke D's validated writer.

D's writer runs on the executor's existing transaction via a narrow transaction
adapter; preview uses a SQLite SAVEPOINT then rolls back EVERY tentative setting,
authority and queue change. No provider/side effect occurs in D's helper. Proposal
preview therefore has no saved state effects; approval revalidates actual expected
version, then commits D settings and common action audit atomically. No second
scheduler or settings copy. Schema additions are typed AutomationScope and action
kind only; numerical policies remain unchanged.

Worker retry/failed path now records actual D last_result ONLY if it still owns the
lease. If cancellation invalidated that lease, it returns actual current status and
never overwrites cancelled state with retry. No success notice for failed analyses.
Software checks cover direct create/pause/resume/cancel, inferred proposal with no
state/history change, approval, failure/retry metadata and stale edits during pending
provider. Existing typed task/profile and legacy action checks stay compatible.

Generated practice advice remains distinct from empirical facts. Current advice-v1
fact_ids is empty; unknown references at acceptance fail closed rather than being
dropped. A source-reference extension must revalidate original role scope/description.
Local model choices are not a new numerical policy or independent labels.

Local SDK/PDF dependencies now installed only in A ignored runtime-venv, Python3.12.15,
Clerk7.0.0,pypdf6.21.2,jsonschema4.26.0 from committed E lock. Shared3.9 environment,
other lane config, credentials and source inputs untouched. This enables actual local
PDF/SDK checks, not live Clerk provisioning or mounted hosted acceptance. New environment
is excluded from Git and not a new private-state backup claim.
