# Minder D01–D09 — canonical product and AI/ML decision context

Date: 22 October 2026 (Asia/Kuala_Lumpur)
Content revision: 6 (23 October 2026; bounded numerical delegation below). Consolidated D01–D09 context, incorporating final market-presentation/agent-authorisation decisions and mandatory per-phase local checkpoints, linked refinements and push-only-on-explicit-instruction. Read this revision as a whole; do not maintain duplicate decision files.
Purpose: Give implementation agents precise product decisions, derived engineering rules, required outputs and remaining dependencies. Presentation and agent-authorisation policies are now confirmed. Exact numerical scoring specifications and operational facts still require repository/data work; do not claim they were settled merely by resolving presentation or permissions.
Basis: The architect's statements in the current conversation. The actual repository, current schemas, acquired datasets, and running model have not been inspected in this task.

## Current numerical implementation authority — 23 October 2026

The user delegates provisional numerical weights, normalization, evidence coverage,
missing-data handling and the personal/current-market combination to Session A
within the seven requirements in the current task. This supersedes waiting for
approval of the original N01 proposal for those bounded choices. N01's original
proposal remains historically unapproved and is preserved unchanged. Its clearly
versioned replacement is N01-R1, `personal-role-fit-v3-provisional`, documented in
`docs/execution/parallel/A/RECOMMENDATION_POLICY_V3.md` and machine configuration
`ml/configs/intelligence/personal-role-fit.v3.json`. Engineering must implement and
verify it rather than asking for coefficient-by-coefficient approval. Provisional
scores are not empirically validated competence/hiring probabilities. Current
Malaysian evidence must influence comparable ordering independently of unavailable
forecasts; unsupported market coverage is explicitly partial, never zero demand.
All other compatible D01–D09, provenance, ownership and local checkpoint rules remain.

## Status and interpretation

| Decision | Status |
| --- | --- |
| D01: user workflow | Confirmed by architect; scoring formula migration remains to be specified |
| D02: audiences | Confirmed by architect |
| D03: catalogue and industry selection | Confirmed: preserve industry-scoring stage; replace automatic industry exclusion with ranking influence and explicit user filters; negative preference lowers ranking without deleting roles |
| D04: market updates and forecasting | Confirmed: Malaysia, next-quarter forecasts, advertisement counts with news support, both role and skill forecasts, separate current/future internal scores, user-facing explanations/sources/trend visuals without raw market-score rankings, unavailable states, separate MNC company exploration. Exact current/future contribution to personal recommendation scores remains numerical-specification work |
| D05: ML implementation and model selection | Confirmed: implement and run Ridge and gradient-boosting experiments where compatible data/targets exist; evidence determines live selection. A simpler live scorer does not excuse skipped learners |
| D06: evaluation | Confirmed: automated, visible evaluations and chronological forecast backtests. Personal-fit validity requires separate evidence; independent human review is not an agreed launch dependency |
| D07: resources | Confirmed: USD25 RunPod, USD20 Replit allowance as reported, Groq provider. Exact Groq model/access limits and deploy access must be verified |
| D08: delivery/navigation | Confirmed: live by 00:00 MYT 24 October 2026; exact navigation below. Current teammate availability and integration ownership need a roster |
| D09: personal agents | Confirmed: direct, specific user requests authorise scoped execution without redundant approval; inferred, proactive or event-driven changes require review and approval before mutation. Notices and proposal preparation may run automatically |

Do not convert a proposal in this document into an approved rule. Do not infer empirical accuracy from complete inputs, synthetic demonstrations, or passing software tests. Do not silently overwrite prior policies. Identify conflicts and migrate the affected contract explicitly, preserving existing work.

## Vocabulary

- Role/occupation: a type of work, such as data analyst. Not necessarily a live vacancy.
- Industry/sector: an employer's economic activity, such as manufacturing. A role can exist in several industries.
- Field: a study or work domain. Preserve its type rather than conflating it with role or industry.
- Interest/preference: what the person likes, wants to explore, or wishes to avoid. It does not establish competence.
- Personal role-fit score: a comparison of the person's evidence and preferences against role requirements. Exact factors, weights, and missing-data rules remain a separate specification.
- Market assessment: a scoped assessment of external labour-market evidence, distinct from personal ability.
- Overall recommendation: the ordering produced by the approved combination of personal fit, market assessment, and applicable constraints.
- Preparation plan/pathway: role-specific learning and execution work proposed after initial matching, or when a user explores a chosen role.
- Milestone: a bounded achievement within that pathway, not a prerequisite for importing or initially matching every occupation.
- Plan feasibility: whether a proposed plan fits the person's available time, budget, prerequisites, and resources. A numerical score is not yet required or approved.
- Progress: completed activities and updated evidence of capability. Completion, self-report, and demonstrated competence are distinct.

## D01 — Confirmed workflow and rules

### Input and understanding

Collect skills, experience, education, CV/resume information, interests, preferences, goals, constraints, and user-supplied conditions. Input channels include selectable options, free text, document input, and conversation with MindBot. Users need not select a career role before receiving recommendations.

Implementation requirements derived from this intent:

1. Consolidate intake into the same structured profile used by recommendation services; chat-only knowledge must not remain invisible to scoring.
2. Preserve the distinction between explicit user statements, document-derived claims, model-extracted interpretations, and verified evidence. Allow users to correct extracted information; request clarification when ambiguity materially affects results.
3. Missing information is unknown, not a zero capability or evidence of dislike.
4. Do not infer skill mastery from a hobby, dream job, course attendance, or interest alone.
5. Do not make current employment or a prior industry mandatory for students and fresh graduates.

### Recommendation and exploration

Understand the person, compare against supported roles, and recommend directions using personal fit and compatible market evidence. Explain the reasons, gaps, prerequisites, and limits. Do not require a completed personalised preparation plan for initial role matching.

Career Explorer allows the user to inspect recommended roles or investigate another supported role, including one outside the first recommendations. The system assesses that role against the same profile and describes the result honestly; curiosity does not force a positive assessment.

Occupational requirements must exist before meaningful matching. A complete learning schedule for every occupation need not exist beforehand.

### Pathways and tracking

For a shortlisted, explored, or pursued role, identify skill gaps and propose learning resources, activities, milestones, execution tasks, and scheduled work, including what to do today. Check the proposed plan against the user's constraints. Track activity completion, self-assessments, projects/assessments and other capability evidence. Update gaps and plans as relevant evidence changes.

Keep learning activity completion separate from demonstrated ability. Keep current qualification for employment separate from potential suitability as a future direction. Keep progress assessment separate from whether upcoming work fits the user's circumstances.

### Acceptance examples

- A user with no chosen job title can complete intake and receive supported recommendations.
- Relevant input supplied through chat is represented in the profile consumed by scoring.
- A role missing a detailed schedule is not excluded solely because that schedule is missing.
- A manually explored role can be assessed without first appearing in the recommended list.
- A completed course does not automatically mark every related skill as mastered.
- Updated evidence can change gaps and next actions without deleting prior progress history.

## D02 — Confirmed audience

Support students, fresh graduates entering employment, career switchers, workers who feel uncertain/lost and seek a reskilling direction, and workers facing displacement or job loss.

These groups can share the product and core pipeline. Intake and assessment must accommodate absent professional experience, transferable experience, and different goals. Do not interpret lack of prior paid employment as lack of all relevant capabilities.

## D03 — Confirmed catalogue, industry scoring, and user control

### Confirmed product requirements

