# Consolidated role and source approval report — calibration v1

Status: **PENDING HUMAN DECISIONS**. Schema approval does not approve any role content or mapping. No boxes are selected, no reviewer is assigned, and this report does not change authoritative JSON records.

Choose exactly one of Approve / Revise / Reject for each decision. Supply reviewer ID, actual date and rationale. For Revise, write the proposed replacement and review it again before use. Blank or ambiguous decisions remain pending. Approval of a role title is not blanket approval of all of its criteria, rubrics or mappings.

All occupational content below is a proposal. Source IM/LV ratings are context, not demonstrated user fractions or approved criterion weights. The three roles are listed in catalogue order, not recommendation order. No model scores or rankings are included.

## Located materials and reconciliation

| Material | Existing path | Coverage |
| --- | --- | --- |
| Original role cards / criterion source rows | [three_roles.pending.json](../../three_roles.pending.json) | 3 roles, 6 criterion proposals |
| Original criterion worksheet | [role_requirements_worksheet.csv](../../role_requirements_worksheet.csv) | Same 6 criterion IDs |
| Canonical role cards | [roles.pending.json](../roles.pending.json) | Same 3 roles / 6 criteria; 3 source-identity mappings |
| Original external mappings | [source_mappings.pending.json](../../source_mappings.pending.json) | 24 candidate relations |
| Canonical external mappings | [role_market_crosswalks.pending.json](../role_market_crosswalks.pending.json) | Same 24 source/target pairs |
| Skill taxonomy mappings | [skill_taxonomy_crosswalks.pending.json](../skill_taxonomy_crosswalks.pending.json) | No records supplied; not evidence of zero skill demand |
| Attribution and source hashes | [source_references.json](../../source_references.json) | Source URLs, licences and limitations |
| Earlier blind packet | [blind_grading_packet.pending.json](../../blind_grading_packet.pending.json) | Copies of the same pending role proposals, not additional role approvals |
| Earlier intake slots | [annotation_intake.pending.csv](../../annotation_intake.pending.csv) | 3 blank slots; no reviewed labels |

## Shared source and scope decisions

O*NET role/skill reference: version 31.0, U.S. occupations. The external crosswalk uses O*NET-SOC 2019 and ESCO v1.1.0, with a September 2022 mapping vintage. A relation in that file does not prove current taxonomy alignment or suitability for a Malaysian initial-preparation pathway. Broad, close, narrow and exact relations are different. No detailed-role Malaysian demand measurement is provided.

| Decision ID | Review question | Approve | Revise | Reject | Reviewer ID / actual date | Rationale / required revision |
| --- | --- | --- | --- | --- | --- | --- |
| SCOPE-01 | Confirm these three pilot role choices and the proposed Malaysia preference context; distinguish U.S. source scope from local applicability. | [ ] | [ ] | [ ] | ______ | ______ |
| SCOPE-02 | Confirm the proposed 12-week preparation horizon; it is not a career-success or hiring horizon. | [ ] | [ ] | [ ] | ______ | ______ |
| SOURCE-01 | Review attribution/reuse terms, including the crosswalk-specific licence still not independently verified. | [ ] | [ ] | [ ] | ______ | ______ |
| SOURCE-02 | Review 2019 crosswalk → 31.0 role identity compatibility; do not silently treat source vintages as equal. | [ ] | [ ] | [ ] | ______ | ______ |

## Software Developers — 15-1252.00

Current role review: **pending**. Canonical version: `three-role-proposal-v1`. Approved preparation milestone: **not supplied**. Initial task/interest tags are not yet reviewed.

### Role scope and preparation fields

