"""Actual anonymous discovery + fetched pages only. No model or private query."""
import json
from pathlib import Path
import time
from minder_app.web_search import SearchRetrieval

root=Path('ml/artifacts/session-a/product/morning')
questions=('What is happening in the Malaysian labour market now?',
    'Which skills should a data analyst learn for Malaysian jobs?',
    'Are cybersecurity skills sought after in Malaysia?')
engine=SearchRetrieval();reports=[]
for index,question in enumerate(questions):
    started=time.perf_counter();result=engine.retrieve(question)
    reports.append(dict(question=question,elapsed_ms=round((time.perf_counter()-started)*1000,3),
        mode=result['mode'],status=result['status'],discovery=result['discovery'],
        fetched_pages=result['fetched_pages'],failures=result['failures'],
        passages=[dict(url=s['url'],title=s['title'],retrieved_at=s['retrieved_at'],origin=s['origin'],
            geography=s['geography'],passage=s['passage']) for s in result['sources']]))
    (root/'live-search-component.json').write_text(json.dumps(reports,indent=2)+'\n')
    print(json.dumps(dict(question=index+1,elapsed_ms=reports[-1]['elapsed_ms'],mode=result['mode'],
        search=[dict(query=x['query'],status=x['status'],count=len(x['results'])) for x in result['discovery']],
        fetched=[dict(url=s['url'],retrieved_at=s['retrieved_at'],origin=s['origin']) for s in result['sources']],failures=result['failures'])))
