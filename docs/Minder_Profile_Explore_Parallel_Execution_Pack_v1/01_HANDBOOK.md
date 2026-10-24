# Operating handbook

## 1. Recommended team shape

Start three new sessions, D/E/F, alongside the running A/B/C. This gives six concurrent lanes. Extra sessions are useful only after files and interfaces can be separated.

| Lane | Main work | Shared boundary |
| --- | --- | --- |
| A | Bootstrap, shared-contract coordination, integration and final acceptance | Sole integration coordinator; retains scoring ownership |
| B | Existing market evidence, mappings, real/synthetic experiments | No product UI or duplicate product persistence |
| C | Existing LLM/provider/grounder/agent continuation | Exports contract; does not build intended UI |
| D | Profile, goal/plan/task/resource user state and ordered migrations | Extends existing C domain services after ownership handoff |
| E | Explore response composition and news/resource retrieval adapters | Reads shared services; requests persistence through D |
| F | Shared frontend shell/client/components and product screens | Sole frontend writer by default |
| G, optional | Assigned Profile/Explore page components | Only after F's foundation and explicit non-overlapping assignment |

Do not create one agent for each table or each screen. Dependencies and review cost can outweigh parallel execution.

## 2. Launch waves

Wave 0: send A the bootstrap continuation. C/B keep working. D/E/F may read context and inspect design sources. A records exact ownership and publishes a committed starting point without waiting for forecast research.

Wave 1: after P0.3, D/E/F implement concurrently. E uses agreed interfaces and isolated contract fixtures while D finishes specific operations; F does the same for presentation. Fixtures are explicitly development-only.

Wave 2: D releases profile/state slices; E releases view/resource slices; F wires those real endpoints progressively. C's frontend contract is consumed when available. A integrates named committed deliveries incrementally.

Wave 3: optional G begins only after F0.2 exports the shared components/client and A/F record page ownership. Without G, F completes those same pages.

Wave 4: A verifies the combined product journey with real APIs. F handles visual corrections; D/E/C fix their owned defects. Close the release handoff and publish task-scoped checkpoints. Deployment remains a separate action.

## 3. Phase ledger

| Owner | Phases | Culminating checkpoint |
| --- | --- | --- |
| A bootstrap | P0.1 inventory; P0.2 contracts/ownership; P0.3 isolated launch | Committed, pushed usable base and exact launch table |
| D | D1.1 persistence; D1.2 profile/intake; D2.1 plan/task operations; D2.2 progress/resource state; D3.1 handoff | Persistent state works through real APIs and shared services |
| E | E1.1 read adapters; E1.2 Explore views; E2.1 resources/feed; E2.2 real integration; E3.1 handoff | Source-backed views and feed with honest missing states |
| F | F0.1 design/source inventory; F0.2 shared UI/client; F1.1 Profile/Career Match; F1.2 remaining Explore; F2.1 Minder; F2.2 Mindbots; F3.1 acceptance | Intended product UI against named real backend revision |
| G optional | G1.1 profile/matches; G1.2 tasks/progress/roadmap; G1.3 feed; G2.1 handoff | Only assigned page components; F registers/integrates |
| A integration | PI1.1 backend slices; PI1.2 frontend/LLM journey; PI1.3 reproducible handoff | Combined acceptance and verified remote SHAs |

Repairs use identifiers such as `D2.1-R01`. Do not confuse a repair with a new product phase. Reuse completed equivalent work and document it rather than rewriting code to create a checkpoint.

## 4. Dependency handling

Missing HTML blocks faithful reproduction of that particular design. It does not block schema/API work, frontend source inventory or shared components. F can build Profile/Explore with available approved design references while Minder/Mindbots references are pending. Do not invent a claimed approved design.

Missing forecasts block forecasts, not current evidence, tasks, profile or chat. Missing independent accuracy prevents accuracy claims, not implementation acceptance. An unavailable operation must be visible and recorded, not replaced by mock success.

If the backend is one tightly coupled file, D/E must serialize those edits or D performs E's backend scope. Do not launch a major rewrite just to manufacture parallelism. F remains independent. Likewise, if the frontend remains one HTML file, keep one writer until a small maintainable separation exists.

## 5. Working without accidental interference

Every lane has its own directory/branch, database, ports, logs and test artifacts. File ownership is exclusive even across different worktrees. Central routes, lockfiles, migrations and shared styles each have one named owner.

A integrates committed snapshots, never another session's in-progress directory. It can integrate an earlier bounded delivery while that owner continues independent work. Shared interface changes need coordinated adoption, not constant rebasing of all lanes.

On a real decision gap, record the exact affected operation, proposed options and safe current behavior; continue unrelated work. Routine implementation choices use engineering judgment. Do not repeatedly ask for previously authorized commits or scoped pushes.

## 6. Progress reporting

Report capability outcomes and their dependencies, not only test counts. Use `13_STATUS_AND_HANDOFF.md`. Keep implemented, tested, committed, pushed, integrated and deployed distinct. A successful unit test cannot establish that the intended UI works against a real backend.
