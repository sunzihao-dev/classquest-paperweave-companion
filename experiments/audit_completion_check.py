"""Exhaustive constructed-state audit. No learner or teacher observations."""
import json
from pathlib import Path
from evidence_report import completion_check

names = ['reteach','recap','advance']
def oracle(k,n):
    # Independent integer inequalities for rounded 55/80 bands:
    # 54.5 rounds down to 54, while 79.5 rounds up to 80 (ties to even).
    return 'advance' if 200*k >= 159*n else 'recap' if 200*k > 109*n else 'reteach'

states=sensitive=monotonic_checks=0
for n in range(1,31):
    for c in range(n+1):
        for w in range(n-c+1):
            for p in range(n-c-w+1):
                m=n-c-w-p
                actual=completion_check(c,w,p,m)
                expected={oracle(k,n) for k in range(c,c+p+m+1)}
                assert actual['possible_bands']==[x for x in names if x in expected]
                assert actual['early_signal']==(c+w<3)
                sensitive+=actual['completion_sensitive']; states+=1
                # Resolving either kind of unknown cannot widen the band set.
                for pending in (True,False):
                    if (p if pending else m)==0: continue
                    for correct in (True,False):
                        after=completion_check(c+correct,w+(not correct),p-pending,m-(not pending))
                        assert set(after['possible_bands']) <= expected
                        monotonic_checks+=1

assert completion_check(0,0,0,0)['completion_sensitive'] is None
invalid=[(-1,0,0,0),(True,0,0,0),(1.0,0,0,0),('1',0,0,0)]
for args in invalid:
    try: completion_check(*args)
    except ValueError: pass
    else: raise AssertionError(args)

result=dict(evidence_type='Exhaustive synthetic software check, not educational validation',
            roster_sizes=[1,30],count_states=states,oracle_mismatches=0,
            completion_sensitive_states=sensitive,monotonic_resolution_checks=monotonic_checks,
            monotonic_violations=0,empty_roster_checked=True,invalid_inputs_rejected=len(invalid),
            rounding='Python nearest-integer ties-to-even before 55/80 thresholds',
            example=completion_check(12,3,5,10),
            limits='One binary-scored item; unknown outcomes unconstrained; thresholds are unvalidated heuristics.')
(Path(__file__).parent/'completion_check_results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
