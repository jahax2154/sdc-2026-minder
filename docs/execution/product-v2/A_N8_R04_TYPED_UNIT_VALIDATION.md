# A-N8-R04 — correct a measured quantitative validation defect

On served527f0d2, Qwen returned a schema-valid current-market explanation with two
findings. The exact rejected text included:

“Unemployment edged down to 2.9% in Aug 2026 from 3.0% in Jul, with participation
at 71.0% and 16.87m employed. This is a two-month national trend, not a sector or
role-level signal.”

“The July baseline (3.0% unemployment, 70.9% participation, 16.85m employed) shows
the small month-on-month improvement, but only two months are available, so the
direction is preliminary.”

Both failed unsupported_web_quantity because the live DOSM CSV reports employed
persons as16874.4 and16845.6thousand. The existing literal-number check rejected
correct unit conversion/rounding. This erased both useful findings; the browser
relevance assertion failed despite actual native provider success. No passing
market-answer result is claimed for that old displayed reply.

public-web-answer-v1.3 accepts only explicitly unit-marked, reproducible conversions
from the typed live DOSM source: thousands→millions, decimal ROUND_HALF_UP to the
precision actually displayed. Wrong values, missing units, arbitrary source text
and fabricated counts remain rejected. Raw CSV hashes, original values and units
remain in the source ledger. This is presentation arithmetic, not a scoring-policy
change or a new measurement. No forecast is generated.

Partial validation now checks independent sentences when a finding contains an
optional rejected sentence, preserving valid prose verbatim and recording the
exact omitted sentence/rule. It never invents a replacement explanation. Dates,
unknown proficiency, source scope and no-action authority remain intact.

14focusedwebchecks PASS0.053s, including the exact two native rejected findings,
wrong-rounding rejection, missing-unit rejection and optional-sentence retention.
The original private ledger and failed browser trace are preserved. Subsequent
actual browser/provider acceptance is separate from this regression proof.
Full backend verification:223tests12.907s PASS,4PostgreSQL-only tests skipped in
this ordinary interpreter. The earlier separate native131-check run remains distinct.