- Give the system access to all eligible roles supported by the acquired dataset, rather than limiting the product to three calibration roles.
- Do not force exactly three suitable recommendations per industry for every user.
- Use the person's current field/industry, where available, and preferences as relevant information.
- Gather interests, hobbies, dream jobs and preferred areas through the intake channels in D01.
- Rank roles using personal fit and market assessment, preserving the intermediate user–industry assessment.
- Primary market scope for the first prototype is Malaysia. This does not prevent using non-Malaysian occupational reference material with its scope disclosed, or using relevant global events as contextual evidence. It does prohibit presenting overseas statistics as Malaysian observations.
- Let users express negative interest in a role or industry. Preserve a visible, reversible 'Not interested' label and lower its preference-related ranking contribution; do not delete or automatically exclude it.

“Eligible role” still requires a concrete data rule: valid source identity, required measurement support, and explicit status. It must not be confused with whether a particular user is already qualified to apply for that role.

### Preserved algorithm, with the approved change to step 3

1. Collect the current field/industry, experience, activities, interests, hobbies, preferred areas, dream roles and explicit user constraints. Preserve 'none yet', 'unknown', 'multiple', and 'want to leave this field' as distinct states where relevant.
2. Calculate a user–industry assessment using the approved interpretation of current experience and preferences. Preserve its component trace so an observed history is distinguishable from a stated desire. This intermediate assessment remains part of the architecture; do not remove it.
3. Keep all supported eligible roles in consideration. Use the user–industry assessment to influence role ranking instead of applying the previous automatic threshold x. An explicit user search restriction can narrow a particular view. 'Not interested' is not that restriction.
4. Calculate personal role fit and compatible market assessment for supported candidates. Transfer industry context through valid many-to-many mappings; do not assign each role to exactly one industry or penalise an entire cross-industry occupation because one possible industry is disliked.
5. Produce the best supported recommendations, explanations and remaining unknowns. Keep Career Explorer access to other supported options. Do not manufacture strong matches to fill a fixed count.

Only the automatic exclusion logic is rejected. The industry's intermediate scoring, user inputs, role-fit assessment, market assessment and final recommendation remain.

### User-feedback behaviour

| User action/state | Required effect |
| --- | --- |
| No feedback / skipped card | Unknown or no additional preference evidence; do not infer dislike |
| Interested | Record a positive preference, not capability |
| Not interested in role | Persist a role-scoped label and negative preference contribution; retain the role in the catalogue and exploration |
| Not interested in industry | Persist an industry-scoped label and lower the relevant industry preference contribution; retain supported roles |
| Undo/reset preference | Remove that explicit preference contribution and label; do not erase skills or work history |
| Explicit 'only show' / search restriction | Apply a transparent, reversible filter to the requested view; do not delete catalogue records or silently rewrite global preferences |
| Open/view a role | Do not equate viewing with an explicit declaration of interest |

Derived engineering requirements:

- Repeating the same 'Not interested' action must not accumulate an unlimited penalty. Store a state, not a penalty per click.
- Feedback updates the user's preferences, not the external market-demand score or demonstrated skill evidence.
- The negative contribution must be monotonic under otherwise unchanged inputs: marking the same result as not interested must not increase its preference-adjusted score. Its ordinal rank need not fall if no other role overtakes it.
- Keep the raw capability evidence visible separately from the preference effect. If personal role fit includes preferences, its combined score can change without rewriting capability measurements.
- Use user–industry preference once in the declared scoring path. Do not add the same signal through an industry score, a role preference component, and a final penalty without explicitly decomposing those contributions.
- Role and industry feedback must be separately typed and scoped. Conflicting positive role and negative industry preferences remain separate evidence; do not silently convert one into a hard exclusion. Numeric conflict resolution must be specified in the measurement contract.
- Optional varied or randomly sampled exploration cards may help gather preferences. Their presentation order must not randomly change the saved match scores, and they must be labelled as exploration rather than claimed to be the top recommendations. Exact sampling design is an implementation choice to document.

### D03 acceptance cases

1. A role outside the user's prior industry remains eligible for evaluation when there is no explicit filter.
2. A student without employment history can be assessed using available evidence and preferences.
3. Marking a role 'Not interested' persists the label, lowers its declared preference contribution, leaves market evidence unchanged, and does not delete it.
4. Repeating that action is idempotent; resetting it restores the prior contribution under unchanged inputs.
5. Disliking one industry does not eliminate a role's supported opportunities in another industry.
6. An explicit search filter is visible and reversible; clearing it restores the full supported search scope.
7. No hidden threshold on the user–industry score removes candidates before role-level assessment.

### Remaining numerical work owned by Codex

Inspect existing policy definitions and propose the exact user–industry factors, scales, missingness behaviour, mapping rules, preference contribution and feedback penalty. Prepare a traceable numerical contract, migration plan, fixtures and sensitivity checks. The architect need not invent arbitrary point penalties. Do not confuse an implementable default with proof that the chosen weighting is empirically optimal.

The obsolete automatic threshold x is no longer a required decision. The existing F formula and F/D blend must still be audited before reuse because the earlier F measured milestone preparation rather than this newly clarified personal role fit.

## D04 — Market evidence, current assessment, and forecasts

### Confirmed desired capabilities

The architect wants changing external evidence to inform industry, role and skill market assessments; current rankings and future estimates; updated overall role recommendations; and relevant changes to skill priorities and pathways. A trained forecasting component is desired. MindBot should explain grounded system outputs and support actions through the application.

Confirmed decisions in this revision:

- Malaysia is the first prototype's primary labour-market geography.
- The internet is the principal acquisition channel for market information, prioritising official government/institutional publications, official company statements and requirements, and credible professional reporting/analysis.
- Rising frequency and prominence of a topic in credible sources is a possible early trend signal, not proof of demand and not the sole forecasting input. The architect did not claim that refreshing scores more often increases forecasting accuracy.
- Anonymous/random personal posts and comments must not become market evidence driving forecasts.
- Both role-demand and skill-demand forecasts are required product outputs with equal product priority. This does not imply a 50/50 numerical blend, identical feature weights, or a single model.
- Current market assessments and future estimates must be stored and described separately. Their numeric score matrices/rankings are internal; users receive explanations, supporting sources and appropriate trend visualisations. A future forecast must identify its target period.
- Company exploration may let a user name a dream company after finding a role, or prioritise investigating the company first. Requirements, gaps and assessment must be grounded in actual company-specific evidence when available.

Online job posting volumes, official reports, employment changes, financial/industry information and credible news/event signals are candidate inputs. Their availability in the current repository is not established by this document. Intended internal rankings are requirements, not a claim that those rankings already exist in the implementation.

### Credible internet evidence and attention signals

The following engineering rules operationalise the architect's source preference:

1. Use broad web discovery to find relevant evidence, but acquire from a maintained registry of approved sources. 'The internet' is a channel, not a single dataset or a guarantee of comprehensive coverage. Record coverage limits.
2. Source trust is claim-specific. A company is a strong primary source for its own dated vacancy or product announcement; its marketing claim about economy-wide impact is still a claim. Official status is not automatic verification of every prediction.
3. Prioritise primary documents and identifiable institutional research. Professional news/analysis may contribute with publisher, author/date, links to underlying evidence, and a label separating reporting from interpretation. Reputation alone does not establish independence.
4. Reject anonymous comments, unsourced personal posts, and engagement counts as inputs to the market signal. They must not be laundered into evidence merely because a news article quotes them.
5. Retrieve the underlying article/document when possible. A headline or search snippet alone may be a discovery lead; it is insufficient for a supported demand-impact assertion. Record unavailable full evidence.
6. Canonicalise topics, entities, roles and skills. Distinguish aliases, ambiguous terms and unrelated uses. Do not equate a product name with an occupation or skill without a supported mapping.
7. Deduplicate syndication, reposts, translations and reports of the same underlying event. Distinguish article volume, unique events and independent corroborating sources. Twenty copies of one announcement do not establish twenty independent developments.
8. Compare topic frequency against the topic's previous level and source coverage over a defined time window. Account for newly added publishers, missing feeds, crawl failures and changes in overall publication volume. Do not treat missing collection as zero interest.
9. Extract event type and claim: product release, actual adoption/deployment, investment, hiring, layoffs, regulation, training demand, or measured outcomes. A mention surge does not establish a positive effect; automation may affect role demand and skill demand differently.
10. Store global events separately from Malaysian labour observations. A global event can be a candidate explanatory feature only with an explicit relevance mapping and disclosed uncertainty; it must not be presented as Malaysian hiring growth.
11. Any manually defined attention index is an attention indicator, not a validated demand forecast. Test whether adding the news features improves forecasts compared with the same method without those features using historical, time-correct evaluation.
12. Do not train a demand model solely to reproduce a manually weighted news score and then describe the result as independently validated demand prediction.

