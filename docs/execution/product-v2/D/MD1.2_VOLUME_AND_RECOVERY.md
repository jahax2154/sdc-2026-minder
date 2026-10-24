# MD1.2 — SQLite volume boundary and restart reconciliation

Dependencies: MD1.1bbe4e1b, E3c32027, Afa1130a86337e13a27d74e28da0200570a2331dd.
Schema remains7. E selected one Railway single-instance candidate, preserving
existing SQLite; Replit current app is an old React/Express mockup without a
verified durable DB/bucket. No PostgreSQL URL/conversion is claimed or implemented.
Real Railway account/mount/backups/restart/login access remain pending.

Store.on_volume(mount_root,database=None) or Store(path,volume_root=mount_root)
requires a canonical absolute actual mounted directory and a DB inside that mount.
Default path /data/minder/runtime.sqlite3. Every subsequent connection rechecks
mount availability and fails closed if absent. Development Store(path) remains
explicitly persistence_mode development/durability_status local_unverified.
Mounted Store reports mounted-sqlite/mount_verified_restart_pending, not hosted
acceptance. Store.engine is sqlite. No environment flag alone asserts durability.

PrivateVolumeDocumentStorage reuses the existing private0600/0700 byte adapter,
checks same actual mount on every operation and rejects paths outside it.
MINDER_DOCUMENT_STORAGE=private-volume requires Store.volume_root; root defaults
beside DB at /data/minder/documents. MINDER_DOCUMENT_STORAGE_ROOT may select another
private path within that volume. Library reports mode private-volume and pending
restart verification, with durable_hosting_verified:false. Local-development remains
separate and never becomes hosted proof by relabeling an environment variable.
A/E must invoke the guarded Store in the hosted factory, not merely check path
containment. No production volume is currently accessible for a real acceptance run.

Store.backup(absolute_new_path) performs a SQLite online backup to a new0600 file,
never overwrites an existing snapshot, and preserves versions/owner IDs. This is a
DB snapshot, not backup of separate CV bytes or proof of hosted backup scheduling.
No existing local user DB was converted/copied/imported; anonymous data stays local.

Compatibility identity_store.resolve_owner aliases actual owner_for_identity,
requiring E VerifiedIdentity. D global conversations.append_notice(store,owner,
event_id,db=None) is safe inside A's existing completion transaction; no nested
migration writer is opened. Afa113 constructs its class service outside transaction,
also safe. reconcile_notices(store,limit=50) finds already-persisted notices not linked
to history and appends each once; returns counts, does not execute jobs/provider.
E invokes on startup/recovery. Source notice/event records remain canonical.

A's now-canonical DocumentUpload requires purpose cv|resume. Synthetic upload test/
runner bodies were updated to that required field; no shared schema was edited.
CV-purpose metadata/extraction refinements follow MD2, not silently assumed complete.

27 focused conversation/identity/migration/library/storage checks passed. Mount
acceptance uses an explicit software mount fixture (not real hosted evidence),
rejects a normal temp directory, tests loss of mount and outside paths, and verifies
online backup/refetch. Notice recovery test proves inline existing-transaction append
and restart reconciliation without replaying jobs. Pending real hosting cannot be
closed by these tests. Full integrated suite result is recorded at checkpoint run.

Integrated verification:116 discovered,112 passed/4 Clerk SDK skips on legacy3.9.
Loopback tests ran with required sandbox permission. No live host/provider claims.
