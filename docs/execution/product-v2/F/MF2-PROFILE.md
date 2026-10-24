# MF2 Profile / reviewed CV integration

Depends on D ab0a8f852171553074c990e80e6722e6b75af656 and prior A fa1130a.
Static wording/icons and scoped CSS come from the committed approved profile-v2.
Three adaptive questions, optional enrichment, explicit review then Overview; no
fictional identity or sample data. Five returning tabs, centered initials identity,
focused Save/Cancel, dirty navigation/back/forward guard with Stay/Discard, one open
record accordion. Profile metadata saves against actual expected version. Uncertain
saves lock until server reload. Self-reported Learning/Practicing/Confident is text
Evidence using the existing explicit-user-statement contract, never a new numerical
rubric. Anchored assessments retain their original API/source meaning, secondary UI.

CV/resume upload requires explicit purpose; only actual server extraction capability
is advertised. TXT and text-PDF extraction stay a draft until corrected review/save;
scanned/unsupported extraction shows exact reason and manual entry. Existing uncertain
review editor lock and exact idempotent retry survive the new layout. Attachment
bytes/private state never enter browser persistent history or committed artifacts.

Actual browser tests morning_profile.cjs passed adaptive answer preservation,
onboarding persistence, five tabs, dirty Stay, inline save/refresh, self-report
separation, resume purpose, no extraction mutation, explicit TXT review/save, actual
text-PDF extraction and blank/scanned unavailable, mobile no document overflow, no
page errors. morning_document_retry.cjs passed again through profile/record/files:
one real mutation, two identical exact requests, unchanged profile version/no mastery.
No provider call needed by these profile/document tests. Syntax/diff checks passed.

F-only PDF dependency installed under ignored ml/artifacts/session-f/product/python-deps;
shared Python environment unchanged. Include that path in local PYTHONPATH (or install
A root requirements in the chosen host). Synthetic fixtures created with frontend
/tools/make_cv_fixtures.py into private temp output, not source/Git.

Actual UI http://127.0.0.1:9106/#profile. Local screenshots:
/private/tmp/minder-f-morning-profile/profile-onboarding.png, profile-overview.png,
profile-cv-record.png, profile-mobile.png. JSON evidence adjacent. Existing old test
selectors for #save-profile are superseded by approved onboarding; F retry/explore
fixtures now seed their partial profile via the actual API then navigate approved UI.
No deployment or hosted durability/managed-account claim. Unrelated ML inputs remain
excluded/untracked and were not backed up by F.
