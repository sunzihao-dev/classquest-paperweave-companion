"""Build prospective assessment examples; no new classroom data or test validation."""
from pathlib import Path
from collections import Counter
import hashlib
import html
import json
import unicodedata
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'teaching_materials/paperweave'
pdf=ROOT/'literature/transformer.pdf'
source=dict(title='Attention Is All You Need',version='NIPS 2017 proceedings PDF',
    url='https://papers.nips.cc/paper/2017/file/3f5ee243547dee91fbd053c1c4a845aa-Paper.pdf',
    sha256='d87d482d5ae7960e2e43d7dd6d21377e60e73e8fce1bf2a01aff7aca8a08c537')
assert hashlib.sha256(pdf.read_bytes()).hexdigest()==source['sha256']
passages={
 'configurations':dict(pdf_page=9,section='6.2, Table 3',anchor='Table 3: Variations'),
 'position':dict(pdf_page=6,section='3.5',anchor='nearly identical'),
 'variation':dict(pdf_page=8,section='6.2',anchor='we varied our base model')}
tasks=[
 dict(id='T1',claim='Both the base and big configurations in Table 3 use six layers in each encoder and decoder stack.',
      passages=['configurations'],judgment='supported',
      rationale='The N column is 6 for both named configurations. This does not assert that every variation uses six layers.',
      evidence_needed='Identify the N column and name both rows; preserve the restriction to base and big.'),
 dict(id='T2',claim='The big configuration in Table 3 uses eight attention heads.',
      passages=['configurations'],judgment='refuted',
      rationale='The h column gives 16 for big and 8 for base. The row is part of the evidence, not an interchangeable detail.',
      evidence_needed='Locate the big row and h column and repair eight to sixteen.'),
 dict(id='T3',claim='The authors report nearly identical results when replacing sinusoidal positional encodings with learned positional embeddings in their comparison.',
      passages=['position','configurations'],judgment='supported',
      rationale='Section 3.5 and Table 3 row E support the reported comparison. Nearly identical is not exact equality or a universal guarantee.',
      evidence_needed='Link the statement to the named comparison; retain its experimental scope.'),
 dict(id='T4',claim='The base-versus-big BLEU difference in Table 3 establishes that increasing attention-head count alone caused the improvement.',
      passages=['variation','configurations'],judgment='not established',
      rationale='The rows also differ in model dimensions, dropout and training steps. This comparison does not isolate the causal effect of head count.',
      evidence_needed='Name a second changed factor and request an otherwise controlled comparison; do not infer that more heads have no effect.')]
examples=[
 dict(task='E6',response='Refuted.',interpretation='A label without a warrant.',feedback='Ask for the source location and a counterexample; correctness of the label alone is insufficient.'),
 dict(task='E6',response='FiD uses more than one retriever.',interpretation='Notices variation but omits the dataset condition.',feedback='Ask which dataset supplies the counterexample and what the revised claim should say.'),
 dict(task='E6',response='FiD section 4, PDF page 4 reports DPR for Natural Questions and TriviaQA and BM25 for SQuAD. SQuAD therefore refutes the all-datasets claim.',interpretation='Pertinent location, condition and inferential reason.',feedback='Retain this qualified statement; then check reasoning on a different source.'),
 dict(task='E9',response='Not established: both use denoising, but these architecture descriptions do not identify historical influence. We need explicit attribution or historical evidence.',interpretation='Preserves comparison and withholds the stronger claim.',feedback='Accept justified uncertainty; ask what source could establish influence.')]
data=dict(version='2026-11-01.2',evidence_type='Constructed teaching materials; not learner responses or a validated transfer test',
          source=source,passages=passages,tasks=tasks,feedback_examples=examples,
          administration='Use after map-based practice, without the answer key or a paired opposite claim. Check vocabulary first; preserve source access. These tasks assess scope and evidence on a new source, not transfer to arbitrary domains or inter-paper synthesis.')
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'assessment_extension.json').write_text(json.dumps(data,indent=2)+'\n')
(ROOT/'experiments/paperweave_extension_manifest.json').write_text(json.dumps({'transformer':source},indent=2)+'\n')
reader=PdfReader(pdf)
def norm(s):return ' '.join(unicodedata.normalize('NFKC',s).split()).lower()
checks={k:norm(v['anchor']) in norm(reader.pages[v['pdf_page']-1].extract_text()) for k,v in passages.items()}
assert all(checks.values()),checks
assert all(set(t['passages']) <= set(passages) for t in tasks)
audit=dict(evidence_type='Mechanical traceability check, not semantic validation',tasks=len(tasks),
           judgments=dict(Counter(t['judgment'] for t in tasks)),source_documents=1,anchor_checks=checks,
           extension_sha256=hashlib.sha256((OUT/'assessment_extension.json').read_bytes()).hexdigest())
(ROOT/'experiments/paperweave_extension_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
css='body{font:17px/1.55 system-ui;color:#203047;max-width:900px;margin:40px auto;padding:20px}section{border:1px solid #bcc9d2;padding:20px;margin:20px 0}h1{line-height:1.2}.line{height:6em;border-bottom:1px solid #bbb}@media print{section{break-inside:avoid}body{font-size:11pt}}'
def page(title,body):return '<!doctype html><html lang="en"><head><meta charset="utf-8"><title>'+title+'</title><style>'+css+'</style></head><body><h1>'+title+'</h1>'+body+'</body></html>'
student='<p>Inspect the linked Transformer paper. For each assigned statement, give a judgment, a source location and your reasoning. Qualify or withhold a claim when appropriate.</p><p><a href="'+source['url']+'">Source PDF</a> · Inspect sections 3.5 and 6.2, including Table 3. Head means one attention mechanism; BLEU is a translation evaluation score; a configuration is a particular experimental setup.</p>'
for t in tasks:student+='<section><h2>'+t['id']+'</h2><p>'+html.escape(t['claim'])+'</p><div class="line"></div></section>'
(OUT/'new_source_student.html').write_text(page('PaperWeave: reasoning with a new source',student))
teacher='<p><strong>Prospective materials, not classroom findings.</strong> These four tasks use a paper outside the original map. They do not establish transfer or constitute a validated assessment.</p><p>'+data['administration']+'</p><p><a href="new_source_student.html">Student tasks (no key)</a> · <a href="assessment_extension.json">Structured examples and key</a></p><h2>Worked feedback examples</h2>'
for e in examples:teacher+='<section><h3>'+e['task']+' · constructed response</h3><p>'+html.escape(e['response'])+'</p><p><strong>Interpretation:</strong> '+e['interpretation']+'</p><p><strong>Feedback:</strong> '+e['feedback']+'</p></section>'
teacher+='<h2>New-source answer key</h2>'
for t in tasks:
 teacher+='<section><h3>'+t['id']+' · '+t['judgment']+'</h3><p>'+html.escape(t['claim'])+'</p><p>'+t['rationale']+'</p><p>'+t['evidence_needed']+'</p><ul>'
 for k in t['passages']:
  q=passages[k];teacher+='<li><a href="'+source['url']+'#page='+str(q['pdf_page'])+'">PDF page '+str(q['pdf_page'])+'</a>, '+q['section']+'</li>'
 teacher+='</ul></section>'
teacher+='<p>These tasks test source-scoped reasoning within one new paper. They do not test building a new graph. Reserve complete paper pairs during practice, avoid revealing contrasting twins during assessment, and record explanations separately from labels. Independent rater calibration and classroom evaluation remain necessary.</p>'
(OUT/'assessment_guide.html').write_text(page('PaperWeave: worked feedback and new-source tasks',teacher))
print(json.dumps(audit,indent=2))
