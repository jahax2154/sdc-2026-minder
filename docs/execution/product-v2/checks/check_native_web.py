"""Actual no-profile HTTP-page/Qwen application check. No secret output."""
import json
from pathlib import Path
import time
from urllib.error import HTTPError
from minder_ml.intelligence.product_runtime import build


def main():
    root = Path('ml/artifacts/session-a/product/morning')
    app, _ = build('A', database=root / 'next-web-native-v2.sqlite3')
    observed, original = [], app.provider.opener
    names = ('retry-after', 'x-ratelimit-limit-requests', 'x-ratelimit-limit-tokens',
        'x-ratelimit-remaining-requests', 'x-ratelimit-remaining-tokens',
        'x-ratelimit-reset-requests', 'x-ratelimit-reset-tokens')
    def capture(request, timeout):
        start = time.perf_counter()
        try:
            response = original(request, timeout=timeout)
            observed.append(dict(status=response.status, elapsed_ms=round((time.perf_counter()-start)*1000,3),
                headers={n:response.headers[n] for n in names if response.headers.get(n)}))
            return response
        except HTTPError as error:
            observed.append(dict(status=error.code,headers={n:error.headers[n] for n in names if error.headers.get(n)}))
            raise
    app.provider.opener = capture
    session = app.store.session()
    conversation = app.dispatch('POST','/api/product/conversations',dict(
        title='Actual public-source question without Profile', idempotency_key='web-native-v2-new'),session['token'])
    started = time.perf_counter()
    result = app.dispatch('POST','/api/product/conversation-turn',dict(
        conversation_id=conversation['conversation']['conversation_id'],
        message='Using current Malaysian sources, what does an occupation being on MyCOL tell me about demand and what does it not show?',
        expected_profile_version=None,idempotency_key='web-native-v2-question'),session['token'])
    response = result['response']
    report = dict(elapsed_ms=round((time.perf_counter()-started)*1000,3), provider=response['provider'],
        response_mode=response['response_mode'],answer=response['answer'],
        source_citations=[s['citation'] for s in response['statements']],
        retrieval=response['diagnostics']['retrieval'], actual_quota_headers=observed,
        profiles=len(app.store.list(session['profile_id'],'profile')), plans=len(app.store.list(session['profile_id'],'plan')))
    (root/'next-web-native-v2-result.json').write_text(json.dumps(result,indent=2)+'\n')
    (root/'next-web-native-v2-summary.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    assert response['provider']['status'] == 'available'
    assert response['statements'] and report['profiles'] == report['plans'] == 0


if __name__ == '__main__':
    main()
