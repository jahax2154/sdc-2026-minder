# Feature scope

Status: **PROPOSED** product boundaries, pending team approval. **APPROVED** task constraint: represent exactly these five user-facing areas; do not add features.

| Product area | Proposed responsibility | Web feature / API modules |
| --- | --- | --- |
| User Profile | Skills and competencies, interests and goals, experience and education, preferences and learning constraints | `profile` / `profiles` |
| LLM Chat | Career conversation and context-aware explanations using user context and validated information | `chat` / `chat` |
| Personal Agents | Personal workspace, bounded automated review and task proposals, execution history and status, user-controlled acceptance of proposed changes | `agents` / `agents` |
| Dashboard | Career and AI market insights, progress tracking, actionable execution tasks, roadmaps, progress visualizations and detailed drill-down interactions | `dashboard` / `dashboard`, `trends`, `roadmaps`, `progress` |
| Career Explorer and Simulation | Role recommendations, skills gaps, alternative futures, what-if simulation, projections and explanations | `career-explorer` / `explorer`, `matching` |

## Logical relationships

**PROPOSED:** Profile context informs chat, matching, exploration and agent proposals. Explorer outcomes may inform roadmaps and dashboard tasks. Dashboard brings together trends, roadmaps and progress; chat explains recommendations using validated evidence. Personal agents propose bounded actions with user acceptance controlling proposed changes. Exact transitions and acceptance rules are **PENDING** mockup and team review.

Matching and decision models, ML inference, market evidence, scenario computation, SDG mappings, persistence and integration contracts are cross-cutting capabilities, not additional product areas. Evidence sourcing, SDG mapping criteria, persistence boundaries and model behavior remain **PENDING**. No finalized design or functionality is specified here.
