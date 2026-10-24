# MA1-R09 — preserve complete guidance after a cut introduction

Actual9111 partial screenshot request succeeds (~1.7s); unseen follow-up first hit
actual rate limit, then a spaced repeat reached Qwen but failed text validation.
A synthetic same-context live diagnostic isolated the remaining reason:
incomplete_guidance_introduction. Qwen returned valid typed arguments and useful
bus-delay evaluation steps but its intro ended 'If it doesn't, that's a ' and a
400-character task description ended mid-word. This was not a renderer inventing
content, missing Profile or a failed action. Exact visible args retained privately;
no hidden reasoning or credentials captured. The initial failed check stays recorded.

A validates all raw structure/citations/targets/unsupported-claim checks, then may
omit ONLY trailing incomplete model sentence fragments when complete useful sentences
already exist. No completion is invented. Prefix remains byte-for-byte model content;
source statements are untouched. Provider metadata records visible_text_adjustments.
Short unusable intros, unexpected mixed language, invalid facts/scores/targets still
fail honestly. No automatic provider/action retry. D stores the actual visible prefix
and typed draft; generation never saves a canonical plan without explicit acceptance.

Safe validation_code now distinguishes known enum reasons without logging raw errors.
A software regression verifies exact retained prefix, adjustment metadata and zero
plan writes. Final actual9111 unseen follow-up must be rechecked after reload; source
rejection is not waived just because the software path now passes.

The check runner supports an explicit <=60s follow-up gap for the observed shared
provider quota. It records real request timings separately from that gap. This is
acceptance pacing, not a production retry or provider-throughput claim.
