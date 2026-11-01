"""Research companion: descriptive evidence fields, not validated pedagogy.
This is deliberately separate from the existing ClassQuest application.
"""

from fractions import Fraction

def completion_check(correct, incorrect, pending, missing):
    """Expose sensitivity of the frozen report's rounded 55/80 bands.

    Exactly one item, one known roster, and non-negative integer counts.
    Unknown responses are allowed either binary outcome; none is imputed.
    A stable band does not validate the item, grading or pedagogical action.
    """
    values = (correct, incorrect, pending, missing)
    if any(type(v) is not int or v < 0 for v in values):
        raise ValueError('Counts must be non-negative integers')
    n = sum(values)
    if not n:
        return dict(n=0, possible_bands=[], completion_sensitive=None,
                    early_signal=True, completion_bounds=None)
    def band(k):
        # Python ties-to-even rounding, as in the frozen implementation.
        rate = round(Fraction(100*k, n))
        return 0 if rate < 55 else 1 if rate < 80 else 2
    low, high = correct, correct + pending + missing
    names = ['reteach', 'recap', 'advance']
    # With small rosters, consecutive attainable totals can skip a band.
    bands = [names[i] for i in sorted({band(k) for k in range(low,high+1)})]
    return dict(n=n, possible_bands=bands, completion_sensitive=len(bands)>1,
                early_signal=correct+incorrect<3,
                completion_bounds=[low/n,high/n])

def item_summary(roster, rows):
    """One response per participant to ONE item. Reject duplicates/unlisted IDs."""
    roster=set(roster); seen=set(); counts={'correct':0,'incorrect':0,'needs_review':0}
    for r in rows:
        pid=r['participant_id']
        if pid not in roster or pid in seen:
            raise ValueError('Expected a unique, rostered participant for each response')
        seen.add(pid);counts[r['outcome']]+=1
    n=len(roster); c=counts['correct'];w=counts['incorrect'];p=counts['needs_review'];m=n-len(seen)
    return dict(n=n,respondents=len(seen),scored=c+w,correct=c,incorrect=w,pending=p,missing=m,
       observed_accuracy=c/(c+w) if c+w else None,
       scored_coverage=(c+w)/n if n else None,
       completion_bounds=[c/n,(c+p+m)/n] if n else None,
       interpretation='Bounds describe possible completion of this item; not mastery or a confidence interval.')

def paired_retry(first,retry):
    """Compare exact participant IDs for one first/retry item pair."""
    def index(rows):
        result={}
        seen=set()
        for r in rows:
            pid=r['participant_id']
            if pid in seen:raise ValueError('Duplicate participant in item pair')
            seen.add(pid)
            if r['outcome'] in ('correct','incorrect'):result[pid]=r['outcome']=='correct'
        return result
    a,b=index(first),index(retry);common=set(a)&set(b)
    return dict(matched_n=len(common),first_only_n=len(set(a)-set(b)),retry_only_n=len(set(b)-set(a)),
        matched_change_pp=100*sum(int(b[x])-int(a[x]) for x in common)/len(common) if common else None,
        interpretation='Descriptive paired change; item equivalence and causal learning are unestablished.')

def offered_item_summary(roster, offered, rows):
    """Summarise ONE item using explicit opportunity-to-respond records.

    Offered means the item was made available, not that it was read. None is
    unknown exposure and must not be inferred from the observed responses.
    The caller supplies one unique roster and the subset offered this item.
    """
    if offered is None:
        raise ValueError('An explicit offered set is required; exposure is unknown')
    roster, offered = list(roster), list(offered)
    if len(set(roster)) != len(roster) or len(set(offered)) != len(offered):
        raise ValueError('Roster and offered IDs must be unique')
    if not set(offered) <= set(roster):
        raise ValueError('Offered IDs must belong to the roster')
    rows = list(rows)
    if any(r['outcome'] not in ('correct', 'incorrect', 'needs_review') for r in rows):
        raise ValueError('Unsupported outcome')
    result = item_summary(offered, rows)
    result.update(roster_n=len(roster), offered_n=len(offered),
                  not_offered=len(roster)-len(offered),
                  interpretation='Coverage and completion bounds concern only learners offered this item; offer does not prove access, reading or learning.')
    return result
