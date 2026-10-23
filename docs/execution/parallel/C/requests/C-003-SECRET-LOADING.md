# C-003 — secure Groq runtime loading handoff to A

C1.1-R02 adds `minder_app.config` and wires it to actual API `runtime.application()` and worker CLI. No dependency/shared schema change. Merge the committed refinement normally; never copy C's secret file or credential values.

The private file is `.env.groq.local` in the current worktree root. C path: `/Users/phuahjunhong/sdc-2026-minder-worktrees/session-c/.env.groq.local`. A should use its own worktree's equivalent path, created locally with owner-only permissions. Existing `.env.*` ignore already covers it. Do not commit, print, attach, inspect in diffs, or source it as shell code. Default loader uses O_NOFOLLOW, owner/regular-file/0600 checks, a size limit and allowlisted literal assignments. Existing files are never overwritten by setup.

Variable names only: GROQ_API_KEY, GROQ_MODEL, optional MINDER_LLM_DAILY_LIMIT. The user enters the key directly in their editor; never request it in chat. Model may remain blank until authorised discovery/selection; no invented model default. MINDER_GROQ_SECRET_FILE optionally selects an absolute owner-controlled file. Inherited nonempty provider variables take precedence. Secret values are passed directly to GroqAdapter, not exported globally. Config repr and error messages are redacted.

No special shell export is needed. After the user's configuration confirmation, restart the API/worker through their existing commands; both use the same loader. Preserve lane-specific ports/database paths and never point A at C's live database. The C runtime/worker DB guards remain C-scoped; A's deployment binding should coordinate its own namespace.

C verified placeholder ignored/untracked/0600 and 23 local tests; no configured real request or restart claimed at this checkpoint. Real model/chat/native tool-calling, action approval/persistence and actual scheduled event checks follow confirmation. No credentials or secret-file contents in this handoff.