No numerical publisher weights, attention-spike thresholds, decay constants or refresh intervals are approved here. Codex must propose them with the supported source history and units in the numerical contract. Automated source-quality checks can enforce rules; uncertainty about a consequential claim must remain explicit.

### Forecast targets and equal product priority

Role demand and skill demand are two different output families. Equal priority means neither is silently dropped; it does not mean they have the same units or should average together.

- The approved initial numerical demand measure is observed advertisement volume. For roles, count unique valid advertisements mapped to that role within the declared source population and period.
- For skills, implement the corresponding count of unique advertisements requesting that skill within the declared source population and period. A single advertisement can request multiple skills, so skill counts are not mutually exclusive and must not be summed as a total job count.
- Counts are observed source counts, not estimates of all jobs in Malaysia. Deduplication and validity checks are still required even though the architect described the quantity as raw volume. Maintain coverage and optionally report shares as supporting diagnostics; do not silently replace the approved count target with a share target.
- Industry information can provide grouping and explanatory features without automatically requiring a third independent forecast model. User-facing industry outlooks use explanatory/visual presentation and must identify their supporting source/forecast, rather than exposing raw internal scoring matrices.
- Attention/news features can help explain or predict those quantities, but are not those quantities themselves.
- A future score alone is insufficiently defined. Its underlying quantity, target period and transformation to an internal index must be explicit. Hiding internal scores from the UI does not remove this requirement.

Advertisement count targets are now approved for the first prototype. They measure advertised recruitment activity, not employment headcount. An agent must not generate invented employment-demand targets to meet a forecast requirement. News attention is a supporting feature, not the demand target itself.

### Company exploration — confirmed product intent and evidence rules

Support role-first and company-first exploration. A dream company is a user goal, not evidence of suitability or an employment offer. Give that preference a distinct recorded scope; do not rewrite the market assessment to favour a desired employer.

For company research, retrieve official careers pages, employer-authorised recruitment pages or identifiable official role descriptions. Store employer identity, source URL, role title/ID, location, publication/retrieval date, vacancy status where known, required versus preferred skills/qualifications, and supporting excerpts or structured evidence. An employer's ATS page may be official even if hosted on a different domain; verify the linkage.

Different postings for the same employer may have different levels and requirements. Preserve job-specific evidence. Never infer a universal company requirement from one posting or label a closed/undated posting as a current vacancy.

Compare sourced requirements with the user's existing profile to show matches, gaps and unknowns. Missing user evidence is unknown, not necessarily lack of ability. Separate preparation suggestions authored by Minder from the employer's stated requirements. Do not invent company interview rubrics, hiring probabilities or confidential criteria.

If no suitable official posting or description can be found, explicitly say company-specific requirements are unavailable. A generic occupation assessment may still be shown under its own label; it must not be presented as that company's verified assessment.

Company Explorer is a separate feature and must not overwrite or replace the main best-match recommendations. The user explicitly chooses whether to explore overall role matches or a chosen company.

Prototype company scope: international/multinational companies with Malaysia-based opportunities. Do not expand to overseas roles or overseas labour-market forecasting. This restriction applies to the company-exploration feature, not to all employers in the Malaysian role-demand dataset.

Company exploration sequence:
1. Accept an optional dream company or company search.
2. Look for official evidence of the user's recommended/selected role at that employer in Malaysia.
3. If found, assess the specific role requirements and offer a focused preparation plan.
4. If not found, say 'No matching role found in the sources checked', not 'This company has no such role'. Distinguish absent evidence from confirmed absence and current vacancy availability from an occupational role's existence.
5. Within Company Explorer, identify and rank other source-supported company roles using the same personal-fit logic and appropriately scoped market evidence. Explain missing company data.
6. Keep these company-scoped rankings and plans separate from the main recommendations and selected goal. Do not change the user's committed roadmap without the D09 approval boundary.

A company's absence from accessible sources is a coverage limitation. 'Any MNC in Malaysia' is a search ambition, not a guarantee that every employer publishes every role or that the system has complete access. Preserve employer identity, subsidiary/location distinctions, and the actual search coverage.

### Measurement distinctions required for implementation

1. Job postings measure advertised recruiting activity within observed sources. They are not all vacancies, actual hires, or the number of people employed. Deduplicate reposts and capture platform coverage, observation window, source dates, and geography.
2. Filled employment is a stock; postings, hires, and job creation measure different flows. Falling employment does not alone prove zero hiring or absence of skill shortages. Replacement hiring can coexist with shrinking employment.
3. Skill demand can be represented by counts or shares of valid postings that request a skill. A share must name its denominator; distinguish within-role shares from whole-market shares.
4. Industry output, revenue, investment, and profitability are contextual indicators. They are not direct substitutes for role vacancies or skill demand.
5. Preserve observed level, growth/change, and uncertainty separately. Largest, fastest-growing, and best for a particular user are different concepts.
6. Official release delays do not make data useless for forecasting. Historical observations are training and evaluation evidence. Record both the period measured and the date the evidence became available to avoid using future information in historical tests.
7. General market changes do not prove AI caused the change. Specific AI-related evidence and supported mappings are required for an AI-impact claim.

### Required current/future separation; numerical contract pending

Maintain separate current observations/assessments and future estimates. Forecast a defined numerical series first, then derive a ranking within a comparable universe. Rankings alone discard magnitude and do not establish forecasting accuracy. Version and compare like-for-like series; do not compare differently scaled current and future indices as if their numerical difference measured real change.

For every series and forecast record preserve:

- entity type and ID (industry, role, or skill);
- geography and data-source scope;
- measured quantity and units/denominator;
- observation period, publication/availability date, and ingestion time;
- forecast issue time and target period/horizon;
- point estimate and uncertainty information appropriate to the method;
- coverage/missingness and observed-versus-estimated status;
- source and model/version identifiers.

The architect approved a three-month initial forecast period expressed as the next quarter. Operational interpretation: target the next full calendar quarter, with explicit start/end dates, not an unnamed rolling window. A forecast issued on 22 October 2026 targets 1 January–31 March 2027. This is a three-month target period; it is not exactly three months from the issue date to the target end. Preserve issue date, last observed period, and actual lead time separately, especially if source publication lags.

Later product ambitions, not initial prototype completion requirements: forecasts for successive quarters ahead (quarter +1 through +4), a one-year outlook, and a five-year outlook for the evolution of existing roles and skills. Do not interpret '+1 quarter' as always calendar Q1. The five-year concept supports students' preparation choices and estimates how existing work might change; it is not permission to invent occupations.

