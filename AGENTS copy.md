# Minder — Repository working instructions

## Read the right context

Follow the current user task and existing authorisation. Read [README](README.md) for orientation, then the document that owns the work:

- Product scope and acceptance: [PRD](PRD.md).
- Boundaries, stack and interfaces: [Architecture](docs/ARCHITECTURE.md), especially [API contract](docs/ARCHITECTURE.md#api-contract).
- Modeling and evaluation: [ML Design](docs/ML_DESIGN.md).
- Data provenance and refresh: [Data Sources](docs/DATA_SOURCES.md).

Consult additional documents when a change crosses their boundaries. Do not load every document into every task or duplicate whole specifications in prompts. Treat `CONFIRMED`, `PROPOSED` and `OPEN` separately; documenting a proposal does not approve it or prove implementation.

## Before changing code

Inspect the relevant code, manifests, existing conventions and instructions. Check the current branch, repository remote, worktree status and diff before Git operations. The remote URL in the actual checkout establishes where work will go; do not guess it from a project name.

Preserve unrelated work. Use separate branches and working copies/worktrees for concurrent writers; coordinate edits to shared contracts. Keep the team's established roles. Make focused commits and review changes through the existing pull-request workflow. Do not rewrite teammates' history or force-push a shared branch.

The stack remains open until the team records its decision. Continue authorised, reversible and stack-neutral work; ask only when a consequential unresolved choice blocks that task. A documentation proposal is not permission to migrate the application or replace its framework.

## Implementation rules

Keep frontend rendering, API orchestration, reusable career logic and offline training separated as described in Architecture. Adapt the proposed paths to the inspected repository; do not create empty infrastructure for future features.

Use the agreed API contract. When changing a request, response or shared type, update affected callers and relevant checks together. A temporary mock must be explicit and contract-aligned; never quietly substitute it for real integration. Shared recommendation versions must mean the same thing across Chat, Explorer and Dashboard.

Use the same versioned transformations during model training and serving. Distinguish transparent baseline results, trained-model results, synthetic data and scenario estimates. Do not present a matching index as employment probability. Follow [competition constraints](PRD.md#competition-constraints); keep source references and required disclosures intact.

Keep secrets, personal data, large raw datasets and model weights out of ordinary commits. Record environment variable names and artifact references safely. Add dependencies only when the task needs them and the selected stack supports them.

Record material AI/tool assistance, third-party code and pre-existing contributions in the relevant change description and declaration inventory. Preserve attribution; do not invent personal ownership or workshop-completion attestations.

## Verify and report

Run relevant existing checks for the changed behaviour. Add tests when they protect meaningful behaviour or a concrete regression risk; documentation-only changes do not require a new application test suite. Check internal links and consistency when editing these documents.

Use actual commands from the repository and report what ran, its result and what remains unverified. Do not invent passing tests, benchmark numbers, completed training, deployed URLs or fulfilled gates. Inspect the final diff for accidental scope expansion, generated junk and unrelated edits.

Update the document that owns a changed decision. Keep README setup and evidence links accurate. End a task with the outcome, relevant verification and remaining decisions; do not impose blanket approval steps for routine authorised work.

## Consolidate existing documentation safely

Before replacing the current documents, read their full contents. Merge unique scope/mockup material into PRD; workflow into this file; interface, stack and decision records into Architecture; modeling into ML Design; provenance into Data Sources. Move general orientation to the root README.

Retire an overlapping file only after preserving its unique content and updating inbound links in the same change. Keep an additional document when it has an independent owner or lifecycle, such as a generated API schema or a necessary long-form decision record. File count alone is not a deletion criterion.
