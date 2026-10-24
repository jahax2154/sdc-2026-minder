# A-N11-R01 — measured grouped-number false rejection

The exact requested browser question passed on88e9201 with a direct answer and
Sources-only diagnostics. Inspection of its actual typed model output revealed
one supported finding omitted by unsupported_web_quantity:
“The labour force participation rate rose slightly from70.9% in July to71.0% in
August2026, while the number of employed persons increased from16,845.6thousand
to16,874.4thousand.” Original private inspection preserves the exact spacing/text.
The official CSV renders the same counts without grouping commas.

Normalize only valid three-digit comma grouping when the exact equivalent number
is present in the typed official DOSM source. This does not permit malformed groups,
invented figures, new derived rates or arbitrary-source conversions. Existing
source/quote/authority rules remain.20focusedwebtests PASS0.096s, including the
actual presentation case and malformed/invented/non-typed-source rejection.

A final real-browser check of the same exact question follows; the earlier native
result and its omitted-claim evidence are preserved, not rewritten as a full pass.