Longer horizons require separate target definitions, data, evaluations and uncertainty. Do not extrapolate a validated short-horizon claim into a five-year accuracy claim or simply roll a quarterly model forward and call the result validated. Counts of advertisements do not automatically establish how many people will be employed five years later. Employment-level forecasts would require a separate observed target and supporting data. Where evidence supports only scenarios, label assumptions and scenarios explicitly.

Do not describe the most recently available observation as today's true market without displaying its date. Do not label an estimate of the present as directly observed. Do not promise monthly or three-month forecasting if the acquired history cannot support it.

If accessible data is insufficient for a role, skill, period or geography, display a precise unavailable status, for example: 'Next-quarter forecast unavailable: insufficient comparable historical observations from the available sources.' This is approved prototype behaviour. Keep supported current observations, company exploration and other outputs operational. It is not a claim that Malaysia has no relevant historical data; the actual accessible source coverage must be inspected. Never substitute fabricated values or zero for missing forecasts.

### Update propagation

- Validated new market observations can update market assessments and compatible rankings.
- Updated market assessment can change overall recommendations under a defined policy; current and future market outputs must stay separate internally. The architect has settled their user-facing presentation, not a numeric blend or default current/future weighting within the recommendation formula. Codex must reconcile this in the numerical contract rather than infer a formula from UI placement.
- A market update alone does not change the user's demonstrated capability.
- Skill gaps change when role requirements or user evidence change. Market importance can reprioritise learning without changing the person's capability or the underlying gap.
- Data refresh, feature recalculation, inference, retraining, and deployment are separate operations. Do not retrain and deploy on every new article automatically.
- Evaluate a newly trained model before replacing the current one, following D05–D06 below.
- Scheduled jobs/events are required to acquire updates and trigger work. The language-model API does not independently maintain the evidence store.

### ML, rules, and language-model responsibilities

Deterministic code handles validated transformations, policy rules, and reproducible calculations. Trained models handle specified predictive tasks supported by suitable training data. The LLM can assist extraction and explanation, but extracted claims require validation and traceability.

The Minder chat interface and Mindbots agents consume structured results with dates, versions, missing-data status and evidence. They use these internal assessments to reason about advice, explanations and proposed actions. They must not invent scores, change saved predictions in explanatory text, or turn uncertainty into certainty. Any change to an official scored recommendation must follow the versioned recommendation policy and be traceable; a conversational phrasing choice cannot silently redefine the score. Tool execution and persistence belong to the application workflow; language generation alone is not execution. D09 defines the confirmed authorisation boundary.

When discussing the present, MindBot must reference current observations/assessments with their dates. When discussing a future period, it must use the forecast for that period and disclose uncertainty. It must not choose whichever current or future value makes its answer persuasive. If no matching forecast exists, return that limitation rather than extrapolating a number in prose. A forecast of rising demand is not a guarantee that a role or skill will survive, grow, or suit a specific user.

### D04 acceptance cases

- A repeated/syndicated story does not become independent corroboration merely by appearing on additional URLs.
- An excluded personal-comment source cannot alter production market features.
- An official product release is stored as an announcement, not automatically as demonstrated Malaysian hiring demand.
- The same event can support different directional hypotheses for different roles/skills; uncertainty is preserved.
- Current and future role/skill records have distinct time semantics, geography, source scope and versions.
- Role and skill forecasts both have supported outputs or explicit unavailable status; a missing series is not manufactured.
- A user preference change does not change market evidence; a news update does not change demonstrated personal skills.
- A historical evaluation uses only information available at the forecast issue date, not later reporting or revised data unavailable then.
- Company-specific claims link to the correct employer, role, geography and document; missing official evidence produces an explicit limitation.
- The agent's explanation faithfully reflects saved results and dates without displaying internal market scores or silently combining incompatible periods.
- The consumer UI and chat do not expose raw current/future market-score leaderboards; forecast visuals use supported observations/projections and clearly labelled periods/uncertainty.

### Sources inspected on 22 October 2026

These are research leads, not confirmation of local ingestion, API availability, licences for every usage, or sufficient longitudinal coverage.

| Source | Verified scope / potential use | Limitation |
| --- | --- | --- |
| DOSM Employment Statistics Q1 2026 | Quarterly Employment Survey of registered private-sector businesses; jobs, filled jobs, vacancies and jobs created by economic activity and skill category | Aggregate categories do not automatically cover each specific career role |
| DOSM Job Market Insights | Quarterly reports based on advertisements on major private recruitment platforms | Published reports do not establish a raw live job-posting API; series coverage and changes need inspection |
| Job-SDF paper and official repository | Historical monthly skill-demand forecasting research using 2021–2023 Chinese advertisements; paper reports 10.35 million advertisements and 2,324 skill types | Useful methodological/benchmark lead; not Malaysian present-day market evidence or proof of cross-country accuracy |

Source links:
- https://www.dosm.gov.my/portal-main/release-content/employment-statistics-q12026
- https://www.dosm.gov.my/portal-main/release-content/big-data-analytics-job-market-insights-q12026
- https://arxiv.org/abs/2406.11920
- https://github.com/Job-SDF/benchmark

### Confirmed product presentation: internal assessments, useful user-facing interpretation

Both current-market and next-quarter assessment capabilities belong in the first prototype, subject to the approved explicit unavailable state where data is insufficient. Do not make the user choose which capability exists.

| Layer/view | Required treatment |
| --- | --- |
| Backend current-market data | Keep source-grounded numerical assessments, role/skill/industry indicators, rankings, coverage and versions internally for the recommendation services and LLM context |
| Backend next-quarter data | Keep forecasts and derived indicators/rankings separate, with target dates, uncertainty, provenance and model versions |
| User-facing current-market section | Explain the relevant current situation, why it matters to the user, and supporting resources/sources. Do not display the internal market-score matrix or a numerical market-score leaderboard |
| Future Explorer | Visualise and describe supported next-quarter trends in user-oriented language; distinguish observations and projections, show dates and uncertainty, and explain personal implications |
| Minder/Mindbots | Use the structured internal evidence to inform reasoning, explanations and proposals without exposing raw market scores or inventing numeric claims |

The product serves career decisions rather than presenting a raw market-analysis dashboard. Trend visualisations may show real, properly labelled quantities or qualitative direction when supported; the restriction concerns internal scoring/ranking matrices, not an absolute ban on all numbers in charts. Do not plot an arbitrary '82/100' market score and relabel it as job demand.

This visibility decision applies to internal market assessments. It does not automatically remove personal role-fit scores, user progress, the recommended role ordering, or other previously requested product outputs. Do not broaden the restriction without an explicit decision.

Current and future narratives must be visibly distinguishable. A missing future forecast must produce the approved unavailable explanation rather than a speculative chart or a current observation presented as a forecast. Resource links must support the nearby claim; stale/current/forecast periods remain distinguishable even when numeric scores are hidden.

The earlier choice between 'current-first' and 'future-first' UI was not accepted as the product framing. Do not install the assistant's prior current-first recommendation as if approved. Codex must separately document exactly how personal fit and current/future market evidence enter the internal recommendation policy, including scales, weights, missingness and comparison scope. Presentation alone does not determine that formula. Reuse compatible existing approved rules; prepare any new meaning-changing combination as a concrete proposal rather than letting the LLM improvise untracked arithmetic.

### Engineering decisions and evidence discovery owned by Codex

The following must not become a request for the architect to manually author datasets or invent arbitrary constants:

