# G1A-R — one pending milestone/template batch

**PENDING — inactive. No human approval, estimate, profile assessment or gold label is recorded.**

Decision for the whole batch: [ ] Approve  [ ] Revise  [ ] Reject

Decision ID / reviewer / date / rationale: **not supplied**. The structured decision record remains `batch_decision.pending.json` with status pending and null reviewer fields. No record has been converted to gold.

The batch SHA-256 is `a7d41f3799a0010df0d5aa17954183f92fa0affc6f66791b58488577621783b3`. Revise the batch first if needed, then bind any actual decision to its updated hash.

## What can be decided once

Approve/revise the bounded artifacts, both criteria per role, content anchors, synthetic exercises, independent task graph, interest/work-style tags, resource group and the absence of additional hard requirements for these local written exercises. That last choice concerns these exercises only; it does not establish occupational or legal eligibility. Equal criterion/tag/group weights of 1 come from existing policy, not a new per-role coefficient decision.

**Still required:** six defensible task-effort ranges in hours, with an accepted named estimate method, per-task basis and evidence linked to the real decision. All bounds are null today. The proposed method separates setup, reference reading, artifact work and checking; use actual task measurements to inform a reviewed estimate or a named accepted work-breakdown estimate. Course duration is not mastery time, and missing effort is not zero. No new completed profile should be claimed before a valid milestone exists.

The loader requires concrete assessment instance IDs, exact batch hash, an actual approval record and these estimates. The six examples below are proposed answer keys, not user answers or relevance labels. After a complete real decision, `activation_plan` is read-only; `activate_batch` explicitly registers a content-addressed release in the ML source registry. Neither has activated this batch.

## Proposed role milestones

### 15-1252.00 — g1ar-initial-15-1252.00

A written brief-analysis and debugging worksheet for supplied fictional examples.

| Criterion | Assessed unmet (0) | Partial (0.5) | Full (1) |
| --- | --- | --- | --- |
| sw-requirements | Cannot identify the brief inputs or outputs. | Identifies the inputs and outputs, but supplies fewer than two relevant acceptance checks. | Identifies the inputs and outputs and gives two acceptance checks linked to the stated brief. |
| sw-debugging | Provides no plausible cause consistent with the supplied failure. | Explains a plausible cause but provides no usable verification step. | Explains a plausible cause and a verification step that could confirm or disconfirm it. |

Two independent worksheet tasks are proposed, one per existing criterion; no prerequisite edges are asserted until this graph is accepted. No essential draft criterion is removed.

Interest tags: requirements-analysis, debugging-explanation. Work-style tag: structured written explanation. These are proposed task mappings, not measured occupation-wide preferences.

Resource group: confirm ability to read the public references and write the supplied fictional worksheet. The proposed browser/local-workbook alternative must be explicitly confirmed by a future synthetic profile. No paid cloud account, assumed access or invented empty resource group clears R.

**sw-requirements — synthetic instance sw-requirements-scenario-v1**

A fictional tool accepts two nonnegative item costs in MYR, displays their total to two decimal places, and rejects a negative input without displaying a total. Identify its inputs, outputs and two explicit acceptance checks.

Expected evidence: Identify both costs as inputs, the formatted total or validation result as output, and give two concrete cases consistent with the brief.

