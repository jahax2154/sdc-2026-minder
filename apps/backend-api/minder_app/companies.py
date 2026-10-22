"""Bounded official-employer evidence. No arbitrary URL fetch or inferred absence.

Discovery is separate from reviewed occupational mapping and live vacancy status.
Unmapped/inaccessible pages yield explicit requirements_unavailable.
"""
from datetime import datetime, timezone
import hashlib
import json
from urllib.request import build_opener, HTTPRedirectHandler, Request
from urllib.parse import urlsplit
from urllib.error import URLError
from minder_ml.intelligence.service_contracts import validate
from .store import AppError, now

REGISTRY = {
    "intel": {"name": "Intel", "geography": "MY", "multinational": True,
              "url": "https://www.intel.com/content/www/us/en/jobs/locations/malaysia.html"},
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
    def __init__(self, services, *, fetch=retrieve, postings=()):
        self.services, self.fetch, self.postings = services, fetch, list(postings)

    def explore(self, profile, employer_id, role_id=None):
        employer = REGISTRY.get(employer_id.lower())
        if employer is None:
            return dict(status="requirements_unavailable", employer_name=employer_id,
                        searched_scope=["curated Malaysia MNC registry; employer not covered"],
                        checked_at=now(), explanation="Company-specific requirements unavailable: "
                        "this employer has not been added to the checked official-source registry.",
                        other_supported_roles=[], assessment=None)
        checked, evidence, access = now(), [], "not_retrieved"
        try:
            raw = self.fetch(employer["url"])
            # A country page establishes checked scope only, never role requirements.
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
        for posting in self.postings:
            if (posting["employer_id"] != employer_id or posting["geography"] != "MY"
                    or not posting.get("official_link_verified") or posting["role_id"] not in known_roles):
                continue
            for source in posting["sources"]:
                validate("Source", source)
                if urlsplit(source["uri"]).scheme != "https":
                    raise AppError("company_source_https_required")
            assessment = None
            if self.services.personal:
                result = self.services.personal.assess(profile, [known_roles[posting["role_id"]]],
                    scorer_kind="baseline", policy_version="N01-pending",
                    market_period_policy_key="personal_only_pending_market_policy")
                from minder_ml.intelligence.service_contracts import public_recommendation
                assessment = public_recommendation(result)
            supported.append(dict(role_id=posting["role_id"], title=posting["title"],
                location=posting["location"], required=posting["required"], preferred=posting["preferred"],
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
        if selected:
            result.update(status="found", official_evidence=selected["sources"],
                          unknown_requirements=["Company criteria assessment unavailable"],
                          explanation="A source-supported role description was found. Current vacancy "
                          "status and posting dates are shown separately; no hiring probability is inferred.")
        validate("CompanyRoleResult", result)
        return dict(result=result, selected_posting=selected, other_supported_roles=supported,
                    ranking_status="pending_N01_same_personal_service_no_company_score",
                    main_recommendations_changed=False)