1. Inspect actual repository instructions, schemas, policy files, manifests, acquired source tables, historical coverage and service loaders. Produce the actual source-to-measurement map.
2. Identify exact accessible sources, retrieval methods and limits. A search result, report link or proposed feed is not a working integration. Record authentication/access dependencies without exposing credentials.
3. Prepare the approved-source registry, claim-type rules, event schema, deduplication, role/industry/skill mappings and Malaysia-relevance checks. Specify bounded collection and refresh behaviour; do not implement an unbounded crawl of the whole internet.
4. Specify current assessment factors and numerical scale; the user–industry score, preference effect and F contract; and the compatible F/market combination. Preserve previous approved values only where their meanings remain valid. Explicitly mark changed score meanings and any migration of labels/models.
5. Prepare news attention windows, source-coverage normalisation, uncertainty handling and a proposed influence mechanism. Put constants in versioned configuration with rationale and sensitivity checks, not scattered implementation literals.
6. Inspect historical role and skill series independently. Prepare target definitions, units, time aggregation, forecast method, comparison baseline and chronological evaluation. Forecasting skill demand and role demand need not use the same model.
7. Test the incremental usefulness of news features rather than assuming it. If only present-day news was collected, do not claim a historical news-feature evaluation was performed.
8. Define stable structured outputs for current results, future results, unavailable data, source provenance, preference traces and company assessments. Preserve D01 input and progress integration.
9. Prepare the exact numerical contract with actual repository/data evidence, keeping confirmed product decisions intact. Avoid another generic audit-only gate when sufficient facts already permit implementation; surface only genuinely unresolved substantive scoring choices as concrete proposals.

Technical parameter selection can be delegated and automated within accepted meanings. Changing the intended forecast target, geography, source standards, feedback semantics or recommendation mode is a product-policy change and must not be hidden as tuning.

## D05 — Required ML work and evidence-based live model selection

### Confirmed intent

The architect requires the agreed ML architecture to be implemented, including the explicit scoring baseline, Ridge regression and gradient boosting (reuse the existing XGBoost path if present and compatible). The team must perform genuine training/comparison work with appropriate targets and data, including the planned RunPod experiment within the available credits. Do not omit the learners and declare the entire ML requirement complete because the baseline can return a number.

At the same time, a new trained model must earn its place in the live service through evidence. Retaining the better-supported existing method is acceptable when a new model fails the agreed checks. This is a deployment decision, not permission to skip implementation or quietly abandon the training experiments.

### Terms and responsibilities

- Baseline: a defined reference method against which alternatives are compared. For personal role fit, it may be an explicit policy formula. For demand forecasting, it should include a relevant simple historical forecast, such as last-observed or seasonal repetition when supported. These are not interchangeable targets.
- Candidate: a newly trained version being evaluated, not a career role or user.
- Model selection: deciding which valid method serves each defined prediction target.
- Fallback: returning a supported prior method or explicit unavailable status when the preferred method is unavailable or fails checks.

Ridge and gradient boosting need not be chained together or averaged. Implement comparable experiments; select a method per task based on evaluation. An ensemble is a separate design choice requiring evidence, not a requirement implied by listing two algorithms.

Keep personal role-fit learning and market forecasting as distinct learning tasks with different inputs, targets, splits and metrics. Do not feed an occupational ranking label into a market-demand experiment or claim a forecasting success validates personal suitability.

### Failure diagnosis, not automatic complexity escalation

Poor performance can result from target ambiguity, missing or biased data, incorrect mappings, leakage, bugs, unsuitable features, changed conditions, or model limitations. Do not assume it proves the algorithm is too simple. Diagnose the actual error, repair supported causes, rerun a bounded experiment, and document the effect. A more complex algorithm is not an accuracy guarantee.

If required targets are missing, the implementation and data blocker must be reported separately. Do not fabricate observed outcomes or claim the training requirement passed because imports/constructors exist. Policy-generated or LLM-generated labels can support explicitly labelled prototype experiments, but performance against them is not independent evidence of career suitability.

### Required experiment evidence

For every baseline and trained candidate record:

- task/target definition and units;
- source snapshots, observation dates, available-at dates, training/validation/test IDs and ranges;
- feature/schema and policy versions;
- algorithm, hyperparameters, seeds, preprocessing and fitting procedure;
- run ID, code commit, environment/dependency version, saved artifact and checksum;
- RunPod job/environment and measured usage where applicable, without secrets;
- metrics on the same held-out examples, subgroup/coverage results and failure cases;
- selection decision, compatibility and operational checks, and fallback behaviour.

Distinguish code implemented, training attempted, training completed, evaluated, selected, and currently live. A file called 'model.pkl' or an available code path does not prove the service loads that artifact.

Prepare the promotion rule before choosing the winning run. Use an untouched final test set for reporting; tune on training/validation only. A gain on an aggregate metric must not hide broken constraints or serious failures on represented groups. Exact metrics and operational limits belong in the task-specific evaluation contract, not a universal invented '90% accuracy' threshold.

Internet citations substantiate source facts and model inputs. Experiment logs and held-out outcomes substantiate performance. A web citation does not prove a model prediction is correct; model output must identify its own version and limitations.

### Acceptance criteria

- Baseline, Ridge and gradient-boosting paths are implemented against explicit compatible targets, and actual runs are performed where the required data exists.
- A failing candidate cannot silently replace the live method.
- The chosen live scorer/forecaster is identifiable from the API output or trace.
- Failure of a training experiment is reported with reasons and next repair, not hidden behind passing software tests.
- Missing targets produce a documented blocker and honest narrower output, not invented labels presented as ground truth.

## D06 — Automated evaluation and historical forecasting backtests

### Confirmed evaluation direction

The architect approves automated, visible evaluations and transparent limits. For forecasting, train using earlier information and predict later periods for which observations are already available, then compare predictions with those actual observations.

The example 'train on 2019–2022 and predict 2023–2025' expresses this principle. It is not evidence that those years are available, not approval to fabricate that history, and not automatically the right test horizon for a next-quarter forecast.

### Initial forecasting protocol

1. Inventory actual historical series and the information availability dates. Define what a row and target period mean, including source coverage and data revisions.
2. Use multiple chronological forecast issue points where data allows. At each issue point, use only information that would have been available then and predict the following full calendar quarter, matching the initial product behaviour.
3. Example only: issue at the end of 2022 to predict 2023 Q1; move the issue point forward and predict the next quarter. Include real publication delays. A model issued in October for the following January–March may require more lead time than a single step from the latest observed data.
4. Fit normalisation, feature selection, imputation and tuning using training/validation information only. Avoid future labels, revised retrospective data unavailable then, and articles published after the issue date.
5. Compare Ridge and gradient boosting with relevant naive/seasonal reference forecasts using identical target periods and data availability.
6. Compare news-enhanced models with the same method without news features. Historical news evaluation requires dated historical evidence; today's collected news cannot be inserted into a past forecast.
7. Reserve a final chronological holdout that is not repeatedly used for tuning. Keep an explicit evaluation cutoff and version.
8. Report results separately by role/skill, source coverage, geography and target horizon. Pooling entities must not conceal missing coverage or errors on rare skills.

Predicting 2023, 2024 and 2025 from a frozen 2022 model tests different multi-year horizons. Updating/retraining as time advances tests an operational rolling system. Report which was done; do not describe either as the other.

### Proposed technical metrics for Codex to specify before runs

- Advertisement count error: MAE (average absolute count error) and a scale-aware aggregate such as WAPE when its denominator is nonzero. Include per-series results; avoid misleading percentage errors for zero/near-zero counts.
- Comparison to simple forecasts: show whether error improves, with the number of evaluated periods/entities and uncertainty where estimable.
- Ranking: evaluate internal ordering against realised demand in the same target universe where those rankings influence recommendations or explanations. Ranking quality does not replace count accuracy, even when market-score rankings are hidden from users.
- Uncertainty: test interval coverage if intervals are claimed. Do not fabricate confidence percentages from an LLM or an arbitrary score.
- Operational: inference failures, latency and cost under the actual prototype workload.