| Decision ID | Item / proposal | Approve | Revise | Reject | Reviewer ID / actual date | Rationale / replacement |
| --- | --- | --- | --- | --- | --- | --- |
| 15-1252.00-ROLE | Confirm stable source identity and role title. | [ ] | [ ] | [ ] | ______ | ______ |
| 15-1252.00-MILESTONE | Define and approve an observable initial-preparation milestone: ______. | [ ] | [ ] | [ ] | ______ | ______ |
| 15-1252.00-TAGS | Define task/interest tags and work conditions supported by reviewed evidence: ______. | [ ] | [ ] | [ ] | ______ | ______ |
| 15-1252.00-EFFORT | Specify remaining effort E used: ______ hours; low: ______; high: ______; estimate basis: ______. All currently null. | [ ] | [ ] | [ ] | ______ | ______ |
| 15-1252.00-WEIGHTS | Approve or replace proposed equal criterion weights (1 each); approved weights are currently null and full weight sum must be positive. | [ ] | [ ] | [ ] | ______ | ______ |
| 15-1252.00-IDENTITY | Source identity O*NET-SOC 15-1252.00 / role reference 31.0. This identity mapping remains pending; it does not approve an ESCO or market mapping. | [ ] | [ ] | [ ] | ______ | ______ |

### Proposed observable criteria

**sw-requirements** — Reading Comprehension

Given a small fictional feature brief, identify its inputs, outputs and two explicit acceptance checks.

Source evidence (not user proficiency):
- `ml/minder_ml_starter/raw/onet_31_0_essential_skills.csv`, row 2282, element `2.A.1.a`, IM=3.50, measured 08/2025, suppression=N, not-relevant=''.
- `ml/minder_ml_starter/raw/onet_31_0_essential_skills.csv`, row 2283, element `2.A.1.a`, LV=4.25, measured 08/2025, suppression=N, not-relevant='N'.

Proposed criterion weight: 1. Approved weight: ______. Define observable content for demonstrated fraction, partial credit and unknown evidence: ______.

| Decision ID | Item / proposal | Approve | Revise | Reject | Reviewer ID / actual date | Rationale / replacement |
| --- | --- | --- | --- | --- | --- | --- |
| sw-requirements | Approve/revise/reject this initial-milestone criterion, source-to-criterion interpretation, weight and observable evidence rule as written above. | [ ] | [ ] | [ ] | ______ | ______ |

**sw-debugging** — Critical Thinking

Given a small fictional failing program and test output, explain a plausible cause and a verification step.

Source evidence (not user proficiency):
- `ml/minder_ml_starter/raw/onet_31_0_essential_skills.csv`, row 2294, element `2.A.2.a`, IM=3.88, measured 08/2025, suppression=N, not-relevant=''.
- `ml/minder_ml_starter/raw/onet_31_0_essential_skills.csv`, row 2295, element `2.A.2.a`, LV=4.12, measured 08/2025, suppression=N, not-relevant='N'.

Proposed criterion weight: 1. Approved weight: ______. Define observable content for demonstrated fraction, partial credit and unknown evidence: ______.

| Decision ID | Item / proposal | Approve | Revise | Reject | Reviewer ID / actual date | Rationale / replacement |
| --- | --- | --- | --- | --- | --- | --- |
| sw-debugging | Approve/revise/reject this initial-milestone criterion, source-to-criterion interpretation, weight and observable evidence rule as written above. | [ ] | [ ] | [ ] | ______ | ______ |

### Feature rubric decisions

These existing generic rubric proposals require role-specific definitions and evidence rules; unknown is not a neutral value. No user alignment has been assessed.

**interest_alignment** — 0 documented conflict/unavailable; 0.5 documented partial alignment/feasibility; 1 documented alignment/feasibility; unknown stays null. Review role-specific criteria and resource checklist.

Role-specific anchors, resource checklist / work conditions, and evidence rule: ______.

| Decision ID | Item / proposal | Approve | Revise | Reject | Reviewer ID / actual date | Rationale / replacement |
| --- | --- | --- | --- | --- | --- | --- |
| 15-1252.00-interest_alignment | Review this role-specific rubric; generic schema validity is not approval. | [ ] | [ ] | [ ] | ______ | ______ |

**resource_feasibility** — 0 documented conflict/unavailable; 0.5 documented partial alignment/feasibility; 1 documented alignment/feasibility; unknown stays null. Review role-specific criteria and resource checklist.

Role-specific anchors, resource checklist / work conditions, and evidence rule: ______.

