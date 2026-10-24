"""Bind committed A/B services in the current worktree, with no fixture fallback."""
import os
from pathlib import Path
from minder_ml.intelligence.app_context import CareerServices
from .config import configured_provider
from .store import Store

ROOT = Path(__file__).resolve().parents[3]


def application():
    from .api import Application
    from minder_ml.intelligence.catalogue_service import OccupationalCatalogue
    from minder_ml.intelligence.personal_service import PersonalMatchingService
    from minder_ml.intelligence.market_service import MarketEvidenceService
    catalogue = OccupationalCatalogue()  # verifies real pinned local sources
    roles = catalogue.roles()
    aliases = {r["role_id"]: catalogue.reference(r["role_id"])["occupation"]["O*NET-SOC Code"] for r in roles}
    market = MarketEvidenceService(aliases={"role": aliases})
    sources = list(catalogue.coverage["sources"]) + [dict(source_id="bosch-smartrecruiters-my",
        version="derived-measurement-snapshot:" + market.version, sha256=market.version,
        uri="https://www.bosch.com.my/careers/", geography="MY",
        available_at=market.snapshot.get("available_at", market.snapshot["collected_at"]), evidence_type="source-derived")]
    services = CareerServices(PersonalMatchingService(market), market, roles, sources,
        mode="local_source_services", skill_entity_ids=[x["source_skill_id"] for x in market.mapping["skills"]])
    path = Path(os.environ.get("MINDER_DB_PATH", ROOT / "ml/artifacts/session-c/runtime/dev.sqlite3")).resolve()
    if not path.is_relative_to((ROOT / "ml/artifacts/session-c").resolve()):
        raise ValueError("C runtime database must stay under reserved Session C artifacts")
    app = Application(Store(path), services, configured_provider())
    app.catalogue_coverage = catalogue.coverage
    return app
