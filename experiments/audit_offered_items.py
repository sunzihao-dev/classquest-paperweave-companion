"""Constructed audit of item opportunity; no participant data or model inference."""
from itertools import product
from pathlib import Path
import json
from audit_classquest import question, row
from frozen.analytics import build_report
from evidence_report import offered_item_summary

def audit():
    # A selected retry in one topic and an unselected retry in another.
    qs = [question(1), question(2, 'retry'), question(3, 'retry')]
    qs[2]['topic'] = 'Loops'
    responses = [row(i, 'correct', q) for i in range(3) for q in (1, 2)]
    old = build_report({'title':'Constructed opportunity example'}, qs, list(range(3)),
                       responses, room={'retry_topic':'Boolean logic'})
    unoffered = next(q for q in old['questions'] if q['id'] == 3)
    repaired = offered_item_summary(range(3), [], [])
    assert unoffered['missing'] == 3 and repaired['missing'] == 0
    # Independent assignment-level oracle: five distinct states per learner.
    states = ('not_offered', 'missing', 'needs_review', 'correct', 'incorrect')
    checked = 0
    for n in range(7):
        for assignment in product(states, repeat=n):
            offered = [i for i, s in enumerate(assignment) if s != 'not_offered']
            rows = [{'participant_id':i, 'outcome':s} for i,s in enumerate(assignment)
                    if s in ('needs_review','correct','incorrect')]
            got = offered_item_summary(range(n), offered, rows)
            expected = {'not_offered':assignment.count('not_offered'),
                        'missing':assignment.count('missing'),
                        'pending':assignment.count('needs_review'),
                        'correct':assignment.count('correct'),
                        'incorrect':assignment.count('incorrect')}
            assert all(got[k] == v for k,v in expected.items())
            assert sum(expected.values()) == got['roster_n'] == n
            assert got['offered_n'] == n-expected['not_offered']
            # Adding an unoffered learner must leave item evidence unchanged.
            larger = offered_item_summary(range(n+1), offered, rows)
            for k in ('n','respondents','scored','pending','missing','observed_accuracy',
                      'scored_coverage','completion_bounds'):
                assert larger[k] == got[k], (assignment,k)
            checked += 1
    invalid = [([0], None, []), ([0,0], [], []), ([0], [0,0], []),
               ([0], [1], []), ([0], [], [{'participant_id':0,'outcome':'correct'}]),
               ([0], [0], [{'participant_id':0,'outcome':'correct'}]*2),
               ([0], [0], [{'participant_id':0,'outcome':'unknown'}])]
    for args in invalid:
        try: offered_item_summary(*args)
        except ValueError: pass
        else: raise AssertionError(('Invalid input accepted',args))
    return {'evidence_type':'Constructed software audit; zero human participants',
            'frozen_unoffered_retry':{'reported_missing':unoffered['missing'],
                                     'actual_offered_in_scenario':0},
            'companion_unoffered_retry':repaired,
            'assignment_states_checked':checked,'roster_sizes':[0,6],
            'accounting_mismatches':0,'unoffered_extension_violations':0,
            'invalid_inputs_rejected':len(invalid),
            'limits':'Explicit offer records are required. Test enumeration is not a classroom error rate or evidence of pedagogical effectiveness.'}

if __name__ == '__main__':
    result = audit()
    Path(__file__).with_name('offered_item_results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
