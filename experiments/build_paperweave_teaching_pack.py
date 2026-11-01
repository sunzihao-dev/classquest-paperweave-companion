"""Build source-linked teaching materials. These are not participant observations."""
from pathlib import Path
from collections import Counter
import csv
import hashlib
import html
import json
import random
import unicodedata
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'teaching_materials/paperweave'
OUT.mkdir(parents=True,exist_ok=True)
docs={
 'dpr':('DPR','ACL Anthology proceedings PDF, 2020','https://aclanthology.org/2020.emnlp-main.550.pdf'),
 'bart':('BART','ACL Anthology proceedings PDF, 2020','https://aclanthology.org/2020.acl-main.703.pdf'),
 't5':('T5','JMLR 21(140), 2020 PDF','https://www.jmlr.org/papers/volume21/20-074/20-074.pdf'),
 'rag':('RAG','arXiv:2005.11401v4, 12 April 2021','https://arxiv.org/pdf/2005.11401v4'),
 'fid':('FiD','ACL Anthology proceedings PDF, 2021','https://aclanthology.org/2021.eacl-main.74.pdf')
}
sources={k:{'title':v[0],'version':v[1],'url':v[2],'sha256':hashlib.sha256((ROOT/'literature'/f'{k}.pdf').read_bytes()).hexdigest()} for k,v in docs.items()}
frozen_manifest=ROOT/'experiments/paperweave_source_manifest.json'
if frozen_manifest.exists():
    expected=json.loads(frozen_manifest.read_text())
    assert all(sources[k]['sha256']==expected[k]['sha256'] for k in sources), 'Source PDF differs from the inspected snapshot'
else:
    frozen_manifest.write_text(json.dumps(sources,indent=2)+'\n')
