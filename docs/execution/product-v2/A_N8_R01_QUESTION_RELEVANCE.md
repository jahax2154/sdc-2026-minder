# A-N8-R01 — detail evidence for the three UI relevance regressions

This refines public-page-discovery-v1 to v1.1 and public-web-answer-v1.1 to v1.2.
It preserves the assessed/starter policies, provider, authentication, owner boundary
and explicit cross-chat approval. No frontend files are edited.

The actual Mwmbl result probes for Malaysia/software/job-market queries returned
few relevant eligible pages. Earlier selection then put the predefined MyCOL/MyNSR
introduction first. That did not answer the question. Search now uses separate
market vs foundational-software queries, and question-bearing detail passages rank
before registry introductions. Anonymous general discovery is still Mwmbl; the
following verified fallback details are predefined references, never relabelled as
search-discovered pages. Runtime records each origin, request, time and failure.

- General current market: live download of DOSM lfs_month.csv, last three observed
  months rendered with the units documented at data.gov.my/data-catalogue/lfs_month.
  Actual native download HTTP200,10868bytes; latest observed August2026, not today's
  vacancies. Month and unknown publication date remain separate. This is fetching
  an external official dataset at request time, not reading Minder's stored data.
  The DOSM Q2 report remains an additional bounded detail fetch; its timeout cannot
  discard the monthly evidence. Population-basis caveat is retained.
- Software job market: actual Randstad emerging-technology guide detail, source
  JSON-LD published2026-09-01. It describes recruitment observations, software
  specialisms and employer needs, not a national vacancy census or proven growth
  rate. The article publication date is parsed from source metadata, never search
  snippets or the retrieval timestamp.
- Software skills: actual O*NET Software Developers tasks and MDN curriculum
  details. US occupational requirements and global foundational web skills do not
  establish current Malaysian popularity or personal competence. Search-discovered
  Toptal detail was fetched successfully, but its2017publication is not current
  market evidence and does not displace the primary technical references.

Exact regression questions:
1. What are the market trends right now?
2. How is the software engineering job market now?
3. What's the most relevant skills now to become a software engineer?

Model instructions now lead with the useful direct explanation and allow labelled
practice advice, keeping quoted passages/URLs server-owned. An optional unsupported
claim is omitted independently. An undated description cannot establish an explicit
current trend; the rejection ledger records the exact claim and rule. Publication
metadata scripts are parsed only as JSON data and excluded from page text.

Pre-check evidence: actual source/passage probes are private files under
/private/tmp/minder-a-relevance-regressions.json and minder-a-current-monthly-probe.json.
Three report-page timeouts were observed honestly; an official monthly-data fetch
completed in242.702ms. These probes make zero model calls. Actual 9111 browser/model
results are a subsequent checkpoint and are not inferred from source availability.

Verification:219backend tests ran in12.857s, PASS with4PostgreSQL-specific tests
skipped in the ordinary runtime interpreter. Native PostgreSQL acceptance is
separate; earlier129native checks remain documented, not relabelled as this run.
