"""Research companion: descriptive evidence fields, not validated pedagogy.
This is deliberately separate from the existing ClassQuest application.
"""

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
