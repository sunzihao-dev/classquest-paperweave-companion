"""Structural audit of the nine original, curated prototype links.
Semantic judgments are recorded separately in edge_review.json.
"""
import hashlib
import json
from collections import Counter
from pathlib import Path

root = Path(__file__).resolve().parent
data = json.loads((root/'paperweave_edges.json').read_text())
fields = ['source_version','page','passage_id','reviewer','review_date','scope']
result = dict(evidence_type='structural census of curated prototype, not extraction benchmark',
    nodes=len({e[k] for e in data for k in ('from','to')}), edges=len(data),
    status_counts=dict(Counter(e['status'] for e in data)),
    informal_source_strings=sum(bool(e.get('source')) for e in data),
    explicit_structured_field_counts={k:sum(bool(e.get(k)) for e in data) for k in fields},
    edge_sha256=hashlib.sha256((root/'paperweave_edges.json').read_bytes()).hexdigest(),
    caveat='Missing structured fields do not establish that a relationship is false. No independent human annotation or learner study was performed.')
(root/'paperweave_results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
