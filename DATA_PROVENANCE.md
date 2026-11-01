# Data and artifact provenance

| Path | Provenance | What can be reproduced |
| --- | --- | --- |
| `data/aggregate_questionnaires.json`, `data/rating_counts.csv` | Corrected practitioner-supplied frequency tables; no individual responses | Counts, means, medians, response rates and high-rating proportions |
| `experiments/frozen/` | Frozen ClassQuest modules used in the technical audit, identified by hashes | Behaviour exercised by the artificial diagnostic inputs |
| `experiments/classquest_results.json` | Previously recorded deterministic audit on a Linux research VM using Python 3.11.11; hostname omitted | Numerical results, with runtime metadata allowed to differ |
| `experiments/companion_results.json` | Constructed first/retry example, no human responses | Coverage, bounds and paired-change calculations |
| `experiments/paperweave_edges.json` | All nine exported curated prototype links | Structural census; not automated relation extraction |
| `experiments/paperweave_source_manifest.json` | Versioned source-PDF identifiers and SHA-256 hashes | Exact-file verification if those source bytes remain obtainable |
| `teaching_materials/paperweave/` | Later authored instructional resource, version 2026-11-01.1 | Stable card order, links, source locators and generated documents |
| `output/pdf/`, `manuscripts/` | Manuscript snapshots prepared for author review | PDF rebuilding with the provided LaTeX sources and compatible dependencies |

Original participant-level records were not independently inspected during companion preparation. They remain outside this repository. Consent records, participant identifiers, student quotations, raw worksheets, private chat transcripts, institutional approval identifiers, machine hostnames and local paths are not distributed as data.

The manuscripts retain the practitioner's general approval/consent account. This repository does not certify or reproduce an ethics approval. Publishing aggregate counts does not license collection of new student data.

AI tools assisted literature discovery, coding, source inspection, teaching-resource authoring and manuscript writing. This is disclosed in both manuscripts. No human responses were generated for the reported classroom aggregates. Constructed software examples are identified explicitly.

The current six-node/five-source distinction is intentional: BERT is a graph node; claims about its use or comparison are checked in the using/comparing papers (DPR, BART, T5, RAG, FiD).
