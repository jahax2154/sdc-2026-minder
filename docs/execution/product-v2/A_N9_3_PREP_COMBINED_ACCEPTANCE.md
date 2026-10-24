# A-N9.3-PREP — bounded combined acceptance harness (not a passing result)

The completed source31e85cb and three actual UI answer passes are preserved.
This harness-only refinement prepares one fresh normal-onboarding journey to
exercise the remaining Explore saved-schedule visual assertion on the latest
served revision. No product code, frontend file, identity control or model changes.

MINDER_APPROVAL_ONLY=1 reuses the actual rejection/idempotency evidence in A-N9.0
and runs one approval/visible-saved-change path in this fresh journey. F's original
onboarding/plan/four-view/completion assertions remain intact. A's added approval
checks still assert no change before approval, one singleton notice, exact replay,
actual saved diff and Explore task-detail schedule after refresh. Restart then
checks the accepted canonical state and histories. It does not invent a rejection
case in this new account.

MINDER_CORE_ONLY=1 reuses the separate real-provider market evidence rather than
spending three redundant model calls. It explicitly records that the market cases
are not run in this core check. MINDER_ACCEPTANCE_START_AT permits a bounded wait
BEFORE starting the journey to reserve the next actual shared-quota window, with
no artificial pause between the user's turns. Any native failure still fails the
assertion; no retry/success stub or profile/plan fixture is introduced.

JavaScript syntax verification PASS. The new combined browser execution is pending;
this is a test-preparation checkpoint, not evidence that the remaining gate passed.