# Short anchors identify places to inspect in full context, not standalone evidence excerpts.
locs=[
 ('dpr_enc','dpr',3,'3.1, Encoders','two independent BERT'),
 ('bart_compare','bart',1,'Abstract and 1','generalizing BERT'),
 ('bart_init','bart',2,'2.1','initialise parameters'),
 ('bart_model','bart',2,'2','sequence-to-sequence model'),
 ('t5_inspiration','t5',12,'3.1.4 (continues on page 13)','Inspired by BERT'),
 ('t5_dropout','t5',13,'3.1.4','word dropout'),
 ('t5_model','t5',11,'3.1.1','standard encoder-decoder Transformer'),
 ('rag_retriever','rag',3,'2.2','pre-trained bi-encoder'),
 ('rag_generator','rag',3,'2.3','We use BART-large'),
 ('rag_training','rag',4,'2.4','keep the document encoder'),
 ('fid_compare','fid',2,'2','differs from these works'),
 ('fid_architecture','fid',3,'3, Reading','such as T5 or'),
 ('fid_joint','fid',3,'3, Reading','jointly in the decoder'),
 ('fid_initialization','fid',4,'4, Technical details','initialize our models'),
 ('fid_retrieval','fid',4,'4, Technical details','with BM25 for SQuAD')
]
passages={i:{'document':d,'pdf_page':p,'section':s,'anchor':a} for i,d,p,s,a in locs}
# Supported and challenged statements are source-scoped author-designed teaching examples.
pairs=[
 {'id':'E1','edge':['bert','dpr'],'relation':'component use','passages':['dpr_enc'],
  'supported':'The reported DPR retriever uses two independent BERT encoders for questions and passages.',
  'challenge':'The reported DPR retriever shares one BERT encoder parameter set between questions and passages.',
  'verdict':'refuted','change':'independent components to shared parameters',
  'rationale':'The architecture description explicitly specifies independent networks. Sharing the BERT architecture does not entail sharing one parameter set.',
  'repair':'Restore the distinction between the question encoder and the passage encoder.'},
 {'id':'E2','edge':['bert','bart'],'relation':'author-stated conceptual relation','passages':['bart_compare','bart_init'],
  'supported':'The BART paper compares its bidirectional encoder with BERT within a broader sequence-to-sequence architecture.',
  'challenge':'BART is initialized by loading a released BERT checkpoint.',
  'verdict':'refuted','change':'architectural comparison to checkpoint reuse',
  'rationale':'The comparison concerns architecture. The model section separately specifies random parameter initialization, rather than BERT checkpoint initialization.',
  'repair':'Describe the architectural comparison without asserting checkpoint reuse.'},
 {'id':'E3','edge':['bert','t5'],'relation':'author-stated conceptual relation','passages':['t5_inspiration','t5_dropout'],
  'supported':'T5 describes its baseline denoising objective as inspired by BERT masked language modelling and word dropout.',
  'challenge':'T5 describes BERT as the sole inspiration for its baseline denoising objective.',
  'verdict':'refuted','change':'multiple influences to sole influence',
  'rationale':'The sentence crosses a page boundary and names a second influence. Reading only its first page drops a consequential part of the statement.',
  'repair':'Retain both named influences and restrict the claim to the baseline objective.'},
 {'id':'E4','edge':['dpr','rag'],'relation':'component use','passages':['rag_retriever','rag_training'],
  'supported':'RAG initializes its retriever from DPR and keeps the document encoder fixed during its reported fine-tuning.',
  'challenge':'RAG fine-tunes both the DPR question encoder and the document encoder in its reported training procedure.',
  'verdict':'refuted','change':'component use to unrestricted updating',
  'rationale':'Initialization and subsequent training are different claims. The training subsection identifies the fixed document encoder.',
  'repair':'Separate initialization from fine-tuning and preserve which encoder stays fixed.'},
 {'id':'E5','edge':['bart','rag'],'relation':'component use','passages':['rag_generator','rag_training'],
  'supported':'RAG uses a BART-large generator and fine-tunes that generator in the reported procedure.',
  'challenge':'RAG keeps its BART generator parameters fixed throughout the reported fine-tuning.',
  'verdict':'refuted','change':'fine-tuned component to frozen component',
  'rationale':'The generator and training subsections identify both the component and its update policy.',
  'repair':'State that the generator is fine-tuned; do not transfer the document encoder policy to it.'},
 {'id':'E6','edge':['dpr','fid'],'relation':'conditional use','passages':['fid_retrieval'],
  'supported':'FiD reports DPR retrieval for Natural Questions and TriviaQA, and BM25 for SQuAD.',
  'challenge':'FiD uses DPR for every dataset reported in the paper.',
  'verdict':'refuted','change':'dataset-qualified use to universal use',
  'rationale':'The SQuAD configuration supplies an explicit counterexample to the universal statement.',
  'repair':'Restore the dataset-to-retriever mapping.',
  'classroom_connection':'The overgeneralisation is described in the practitioner account; these card wordings are authored paraphrases, not student quotations.'},
 {'id':'E7','edge':['t5','fid'],'relation':'experimental instantiation','passages':['fid_architecture','fid_initialization'],
  'supported':'The reported FiD experiments initialize from T5; the method description also allows a model such as BART.',
  'challenge':'The FiD method requires T5 and excludes BART as a possible sequence-to-sequence model.',
  'verdict':'refuted','change':'experimental choice to architectural necessity',
  'rationale':'The method explicitly gives another possible model. An experimental instantiation is not an architectural requirement.',
  'repair':'Keep the T5 initialization claim within the scope of the reported experiments.'},
 {'id':'E8','edge':['rag','fid'],'relation':'author-stated conceptual relation','passages':['fid_compare','fid_joint','fid_initialization'],
  'supported':'The FiD paper compares its handling of retrieved passages with RAG and describes joint processing in the decoder.',
  'challenge':'The comparison establishes that FiD loads a previously trained RAG system as a component.',
  'verdict':'not established','change':'comparison to component inheritance',
  'rationale':'The comparison and method description do not establish the asserted component inheritance. Withhold that claim; a comparison is not a lineage record.',
  'repair':'Retain the processing comparison. To assert reuse, obtain explicit implementation or initialization evidence.'},
 {'id':'E9','edge':['t5','bart'],'relation':'curator comparison','passages':['t5_model','t5_inspiration','t5_dropout','bart_model'],
  'supported':'T5 and BART can be compared as encoder-decoder approaches with denoising pre-training.',
  'challenge':'Their shared encoder-decoder and denoising properties establish that T5 historically influenced BART.',
  'verdict':'not established','change':'similarity to historical influence',
  'rationale':'Shared properties support an analytical comparison. They do not supply evidence of the direction or existence of historical influence.',
  'repair':'Label the relation as a curator comparison; request a historical or author-attribution source before claiming influence.'}
]
for pair in pairs:
    pair['review_status']='AI-assisted source inspection; no independent human annotation'
