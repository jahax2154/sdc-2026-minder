# A-N6.2 — integrate E's selected-host safety guard

Exact E handoff e8ae2ca0af654db15d66d5c381a56db2046340e6, descendant of the
already integrated d6b18e3, changes only deploy/operator.py and its tests. Reviewed
and integrated missing changes with a normal merge preserving E/A history. No
worktree changes from E are staged.11deploy checks pass0.138s in
replit-e-me5-merged.log. With MINDER_HOSTING_TARGET=replit the operator does not
require Railway account fields and rejects Railway inspect/prepare-service/deploy
before making any Railway call. Existing private config stays untouched.

E reports a newer ec0b089b4c17821c7d05adbf5110638f8dae4a2e integration checkpoint
and prepared Replit wrapper/dependency work. Integrate only its committed missing
files after review; do not infer uncommitted prepared work is present in A. Existing
legacy Replit app is not Minder. This checkpoint does not publish an app or waive
native PostgreSQL/private CV, Clerk or F's remaining product acceptance gates.
