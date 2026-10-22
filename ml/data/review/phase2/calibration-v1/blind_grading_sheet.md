# Blind calibration sheet — five synthetic families × three roles

**Preparation only — role approvals are still pending. All relevance grades are blank.** Do not grade until the applicable milestone, criteria, effort, resource/work-style requirements and source scope are substantively reviewed. These five fictional scenario origins are not real people, observed outcome data or proof of empirical independence. Each has one profile; keep any future variants in that same family.

## Reviewer workflow

1. Complete [the approval report](approval_report.md). Record actual decisions, reviewer/date and rationale; nothing is pre-approved. An accepted title alone does not approve its criteria or mappings.
2. Have the engineering owner record the accepted content in the authoritative role cards through a reviewed change. Regenerate a fresh packet against those frozen approved versions before grading; the current packet intentionally remains a pending proposal snapshot. Do not edit pending roles inside a frozen packet to simulate approval.
3. Give independent graders only the approved-version blind packet and a copy of this sheet or its JSON response template. Do not supply engineering feature files, model outputs, score-based orderings or other reviewers' initial judgments. Declare any earlier exposure.
4. Grade preparation relevance within the stated 12-week horizon: 0 = weak; 1 = plausible pathway; 2 = strong. Exclude market attractiveness, salary and hiring probability. Unknown or ambiguous evidence may leave the grade blank with an explanation. Role acceptance is not a target label.
5. Enter your actual reviewer ID, date, independent-review declaration and rationale. Use a separate unique annotation ID per independent judgment. Keep original votes; resolve disagreements explicitly, without averaging them into a generated grade.

## Files and import format

- [profiles.synthetic.json](profiles.synthetic.json): five schema-valid synthetic draft profiles; all profile reviews pending.
- [blind_packet.json](blind_packet.json): all 15 profile–role contexts with proposed role requirements. It omits normalized role alignments and model outputs.
- [blind_grading_sheet.csv](blind_grading_sheet.csv): spreadsheet-friendly 15-row sheet. All relevance_grade, reviewer/date, rationale and independence cells start empty.
- [responses.pending.json](responses.pending.json): the matching canonical annotation array. Grades, label sources and reviewer provenance are null; statuses remain pending.
- [approval_report.md](approval_report.md): source-linked substantive decisions; no choices selected.

The existing annotation importer consumes JSON, not this CSV directly. After genuine grading, transfer `relevance_grade` → JSON `grade`, `review_date` → an actual ISO timestamp in `reviewed_at`, and preserve the pair/family/profile/role versions. Use `label_source=human_reviewed`, `independent_review=true`, and `review_status=approved` only when those claims are actually true and supported by the human review. Pending blanks stay null. Do not promote grades merely to clear a gate. Approval report fields are not machine-applied approvals.

Current frozen export/engineering inputs are under `ml/artifacts/phase2/calibration-v1/export/`. The import-compatible response file above matches that packet; initial graders should not receive `engineering_inputs.json` or `engineering_features.json`. Re-export after role approvals rather than attempting to attach later judgments to these pending-version IDs.

## Synthetic profile cards

All cards use a common proposed 12-week horizon and Malaysia country preference, with no region assumed. No demographic attributes or sensitive identifying information are included. Project descriptions and skill self-reports are fictional, unreviewed narrative evidence; none implies an assessed demonstrated fraction.

### calibration-profile-01 / calibration-family-01

- Goal: Explore building small applications that simplify everyday workflows.
- Available preparation time: 6 hours/week.
- Interests: Building simple tools; Understanding how programs behave
- Education: Fictional introductory computing course; no assessed qualification claimed
- Experience: Fictional beginner with no professional technology experience
- Project/achievement evidence: Fictional tutorial exercise: adapted a short command-line to-do list; no independent assessment.
- Self-reported, unmapped skills: introductory-programming. Assessed fractions: unknown.
- Work preferences: Small clearly defined tasks; Regular feedback
- Resources: Shared laptop on evenings; Home internet
- Learning budget: MYR 0.
- Constraints: Laptop access limited to evenings; Use free learning resources
- Review state: pending; no reviewer assigned.

### calibration-profile-02 / calibration-family-02

- Goal: Explore moving from spreadsheet reports toward reproducible data analysis.
- Available preparation time: 5 hours/week.
- Interests: Explaining patterns in tables; Checking data quality
- Education: Fictional business diploma with an introductory statistics module
- Experience: Three fictional years preparing operational spreadsheet reports; no reviewed data-science competence
- Project/achievement evidence: Fictional work sample: a spreadsheet summarizing monthly service volumes with missing entries noted.
- Self-reported, unmapped skills: spreadsheet-reporting. Assessed fractions: unknown.
- Work preferences: Written explanations; Predictable study sessions
- Resources: Personal laptop; Internet; Spreadsheet software
- Learning budget: MYR 40.
- Constraints: Preparation happens in short evening sessions
- Review state: pending; no reviewer assigned.

