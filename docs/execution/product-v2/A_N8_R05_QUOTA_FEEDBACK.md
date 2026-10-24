# A-N8-R05 — distinguish provider quota from evidence rejection

When actual live sources are available but Groq returns a usage-limit/queue error,
the displayed answer now says the language service reached its usage limit and
shows its actual retry window when supplied. It retains links and saved work,
without claiming that the evidence failed validation. Native HTTP/model failures
and actual validation failures have separate truthful explanations. No canned
market finding, invisible retry, billing change or approval bypass is introduced.

15focusedwebchecks PASS0.055s, including a locally held quota failure making no
outbound call and retaining actual source references. The integrated native
PostgreSQL run passed135tests11.904s and actual stop/start/fresh-process refetch;
provider/retrieval fixtures are explicit and no hosted acceptance is inferred.
E's pinned reviewed source remains27bc760; this later feedback-only refinement is
available as a normal descendant, not silently added to that pinned deployment.
