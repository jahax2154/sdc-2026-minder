"""Approved primary-source events; attention is auxiliary, never an ad target."""
from collections import defaultdict
from datetime import datetime
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

from .data_pipeline import MARKET_DATA, MARKET_ARTIFACTS, fetch_public, plain_text, encoded, utc_now
from .market_service import timestamp

VERSION = 'credible-events-v1'


def normalize_events(documents, registry, *, as_of):
    approved = {r['source_id']: r for r in registry['sources']}
    accepted, rejected = {}, []
    for doc in documents:
        try:
            source = approved[doc['source_id']]
            if urlsplit(doc['url']).hostname != source['host']:
                raise ValueError('source_host_mismatch')
            if doc['claim_type'] not in source['claim_types']:
                raise ValueError('unsupported_claim_type')
            if not doc.get('full_document_sha256') or doc.get('evidence_kind') != 'underlying_document':
                raise ValueError('headline_or_snippet_is_not_evidence')
            if doc['geography'] not in ('MY', 'GLOBAL'):
                raise ValueError('invalid_geography')
            if doc['direction'] not in ('positive', 'negative', 'ambiguous'):
                raise ValueError('invalid_direction')
            if timestamp(doc['available_at']) > timestamp(as_of) or timestamp(doc['published_at']) > timestamp(as_of):
                raise ValueError('not_yet_available')
            if doc['claim_type'] in ('announcement', 'investment') and doc['outcome_verified']:
                raise ValueError('announcement_is_not_verified_outcome')
            # One underlying event can have multiple reporting URLs.
            key = (doc['event_key'], doc['geography'])
            if key not in accepted:
                accepted[key] = dict(doc, document_urls=[doc['url']], source_ids=[doc['source_id']])
            else:
                event = accepted[key]
                if (event['claim_type'], event['direction'], event['outcome_verified']) != (
                        doc['claim_type'], doc['direction'], doc['outcome_verified']):
                    raise ValueError('conflicting_event_claims_require_review')
                event['document_urls'] = sorted(set(event['document_urls'] + [doc['url']]))
                event['source_ids'] = sorted(set(event['source_ids'] + [doc['source_id']]))
        except (KeyError, ValueError, TypeError) as exc:
            rejected.append({'url': doc.get('url'), 'reason': str(exc)})
    return {'version': VERSION, 'events': list(accepted.values()), 'rejected': rejected}


def attention(events, *, coverage, topic, start, end, as_of, geography='MY'):
    """Unique events per completely collected document, comparable source cohort.

    Coverage entries are source-level denominators for exactly the same window;
    missing collection is unknown. Compare rates only with equal cohort keys.
    """
    if not coverage or any(not c['complete'] or c['documents'] <= 0 or
                           c['start'] != start or c['end'] != end or
                           timestamp(c['available_at']) > timestamp(as_of) for c in coverage):
        return {'value': None, 'reason': 'incomplete_or_missing_collection_coverage', 'cohort': None}
    ids = {c['source_id'] for c in coverage}
    keys = {e['event_key'] for e in events if e['geography'] == geography and topic in e['topics']
            and set(e['source_ids']) & ids and start <= e['published_at'][:10] <= end
            and timestamp(e['available_at']) <= timestamp(as_of)}
    return {'value': len(keys) / sum(c['documents'] for c in coverage),
            'reason': None, 'cohort': sorted(ids), 'event_count': len(keys),
            'document_count': sum(c['documents'] for c in coverage)}


def collect_events(plan_path=MARKET_DATA / 'news-plan.v1.json', output=MARKET_DATA / 'events.v1.json'):
    plan = json.loads(Path(plan_path).read_text())
    documents, attempts = [], []
    for entry in plan['documents']:
        try:
            body, record = fetch_public(entry['url'], MARKET_ARTIFACTS / 'news' / (entry['event_key'] + '.html'))
            attempts.append(record)
            text = plain_text(body.decode('utf-8', errors='replace')).casefold()
            if not all(anchor.casefold() in text for anchor in entry['required_anchors']):
                raise ValueError('underlying_document_anchor_mismatch')
            doc = {k: v for k, v in entry.items() if k != 'required_anchors'}
            doc.update(full_document_sha256=record['sha256'], available_at=record['retrieved_at'],
                       evidence_kind='underlying_document')
            documents.append(doc)
        except (OSError, ValueError) as exc:
            attempts.append({'url': entry['url'], 'status': 'unavailable', 'reason': type(exc).__name__})
    result = normalize_events(documents, json.loads((MARKET_DATA / 'sources.v1.json').read_text()), as_of=utc_now())
    result.update(synthetic=False, collection_attempts=attempts, coverage=[],
                  attention_status='unavailable_without_complete_feed_denominators',
                  historical_news_evaluation='not_run_no_archived_as_of_corpus')
    Path(output).write_text(encoded(result))
    return result


if __name__ == '__main__':
    print(encoded(collect_events()), end='')