Context reference: [govuk-requirements-reference](https://www.gov.uk/service-manual/agile-delivery/writing-user-stories). This supports background concepts, not approval of this role-specific criterion or an effort estimate.

**sw-debugging — synthetic instance sw-debugging-scenario-v1**

Fictional Python function: def total(values): return values[0]. The test total([2, 3]) expects 5 but returns 2. Explain a plausible cause and one verification step.

Expected evidence: Explain that only the first element is returned; verify a proposed correction against the two-element test and its stated expected total.

Context reference: [python-errors-reference](https://docs.python.org/3.9/tutorial/errors.html). This supports background concepts, not approval of this role-specific criterion or an effort estimate.


### 15-2051.00 — g1ar-initial-15-2051.00

A written table-summary and toy-model evaluation worksheet using supplied synthetic examples.

| Criterion | Assessed unmet (0) | Partial (0.5) | Full (1) |
| --- | --- | --- | --- |
| ds-statistics | Provides no correct basic summary of the supplied table. | Provides a correct summary but omits units or missingness. | Computes and explains the agreed table summaries with units and missingness. |
| ds-evaluation | Explains neither a baseline comparison nor a valid leakage example. | Explains either a baseline comparison or a valid leakage example, but not both. | Explains a baseline comparison and a valid leakage example in the supplied toy task. |

Two independent worksheet tasks are proposed, one per existing criterion; no prerequisite edges are asserted until this graph is accepted. No essential draft criterion is removed.

Interest tags: table-analysis, model-evaluation-reasoning. Work-style tag: structured written explanation. These are proposed task mappings, not measured occupation-wide preferences.

Resource group: confirm ability to read the public references and write the supplied fictional worksheet. The proposed browser/local-workbook alternative must be explicitly confirmed by a future synthetic profile. No paid cloud account, assumed access or invented empty resource group clears R.

**ds-statistics — synthetic instance ds-statistics-scenario-v1**

Synthetic table: record A=10 minutes, B=20 minutes, C=missing, D=30 minutes. Compute the mean of observed durations, state its units, and describe missingness.

Expected evidence: The observed mean is 20 minutes; one of four records is missing. Explain that the missing value was not treated as zero.

Context reference: [learn-data-reference](https://learn.microsoft.com/en-us/training/modules/explore-analyze-data-with-python/). This supports background concepts, not approval of this role-specific criterion or an effort estimate.

**ds-evaluation — synthetic instance ds-evaluation-scenario-v1**

A fictional model predicts course completion at enrollment. Explain a comparison with a rule that always predicts the training-set majority class on held-out cases. Would the eventual final-exam result be a valid enrollment-time feature?

Expected evidence: Explain using the same held-out cases for the model and baseline. Identify the eventual exam result as unavailable at enrollment and therefore leakage.

Context reference: [sklearn-leakage-reference](https://scikit-learn.org/1.6/common_pitfalls.html#data-leakage). This supports background concepts, not approval of this role-specific criterion or an effort estimate.


### 15-1212.00 — g1ar-initial-15-1212.00

A written fictional access-policy and risk-mitigation worksheet.

| Criterion | Assessed unmet (0) | Partial (0.5) | Full (1) |
| --- | --- | --- | --- |
| sec-policy | Does not correctly apply the fictional access policy to an example. | Correctly identifies access for some examples but leaves the rationale or remaining examples incomplete. | Correctly identifies access for every supplied example and links each decision to the fictional policy. |
| sec-risk | Identifies no plausible risk grounded in the fictional system. | Identifies a plausible risk but does not justify a proportionate mitigation. | Identifies a plausible risk and justifies a proportionate mitigation tied to that system. |

Two independent worksheet tasks are proposed, one per existing criterion; no prerequisite edges are asserted until this graph is accepted. No essential draft criterion is removed.

Interest tags: access-policy-reasoning, risk-mitigation-reasoning. Work-style tag: structured written explanation. These are proposed task mappings, not measured occupation-wide preferences.

Resource group: confirm ability to read the public references and write the supplied fictional worksheet. The proposed browser/local-workbook alternative must be explicitly confirmed by a future synthetic profile. No paid cloud account, assumed access or invented empty resource group clears R.

**sec-policy — synthetic instance sec-policy-scenario-v1**

Fictional policy: readers may read public files only; editors may read/write public and private files. Decide and justify: reader reads public; reader writes public; reader reads private; editor writes private.

Expected evidence: The decisions are allow, deny, deny, allow respectively, each tied to a stated policy clause.

Context reference: [owasp-authorization-reference](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html). This supports background concepts, not approval of this role-specific criterion or an effort estimate.

**sec-risk — synthetic instance sec-risk-scenario-v1**

A fictional team keeps a shared API credential in a folder readable by every member and has no access log. Identify one plausible risk and justify one proportionate mitigation. Do not assume a breach occurred.

Expected evidence: Describe a plausible unauthorized-use or disclosure risk and justify limiting credential access, moving it to controlled storage, or another proportionate mitigation. Do not claim an observed incident.

Context reference: [learn-security-reference](https://learn.microsoft.com/en-us/training/modules/describe-basic-cybersecurity-threats-attacks-mitigations/). This supports background concepts, not approval of this role-specific criterion or an effort estimate.

## Expected effect and limits

Approval of complete templates could clear catalogue definitions for three roles. It would not fill any of the six existing profiles, clear Q, generate labels or establish recommendation quality. All 18 original pairs remain unscored until version-bound profile measurements also exist. Optional ESCO mappings are unnecessary for native identity; source-side taxonomy alignment is now verified, while relation/target-scope/reuse checks remain unresolved.

The source captures record exact excerpt/summary hashes with explicit scope; they are not raw HTML checksums. Microsoft overview renderings had no usable numeric durations. Actual primary-source versions that were not exposed remain null.

The original pending role cards, criteria, profiles, annotation sheets and all G1A reports remain unchanged.
