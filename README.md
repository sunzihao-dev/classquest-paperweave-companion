# ClassQuest and PaperWeave — research companion

Teaching materials, aggregate classroom feedback, reproducible technical audits and manuscript snapshots for two computing-education practitioner papers.

**Status:** revised manuscripts and supporting resources, version **v1.2.0 (1 November 2026)**. This repository does not assert conference acceptance or ACM publication. The PDF files retain their anonymous review formatting.

## Start here

| Resource | Contents |
| --- | --- |
| [ClassQuest paper](output/pdf/classquest_submission.pdf) | *From Source-Based Quizzes to Reteaching Decisions: A Practitioner Guide to ClassQuest* — 8 pages, 25 references |
| [PaperWeave paper](output/pdf/paperweave_submission.pdf) | *Teaching Students to Qualify AI Research Claims with PaperWeave* — 9 pages, 30 references |
| [PaperWeave teacher guide](teaching_materials/paperweave/teacher_guide.html) | 18 claim cards, all nine original links, source locations, answer rationales and a proposed feedback guide |
| [Worked feedback and new-source tasks](teaching_materials/paperweave/assessment_guide.html) | Constructed explanations, four Transformer-paper prompts and a separate student sheet; not a validated transfer test |
| [Student workbook](teaching_materials/paperweave/student_workbook.html) | Printable student-facing activities without answers |
| [Results and evidence boundaries](RESULTS.md) | Classroom aggregates, constructed audit results, and their limitations |
| [Reproduction instructions](REPRODUCING.md) | Recalculate summaries, rerun software audits and rebuild the teaching resource |
| [Data provenance](DATA_PROVENANCE.md) | What each file represents and what is not available |

GitHub shows HTML as source. Download the repository and open the teacher guide or workbook in your browser. No server is needed for these teaching materials. For the complete repository use **Code → Download ZIP**.

## What was evaluated?

- **Earlier classroom use:** practitioner-reported ClassQuest and PaperWeave sessions, aggregate usefulness ratings and classroom reflection. These are separate cohorts with different purposes. ClassQuest's May sessions used an earlier or separate prototype; they do not evaluate the later October implementation or reporting companion.
- **Constructed ClassQuest tests:** deterministic diagnostics of a frozen software snapshot, plus companion checks that distinguish not-offered items from offered-but-unanswered items. They contain no learner responses.
- **PaperWeave artifact audit:** a census of nine curated relationships and a source-traceability check of a later teaching resource.
- **New teaching materials:** completed after the classroom sessions. They have **not** been evaluated with students. The labels are AI-assisted author judgments, not independently validated expert annotations.

This repository does not establish causal learning gains, a difference in effectiveness between the tools, long-term retention or generalisation. Public data are aggregate counts only. Individual questionnaires, worksheets, participant identifiers and consent documentation are not included. Third-party research PDFs are linked, not redistributed.

## Quick reproduction

```sh
python3 scripts/reproduce.py
```

This offline command uses only Python's standard library and checks the aggregate arithmetic, constructed software tests, source-module hashes and teaching-resource structure. See [REPRODUCING.md](REPRODUCING.md) for the separate source-PDF traceability check and LaTeX build.

The repository contains the **frozen modules necessary for the reported audits**, not a deployable copy of either full historical classroom application.

## Citation and versioning

Use the repository URL together with the version or commit you consulted. [CITATION.cff](CITATION.cff) supplies repository citation metadata; it is not a citation to an accepted conference paper. [CITATION.bib](CITATION.bib) provides a BibTeX equivalent. Update paper citations to the final proceedings records only after publication.

For the anonymous ACE review version, retain the self-contained manuscript and do not insert this identifying repository URL. The current [ACE author instructions](https://aceconference2027.github.io/authors.html) say not to link webpages in the anonymous paper. [PUBLICATION_LINK.txt](PUBLICATION_LINK.txt) contains wording reserved for a later non-anonymous version, subject to final venue instructions.

See [REUSE.md](REUSE.md) for reuse and third-party notices. Report source or arithmetic errors through the repository's Issues page, identifying the file/card and source passage. Do not post student information.
