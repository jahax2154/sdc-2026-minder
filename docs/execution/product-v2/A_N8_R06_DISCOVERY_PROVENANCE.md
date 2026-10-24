# A-N8-R06 — distinguish discovered pages from cited evidence

public-page-discovery-v1.2 prevents a general national aggregate fallback from
outranking a relevant discovered page for a non-software role-specific question.
General national statistics remain contextual evidence, not role hiring demand.
Known software questions retain the verified technical/recruitment detail sources.

An actual software-skills search discovered/fetched Toptal, but the model's two
sources were the stronger primary O*NET/MDN references. The earlier operation mode
correctly said search_and_fetch, but that alone could imply search discovered the
cited sources. The response now explicitly distinguishes additional discovered
pages from the predefined pages actually cited. Diagnostics expose
answer_source_origins and answer_uses_search_discovered_pages separately from the
complete discovery/fetch ledger. No stored Minder dataset is used by this route.
The frontend response shape and ownership remain compatible; F files are untouched.

17focusedwebtests PASS0.066s, including role-specific priority and the case where
an uncited discovered page must not relabel a predefined cited source. Native search
index limitations and genuine data gaps remain explicit; this does not create new
Malaysian role coverage or a current skills popularity ranking.
Full backend verification:226tests13.039s PASS,4PostgreSQL-only skips in the ordinary
interpreter. No model quota was consumed by these checks.
