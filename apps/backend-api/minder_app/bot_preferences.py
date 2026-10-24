"""Owner-scoped display identity, separate from conversation and automation authority."""
from functools import lru_cache
import json
from pathlib import Path
from jsonschema import Draft202012Validator
from .product_state_schemas import schemas
from .store import AppError

CONTRACT_VERSION = "bot-preferences-v1"
OPERATIONS = (("GET","/api/product/bot-preferences"),("PUT","/api/product/bot-preferences"))


def validate(kind, value):
    Draft202012Validator({"$defs":schemas(),"$ref":"#/$defs/"+kind}).validate(value)


@lru_cache(maxsize=1)
def defaults():
    manifest = json.loads((Path(__file__).resolve().parents[3] /
        "docs/execution/product-v2/BOT_AVATARS.v1.json").read_text())
    result = dict(display_name=manifest["default_display_name"],avatar_id=manifest["default_avatar_id"],version=None)
    validate("BotPreferences", result)
    return result


def result(preferences, configured):
    value = dict(contract_version=CONTRACT_VERSION,configured=configured,preferences=dict(preferences))
    validate("BotPreferencesResult",value)
    return value


def get_preferences(store, owner):
    try:
        return result(store.get(owner,"bot_preferences",owner),True)
    except AppError as error:
        if error.status!=404:
            raise
        return result(defaults(),False)


def save_preferences(store, owner, body):
    # Normalize only display text; no field can select owner, model, role or schedule.
    if isinstance(body,dict):
        body=dict(body)
        if isinstance(body.get("display_name"),str):
            body["display_name"]=body["display_name"].strip()
    validate("BotPreferencesWrite",body)
    with store.transaction() as db:
        try:
            previous=store.get(owner,"bot_preferences",owner,db=db)
        except AppError as error:
            if error.status!=404:
                raise
            previous=None
        if (previous["version"] if previous else None)!=body["expected_version"]:
            raise AppError("stale_state_version",409)
        value=dict(display_name=body["display_name"],avatar_id=body["avatar_id"])
        if previous and all(previous[key]==value[key] for key in value):
            return result(previous,True)
        return result(store.put(owner,"bot_preferences",owner,value,body["expected_version"],db=db),True)


def dispatch(app,owner,method,path,body):
    if (method,path) not in OPERATIONS:
        raise AppError("product_capability_unavailable",404)
    if method=="GET":
        Draft202012Validator(dict(type="object",additionalProperties=False)).validate(body)
        return get_preferences(app.store,owner)
    return save_preferences(app.store,owner,body)
