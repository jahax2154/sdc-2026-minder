"""Application composition: backend ranks; explanations preserve coverage scopes."""
from datetime import datetime, timezone
from urllib.parse import urlsplit
from .service_contracts import public_recommendation, validate
from .role_fit import POLICY_ID, MARKET_POLICY

PRESENTATION_VERSION = 'career-explanations-v1'


class CareerServices:
    def __init__(self, personal=None, market=None, roles=(), sources=(), *, mode="unavailable", skill_entity_ids=()):
        self.personal, self.market = personal, market
        self.roles, self.sources, self.mode = list(roles), list(sources), mode
        self.skill_entity_ids = set(skill_entity_ids)

    def career_context(self, profile, *, expected_profile_version, selected_role_ids=None, selected_skill_ids=None):
        validate("Profile", profile)
        if profile["version"] != expected_profile_version:
            raise ValueError("stale profile context")
        if selected_role_ids is not None and (not isinstance(selected_role_ids, list) or
                len(selected_role_ids) > 3 or len(set(selected_role_ids)) != len(selected_role_ids) or
                not set(selected_role_ids).issubset({r["role_id"] for r in self.roles})):
            raise ValueError("explicit selected view requires at most three known roles")
        if selected_skill_ids is not None and (not isinstance(selected_skill_ids, list) or
                len(selected_skill_ids) > 3 or not set(selected_skill_ids).issubset(self.skill_entity_ids)):
            raise ValueError("skill market query requires typed registered skill IDs")
        view = self.roles if selected_role_ids is None else [r for r in self.roles if r["role_id"] in selected_role_ids]
        result = None
        if self.personal is not None:
            result = self.personal.assess(profile, view, scorer_kind="baseline",
                policy_version=POLICY_ID, market_period_policy_key=MARKET_POLICY)
            validate("Recommendation", result)
            if (result["public"]["profile_id"] != profile["profile_id"] or
                    result["public"]["profile_version"] != profile["version"]):
                raise ValueError("service profile identity/version mismatch")
        market = []
        if self.market is not None:
            stamp = datetime.now(timezone.utc).isoformat()
            entities = [("role", r["role_id"]) for r in view] if selected_role_ids is not None else []
            entities += [("skill", sid) for sid in selected_skill_ids or []]
            for entity_type, entity_id in list(dict.fromkeys(entities))[:10]:
                for kind in ("current", "forecast"):
                    item = (self.market.current(entity_type, entity_id, as_of=stamp)
                            if kind == "current" else
                            self.market.forecast(entity_type, entity_id, issued_at=stamp))
                    validate("MarketResult", item)
                    if (item["kind"], item["entity_type"], item["entity_id"]) != (kind, entity_type, entity_id):
                        raise ValueError("market identity mismatch")
                    market.append(item)
        elif result:
            market = result["internal"]["current_market"] + result["internal"]["forecast_market"]
        labels = {'role': {r['role_id']: r['label'] for r in self.roles if r.get('label')},
                  'skill': {key: value['label'] for key, value in
                      getattr(self.personal, 'ref', {}).get('skill_rubrics', {}).items() if value.get('label')}}
        return {"integration_mode": self.mode, "recommendation": result, "market": market, 'entity_labels': labels,
                "selected_role_ids": selected_role_ids, "selected_skill_ids": selected_skill_ids,
                "limitations": [] if result else ["Personal service not connected; assessment unavailable."],
                "sources": self.sources}

    def public_context(self, context):
        return dict(integration_mode=context["integration_mode"], presentation_version=PRESENTATION_VERSION,
                    recommendation=public_recommendation(context["recommendation"])
                    if context["recommendation"] else None,
                    assessment_details=[a for a in context['recommendation']['internal']['personal_assessments']
                        if a['role_id'] in context.get('selected_role_ids', [])]
                        if context['recommendation'] and context.get('selected_role_ids') else [],
                    limitations=context["limitations"],
                    statements=grounded_statements(context))


def grounded_statements(context):
    """Allowlisted renderable facts. Raw internal indices never enter LLM/public DTOs."""
    sources = {}
    for source in context["sources"]:
        validate("Source", source)
        if urlsplit(source["uri"]).scheme in ("http", "https"):
            sources[source["source_id"]] = source
    statements = []
    def add(text, ids=(), **metadata):
        statements.append(dict(id="fact-" + str(len(statements)), text=text,
            sources=[sources[x] for x in ids if x in sources], **metadata))
    add("Recommendations use your described skill activities and separate optional interests. "
        "Comparable current Malaysian observations also influence the order; future forecasts are separate. "
        "This is a provisional assessment, not verified competence or a proven career prediction.")
    if context["integration_mode"] != "live":
        add("These results use recorded source observations with their original dates and scope. "
            "Predictive accuracy has not been established." if context['integration_mode'] == 'local_source_services' else
            "Some assessment services are unavailable. Only the evidence returned below can be considered.")
    result = context["recommendation"]
    if result:
        public = public_recommendation(result)
        selected = context.get("selected_role_ids")
        if selected is None:
            c = public.get('coverage', {})
            add(f"{c.get('assessed', 0)} of {len(public['candidate_ids'])} candidates have a supported personal assessment; "
                f"{c.get('current_comparable_ranked', 0)} have comparable current Malaysian evidence and "
                f"{c.get('personal_only_ranked', 0)} have personal-only ranks. "
                "Ranks compare roles within each coverage group only; personal-only results are incomplete market comparison.")
        explain_ids = set(selected or [])
        if selected is None:
            for group in public.get('ranking_groups', []):
                explain_ids.update(group['role_ids'][:3])
                add(group.get('label', 'Career comparison group') + ': ' + group['limitation'])
            for question in public.get('targeted_questions', []):
                add(question)
        for option in [o for o in public['options'] if o['role_id'] in explain_ids]:
            add(context.get('entity_labels', {}).get('role', {}).get(option['role_id'], 'This career')
                + ": " + option["explanation"], option["source_ids"],
                kind="personal_assessment", score_status=option["score_status"],
                personal_score=option["personal_score"], unknowns=option["unknowns"])
    else:
        add("A personal assessment is not available. You can still explore careers and add supporting skill evidence.")
    for item in context.get("market", []):
        validate("MarketResult", item)
        prefix = ("Current observation" if item["kind"] == "current" else "Next-quarter forecast")
        period = item["observation_period"] if item["kind"] == "current" else item["target_period"]
        name = context.get('entity_labels', {}).get(item['entity_type'], {}).get(item['entity_id'])
        label = prefix + (" for " + name if name else " for this " + item['entity_type'])
        if item["status"] == "unavailable" or any(x not in sources for x in item["source_ids"]):
            add(label + " unavailable. " + (item.get('explanation') if item['status'] == 'unavailable'
                and item.get('explanation') else 'A supporting source could not be verified.'), kind=item["kind"], status="unavailable",
                period=period, issued_at=item["issued_at"])
        else:
            add(label + ": " + str(item["value"]) + " " + item["unit"] + ". "
                "This describes the declared source population, not all Malaysian jobs.", item["source_ids"],
                kind=item["kind"], status="available", period=period,
                published_at=item["published_at"], available_at=item["available_at"],
                issued_at=item["issued_at"], source_universe_id=item["source_universe_id"],
                model_version=item["model_version"], uncertainty=item["uncertainty"])
    if not context.get("market"):
        add("Choose a career to review its available current market observations and their scope.", kind="current", status="unavailable")
        add("No next-quarter forecast is available in this view. Current observations do not establish a future trend.",
            kind="forecast", status="unavailable")
    return statements
