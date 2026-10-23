"""Bounded official-employer evidence. No arbitrary URL fetch or inferred absence.

Discovery is separate from reviewed occupational mapping and live vacancy status.
Unmapped/inaccessible pages yield explicit requirements_unavailable.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.request import build_opener, HTTPRedirectHandler, Request
from urllib.parse import urlsplit
from urllib.error import URLError
from minder_ml.intelligence.service_contracts import validate
from .store import AppError, now

REGISTRY = {
    "intel": {"name": "Intel", "geography": "MY", "multinational": True,
              "url": "https://jobs.intel.com/"},
    "bosch": {"name": "Bosch Group", "geography": "MY", "multinational": True,
              "url": "https://www.bosch.com.my/careers/"},
}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None  # do not follow an unverified ATS/off-domain destination


def retrieve(url):
    with build_opener(NoRedirect()).open(Request(url, headers={
            "User-Agent": "MinderPrototype/1.0"}), timeout=10) as response:
        content = response.read(262145)
        if len(content) > 262144:
            raise ValueError("source_too_large")
        return content


class CompanyExplorer:
    def __init__(self, services, *, fetch=retrieve, postings=None):
        if postings is None:
            path = Path(__file__).resolve().parents[1] / "data/company-postings.v1.json"
            postings = json.loads(path.read_text())["postings"] if path.exists() else []
        self.services, self.fetch, self.postings = services, fetch, list(postings)

    def explore(self, profile, employer_id, role_id=None):
        employer_id = employer_id.lower()
        employer = REGISTRY.get(employer_id)
        if employer is None:
            return dict(status="requirements_unavailable", employer_name=employer_id,
                        searched_scope=["curated Malaysia MNC registry; employer not covered"],
                        checked_at=now(), explanation="Company-specific requirements unavailable: "
                        "this employer has not been added to the checked official-source registry.",
                        other_supported_roles=[], assessment=None)
        checked, evidence, access = now(), [], "not_retrieved"
        cached_postings = []
        market = self.services.market
        if employer_id == "bosch" and market is not None and hasattr(market, "snapshot"):
            # B's committed bounded collector verified the employer/ATS linkage.
            # Reuse summaries, never pretend cached descriptions are current vacancies.
            collected = market.snapshot["collected_at"]
            evidence = [dict(source_id="bosch-smartrecruiters-my", version=market.version,
                sha256=market.version, uri=employer["url"], geography="MY", available_at=collected,
                evidence_type="source-derived")]
            inverse = {native: canonical for canonical, native in market.aliases.get("role", {}).items()}
            for ad in market.snapshot["ads"]:
                for native in ad["role_ids"]:
                    if native in inverse:
                        cached_postings.append(dict(employer_id="bosch", geography="MY", role_id=inverse[native],
                            official_link_verified=True, title=ad["title"], location=ad["city"] + ", Malaysia",
                            required=[], preferred=[], published_at=ad["published_at"], retrieved_at=ad["ingested_at"],
                            vacancy_status="listed_at_collection_only; current_status_unknown", sources=[dict(
                                source_id=ad["source_id"] + ":" + ad["ad_id"], version=ad["ingested_at"],
                                sha256=ad["content_sha256"], uri=ad["url"], geography="MY",
                                available_at=ad["available_at"], evidence_type="source-derived")]))
            access = "B_committed_bounded_snapshot_at_" + collected + "; role_criteria_not_preserved_in_summary"
        try:
            raw = self.fetch(employer["url"]) if not evidence else None
            # A country page establishes checked scope only, never role requirements.
            if raw is not None:
                evidence = [dict(source_id="company:" + employer_id, version=checked,
                    sha256=hashlib.sha256(raw).hexdigest(), uri=employer["url"], geography="MY",
                    available_at=checked, evidence_type="source-derived")]
                access = "retrieved_country_page_no_verified_role_requirements"
        except (URLError, TimeoutError, OSError, ValueError):
            access = "official_page_unavailable"
        # Postings are server-side reviewed records, not user/LLM assertions. Only
        # mappings to A's catalogue can be assessed; same personal service, no new score.
        supported = []
        known_roles = {r["role_id"]: r for r in self.services.roles}
        seen_postings = set()
        for posting in self.postings + cached_postings:
            if (posting["employer_id"] != employer_id or posting["geography"] != "MY"
                    or not posting.get("official_link_verified") or posting["role_id"] not in known_roles):
                continue
            key = (posting["employer_id"], posting["role_id"], posting["title"])
            if key in seen_postings:
                continue
            seen_postings.add(key)
            for source in posting["sources"]:
                validate("Source", source)
                if urlsplit(source["uri"]).scheme != "https":
                    raise AppError("company_source_https_required")
            assessment = None
            if self.services.personal:
                context = self.services.career_context(profile,
                    expected_profile_version=profile["version"], selected_role_ids=[posting["role_id"]])
                from minder_ml.intelligence.service_contracts import public_recommendation
                assessment = public_recommendation(context["recommendation"])
            supported.append(dict(role_id=posting["role_id"], title=posting["title"],
                location=posting["location"], required=posting["required"], preferred=posting["preferred"],
                qualifications_requirement_level_unspecified=posting.get("qualifications_requirement_level_unspecified", []),
                requirement_interpretation=posting.get("requirement_interpretation", "Required/preferred criteria unavailable."),
                published_at=posting.get("published_at"), retrieved_at=posting["retrieved_at"],
                vacancy_status=posting.get("vacancy_status", "unknown"),
                sources=posting["sources"], generic_occupation_assessment=assessment,
                company_specific_assessment="unavailable: job requirements not mapped to assessment criteria"))
        selected = next((r for r in supported if r["role_id"] == role_id), None)
        result = dict(employer_id=employer_id, employer_name=employer["name"], location="Malaysia",
            role_id=role_id, status="requirements_unavailable", searched_scope=[employer["url"] + ": " + access],
            checked_at=checked, official_evidence=evidence, matching_requirements=[],
            unknown_requirements=["No verified role-specific requirements in checked sources"],
            preparation_suggestions=[], explanation="Company-specific requirements unavailable in the "
            "sources checked. This does not establish that the company has no matching role.")
        if selected and (selected["required"] or selected["preferred"] or selected["qualifications_requirement_level_unspecified"]):
            result.update(status="found", official_evidence=selected["sources"],
                          unknown_requirements=["User competence against company criteria unknown; no compatible personal rubric",
                              "Core qualification mandatory status not explicit; see requirement interpretation"],
                          explanation="A source-supported role description was found. Current vacancy "
                          "status and posting dates are shown separately; no hiring probability is inferred.")
        validate("CompanyRoleResult", result)
        return dict(result=result, selected_posting=selected, other_supported_roles=supported,
                    ranking_status="generic_occupation_context_same_service_no_company_specific_score",
                    main_recommendations_changed=False)
