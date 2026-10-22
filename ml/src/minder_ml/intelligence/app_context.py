"""Application-facing service composition. No new numeric policy or ranking."""
from datetime import datetime, timezone
from urllib.parse import urlsplit
from .service_contracts import public_recommendation, validate


class CareerServices:
    def __init__(self, personal=None, market=None, roles=(), sources=(), *, mode="unavailable"):
        self.personal, self.market = personal, market
        self.roles, self.sources, self.mode = list(roles), list(sources), mode

    def career_context(self, profile, *, expected_profile_version):
        validate("Profile", profile)
        if profile["version"] != expected_profile_version:
            raise ValueError("stale profile context")
        result = None
        if self.personal is not None:
            result = self.personal.assess(profile, self.roles, scorer_kind="baseline",
                policy_version="N01-pending", market_period_policy_key="personal_only_pending_market_policy")
            validate("Recommendation", result)
            if (result["public"]["profile_id"] != profile["profile_id"] or
                    result["public"]["profile_version"] != profile["version"]):
                raise ValueError("service profile identity/version mismatch")
        market = []
        if self.market is not None:
            stamp = datetime.now(timezone.utc).isoformat()
            entities = [("role", r["role_id"]) for r in self.roles]
            entities += [("skill", e["subject_id"]) for e in profile["evidence"]]
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
        return {"integration_mode": self.mode, "recommendation": result, "market": market,
                "limitations": [] if result else ["Personal service not connected; N01 remains pending."],
                "sources": self.sources}

    def public_context(self, context):
        return dict(integration_mode=context["integration_mode"],
                    recommendation=public_recommendation(context["recommendation"])
                    if context["recommendation"] else None,
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
    add("Numerical role-fit policy N01 remains pending; no new scoring weights have been selected.")
    if context["integration_mode"] != "live":
        add("Integration mode: " + context["integration_mode"] + "; these results are not live ML acceptance evidence.")
    result = context["recommendation"]
    if result:
        public = public_recommendation(result)
        for option in public["options"]:
            add(option["role_id"] + ": " + option["explanation"], option["source_ids"],
                kind="personal_assessment", score_status=option["score_status"],
                personal_score=option["personal_score"], unknowns=option["unknowns"])
    else:
        add("Personal assessment unavailable: the personal service is not connected.")
    for item in context.get("market", []):
        validate("MarketResult", item)
        prefix = ("Current observation" if item["kind"] == "current" else "Next-quarter forecast")
        period = item["observation_period"] if item["kind"] == "current" else item["target_period"]
        label = prefix + " for " + item["entity_type"] + " " + item["entity_id"]
        if item["status"] == "unavailable" or any(x not in sources for x in item["source_ids"]):
            add(label + " unavailable: " + ("; ".join(item["missing_reasons"]) or
                "supporting source registry unavailable"), kind=item["kind"], status="unavailable",
                period=period, issued_at=item["issued_at"])
        else:
            add(label + ": " + str(item["value"]) + " " + item["unit"] + ". "
                "This describes the declared source population, not all Malaysian jobs.", item["source_ids"],
                kind=item["kind"], status="available", period=period,
                published_at=item["published_at"], available_at=item["available_at"],
                issued_at=item["issued_at"], source_universe_id=item["source_universe_id"],
                model_version=item["model_version"], uncertainty=item["uncertainty"])
    if not context.get("market"):
        add("Current market evidence unavailable: market service not connected.", kind="current", status="unavailable")
        add("Next-quarter role and skill forecasts unavailable: market service not connected.",
            kind="forecast", status="unavailable")
    return statements
