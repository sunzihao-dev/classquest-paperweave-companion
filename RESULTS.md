# Results and their interpretation

## Classroom usefulness ratings

These counts were supplied in the practitioner's corrected classroom account. Recalculation verifies the arithmetic; it does not independently verify the original collection. Individual-level records are unavailable in this companion.

| Measure | ClassQuest | PaperWeave |
| --- | ---: | ---: |
| Year level | 10 | 11 |
| Questionnaire invitees | 24 | 22 |
| Responses | 20 | 20 |
| Response rate | 83.3% | 90.9% |
| Mean rating / 10 | 8.0 | 8.1 |
| Median / 10 | 9 | 8 |
| Rating at least 8 | 13/20 (65%) | 15/20 (75%) |

Both questionnaires used 1 = not at all useful and 10 = extremely useful. The questions differ by tool and concern perceived usefulness. The cohorts, activities and questionnaires do not support ranking the tools or estimating comparative effectiveness. See [aggregate data](data/aggregate_questionnaires.json) and [frequency table](data/rating_counts.csv).

## Constructed ClassQuest software audit

- Enumerated **5,456** count compositions for a constructed class size of 30; no mismatches in the checked accuracy/missing/pending fields.
- **4,141 of 5,278** compositions eligible for a substantive prototype action crossed an action boundary under possible completion of unresolved answers. These are enumeration counts, not frequencies observed in classrooms.
- In a deliberately selective retry example, displayed accuracy rose from 20% to 100%, while the four matched respondents had zero percentage-point change.
- Structural validation accepted a deliberately wrong answer key and unrelated prompt; it rejected a fabricated source quotation and a wrong locator. This distinguishes source-format checks from semantic correctness.
- A deliberately incorrect short answer containing rubric words received an overlap hint of 1.0 but correctly remained marked `needs_review`.

The [recorded results](experiments/classquest_results.json) concern the frozen snapshot only. [Companion calculations](experiments/companion_results.json) add coverage, completion bounds and matched retry counts; they are not integrated classroom interface features or validated pedagogy.

## PaperWeave structural and source audit

The original export contains six nodes and nine links: five labelled `verified`, three `conceptual`, one `inferred`. These are prototype status strings, not independent review verdicts. All nine have informal source descriptions; none has the six explicit structured fields checked by the audit. A missing field does not make a relationship false.

The subsequent authored teaching resource covers all nine links with **18 cards**. It deliberately contains nine supported claims, seven refuted challenges and two challenges not established by the cited context. These counts describe resource design, not measured model performance or student misconception prevalence.

All **15 locator anchors** resolve on the declared PDF pages across five source documents with pinned SHA-256 hashes. The check validates traceability, not semantic correctness. The source judgments and rationales were AI-assisted; no independent human annotation study has been conducted. See [structural results](experiments/paperweave_results.json), [resource audit](experiments/paperweave_resource_audit.json) and [teacher guide](teaching_materials/paperweave/teacher_guide.html).

## Remaining evaluation limits

The new card resource was prepared after the reported classroom sessions and has not been tested with students. The earlier PaperWeave group activities have no complete group-specific outcome comparison available, and the teacher's clarification reached both groups. No causal advantage is claimed. The manuscripts describe qualitative teaching episodes without converting them into numerical success rates. No withdrawn illustrative follow-up scores are included.

## Completion-sensitive reporting check (v1.1.0)

The implemented companion enumerates attainable reporting bands when pending or missing responses are resolved for one item. It preserves the frozen report's nearest-integer, ties-to-even rounding and provisional 55/80 cutoffs. All **46,375** count configurations for rosters of 1–30 matched an independent integer oracle. All **163,680** applicable one-response resolution transitions narrowed or retained the possible band set. The check preserves the early-signal flag separately and returns no band for an empty roster. A stable band is not evidence of mastery or a validated teaching recommendation. See [results](experiments/completion_check_results.json).

## Worked feedback and new-source exercise (v1.1.0)

The extension supplies four constructed feedback examples and four tasks using the Transformer paper, outside the original map. Two tasks are supported, one refuted and one not established by the named source context; these are designed judgments. Three anchors resolve in one additional pinned PDF. This tests traceability, not semantic validity. The exercise concerns source-scoped reasoning within a new paper, not building a new inter-paper map.

The practitioner reports researcher feedback on an **earlier prototype/draft** concerning DPR–FiD dataset scope, T5–FiD experimental choice and T5–BART comparison versus historical influence. The original feedback sheet was not inspected, and the feedback does not validate the current 18-card key or the new exercise. No new student results are claimed.
