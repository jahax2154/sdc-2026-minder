# Mandatory phase checkpoints, refinement loops and no-push policy

Pack revision: 2. These rules implement the architect's latest instruction and apply to every session, including bootstrap, optional D and integration. They supersede any earlier execution-prompt wording allowing a push under previous general authorisation.

## Required loop

For each phase: read its contract/dependencies -> implement the bounded output -> verify the relevant behaviour -> fix identified implementation defects within that scope -> record evidence/status -> create a local Git checkpoint commit -> report its SHA -> continue to the next eligible phase.

The large sections in each lane prompt describe the work; its checkpoint table defines the smaller phase boundaries. Do not postpone all commits until the entire lane finishes. A phase should normally have one coherent service capability, data transformation, experiment or integration result with a reviewable diff. Aim for roughly 30–90 minutes of active work per phase where practical; this is a sizing guide, not a timeout for training or permission to rush validation. Split an unexpectedly broad phase into recorded child IDs before continuing. More intermediate commits are allowed.

Each phase ends with a truthful local checkpoint. A completed workstream also ends with a culminating handoff checkpoint recording its finished, limited, blocked and deferred work. Final integration ends with a culminating release-readiness checkpoint. These commits do not imply every feature passed.

## Phase state and evidence

Use explicit states: `not_started`, `in_progress`, `passed`, `limited`, `blocked_decision`, `blocked_external`, `failed_check`, `deferred_dependency`, `already_satisfied`.

- `passed`: that phase's required behaviour was actually verified.
- `limited`: a stated portion is working; identify the unmet acceptance items. This is not a full pass.
- `blocked_decision`: a genuine unresolved human/product decision is necessary.
- `blocked_external`: inaccessible credentials/service/data or another external dependency prevents the output.
- `failed_check`: an implemented output failed a required check; do not merge it as passing.
- `deferred_dependency`: the phase cannot run because an earlier output/decision is missing.
- `already_satisfied`: existing implementation was verified; cite its existing commit/evidence rather than manufacturing an empty commit.

Record phase ID, owner, branch, objective, inputs/contracts, changes, exact checks and results, actual coverage, limitations, dependency IDs, decision request if any, and next eligible work. Keep the record in a lane-owned report/ledger path mapped by G0. Do not have all sessions write one ledger concurrently.

Include the phase record in the checkpoint commit. Obtain the SHA after committing and report it to the user/handoff. Avoid a self-referential SHA loop: the record can identify its checkpoint as 'the commit containing this phase record'; the handoff/final report carries the resulting real SHA. Update indexes on the next natural checkpoint instead of repeatedly amending just to insert a hash.

## Local Git checkpoints

Before committing, inspect status/diff, stage only owned relevant files, and exclude credentials, private data and unrelated work. Commit the code plus applicable tests/config/report needed to understand the phase. Test failures may be captured in a clearly labelled work-in-progress checkpoint on the lane branch, but that checkpoint does not pass the gate or become integration-ready automatically.

Suggested traceable subjects:

- `feat(A1.2): implement personal role-fit service`
- `data(B1.1): load supported Malaysia observations`
- `test(B2.2): record forecast backtest and model comparison`
- `fix(A1.2-R01): correct missing-evidence handling`
- `docs(C2.3): record blocked provider access and completed local checks`
- `chore(I2.4): checkpoint integrated release readiness`

Use accurate types/subjects, not a mandatory vocabulary that forces empty commits. If Git author configuration or hooks prevent a commit, do not invent an identity or bypass controls; preserve work, report `checkpoint_failed` with the reason, and continue safe independent work. Never claim a SHA for a failed commit.

## Refinement and fixing stay attached to the original phase

An implementation defect discovered while a phase is in progress is fixed in that phase's loop. After a checkpoint exists, name a focused repair `PHASE-ID-R01`, then R02 and so on. Record the original phase ID, defect evidence, root cause, narrow change, regression check and resulting fix commit. Do not reopen the whole lane or disguise the refinement as a new unrelated architecture gate.

Example: A1.2 passes; C integration finds that a missing preference became zero skill. Create A1.2-R01, correct that behaviour, rerun the relevant service/contract check, commit the fix and hand it to the integrator. Preserve the earlier commit. Only expand scope when evidence shows a wider dependency, and document the reason.

Repair loops are evidence-driven. Do not rerun the same failed operation indefinitely or rewrite the architecture without diagnosis. If no further progress is possible without a human decision or external resource, record that blocker and move to another eligible phase.

## Human decisions: defer only dependent work

The instruction to skip human-dependent tasks means defer them, not mark them done or remove their requirement. Prepare one concrete decision entry with the precise question, relevant evidence, recommended option, affected phases, and work that can proceed independently. Do not invent an answer, quietly weaken a policy, substitute fabricated data or bypass approval controls.

Checkpoint safe completed work, mark dependent phases `blocked_decision`/`deferred_dependency`, and continue eligible work. Ordinary debugging, choosing a technical implementation within settled rules, and running agreed checks are Codex work—not a reason to ask for permission. When the user resolves a question, resume the original phase or a linked refinement rather than restarting everything.

## Push policy — explicit later instruction required

Create local phase commits now. DO NOT push to GitHub or any remote until the user explicitly instructs a push. Do not infer permission from this pack, the deadline, checkpoint creation, previous general backup wording, remote configuration, or authorisation to implement.

Do not invoke IDE auto-sync, a PR flow that pushes branches, mirror/backup pushes or automated remote updates as a substitute. Read-only remote inspection is permitted. Local branch merges and local release-readiness checkpoints remain part of the authorised work.

If the normal deployment requires a GitHub push, prepare and verify the release locally, then report deployment waiting on the requested push. Do not bypass that boundary. An independently authorised deployment path that does not push Git is distinct, but report it truthfully and do not use it to conceal an unapproved push.

After an explicit push instruction, verify the intended remote/branches and push only the requested scope. No force push or history rewriting unless separately authorised.

## End-of-run handoff

Return one table per lane: phase ID, status, actual delivered behaviour, verification, checkpoint SHA, refinement IDs and blockers. Then state current branch/HEAD, remaining uncommitted changes and why, actual model/service readiness, exact deferred decisions, next runnable phases, and `Push status: not pushed — awaiting explicit instruction`.

Do not end at 'all tests passed' or 'implementation complete' without phase/evidence status. Do not automatically stop after every successful phase; continue the assigned eligible work until complete or only blocked/deferred phases remain.