These are methodological recommendations, not a claim that data already supports all metrics. Codex selects and documents exact metrics before comparison and does not suppress unsuccessful results.

### Personal role-fit evaluation is a separate requirement

Historical job-advertisement counts provide targets for market forecasting. They do not tell us whether a specific person would enjoy, succeed in, or be suited to a role. Therefore forecasting backtests do not close personal-fit evaluation by themselves.

Use automated checks for:

- valid inputs, units, mappings and complete traces;
- correct missing-data treatment;
- consistency with the declared policy;
- role/industry feedback semantics and no accidental hard exclusion;
- expected changes under controlled profile changes, holding unrelated inputs fixed;
- robustness to equivalent phrasing and CV/chat extraction variants;
- group-level coverage across the D02 audiences and role families;
- correct prerequisite and preference explanations.

For empirical personal-fit learning/ranking, identify a suitable labelled benchmark or other independent outcomes if available. Partition by user/profile and relevant groups to prevent near-duplicate leakage. If only synthetic/provisional/teacher-generated labels are available, report their generation and target explicitly; performance measures agreement with those labels, not independently validated real-world suitability.

The earlier 'bounded blind review sample' meant a small fixed number of profile–role cases that a reviewer judges before seeing the model's score, to reduce anchoring. The architect has not committed team time to this. Do not make human review a hidden mandatory launch gate. Automated-only evaluation is the current delivery direction; report the narrower validity claim where independent evidence is absent. A human review can remain an optional later improvement.

### Visible evaluation deliverable

Produce a concise evaluation report/view backed by machine-readable results. Show data period, targets, source coverage, model versions, baseline comparisons, errors, failed cases, subgroup coverage, missing evaluations and limitations. Do not present one unexplained 'accuracy' percentage across forecasting, matching and chat.

Also evaluate the chat/agent integration: explanations match saved values and evidence, missing forecasts remain missing in prose, tool calls respect constraints, changes persist exactly once, failed writes are reported honestly, and approval states are enforced.

## D07 — Resources, providers and execution costs

### Confirmed resources

- RunPod credits remaining: USD25, as reported by the architect.
- Replit allowance/Core access: USD20, as reported by the architect; inspect actual balance and included deployment capacity rather than assuming this buys a specific hosting arrangement.
- Groq is the selected LLM API provider for the Minder interface and Mindbots agents. Exact model ID, account tier, available limits/credit and credentials configured in the project remain operational facts to verify; never request secrets in a report or commit them.
- No additional paid budget has been provided. Do not treat these services' balances as interchangeable.
- Replit use and RunPod training were previously described by the architect as hackathon requirements; inspect the supplied participant handbook for exact compliance/submission requirements. Do not imply the handbook was reverified here.

RunPod serverless can scale flex workers to zero, but startup, execution and waiting before shutdown may be billed; storage and always-active workers may also cost money. An always-available agent is saved state plus events/schedules, not a permanently computing GPU loop. Groq calls, application hosting, database/storage and RunPod execution are separate resources.

Training jobs and deployed inference are separate workloads. Codex must choose the appropriate RunPod execution mode for the actual bounded training/inference work and report it. The presence of a Groq-powered agent does not itself require GPU hosting on RunPod. Ridge and small tabular models do not automatically need a GPU for serving; use the required platform purposefully and within credits.

Before a paid run, use the existing task's spending authorisation and inspect balance/access, estimated duration, termination limits and maximum workers. Do not exceed provided funds or silently enable a paid top-up. Apply bounded jobs, retries and per-user/task LLM limits. Log actual usage. Readiness checks and estimates do not require repeatedly asking for permission already granted in the execution task.

Do not promise continuous availability on a free tier or a deployment that sleeps. Verify the deployed scheduler, persisted job state and service limits. Use no secrets in source control, context files, screenshots or model reports.

## D08 — Delivery, exact navigation and collaboration

### Confirmed deadline

The complete first prototype must be live by 00:00 Asia/Kuala_Lumpur on 24 October 2026: midnight immediately after 23 October. The architect also expressed the cutoff as 23 October 11:59 p.m.; schedule delivery before that cutoff. This is not noon on 24 October. The architect reports a 25 October submission date and intends to submit early. Verify any exact official submission requirements against the participant handbook; do not invent them.

Later multi-quarter/year/five-year forecasting ambitions do not silently become this deadline's required validated forecasts.

### Exact navigation confirmed by architect

| Top-level area | Purpose / children |
| --- | --- |
| Homepage / Overview | Same area, not two separate pages |
| User Profile | Intake, evidence, preferences, constraints and profile updates |
| Minder | LLM chat interface |
| Mindbots | Personal agents, notices, proposals, action history and applicable approvals |
| Explore | Progress; Tasks; Future Explorer; Career Match; Roadmap (reskilling path) |

Company Explorer is a separate exploration feature within the Explore/Career Match experience, not an automatically added sixth top-level navigation area or sixth mandatory Explore tab. Its exact subview placement is an implementation choice consistent with the approved five Explore areas. Keep company-specific results distinct from the overall Career Match output.

Earlier conversations used MindBot/Mindbots loosely for chat and agent interactions. This explicit navigation is authoritative: Minder is chat, Mindbots is personal agents. Both may share the Groq adapter, structured context and action services.

### Minimum integrated prototype behaviours

- Intake from supported options/text/CV and conversation reaches the persisted profile used by scoring.
- Runtime contains the actual supported role catalogue, not only three calibration roles, with honest source and measurement coverage.
- Career Match produces real service results or specific missing-input status, preference feedback works, and company exploration uses actual retrieved requirements or an honest unavailable state.
- Future Explorer displays current evidence and supported next-quarter forecasts separately; limited-data unavailability is approved. No invented values to fill charts.
- Roadmap, Tasks and Progress share persistent state and reflect accepted plan changes and completed work.
- Minder explains system results and evidence with the correct dates and limitations.
- Mindbots responds to the approved trigger events and performs/proposes persisted actions according to the final approval policy.
- Frontend, backend, storage, model loading, source retrieval and authentication/access boundaries required by the actual app are integrated and exercised on the deployed prototype. Do not call a static page with synthetic screenshots a functioning integration.
- Record what was verified live versus locally. Treat the deadline as a delivery target, not evidence every feature is already complete.

### Mandatory execution loop and checkpoints

For each bounded phase: implement, verify, refine defects, record actual status/evidence, commit locally, then continue the next eligible phase. Do not accumulate all lane work into one final commit. Each lane and the final integration also receive a culminating status/handoff checkpoint. Ordinary phases should have a cohesive reviewable output; split broad phases into named children.

A refinement after an existing checkpoint is identified as PHASE-ID-R01, R02, etc., with defect evidence, original phase reference, narrow fix and regression check. Preserve earlier history. A failing or blocked checkpoint is not a passed engineering gate.

If human input is genuinely required, prepare the exact decision and affected phases, checkpoint safe completed work, mark that work blocked/deferred and continue independent tasks. Do not invent the answer or silently skip the requirement. Routine debugging within agreed policy is agent work. Final reports must list delivered behaviour, checks, phase status, refinement IDs, actual local commit SHAs, remaining dirty work, decision blockers and next runnable work.

Push permission is separate: no GitHub/remote push, IDE auto-sync, PR-triggered push or backup push until the user explicitly requests it. If deployment requires a push, prepare the release and report the dependency. Local commits/merges are allowed. Do not fabricate commits, create empty commits merely for appearance, rewrite prior history, or claim a checkpoint when committing failed.

### Team and repository coordination

