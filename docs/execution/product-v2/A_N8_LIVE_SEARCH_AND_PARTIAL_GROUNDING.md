# A-N8 — actual general search, page fetch and partial grounding

Additional user acceptance distinguishes three operations. Prior A-N2 only fetched
predefined official URLs; it was not general search. This checkpoint adds actual
Mwmbl v2 general web discovery, separately fetches discovered public pages, and
labels any predefined official supplementation/fallback. Stored datasets are NOT
used in this web-answer route. Existing scorer, authentication, owned histories,
private profile handling and approval-only mutations are preserved.

## Actual supported provider, limits and privacy

https://developer.mwmbl.org/ documents anonymous API access without a key/signup/
payment: https://api.mwmbl.org/api/v2/search/?q=... . Primary docs list1000monthly
requests/IP and1request/second. App adds a shared private file lock,1.1second spacing,
4second queue bound,5second search HTTP timeout,900/month local cap,300second positive
search cache/30second failures. No account/payment/subscription or external key is
created. A inspected only search key names (no values) in its environment/private
files: no search credential exists. Tavily would require server-only TAVILY_API_KEY,
but this functioning anonymous provider avoids that dependency for the prototype.
Mwmbl has limited index coverage and is not claimed to find every Malaysian source.

Queries derive only from a fixed PUBLIC role/topic vocabulary, never CV/contact/
profile/history excerpts. Search snippets only discover URLs; they are not quoted
or passed as verified page content. Candidate pages are limited to Malaysian public
agencies and named professional publishers; HTTPS/public DNS/redirect/size/type
checks remain enforced. Fetched page text/title/publication metadata/hash and actual
retrieval time support quotes. Global learning articles are not Malaysian demand
measurements. Four concurrent page fetches max,4seconds per socket, recent cache/
failure circuit breaks; available pages survive unrelated failures.

Actual semantic routing covers differently worded Malaysian role/skill/labour/
industry questions and KL/Kuala Lumpur/other Malaysian-place aliases without a
complete Profile. Normal personal learning questions and explicit action commands
retain their prior routes. No tool instruction or action authority comes from pages.

## Answer policy public-web-answer-v1.1

Real Qwen explains retrieved passages using server-extracted exact quote IDs. URLs
and quotes are attached server-side; unsupported numeric/scoring/guarantee/URL
claims are rejected. Distinct passages from the same page may support separate
findings. Optional unsupported findings/introduction/limitations/advice are omitted
independently; valid findings and natural explanations remain. Exact rejected
visible claim and rule are retained in the owned public_web_evidence ledger.
Malformed native tool responses unavailable at this layer cannot be reconstructed;
that missing raw content is not invented. Advice is labelled and never a market
measurement/proficiency assertion or saved plan. A valid advice-only answer has no
factual completion claim. No task/profile mutation is executed by this route.

Source.title is an additive optional shared-contract display field backed by the
actual fetched page. Existing F source rendering already reads title, so no F file
is overwritten. Full citation origin/cache/publication/retrieval scope and handler/
search/fetch/validation/model diagnostics remain available. Source-method text is
server-owned and explicitly distinguishes discovered-page fetching from predefined
fetching; a search failure cannot silently become a claim that the dataset was searched.
Additional F source/status/roadmap-handoff UI contract: F_LIVE_SEARCH_RENDER_HANDOFF.md.

## Actual evidence at checkpoint

Three actual anonymous search/fetch component cases (NO model calls):
1. Malaysian labour market: search200/10candidates, no eligible discovered page;
   actual predefined TalentCorp MyCOL fetch at2026-10-24T15:57:06.437040Z.1923.115ms.
2. Malaysian data-analyst skills: two searches200; actual discovered Dataquest
   https://www.dataquest.io/blog/data-analyst-skills/ fetched at15:57:09.936654Z and
   https://roadmap.sh/data-analyst at15:57:08.642782Z, plus predefined MyNSR FAQ.
  3499.471ms. Their global skills context is explicitly not Malaysian hiring demand.
3. Malaysian cybersecurity: two searches200, rawsec redirect rejected by host scope;
   relevant available MyCOL context retained from the labelled recent cache.2251.688ms.
These demonstrate discovery/fetch and real limitations, not complete browser/model
answers. Exact public URL/time/query/failure metadata is in the accompanying JSON;
raw passages and original-before-relevance-refinement reports remain ignored.

214backend regressions PASS14.948s;129actual native PostgreSQL16.2 integrated checks
PASS13.414s plus real server stop/start/fresh-process refetch.15deploy regressions
also pass. Provider/retrieval tests are declared fixtures; live component evidence
above is actual HTTPS and separate. The optional-claim regression retains a valid
shortage explanation, omits 'There are 999999 jobs available for everyone.', records unsupported_web_quantity and leaves profile/plans
unchanged. No source-backed URL or quote is invented to obtain a pass.

Next gate is actual9111 browser request→handler→search→fetched passages→real Qwen→
validation→displayed answer, several questions without a Profile, then the complete
fresh-user plan/progress/approval journey. Earlier F0c743623 starter UI is integrated;
A's first post-integration plan attempt hit a genuine daily quota and remains
recorded, not replaced with a passing claim. Replit GitHub connection/prodDB/bucket/
managed identities remain E access dependencies. No deployment/main merge.
