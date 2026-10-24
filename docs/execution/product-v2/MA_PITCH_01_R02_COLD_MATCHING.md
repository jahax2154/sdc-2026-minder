# MA-PITCH-01-R02 — fresh-process first matching request

Independent follow-up to MA-PITCH-01-R01, not a new ranking policy or cache expansion.
Measured committed c7d6ebfb3ad60e13f07b03bb20325be28926bfc1 (includes A-UX0 contracts
and F's committed UX0 inventory). Each case runs in its own new Python process,
disposable A-only database and newly constructed actual source services. The first
global matching request includes WSGI request/response serialization/parsing. There
is no earlier assessment or provider call in that process. No source data changed.

| Case | Imports/application setup | First global WSGI request | Actual assessed/current-comparable coverage |
| --- | ---: | ---: | --- |
| Sparse synthetic Profile |1130.644ms |6341.541ms |0/0 of910eligible |
| Adequate anchored synthetic Profile |1082.099ms |6637.470ms |910/5 of910eligible |

The adequate case retains2employer+3published-category comparable ranks,
900personal-only ranks,7related shortage context/0exact whole-role shortage,
7published-supported and907sector-context roles. Counts overlap. The sparse
case retains source context but invents no personal score. Current_available4
is the legacy employer-availability count, not the5comparable role ranks.

Both measured first application requests fit the existing frontend12s read bound
on this Mac. This does not certify browser/network/hosted latency or every workload.
OS filesystem caches are uncontrolled; these are not reboot/disk-cold measurements.
Startup includes the measured imports/factory after command argument parsing, not
the complete interpreter-launch time. Actual A browser first matching at the earlier
functional candidate was6572ms; that separate evidence is retained in MA2.

```sh
source .env.local
PYTHONPATH=ml/src:apps/backend-api "$MINDER_PYTHON" docs/execution/product-v2/checks/check_cold_matching.py --case sparse
PYTHONPATH=ml/src:apps/backend-api "$MINDER_PYTHON" docs/execution/product-v2/checks/check_cold_matching.py --case adequate
```

Run sequentially in separate processes, not competing performance processes. Logs/
full source coverage records remain ignored under A morning/cold-matching-*.json;
this report is sanitized aggregate evidence. No full-suite repetition, model call,
new dependency, database migration, shared environment change or F edit was needed.
Live hosting/Clerk acceptance and F's current scrolling/Home gate remain separate.