The actual checkout, worktree state and latest R0 context export are still unavailable in this authoring task. The previous reports described uncommitted engineering work and a requirement to recover truthful checkpoints. Verify the current state rather than assuming those reports are still current.

Codex should gather the current branch/commit, dirty-state summary, policies, schemas, manifests, reports, runtime configuration, selected model/artifact, tests run and integration failures in the agreed context export. Keep source data and secrets out where inappropriate; record identifiers and hashes instead.

Use truthful commits for completed increments and recover current work without fabricated historical timestamps. Remove obsolete blanket 'no commits' restrictions in the task instructions only within the architect's explicit checkpoint authorisation. Check staged contents for unrelated work and secrets. Commit history cannot recreate development checkpoints that never happened.

Parallel sessions require separate worktrees/branches, compatible committed shared contracts, explicit owned areas and one integration owner. A worktree from HEAD does not inherit uncommitted changes. Do not blindly commit or copy another active session's unrelated work. Do not overwrite root schemas/configuration/lockfiles concurrently without coordination. Do not push to GitHub or any remote until the user explicitly requests a push. Prior generic backup/push wording no longer authorises a push. Local phase checkpoints and local merges remain authorised.

Missing team input: name/role of each active owner, their realistic available time before cutoff, current branches and who integrates/deploys. Existing tentative role assignments are not proof of current availability. Codex can inspect repository facts; the team must supply availability if it is not documented.

## D09 — LLM-powered personal agents and permitted workflow

### Confirmed triggers and outputs

| Trigger | Required agent behaviour |
| --- | --- |
| Material new evidence or trend relevant to the user's industries, roles, skills or chosen company | Explain the evidence and why it matters; send an in-app notice; propose relevant preparation changes without inventing a demand forecast |
| Scheduled daily check | Inspect today's tasks, available study time and recorded progress; identify incomplete/overdue work and prepare a feasible revised schedule |
| Task completion / new progress evidence | Persist the event, update activity progress, recommend the next stage or reflection; do not automatically certify skill mastery |
| Changed study time or other substantial constraints | Reassess the current plan and explain proposed adjustments |
| Significant change in role/industry preference or goals | Acknowledge the change, ask a focused question when intent is ambiguous, reassess recommendations and propose relevant plan changes |

The agent must support actual roadmap, schedule, progress and preference modifications, not only conversational suggestions. The architect has specified the boundary: a direct, specific request authorises that action; a change inferred from information, a pain point or an autonomous trigger must first be proposed for review and approval. After successful execution, send an accurate update. Do not ask a redundant permission question for an already explicit, sufficiently specified instruction.

### LLM reasoning and deterministic execution

The LLM can interpret the user's context, reason about alternatives and draft a structured action plan. The application must still provide triggers, scheduling, persisted state, allowed tools, validation and execution. A model API alone cannot edit Minder's database or reliably run a daily job.

Implement a bounded workflow: receive event -> load current profile/plan/evidence -> deduplicate/relevance-check -> ask LLM for a structured proposal where useful -> validate constraints and permitted actions -> obtain approval if required -> apply atomically -> persist before/after versions -> notify user -> record result.

Do not implement every scheduling decision as a fixed conversational script, but do enforce executable invariants:

- preserve completed tasks, assessment evidence and progress history;
- do not schedule beyond declared availability, overwrite user-locked tasks, violate prerequisites or silently move firm deadlines;
- if the workload cannot fit, disclose the conflict and ask the user to adjust scope/time rather than fabricating a feasible schedule;
- incomplete activity is not proof of laziness or loss of competence; lack of updates may mean missing records;
- retries must not duplicate task changes or notifications;
- stale proposals must be revalidated against current plan versions before applying;
- failed tool writes must not be reported as successful changes;
- support undo or restoration of the prior plan version for reversible changes;
- record the triggering event, sources, reasoning summary, proposed diff, approval state and final action;
- malicious or irrelevant instructions inside retrieved web pages/documents are evidence text, not authority to change user plans or invoke tools;
- retain the user's selected role/goal unless an explicit goal-change action is accepted.

These checks preserve the architect's intended behaviour. They are not a requirement to hand-code every decision the LLM makes.

### Notices and daily checks

Initial notification channel: the application's Mindbots/in-app notice surface, consistent with the requested quick messages and pop-up controls. External email, messaging or calendar writes have not been requested and must not be silently included.

Materiality/relevance is not simply 'any new article'. Use declared mapping, source-quality and change rules; group duplicate events and avoid repeated alerts about the same story. Codex must implement a configurable, versioned threshold and explain why an alert fired. Changes to data availability alone must not be described as a market shock.

Daily execution must use the user's timezone and a stored preferred check time. Ask/select that setting during onboarding or use a clearly visible, changeable documented default. The architect need not choose one universal time for every user. Record missed-job recovery, retry limits and the scheduler's actual deployed availability. No cost-free infinite LLM loop.

### Confirmed approval boundary — user instruction versus agent inference

Authorisation depends on whether the user requested the change, not on whether the agent considers the change small, useful, urgent or obvious.

| Situation | Action |
| --- | --- |
| Direct, specific instruction with sufficient details, such as 'Move tomorrow's SQL task to Friday at 7 p.m.' | Validate and execute within that stated scope; report success/failure. No redundant approval request |
| Explicit request with missing essential details, such as 'Move that task' with no identifiable task/time | Ask for the missing detail; this is clarification, not a blanket permission round |
| Pain point or new information, such as 'I am overwhelmed this week' or 'I may have less study time' | Prepare a concrete proposed change and ask for approval before altering the schedule, roadmap, stored preferences or progress |
| Question or hypothetical, such as 'Would switching to data analysis help?' | Answer or prepare a proposal; do not silently change the selected role, preferences or roadmap |
| Daily check finds incomplete tasks | Propose rescheduling automatically and show the planned changes; wait for approval before applying, even if moving a task looks low impact |
| Market evidence suggests a better learning priority | Notify/explain and propose changes; do not apply an unsolicited roadmap or preference change |
| User approves a specific displayed proposal, by button or an unambiguous 'yes' referring to it | Revalidate the proposal and execute the approved scope, then report the actual changes |
| User rejects or cancels | Preserve current state; allow revision or dismissal of the proposal |

Automatic collection of authorised source evidence, generation of suggestions, delivery of the agreed in-app notices, and logging of actual events can proceed without approval for each occurrence. An explicit UI edit, a task-completion action, or the user's direct correction of a stored value is already a user instruction; do not demand a second approval for the identical edit. Still distinguish self-reported completion from verified skill mastery.

A piece of conversational context may inform a proposed plan without silently replacing confirmed persistent profile values. Extract and stage inferred changes with provenance; present the proposed persistent update when intent is uncertain. Explicitly supplied intake answers or direct profile-edit controls follow D01's authorised intake flow.

Approval covers the specific action/diff and scope shown, not blanket future authority. If material changes to the proposed action become necessary, show the revised proposal. If the underlying state changed, revalidate and obtain renewed approval only where the resulting action materially differs. Do not execute a stale plan blindly.

Proposal UI requirements: show what will change, the reason, relevant constraints and affected tasks/roadmap items, with Approve and Reject/Edit controls. Approval must precede the write. After execution, give a concise result and provide the existing reversible-change history/undo where applicable. An after-the-fact notice or Undo option is not a substitute for required prior approval.

The assistant's earlier proposal to automatically reschedule unfinished tasks merely because they fit within availability is not adopted. Neither a 'huge problem' nor an urgent inference grants extra authority. The LLM identifies intent and drafts actions; the application enforces the authorisation state and tool scopes.

