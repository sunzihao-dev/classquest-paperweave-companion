"""Deterministic technical audit; every response is constructed, not learner data.

Run with Python >=3.9. No network, model calls, or third-party dependencies.
The state sweep enumerates count compositions, not independent classrooms.
"""
import hashlib
import json
import platform
from pathlib import Path
from frozen.analytics import build_report
from frozen.quiz import validate_question, grade

ROOT = Path(__file__).resolve().parent

def question(qid=1, stage="main"):
    return dict(id=qid, stage=stage, topic="Boolean logic", kind="mcq",
                prompt="What does True AND False evaluate to?",
                options=["False", "True"], answer=0, rubric=[],
                evidence="An AND expression is true only when both inputs are true.",
                locator="Section 1", explanation="Both inputs must be true.")

def row(pid, outcome, qid=1):
    return dict(id=qid*1000+pid, participant_id=pid, nickname="Synthetic %d"%pid,
                question_id=qid, outcome=outcome,
                answer_json=json.dumps(0 if outcome=="correct" else 1),
                score=1 if outcome=="correct" else 0, confidence="sure")

def audit():
    n=30; total=0; mismatches=[]; supported_actions=0; ambiguous_actions=0
    # Unknown outcomes can range from all incorrect to all correct. These are
    # logical bounds on a completed item, NOT confidence intervals or mastery.
    def band(rate):
        return "reteach" if rate<55 else "recap" if rate<80 else "advance"
    for correct in range(n+1):
        for incorrect in range(n-correct+1):
            for pending in range(n-correct-incorrect+1):
                missing=n-correct-incorrect-pending
                states=["correct"]*correct+["incorrect"]*incorrect+["needs_review"]*pending
                rows=[row(i,s) for i,s in enumerate(states)]
                report=build_report({"title":"Synthetic audit"},[question()],list(range(n)),rows)
                q=report["questions"][0]; total+=1
                expected=round(correct/(correct+incorrect)*100) if correct+incorrect else None
                if (q["accuracy"],q["missing"],q["needs_review"])!=(expected,missing,pending):
                    mismatches.append([correct,incorrect,pending,missing])
                if correct+incorrect>=3:
                    supported_actions+=1
                    if band(100*correct/n)!=band(100*(correct+pending+missing)/n):
                        ambiguous_actions+=1
    # Same responses on the same logical skill; only the responding cohort changes.
    first=[row(i,"correct" if i<4 else "incorrect") for i in range(20)]
    retry=[row(i,"correct",2) for i in range(4)]
    drift=build_report({"title":"Synthetic selection"},[question(),question(2,"retry")],list(range(20)),first+retry)
    matched=[(r["outcome"],first[r["participant_id"]]["outcome"]) for r in retry]
    paired_change=100*sum((a=="correct")-(b=="correct") for a,b in matched)/len(matched)
    # Three answers from one learner are not evidence from three learners.
    qs=[question(i) for i in (1,2,3)]
    sparse=build_report({"title":"Synthetic repeated items"},qs,list(range(30)),[row(0,"correct",i) for i in (1,2,3)])
    source=question()["evidence"]
    cases=[]
    for label,change in [("valid_control",{}),("wrong_key",{"answer":1}),
                         ("unrelated_prompt",{"prompt":"Which planet is closest to the Sun?"}),
                         ("fabricated_quote",{"evidence":"Every AND expression is always true."}),
                         ("wrong_locator",{"locator":"Section 2"})]:
        q=question();q.update(change)
        try:validate_question(q,source,{"Section 1":source});accepted=True
        except ValueError:accepted=False
        cases.append(dict(case=label,accepted_by_structural_validator=accepted))
    short=question();short.update(kind="short",options=[],answer="Both inputs must be true",rubric=[["both"],["true"]])
    short_result=grade(short,"It is not necessary for both inputs to be true.")
    return dict(evidence_type="constructed software audit; zero human participants",
       state_sweep=dict(class_size=n,compositions=total,mismatches=mismatches,
           substantive_action_compositions=supported_actions,
           action_compositions_crossing_completion_bands=ambiguous_actions,
           caveat="Enumeration frequencies are not estimates of real classroom frequency; thresholds are existing prototype heuristics."),
       cohort_drift=dict(first_rate=drift["topics"][0]["first_rate"],retry_rate=drift["topics"][0]["retry_rate"],
           displayed_change=drift["topics"][0]["change"],matched_change=paired_change,matched_n=len(matched),
           caveat="Even matching participants does not equate item difficulty or establish learning."),
       repeated_items=dict(unique_respondents=1,scored_answers=3,displayed_action=sparse["topics"][0]["action"]),
       source_validation=cases,short_answer=dict(overlap_hint=short_result[0],outcome=short_result[1],
           caveat="The deliberately incorrect answer includes rubric words; the application correctly requires review."),
       provenance=dict(python=platform.python_version(),
           source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'frozen').glob('*.py')}))

if __name__=="__main__":
    results=audit()
    (ROOT/'classquest_results.json').write_text(json.dumps(results,indent=2)+"\n")
    print(json.dumps(results,indent=2))
