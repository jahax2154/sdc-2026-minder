# A-N8 — live-search response rendering and remaining cross-chat UI

Additional current user acceptance requires general page discovery, not a stored
dataset or predefined URL list labelled as search. A is implementing documented
anonymous Mwmbl v2 search (https://api.mwmbl.org/api/v2/search/), no new secret/account/
subscription. Limited search index is explicit. Search results discover candidates;
only separately fetched HTML/PDF text can support quoted facts. Fixed public-topic
query construction excludes CV/contact/profile/history. Partial fetches are retained.

Standard conversation response fields remain; no auth/schema/authority relaxation.
F's starter checkpoint0c743623 is already integrated in A. Necessary small rendering
slice for F (exclusive frontend ownership):

- response.answer remains a natural model explanation. statements[].text is the
  exact server-owned supporting quote, citation contains actual url/title/published_at
  nullable/retrieved_at/geography/scope/sha256/cache_status/origin/fetch_elapsed_ms.
  Render actual citation title/link and publication unknown vs retrieval time. Do
  not use internal source_id as a display title when citation.title is available.
- diagnostics.retrieval.mode distinguishes search_and_fetch from
  predefined_fetch_after_search; discovery[] gives provider, public query,
  searched_at, status/cache_status, results[] URLs/titles and elapsed_ms.
  fetched_pages[] gives actual page fetch URL/title/time/cache/origin. Display a
  concise source-discovery status and missing/failed pages. No search snippet is
  rendered as verified page evidence; stored_dataset_used is false in this route.
- Available sources survive another fetch timeout. Upcoming partial-validation
  metadata will identify omitted optional claims; keep useful supported explanation
  visible. Clearly labelled model advice is not a market measurement or skill score.
- Existing Mindbot Proposed changes panel can approve/reject action proposals via
  the canonical executor. For planning handoffs, GET product/minder-handoffs has
  kind=roadmap, concrete draft preview and version, with handoff-decision for explicit
  approval/rejection. Use A_MINDBOT_HANDOFF_V1.md. Never auto-navigate from Minder,
  apply on receipt, or treat a missing UI control as completed integration.

A will run actual9111 browser traces with several differently worded market/role/
skill questions and no complete profile, then the fresh-user plan/progress/approval
journey. F should provide an exact bounded committed handoff for the rendering/UI
slice; A will integrate that history, never overwrite F's worktree or frontend files.