### calibration-profile-03 / calibration-family-03

- Goal: Explore an initial information-security preparation milestone grounded in support work.
- Available preparation time: 8 hours/week.
- Interests: Access controls; Investigating system problems
- Education: Fictional IT support certificate; competence not independently assessed
- Experience: Two fictional years handling support tickets and account-access requests
- Project/achievement evidence: Fictional home-lab note: documented account permissions and a routine troubleshooting checklist.
- Self-reported, unmapped skills: support-troubleshooting; account-administration. Assessed fractions: unknown.
- Work preferences: Practical troubleshooting; Documented procedures
- Resources: Personal laptop; Internet; Local virtual-machine lab
- Learning budget: MYR 100.
- Constraints: Use only an isolated authorized lab; no access to real systems is implied
- Review state: pending; no reviewer assigned.

### calibration-profile-04 / calibration-family-04

- Goal: Compare further application development, analytical work and security preparation without assuming a preferred answer.
- Available preparation time: 10 hours/week.
- Interests: Reproducible experiments; Building and testing small tools
- Education: Fictional computing degree; no assessed criterion fractions supplied
- Experience: Three fictional years contributing to small application projects
- Project/achievement evidence: Fictional portfolio description: a small Python program with automated tests; no independently reviewed artifact is supplied.
- Self-reported, unmapped skills: python-scripting; automated-testing. Assessed fractions: unknown.
- Work preferences: Focused individual work; Occasional peer review
- Resources: Personal laptop; Internet; Local development tools
- Learning budget: MYR 150.
- Constraints: No prior approved statistics or security assessment supplied
- Review state: pending; no reviewer assigned.

### calibration-profile-05 / calibration-family-05

- Goal: Explore which initial technology pathway is plausible while career interests remain undecided.
- Available preparation time: 2 hours/week.
- Interests: Unknown — clarification required
- Education: Fictional secondary education; no technology training claimed
- Experience: Four fictional years coordinating routine operations and updating paper/digital checklists
- Project/achievement evidence: Fictional process note: reorganized a recurring operations checklist; no technical skill mastery inferred.
- Self-reported, unmapped skills: process-documentation. Assessed fractions: unknown.
- Work preferences: Step-by-step written instructions; Predictable daytime tasks
- Resources: Phone with intermittent internet; Library computer for a booked weekly session
- Learning budget: MYR 0.
- Constraints: No personal laptop; At most two preparation hours per week; Interests need clarification; do not replace unknown with neutral alignment
- Review state: pending; no reviewer assigned.

## Empty grading grid

Rows are grouped by profile and role identifier for administration, not by recommendation quality. Use the CSV/JSON for full immutable IDs and editable records. All decisions below remain blank.

| Profile / family | Role | Relevance grade (0/1/2) | Reviewer ID / date | Rationale / missing information | Independence / ambiguity |
| --- | --- | --- | --- | --- | --- |
| calibration-profile-01 / calibration-family-01 | Information Security Analysts (`15-1212.00`) |  |  |  |  |
| calibration-profile-01 / calibration-family-01 | Software Developers (`15-1252.00`) |  |  |  |  |
| calibration-profile-01 / calibration-family-01 | Data Scientists (`15-2051.00`) |  |  |  |  |
| calibration-profile-02 / calibration-family-02 | Information Security Analysts (`15-1212.00`) |  |  |  |  |
| calibration-profile-02 / calibration-family-02 | Software Developers (`15-1252.00`) |  |  |  |  |
| calibration-profile-02 / calibration-family-02 | Data Scientists (`15-2051.00`) |  |  |  |  |
| calibration-profile-03 / calibration-family-03 | Information Security Analysts (`15-1212.00`) |  |  |  |  |
| calibration-profile-03 / calibration-family-03 | Software Developers (`15-1252.00`) |  |  |  |  |
| calibration-profile-03 / calibration-family-03 | Data Scientists (`15-2051.00`) |  |  |  |  |
| calibration-profile-04 / calibration-family-04 | Information Security Analysts (`15-1212.00`) |  |  |  |  |
| calibration-profile-04 / calibration-family-04 | Software Developers (`15-1252.00`) |  |  |  |  |
| calibration-profile-04 / calibration-family-04 | Data Scientists (`15-2051.00`) |  |  |  |  |
| calibration-profile-05 / calibration-family-05 | Information Security Analysts (`15-1212.00`) |  |  |  |  |
| calibration-profile-05 / calibration-family-05 | Software Developers (`15-1252.00`) |  |  |  |  |
| calibration-profile-05 / calibration-family-05 | Data Scientists (`15-2051.00`) |  |  |  |  |

This preparation batch contains 5 synthetic draft families, 15 pending pairs, 0 approved roles, 0 approved profile families and 0 gold labels. It authorizes no empirical fitting, baseline-quality claim or learner comparison.
