# MD1.2-R01 — first-read portable SQLite snapshot

During actual D pre-upgrade backup verification, a fresh backup's first read-only
URI open failed ('unable to open database file'). A subsequent normal SQLite open
verified the expected schema1–5; source data and backup contents were intact. A
fresh synthetic reproduction confirmed the initial read-only failure with the old
backup helper. SQLite backup inherited WAL mode without ready sidecars.

The helper now switches only the destination snapshot to journal_mode DELETE after
online backup, before closing. Source WAL behavior is unchanged. Regression opens
the fresh backup read-only BEFORE any normal restore/open, checks delete journal
and its row count; overwrite prevention and600 permissions remain.8 focused storage/
migration tests pass. The new-process morning persistence runner also passed.
No backup/file was discarded or prior result rewritten. This is a linked refinement
of MD1.2, not a database conversion or hosted restart claim.
