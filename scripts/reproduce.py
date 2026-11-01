"""Recompute public results without changing published snapshots."""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import statistics
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--with-sources', action='store_true')
args = parser.parse_args()
checks = []
data = json.loads((root/'data/aggregate_questionnaires.json').read_text())
expected = {'classquest':(8.0,9.0,13), 'paperweave':(8.1,8.0,15)}
summaries = {}
for name, row in data.items():
    values = [int(k) for k,n in row['rating_counts'].items() for _ in range(n)]
    summary = {'n':len(values), 'mean':statistics.mean(values), 'median':statistics.median(values),
               'at_least_8':sum(x>=8 for x in values), 'response_rate':len(values)/row['invited']}
    assert summary['n'] == row['respondents'] == 20
    assert (summary['mean'],summary['median'],summary['at_least_8']) == expected[name]
    summaries[name] = summary
checks.append('Aggregate questionnaire arithmetic')

with tempfile.TemporaryDirectory() as work:
    tmp = Path(work)
    shutil.copytree(root/'experiments',tmp/'experiments')
    def run(script):
        subprocess.run([sys.executable,str(tmp/'experiments'/script)],check=True,stdout=subprocess.DEVNULL)
    run('audit_classquest.py')
    actual = json.loads((tmp/'experiments/classquest_results.json').read_text())
    recorded = json.loads((root/'experiments/classquest_results.json').read_text())
    assert actual['provenance']['source_sha256'] == recorded['provenance']['source_sha256']
    for name, digest in recorded['provenance']['source_sha256'].items():
        assert hashlib.sha256((root/'experiments/frozen'/name).read_bytes()).hexdigest() == digest
    actual.pop('provenance'); recorded.pop('provenance')
    assert actual == recorded
    checks.append('ClassQuest audit and frozen module hashes')
    run('audit_completion_check.py')
    assert json.loads((tmp/'experiments/completion_check_results.json').read_text()) == json.loads((root/'experiments/completion_check_results.json').read_text())
    checks.append('Completion check: 46,375 states and 163,680 resolution transitions')
    run('audit_paperweave.py')
    assert json.loads((tmp/'experiments/paperweave_results.json').read_text()) == json.loads((root/'experiments/paperweave_results.json').read_text())
    checks.append('PaperWeave original nine-edge census')
    spec = importlib.util.spec_from_file_location('companion', root/'experiments/evidence_report.py')
    companion = importlib.util.module_from_spec(spec); spec.loader.exec_module(companion)
    first = [{'participant_id':i,'outcome':'correct' if i<4 else 'incorrect'} for i in range(20)]
    retry = [{'participant_id':i,'outcome':'correct'} for i in range(4)]
    computed = {'first':companion.item_summary(range(20),first),
                'retry':companion.item_summary(range(20),retry),
                'paired':companion.paired_retry(first,retry)}
    assert computed == json.loads((root/'experiments/companion_results.json').read_text())
    checks.append('Constructed coverage and paired-retry example')
    bankpath = root/'teaching_materials/paperweave/claim_bank.json'
    bank = json.loads(bankpath.read_text())
    audit = json.loads((root/'experiments/paperweave_resource_audit.json').read_text())
    edges = json.loads((root/'experiments/paperweave_edges.json').read_text())
    assert {tuple(p['edge']) for p in bank['pairs']} == {(p['from'],p['to']) for p in edges}
    assert len(bank['cards']) == len({c['id'] for c in bank['cards']}) == 18
    assert dict(Counter(c['judgment'] for c in bank['cards'])) == audit['card_judgments']
    assert hashlib.sha256(bankpath.read_bytes()).hexdigest() == audit['claim_bank_sha256']
    assert all(set(c['passages']) <= set(bank['passages']) for c in bank['cards'])
    checks.append('Teaching resource coverage, IDs, judgments and hash')
    extension_path = root/'teaching_materials/paperweave/assessment_extension.json'
    extension = json.loads(extension_path.read_text())
    extension_audit = json.loads((root/'experiments/paperweave_extension_audit.json').read_text())
    assert len(extension['tasks']) == 4
    assert len({t['id'] for t in extension['tasks']}) == 4
    assert all(set(t['passages']) <= set(extension['passages']) for t in extension['tasks'])
    assert hashlib.sha256(extension_path.read_bytes()).hexdigest() == extension_audit['extension_sha256']
    checks.append('New-source exercise structure and hash')
    if args.with_sources:
        (tmp/'literature').mkdir()
        for name in [*bank['documents'], 'transformer']:
            source = root/'literature'/f'{name}.pdf'
            if not source.exists(): raise SystemExit('Run scripts/fetch_sources.py first: missing '+source.name)
            shutil.copy2(source,tmp/'literature'/source.name)
        run('build_paperweave_teaching_pack.py')
        run('build_paperweave_extension.py')
        for file in (root/'teaching_materials/paperweave').iterdir():
            if file.is_file(): assert file.read_bytes() == (tmp/'teaching_materials/paperweave'/file.name).read_bytes(), file.name
        assert json.loads((tmp/'experiments/paperweave_resource_audit.json').read_text()) == audit
        assert json.loads((tmp/'experiments/paperweave_extension_audit.json').read_text()) == json.loads((root/'experiments/paperweave_extension_audit.json').read_text())
        checks.append('Six exact source hashes, 15 core and 3 extension anchors, byte-identical teaching materials')

report = {'status':'passed','checks':checks,'classroom_aggregate_summaries':summaries,
          'source_pdf_check_run':args.with_sources,
          'limits':'Arithmetic and artifact integrity, not independent participant verification or pedagogical effectiveness'}
(root/'build').mkdir(exist_ok=True)
(root/'build/reproduction_report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
