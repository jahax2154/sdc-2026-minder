# ME2-R01 — actual canonical worker refinement, local acceptance

Cumulative follow-up to published E ME2
`dc2d644c7cafb36e7e9d8f821013c59493549a2f`. Includes D automation
`3299176066dcee3e2f5244986e04affc19994c8f`, D portable backup fix
`24f0061cf4413a5fafc8a583ffe9bf9208cfdee0`, A worker hooks
`e3404103182c58898de5b6519d9dcdd72cc25527`, A failure-result fix
`9a69058b1a7bb7e7c13f2902b8ed0ee34eee3038`, and A/F integrated snapshot
`7ccdd6b6163998464349733284716d7504524893`.

E changed only owned worker tests, deployment guards/docs and this record. The
existing A Worker remains the scheduler; D remains the only persistence writer.
No new queue, scheduler, profile/task store, SQL or source acquisition.

## Observed actual Worker checks

Seven focused worker tests pass using real Store/ActionExecutor/Conversations and
the actual Worker.tick/daily methods. All users/documents are synthetic and clocks
are explicitly controlled test inputs, not real hosted runs.

- One due event with no browser stores one notice and one assistant message in the
  user's same Mindbot singleton. Repeating tick does not duplicate it; opening
  through a new Store instance preserves identical history.
- Paused settings suppress a previously queued event. Explicit cancellation also
  invalidates an in-flight analysis lease: the tick reports cancelled, stores no
  notice/message/action and cannot commit a stale proposal.
- Failed analysis retries three times then reaches failed; the canonical settings
  last_result records the actual terminal failure. No fabricated success message.
- Saved Asia/Kuala_Lumpur schedule timezone is honored independently of a UTC
  profile timezone. Missing two days produces one current due event, not a backlog;
  next_run advances to the next actual local09:00 and last_result resolves to the
  existing conversation/message ID.
- A selected owned empty plan excludes another owned plan's overdue task from the
  daily analysis/proposals. No task outside the explicit daily scope is proposed.
- Wrapper stops cleanly and logs only status/code, never private notice fields.

The checks caught two real A integration gaps: profile-timezone use instead of
schedule timezone, and missing failure metadata after exhausted retries. A fixed
those in its own committed worker files. E integrated the named commits; no active
sibling files were copied. Tests also anchor initial schedule creation and retry
reenabling to explicit fixture time, preserving the real next_run guard. The earlier
A MA2 findings about E's inconsistent-clock fixtures are resolved by this checkpoint.

## Candidate and recovery refinement

Production startup now refuses disabled/non-volume CV storage or document paths
outside the private mounted volume, in addition to the existing database/identity/
provider gates. D backup fix makes a new SQLite online snapshot readable standalone
without writable WAL sidecars; E's maintenance command uses that unchanged D API.
Use the current deploy/README.md and runtime.env.example; the selected single host
remains Railway, with same-instance HTTP/worker and one volume.

Final local verification: **146 backend tests passed, zero skips**, with the official
Clerk SDK and pypdf installed in E's isolated Python3.12 environment; **4 deployment
candidate tests passed**. Loopback concurrency tests ran under the necessary sandbox
permission. The equivalent Docker filesystem smoke again passed with1016actual
catalogue roles, four hash-pinned untracked O*NET CSVs, real resource metadata and
canonical policy. It explicitly reports hosted=false/docker_build=false and made
zero provider calls. No numerical/model/forecast policy changed.

```sh
PYTHONPATH=ml/src:apps/backend-api:apps/backend-api/tests /private/tmp/minder-e-auth-py312/bin/python -m unittest test_hosted_worker
PYTHONPATH=ml/src:apps/backend-api /private/tmp/minder-e-auth-py312/bin/python -m unittest discover -s apps/backend-api/tests
/private/tmp/minder-e-auth-py312/bin/python -m unittest deploy.test_candidate
PYTHONPATH=ml/src:apps/backend-api /private/tmp/minder-e-auth-py312/bin/python -m deploy.verify_package
```

## Remaining hosted boundary

This closes the independent local cancel/retry/timezone/scope/singleton checks; it
does not waive actual hosted acceptance. Railway account/project/credits/volume
access and Clerk provisioning/two live accounts remain unavailable. Actual Linux
image build, provider cost check, live login/expiry/logout, private persistence and
backup recovery across restart, and a due daily check with browsers closed must run
on the chosen target. No judge deployment or new billing resources were created.
User already authorizes scoped publication after A's integrated acceptance within
existing verified resources; no repeat generic permission is needed.

Original untracked raw/derived inputs, private config, runtime DB/uploads and local
SDK/artifact checks remain excluded and are not backed up by these source commits.