Derived tool-execution rule: every mutation carries its authorising user request or approved proposal ID, intended scope, and expected state version. The executor checks these before applying. This makes the same boundary enforceable across chat, Mindbots, UI actions and scheduled workflows rather than relying on prompt wording alone.

### Acceptance cases

- A relevant validated market event produces one source-linked notice; repeated ingestion does not produce duplicate notices.
- A daily check produces a structured feasible plan diff or an explicit infeasibility explanation.
- User completion triggers a next-action recommendation while preserving evidence distinctions.
- Preference/time changes reach the profile and the next agent decision.
- Proposed changes show before/after details and reason; approved writes persist, cancellation leaves state unchanged, and stale proposals are not blindly applied.
- A direct, sufficiently specific request executes without a second permission prompt; an ambiguous request asks only for necessary clarification.
- A pain point, hypothetical question, market event or daily check cannot mutate schedule/roadmap/preferences/progress without a matching approval.
- An approval applies only the previewed scope; rejection leaves confirmed state unchanged; notifications report actual successful writes.

## Cross-cutting decision register and remaining dependencies

### Final product clarifications recorded

| Topic | Approved rule |
| --- | --- |
| Market-score presentation | Current and next-quarter internal scoring both belong in the prototype. Expose explanations, sources and appropriate trend visualisations; do not expose internal market-score matrices/ranking tables. Preserve separate time semantics |
| Agent editing authority | Execute an explicit, sufficiently specific user instruction within scope. Propose and obtain approval before changes inferred from information or initiated proactively. No automatic low-impact rescheduling exception |

Do not reopen these as the previous binary UI/permission questions. They are settled at the product level. Exact recommendation arithmetic, data coverage, model evaluation and operational access remain engineering dependencies described below. In particular, no new current/future weighting is implied by hiding scores from the user.

### Operational inputs to retrieve or supply, not invented product decisions

- R0/current repository context export or actual checkout, including current policy and implementation evidence.
- Latest Participant Handbook/submission instructions for real compliance and deliverable checks.
- Team availability, ownership, integration/deployment responsibility and actual access status.
- Groq model ID, usable account limits/credit and configured service credentials checked in the environment, without exposing keys.
- Replit deployment/DB/storage and scheduled-job capability; current RunPod credits/access.

Codex should inspect discoverable facts first and request only genuinely unavailable access/owner information. Do not ask the architect to manually list hundreds of roles, annotate every source or manufacture training targets.

### Numerical specifications to prepare within the agreed decisions

The product intent is substantially settled; exact formulas, weights, scales, missing-data rules, mappings, feedback penalty, market factors, learning targets, evaluation thresholds and source-refresh settings still require one coherent engineering contract based on the actual repository and data. Reuse valid approved decisions. Do not silently carry the old milestone-dependent F into the new role-fit meaning. Do not spread contradictory constants across chat, ML and backend.

Automate routine review of schema validity, source status, deterministic policy checks, tests and reports. Human involvement is for remaining product meaning, inaccessible account decisions, or unresolved consequential evidence—not approval of every ordinary role or record. Independent empirical validity must be honestly distinguished from automated self-consistency checks.

## Execution dependency map for the repository agent

This is an implementation dependency map, not evidence that any gate has passed. Prepare concrete file paths after inspecting the actual repository; do not invent paths or discard existing implementation. Gates require usable outputs, not just new tooling or passing test counts.

| Work package | Required output | Dependencies / parallelism |
| --- | --- | --- |
| E0 — Recover and inspect current state | Truthful checkpoint, current context, actual source/runtime role inventory and shared-file ownership | First; existing isolated work can continue safely |
| E1 — Integrate decisions and shared contracts | This canonical policy integrated; versioned profile, role, current/future forecast, company and action contracts; one numerical specification; confirmed visibility and user-request/proposal authority semantics | After E0; do not duplicate conflicting policy sources |
| E2 — Catalogue, intake and personal matching | All eligible acquired roles loaded, D03 industry stage retained, feedback works, actual profile-to-result service outputs and coverage | After stable relevant E1 contracts; parallel with market ingestion and chat |
| E3 — Malaysia evidence and company retrieval | Working scoped sources, historical series, credible-event processing, company-first/role-first results with provenance and unavailable states | After E1; can run alongside E2/E4 |
| E4 — Minder chat, pathways and progress | Grounded chat adapter, profile updates, persistent tasks/progress/roadmap and plan feasibility checks | Stable contracts and existing interfaces; integrate real outputs from E2/E3 when ready |
| E5 — Train and evaluate | Baseline/Ridge/gradient-boosting implementation and real bounded runs, forecasting backtests, separate personal-fit evidence, model selection and artifacts | Relevant targets and datasets available; label/data preparation may run alongside E2/E3; missing forecast series use approved unavailable state |
| E6 — Mindbots workflow | Deployed triggers, notices, proposal diffs, tested action persistence and enforcement of the confirmed direct-request versus inferred-change rule | E3/E4 context and action services; request/proposal authorisation checks implemented; scheduler access verified |
| E7 — Integrate, deploy and freeze evidence | End-to-end live prototype across exact navigation; source/model/evaluation evidence; meaningful commit history and frozen submission revision | Integrate completed increments continuously; final pass consumes all required outputs and records honest limitations |

If supervised personal-fit labels are absent, that learning subtask remains explicitly limited; do not misreport market forecasting runs as personal-fit training. If all forecast data is insufficient, visible unavailable states are allowed, but do not claim a successful forecasting experiment. Report implemented functionality, coverage, evaluated quality and competition compliance separately.

## Integration instructions for Codex

1. Read applicable repository instructions and current policies/reports. Treat this file as an explicit update to product intent, not evidence that runtime behaviour already matches it.
2. Preserve D01–D02 and the approved D03 pipeline. Preserve confirmed D04 scope and source/time distinctions. Identify the old milestone-dependent score and all consumers, labels and fixtures affected by changing its meaning. Do not reopen automatic industry exclusion as an undecided option.
3. Do not silently reuse the old F identifier/formula for a different measurement or assume an earlier F/D blend is automatically valid for new score definitions.
4. Read the actual role inventory and data manifests. Report source, normalised, runtime, and profile-dependent score coverage separately.
5. Work on independent confirmed components while exact numerical specifications are prepared. Enforce the settled visibility and authorisation rules now. Do not treat the whole project as blocked or claim all formulas are final; surface any new substantive scoring choice as a concrete specification change rather than an invented assumption.
6. Use real service-level outputs as acceptance evidence. Record implementation success, usable data coverage, and measured model quality separately.
7. Commit a local checkpoint after each bounded engineering phase and a culminating checkpoint for each lane and final integration. Keep post-checkpoint refinements linked as PHASE-ID-R01/R02 with their own fix commits and evidence. Defer tasks requiring genuine human decisions, continue independent work, and report exact statuses/SHAs. Do not push until the user explicitly requests it. Do not fabricate retrospective history. This document itself makes no project-repository changes or commits.

## Scope boundary

This is the single canonical D01–D09 decision context, including the architect's final market-presentation and agent-authorisation choices. It does not assert a trained model or working deployment exists, grant new paid resources, invent dataset coverage, guarantee future accuracy, select an unstated numeric current/future blend, or claim the unseen repository was audited. It preserves the user's intended implementation scope and makes engineering/evidence dependencies visible rather than silently substituting generated facts.

## Technical references for implementation

- Time-ordered validation: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html
- Ridge regression: https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html
- Groq local/application tool execution: https://console.groq.com/docs/tool-use/local-tool-calling
- RunPod serverless billing: https://docs.runpod.io/serverless/pricing

Reference documentation supports implementation mechanics; it does not establish the quality of this project's own trained models or available credits. Verify installed/runtime versions when implementing.
