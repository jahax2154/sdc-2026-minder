"""Application-facing service composition. No new numeric policy or ranking."""
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
        return {"integration_mode": self.mode, "recommendation": result,
                "limitations": [] if result else ["Personal service not connected; N01 remains pending."],
                "sources": self.sources}

    def public_context(self, context):
        return dict(integration_mode=context["integration_mode"],
                    recommendation=public_recommendation(context["recommendation"])
                    if context["recommendation"] else None,
                    limitations=context["limitations"])