| Decision ID | Item / proposal | Approve | Revise | Reject | Reviewer ID / actual date | Rationale / replacement |
| --- | --- | --- | --- | --- | --- | --- |
| 15-1252.00-resource_feasibility | Review this role-specific rubric; generic schema validity is not approval. | [ ] | [ ] | [ ] | ______ | ______ |

**work_style_alignment** — 0 documented conflict/unavailable; 0.5 documented partial alignment/feasibility; 1 documented alignment/feasibility; unknown stays null. Review role-specific criteria and resource checklist.

Role-specific anchors, resource checklist / work conditions, and evidence rule: ______.

| Decision ID | Item / proposal | Approve | Revise | Reject | Reviewer ID / actual date | Rationale / replacement |
| --- | --- | --- | --- | --- | --- | --- |
| 15-1252.00-work_style_alignment | Review this role-specific rubric; generic schema validity is not approval. | [ ] | [ ] | [ ] | ______ | ______ |

## Data Scientists — 15-2051.00

Current role review: **pending**. Canonical version: `three-role-proposal-v1`. Approved preparation milestone: **not supplied**. Initial task/interest tags are not yet reviewed.

### Role scope and preparation fields

| Decision ID | Item / proposal | Approve | Revise | Reject | Reviewer ID / actual date | Rationale / replacement |
| --- | --- | --- | --- | --- | --- | --- |
| 15-2051.00-ROLE | Confirm stable source identity and role title. | [ ] | [ ] | [ ] | ______ | ______ |
| 15-2051.00-MILESTONE | Define and approve an observable initial-preparation milestone: ______. | [ ] | [ ] | [ ] | ______ | ______ |
| 15-2051.00-TAGS | Define task/interest tags and work conditions supported by reviewed evidence: ______. | [ ] | [ ] | [ ] | ______ | ______ |
| 15-2051.00-EFFORT | Specify remaining effort E used: ______ hours; low: ______; high: ______; estimate basis: ______. All currently null. | [ ] | [ ] | [ ] | ______ | ______ |
| 15-2051.00-WEIGHTS | Approve or replace proposed equal criterion weights (1 each); approved weights are currently null and full weight sum must be positive. | [ ] | [ ] | [ ] | ______ | ______ |
| 15-2051.00-IDENTITY | Source identity O*NET-SOC 15-2051.00 / role reference 31.0. This identity mapping remains pending; it does not approve an ESCO or market mapping. | [ ] | [ ] | [ ] | ______ | ______ |

### Proposed observable criteria

**ds-statistics** — Mathematics

Given a small public or synthetic table, calculate and explain basic summaries, units and missingness.

Source evidence (not user proficiency):
- `ml/minder_ml_starter/raw/onet_31_0_essential_skills.csv`, row 2670, element `2.A.1.e`, IM=4.38, measured 08/2026, suppression=N, not-relevant=''.
- `ml/minder_ml_starter/raw/onet_31_0_essential_skills.csv`, row 2671, element `2.A.1.e`, LV=5.00, measured 08/2026, suppression=N, not-relevant='N'.

Proposed criterion weight: 1. Approved weight: ______. Define observable content for demonstrated fraction, partial credit and unknown evidence: ______.

| Decision ID | Item / proposal | Approve | Revise | Reject | Reviewer ID / actual date | Rationale / replacement |
| --- | --- | --- | --- | --- | --- | --- |
| ds-statistics | Approve/revise/reject this initial-milestone criterion, source-to-criterion interpretation, weight and observable evidence rule as written above. | [ ] | [ ] | [ ] | ______ | ______ |

**ds-evaluation** — Critical Thinking

Given a toy prediction task, explain a baseline comparison and identify an example of data leakage.

Source evidence (not user proficiency):
- `ml/minder_ml_starter/raw/onet_31_0_essential_skills.csv`, row 2674, element `2.A.2.a`, IM=4.25, measured 08/2026, suppression=N, not-relevant=''.
- `ml/minder_ml_starter/raw/onet_31_0_essential_skills.csv`, row 2675, element `2.A.2.a`, LV=4.62, measured 08/2026, suppression=N, not-relevant='N'.

Proposed criterion weight: 1. Approved weight: ______. Define observable content for demonstrated fraction, partial credit and unknown evidence: ______.