cards=[]
for p in pairs:
    for variant in ('supported','challenge'):
        cards.append({'pair':p['id'],'claim':p[variant],'judgment':'supported' if variant=='supported' else p['verdict'],'variant':variant,'passages':p['passages']})
random.Random(20261101).shuffle(cards)
for i,c in enumerate(cards,1): c['id']=f'C{i:02d}'
bank={'version':'2026-11-01.1','evidence_type':'Author-constructed instructional resource; no new classroom observations','judgment_scope':'Support, refutation or non-establishment relative to the named source context, not global truth','documents':sources,'passages':passages,'pairs':pairs,'cards':cards}
(OUT/'claim_bank.json').write_text(json.dumps(bank,indent=2)+'\n')
with (OUT/'student_cards.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['id','claim']);w.writeheader();w.writerows({k:c[k] for k in ['id','claim']} for c in cards)
with (OUT/'teacher_key.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['id','pair','claim','judgment','passages']);w.writeheader();w.writerows({k:(', '.join(c[k]) if k=='passages' else c[k]) for k in w.fieldnames} for c in cards)

# Independent integrity check against actual PDF pages and the original exported graph.
def norm(s): return ' '.join(unicodedata.normalize('NFKC',s).split()).lower()
checks=[]
pdfs={k:PdfReader(ROOT/'literature'/f'{k}.pdf') for k in docs}
for key,p in passages.items():
    found=norm(p['anchor']) in norm(pdfs[p['document']].pages[p['pdf_page']-1].extract_text() or '')
    checks.append({'passage':key,'anchor_resolves_on_declared_page':found})
original=json.loads((ROOT/'experiments/paperweave_edges.json').read_text())
original_edges={(e['from'],e['to']) for e in original}
assert {tuple(p['edge']) for p in pairs}==original_edges
assert all(c['anchor_resolves_on_declared_page'] for c in checks), checks
assert all(set(c['passages'])<=set(passages) for c in cards)
assert len({c['id'] for c in cards})==18
audit={'evidence_type':'Source-traceability and teaching-resource audit, not a learning study or classifier benchmark','date':'2026-11-01','original_edges':len(original_edges),'covered_edges':len(pairs),'cards':len(cards),'source_documents':len(sources),'source_passages':len(passages),'resolvable_anchors':sum(c['anchor_resolves_on_declared_page'] for c in checks),'relation_counts':dict(Counter(p['relation'] for p in pairs)),'card_judgments':dict(Counter(c['judgment'] for c in cards)),'original_status_counts':dict(Counter(e['status'] for e in original)),'passage_checks':checks,'semantic_review':'AI-assisted, not independently human-validated','claim_bank_sha256':hashlib.sha256((OUT/'claim_bank.json').read_bytes()).hexdigest(),'interpretation':'Counts describe a deliberately designed resource. Successful locator checks validate traceability, not the truth of claims, annotation accuracy or student learning.'}
(ROOT/'experiments/paperweave_resource_audit.json').write_text(json.dumps(audit,indent=2)+'\n')

css='body{font:17px/1.55 system-ui,sans-serif;color:#203047;margin:0;background:#f3f6f8}main{max-width:980px;margin:auto;padding:36px 24px}h1{line-height:1.2}section,.card{background:white;border:1px solid #ccd7e0;border-radius:10px;padding:22px;margin:18px 0}table{width:100%;border-collapse:collapse}td,th{padding:10px;border-bottom:1px solid #ccd7e0;text-align:left;vertical-align:top}a{color:#155d9b}.line{min-height:2.7em;border-bottom:1px solid #aab6c1}small{color:#526176}@media print{body{background:white;font-size:11pt}main{padding:0}.card{break-inside:avoid;border-radius:0}a{color:inherit}button{display:none}}'
def document(title,body):return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+title+'</title><style>'+css+'</style></head><body><main>'+body+'</main></body></html>'
student='<h1>What does this research-paper claim support?</h1><p>For each assigned card, first write your prediction. Then inspect the source context supplied by your teacher, record the relevant location and condition, and justify a final judgment: supported, refuted or not established. A source title or agreement with a partner is not a justification.</p><p><strong>Not established</strong> means the named evidence does not settle the claim. It does not mean the claim is globally false.</p><section><h2>Working vocabulary</h2><p><strong>Encoder:</strong> represents input text. <strong>Decoder:</strong> produces an output sequence. <strong>Retriever:</strong> selects relevant passages. <strong>Generator:</strong> produces an answer. <strong>Checkpoint:</strong> saved model weights. <strong>Initialize:</strong> choose starting weights. <strong>Fine-tune:</strong> update weights through training. <strong>Scope:</strong> the conditions under which a claim applies.</p></section>'
for c in cards:
    student+='<article class="card"><h2>'+c['id']+'</h2><p>'+html.escape(c['claim'])+'</p>'
    for label in ['Initial judgment and reason','Source document, version and location','Condition or distinction that matters','Final judgment and explanation','Revised claim, or evidence still needed']:
        student+='<p><strong>'+label+'</strong></p><div class="line"></div>'
    student+='</article>'
(OUT/'student_workbook.html').write_text(document('PaperWeave student claim workbook',student))
guide='<h1>PaperWeave: source-linked claim workshop</h1><p><strong>Completed teaching resource, prepared after the June classroom account.</strong> The 18 cards are authored examples, not additional student responses or a validated assessment. Their labels and rationales are AI-assisted and should be checked by the adopting teacher.</p><p><a href="student_workbook.html">Print the student workbook</a> · <a href="student_cards.csv">Student cards CSV</a> · <a href="teacher_key.csv">Teacher key CSV</a> · <a href="claim_bank.json">Structured source and claim bank</a></p><section><h2>Suggested implementation</h2><p>Begin with E1 (component identity), E6 (dataset scope), E7 (choice versus necessity) and E9 (comparison versus history). These eight cards form a proposed core; the remaining ten are extensions. Check the vocabulary first. Model one source-based explanation, then give pairs a different card, followed by an individual explanation on an unseen relation. Choose timings according to prior knowledge; this is not a reconstruction of the June sessions.</p><p>Keep the answer key separate. Obtain an initial answer before supplying the relevant source context. Require a location and explanation, then permit peer challenge and revision. Eventually remove the leading prompts while retaining access to sources. Fading is motivated by prior educational work, not evaluated here. Do not score students from the judgment label alone.</p></section><section><h2>Feedback guide</h2><table><tr><th>Look for</th><th>If missing or mistaken</th><th>Follow-up</th></tr><tr><td>Correct component or relation meaning</td><td>Model names substitute for roles</td><td>Ask which component encodes, retrieves or generates.</td></tr><tr><td>Relevant source and location</td><td>A citation is supplied without pertinent evidence</td><td>Locate the paragraph; retain its context.</td></tr><tr><td>Condition retained</td><td>Some becomes all; an experiment becomes a requirement</td><td>Request a counterexample or a qualified rewrite.</td></tr><tr><td>Justified judgment</td><td>Unsupported is treated as false, or label-only answers</td><td>Explain what the evidence establishes and what further evidence is needed.</td></tr></table><p>This is a prospective feedback guide, not a validated numeric rubric or a scoring of earlier worksheets.</p></section><section><h2>Source manifest</h2>'
for k,s in sources.items():guide+='<p><a href="'+s['url']+'">'+s['title']+'</a> · '+s['version']+'<br><small>SHA-256 '+s['sha256']+'</small></p>'
guide+='</section>'
guide+='<section><h2>Four inference boundaries</h2><p>These distinctions organise the authored cases, not observed misconception frequencies. More than one distinction can apply to a case.</p><table><tr><th>Distinction</th><th>Pairs</th><th>Explanation to request</th></tr><tr><td>Component identity and operation</td><td>E1, E2, E4, E5</td><td>Name what is shared, loaded, frozen or trained; architecture and parameters are different objects.</td></tr><tr><td>Experimental scope</td><td>E3, E6</td><td>Restore an omitted contributor or dataset; test only/every against a counterexample.</td></tr><tr><td>Use versus necessity</td><td>E7</td><td>Separate the reported implementation from the alternatives allowed by the method.</td></tr><tr><td>Comparison versus lineage</td><td>E8, E9</td><td>Retain the comparison while requesting explicit reuse or historical-attribution evidence.</td></tr></table></section>'
guide+='<section><h2>Preparing another pair</h2><p>Choose a relation that serves a computing learning objective. Inspect its primary source in context and write the strongest claim it warrants. Change one consequential premise: a component, condition, necessity or attribution. Decide whether the changed claim is explicitly refuted or merely not established. Retain the location, context and repair rationale, and ask a second reader to check both interpretations before classroom use. This is an adaptation method, not a tested result in a new domain.</p><p>Use contrasting twins for practice, but do not split a pair between practice and an assessment intended to measure independent reasoning. A visible opposite claim can cue the answer. Check vocabulary separately, preserve source access and assess explanations rather than labels alone.</p></section>'
for p in pairs:
    guide+='<section><h2>'+p['id']+' · '+html.escape(' → '.join(p['edge']).upper())+'</h2><p><strong>Relationship:</strong> '+p['relation']+'</p><p><strong>Supported claim:</strong> '+html.escape(p['supported'])+'</p><p><strong>Challenge:</strong> '+html.escape(p['challenge'])+' <strong>('+p['verdict']+')</strong></p><p>'+html.escape(p['rationale'])+'</p><p><strong>Repair:</strong> '+html.escape(p['repair'])+'</p><ul>'
    for key in p['passages']:
        q=passages[key];s=sources[q['document']]
        guide+='<li><a href="'+s['url']+'#page='+str(q['pdf_page'])+'">'+s['title']+', PDF page '+str(q['pdf_page'])+'</a>, section '+q['section']+'. Locator anchor: “'+html.escape(q['anchor'])+'”. Read the surrounding paragraph.</li>'
    guide+='</ul><p><small>Cards: '+', '.join(c['id'] for c in cards if c['pair']==p['id'])+'. '+p['review_status']+'.</small></p></section>'
guide+='<section><h2>Related foundations</h2><p>The support/refutation distinction builds on <a href="https://aclanthology.org/2020.emnlp-main.609/">SciFact</a>. Citation intent is a different judgment, as illustrated by <a href="https://aclanthology.org/N19-1361/">SciCite</a>. Explanation scaffolding and eventual independent performance build on <a href="https://doi.org/10.1207/s15327809jls1502_1">McNeill et al.</a>. This resource does not claim those ideas as inventions.</p></section>'
(OUT/'teacher_guide.html').write_text(document('PaperWeave teacher guide and source key',guide))
(OUT/'README.txt').write_text('PaperWeave teaching resource, version 2026-11-01.1\nOpen teacher_guide.html; student_workbook.html omits the answer key.\nThese materials were produced after the classroom sessions. No new participant evidence is included.\nAll source files are identified by version, PDF page, section and SHA-256. Download the originals from the links; they are not redistributed.\nThe author-constructed judgments are AI-assisted, not independent expert annotations or benchmark labels.\nResource integrity audit: experiments/paperweave_resource_audit.json in the project workspace.\n')
print(json.dumps({k:audit[k] for k in ['covered_edges','cards','source_documents','source_passages','resolvable_anchors','relation_counts','card_judgments']},indent=2))
