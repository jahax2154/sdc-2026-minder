# contracts

**PROPOSED:** Shared interface definitions and examples after agreement. See `../docs/API_CONTRACT_DRAFT.md`; no finalized schemas are present.

## ML foundation v1

The authorized foundation task introduces executable [recommendation result](recommendation-result.v1.schema.json) and [annotation](personal-fit-annotation.v1.schema.json) contracts. These cover the callable intelligence boundary, not an implemented HTTP route. See [semantics and verification](../docs/ml-foundation.md). Broader API schemas remain pending.

## G0 additive parallel interfaces

[parallel-services.v1.schema.json](parallel-services.v1.schema.json) defines the new versioned lane DTOs without replacing the legacy preparation/annotation contracts. See [shared interfaces](../docs/execution/parallel/SHARED_INTERFACES.md), [ownership](../docs/execution/parallel/ownership.v1.json), and [pending numeric migration](../docs/execution/parallel/NUMERICAL_POLICY_MAP.md). Synthetic examples in `fixtures/parallel-v1/` are contract inputs, not labels or live data.