| Decision ID | Item / proposal | Approve | Revise | Reject | Reviewer ID / actual date | Rationale / replacement |
| --- | --- | --- | --- | --- | --- | --- |
| ds-evaluation | Approve/revise/reject this initial-milestone criterion, source-to-criterion interpretation, weight and observable evidence rule as written above. | [ ] | [ ] | [ ] | ______ | ______ |

### Feature rubric decisions

These existing generic rubric proposals require role-specific definitions and evidence rules; unknown is not a neutral value. No user alignment has been assessed.

**interest_alignment** — 0 documented conflict/unavailable; 0.5 documented partial alignment/feasibility; 1 documented alignment/feasibility; unknown stays null. Review role-specific criteria and resource checklist.

Role-specific anchors, resource checklist / work conditions, and evidence rule: ______.

| Decision ID | Item / proposal | Approve | Revise | Reject | Reviewer ID / actual date | Rationale / replacement |
| --- | --- | --- | --- | --- | --- | --- |
| 15-2051.00-interest_alignment | Review this role-specific rubric; generic schema validity is not approval. | [ ] | [ ] | [ ] | ______ | ______ |

**resource_feasibility** — 0 documented conflict/unavailable; 0.5 documented partial alignment/feasibility; 1 documented alignment/feasibility; unknown stays null. Review role-specific criteria and resource checklist.

Role-specific anchors, resource checklist / work conditions, and evidence rule: ______.

| Decision ID | Item / proposal | Approve | Revise | Reject | Reviewer ID / actual date | Rationale / replacement |
| --- | --- | --- | --- | --- | --- | --- |
| 15-2051.00-resource_feasibility | Review this role-specific rubric; generic schema validity is not approval. | [ ] | [ ] | [ ] | ______ | ______ |

**work_style_alignment** — 0 documented conflict/unavailable; 0.5 documented partial alignment/feasibility; 1 documented alignment/feasibility; unknown stays null. Review role-specific criteria and resource checklist.

Role-specific anchors, resource checklist / work conditions, and evidence rule: ______.

| Decision ID | Item / proposal | Approve | Revise | Reject | Reviewer ID / actual date | Rationale / replacement |
| --- | --- | --- | --- | --- | --- | --- |
| 15-2051.00-work_style_alignment | Review this role-specific rubric; generic schema validity is not approval. | [ ] | [ ] | [ ] | ______ | ______ |

## Information Security Analysts — 15-1212.00

Current role review: **pending**. Canonical version: `three-role-proposal-v1`. Approved preparation milestone: **not supplied**. Initial task/interest tags are not yet reviewed.

### Role scope and preparation fields

| Decision ID | Item / proposal | Approve | Revise | Reject | Reviewer ID / actual date | Rationale / replacement |
| --- | --- | --- | --- | --- | --- | --- |
| 15-1212.00-ROLE | Confirm stable source identity and role title. | [ ] | [ ] | [ ] | ______ | ______ |
| 15-1212.00-MILESTONE | Define and approve an observable initial-preparation milestone: ______. | [ ] | [ ] | [ ] | ______ | ______ |
| 15-1212.00-TAGS | Define task/interest tags and work conditions supported by reviewed evidence: ______. | [ ] | [ ] | [ ] | ______ | ______ |
| 15-1212.00-EFFORT | Specify remaining effort E used: ______ hours; low: ______; high: ______; estimate basis: ______. All currently null. | [ ] | [ ] | [ ] | ______ | ______ |
| 15-1212.00-WEIGHTS | Approve or replace proposed equal criterion weights (1 each); approved weights are currently null and full weight sum must be positive. | [ ] | [ ] | [ ] | ______ | ______ |
| 15-1212.00-IDENTITY | Source identity O*NET-SOC 15-1212.00 / role reference 31.0. This identity mapping remains pending; it does not approve an ESCO or market mapping. | [ ] | [ ] | [ ] | ______ | ______ |

### Proposed observable criteria

**sec-policy** — Reading Comprehension

Given a fictional access policy, explain who may access each example resource and why.

Source evidence (not user proficiency):
- `ml/minder_ml_starter/raw/onet_31_0_essential_skills.csv`, row 2062, element `2.A.1.a`, IM=4.00, measured 08/2018, suppression=N, not-relevant=''.
- `ml/minder_ml_starter/raw/onet_31_0_essential_skills.csv`, row 2063, element `2.A.1.a`, LV=4.12, measured 08/2018, suppression=N, not-relevant='N'.

Proposed criterion weight: 1. Approved weight: ______. Define observable content for demonstrated fraction, partial credit and unknown evidence: ______.

| Decision ID | Item / proposal | Approve | Revise | Reject | Reviewer ID / actual date | Rationale / replacement |
| --- | --- | --- | --- | --- | --- | --- |
| sec-policy | Approve/revise/reject this initial-milestone criterion, source-to-criterion interpretation, weight and observable evidence rule as written above. | [ ] | [ ] | [ ] | ______ | ______ |

**sec-risk** — Critical Thinking

Given a fictional system description, identify a plausible risk and justify a proportionate mitigation.

Source evidence (not user proficiency):
- `ml/minder_ml_starter/raw/onet_31_0_essential_skills.csv`, row 2074, element `2.A.2.a`, IM=3.88, measured 08/2018, suppression=N, not-relevant=''.
- `ml/minder_ml_starter/raw/onet_31_0_essential_skills.csv`, row 2075, element `2.A.2.a`, LV=4.12, measured 08/2018, suppression=N, not-relevant='N'.

Proposed criterion weight: 1. Approved weight: ______. Define observable content for demonstrated fraction, partial credit and unknown evidence: ______.

| Decision ID | Item / proposal | Approve | Revise | Reject | Reviewer ID / actual date | Rationale / replacement |
| --- | --- | --- | --- | --- | --- | --- |
| sec-risk | Approve/revise/reject this initial-milestone criterion, source-to-criterion interpretation, weight and observable evidence rule as written above. | [ ] | [ ] | [ ] | ______ | ______ |

### Feature rubric decisions

These existing generic rubric proposals require role-specific definitions and evidence rules; unknown is not a neutral value. No user alignment has been assessed.

**interest_alignment** — 0 documented conflict/unavailable; 0.5 documented partial alignment/feasibility; 1 documented alignment/feasibility; unknown stays null. Review role-specific criteria and resource checklist.

Role-specific anchors, resource checklist / work conditions, and evidence rule: ______.

| Decision ID | Item / proposal | Approve | Revise | Reject | Reviewer ID / actual date | Rationale / replacement |
| --- | --- | --- | --- | --- | --- | --- |
| 15-1212.00-interest_alignment | Review this role-specific rubric; generic schema validity is not approval. | [ ] | [ ] | [ ] | ______ | ______ |

**resource_feasibility** — 0 documented conflict/unavailable; 0.5 documented partial alignment/feasibility; 1 documented alignment/feasibility; unknown stays null. Review role-specific criteria and resource checklist.

Role-specific anchors, resource checklist / work conditions, and evidence rule: ______.

| Decision ID | Item / proposal | Approve | Revise | Reject | Reviewer ID / actual date | Rationale / replacement |
| --- | --- | --- | --- | --- | --- | --- |
| 15-1212.00-resource_feasibility | Review this role-specific rubric; generic schema validity is not approval. | [ ] | [ ] | [ ] | ______ | ______ |

**work_style_alignment** — 0 documented conflict/unavailable; 0.5 documented partial alignment/feasibility; 1 documented alignment/feasibility; unknown stays null. Review role-specific criteria and resource checklist.

Role-specific anchors, resource checklist / work conditions, and evidence rule: ______.

| Decision ID | Item / proposal | Approve | Revise | Reject | Reviewer ID / actual date | Rationale / replacement |
| --- | --- | --- | --- | --- | --- | --- |
| 15-1212.00-work_style_alignment | Review this role-specific rubric; generic schema validity is not approval. | [ ] | [ ] | [ ] | ______ | ______ |

## All external source-mapping candidates

For every candidate, review the specific relation, taxonomy/version alignment, applicable scope, reuse terms and rationale. Approving an external mapping does not approve personal-fit labels, detailed-role demand or skill-demand measurements. An ISCO aggregate relation is not interchangeable with an ESCO occupation relation.

From taxonomy for all rows: **O*NET-SOC 2019**. ESCO target version: **1.1.0**. ISCO target version: **not supplied**. Source: `esco_onet_crosswalk`, source CSV SHA-256 `82179a0a3340da97b63df90134d8d941ec3c2c478334d855b69e4dd57a91b620`.

| Mapping ID / source row | From role | Target identifier / label | Source relation / scope | Approve | Revise | Reject | Reviewer ID / actual date | Rationale / replacement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| esco-onet-review-1 / row 581 | 15-1212.00 | ICT security engineer — http://data.europa.eu/esco/occupation/0ce5a9f4-e00a-4bbe-b255-3c63407167a4 | exactMatch; ESCO | [ ] | [ ] | [ ] | ______ | ______ |
| esco-onet-review-2 / row 582 | 15-1212.00 | ICT resilience manager — http://data.europa.eu/esco/occupation/a99b38bc-6e71-4bef-b127-0f2b5e357815 | narrowMatch; ESCO | [ ] | [ ] | [ ] | ______ | ______ |
| esco-onet-review-3 / row 583 | 15-1212.00 | embedded systems security engineer — http://data.europa.eu/esco/occupation/1c5a896a-e010-4217-a29a-c44db26e25da | broadMatch; ESCO | [ ] | [ ] | [ ] | ______ | ______ |
| esco-onet-review-4 / row 584 | 15-1212.00 | ICT security administrator — http://data.europa.eu/esco/occupation/0464b062-cea6-4164-b10d-956c61956ae7 | closeMatch; ESCO | [ ] | [ ] | [ ] | ______ | ______ |
| esco-onet-review-5 / row 585 | 15-1212.00 | ICT security manager — http://data.europa.eu/esco/occupation/7754d570-9519-48c2-b1c9-8e165f8bca0f | closeMatch; ESCO | [ ] | [ ] | [ ] | ______ | ______ |
| esco-onet-review-6 / row 620 | 15-1252.00 | ICT application developer — http://data.europa.eu/esco/occupation/bd272aee-adc9-4a06-a15c-a73b4b4a46a7 | broadMatch; ESCO | [ ] | [ ] | [ ] | ______ | ______ |
| esco-onet-review-7 / row 621 | 15-1252.00 | software developer — http://data.europa.eu/esco/occupation/f2b15a0e-e65a-438a-affb-29b9d50b77d1 | broadMatch; ESCO | [ ] | [ ] | [ ] | ______ | ______ |
| esco-onet-review-8 / row 622 | 15-1252.00 | ICT system developer — http://data.europa.eu/esco/occupation/a7c1d23d-aeca-4bee-9a08-5993ed98b135 | broadMatch; ESCO | [ ] | [ ] | [ ] | ______ | ______ |
| esco-onet-review-9 / row 623 | 15-1252.00 | software architect — http://data.europa.eu/esco/occupation/d0aa0792-4345-474b-9365-686cf4869d2e | broadMatch; ESCO | [ ] | [ ] | [ ] | ______ | ______ |
| esco-onet-review-10 / row 624 | 15-1252.00 | software analyst — http://data.europa.eu/esco/occupation/04ba4d6c-957d-417f-bf63-5b9e015a9f86 | broadMatch; ESCO | [ ] | [ ] | [ ] | ______ | ______ |
| esco-onet-review-11 / row 625 | 15-1252.00 | industrial mobile devices software developer — http://data.europa.eu/esco/occupation/bb6198c4-1d3e-40b9-9cc4-ad2dd9d7c74b | broadMatch; ESCO | [ ] | [ ] | [ ] | ______ | ______ |
| esco-onet-review-12 / row 626 | 15-1252.00 | database developer — http://data.europa.eu/esco/occupation/b11e1742-5e28-4270-b081-b0193d85ee7d | broadMatch; ESCO | [ ] | [ ] | [ ] | ______ | ______ |
| esco-onet-review-13 / row 627 | 15-1252.00 | mobile application developer — http://data.europa.eu/esco/occupation/2ed56c3f-61d6-4f7e-9ef8-8849eb102e4c | broadMatch; ESCO | [ ] | [ ] | [ ] | ______ | ______ |
| esco-onet-review-14 / row 628 | 15-1252.00 | user interface developer — http://data.europa.eu/esco/occupation/866c7813-2c03-47d7-9bdc-192cfbace57c | broadMatch; ESCO | [ ] | [ ] | [ ] | ______ | ______ |
| esco-onet-review-15 / row 629 | 15-1252.00 | embedded systems software developer — http://data.europa.eu/esco/occupation/57af9090-55b4-4911-b2d0-86db01c00b02 | broadMatch; ESCO | [ ] | [ ] | [ ] | ______ | ______ |
| esco-onet-review-16 / row 630 | 15-1252.00 | Software developers — http://data.europa.eu/esco/isco/C2512 | exactISCO; ISCO (version unspecified) | [ ] | [ ] | [ ] | ______ | ______ |
| esco-onet-review-17 / row 631 | 15-1252.00 | digital games developer — http://data.europa.eu/esco/occupation/9ebaf3f0-0be0-47b7-b2b1-b3b04130fa81 | broadMatch; ESCO | [ ] | [ ] | [ ] | ______ | ______ |
| esco-onet-review-18 / row 632 | 15-1252.00 | gambling games developer — http://data.europa.eu/esco/occupation/18552245-3c36-4a52-b4c6-295cabb5c93b | broadMatch; ESCO | [ ] | [ ] | [ ] | ______ | ______ |
| esco-onet-review-19 / row 694 | 15-2051.00 | data scientist — http://data.europa.eu/esco/occupation/258e46f9-0075-4a2e-adae-1ff0477e0f30 | exactMatch; ESCO | [ ] | [ ] | [ ] | ______ | ______ |
| esco-onet-review-20 / row 695 | 15-2051.00 | statistician — http://data.europa.eu/esco/occupation/ac8b3cd1-a127-4e6a-8208-5cfcf7111955 | closeMatch; ESCO | [ ] | [ ] | [ ] | ______ | ______ |
| esco-onet-review-21 / row 696 | 15-2051.00 | data analyst — http://data.europa.eu/esco/occupation/d3edb8f8-3a06-47a0-8fb9-9b212c006aa2 | closeMatch; ESCO | [ ] | [ ] | [ ] | ______ | ______ |
| esco-onet-review-22 / row 697 | 15-2051.00 | ICT intelligent systems designer — http://data.europa.eu/esco/occupation/35553663-deab-4d9a-bf22-15c1625d28e8 | broadMatch; ESCO | [ ] | [ ] | [ ] | ______ | ______ |
| esco-onet-review-23 / row 698 | 15-2051.00 | computer vision engineer — http://data.europa.eu/esco/occupation/1c5a45b9-440e-4726-b565-16a952abd341 | closeMatch; ESCO | [ ] | [ ] | [ ] | ______ | ______ |
| esco-onet-review-24 / row 699 | 15-2051.00 | knowledge engineer — http://data.europa.eu/esco/occupation/812c217d-32b7-4f6a-9faf-993d3577ac7f | closeMatch; ESCO | [ ] | [ ] | [ ] | ______ | ______ |

## Reviewer completion and transfer

- Keep every original JSON card, criterion and mapping pending until an actual reviewer records the corresponding decision, identity/date and rationale. Do not treat checked boxes alone as validated pipeline input.
- Record precise accepted content, effort ranges, weights, evidence rules and mapping scope before updating the authoritative canonical records in a separately reviewed change. Preserve rejected and revised proposals in the audit trail.
- The five supplied synthetic scenario families are drafts, not empirical examples or proof of statistical independence. Confirm their varied raw evidence and family grouping before calibration.
- Begin relevance grading only after the applicable role cards and requirements are approved and the profile evidence is sufficient. Keep initial judgments independent of algorithm outputs.
- No approved roles, approved profile families or gold labels are created by this report. Empirical training remains blocked until actual approvals, independently reviewed compatible labels, grouped evaluation prerequisites and the authorized training runtime exist.
