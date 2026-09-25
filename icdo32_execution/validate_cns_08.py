import json

with open('/home/user/workspace/icdo32_execution/batches/cns_08.json') as f:
    batch = json.load(f)
with open('/home/user/workspace/icdo32_execution/results/cns_08.json') as f:
    res = json.load(f)

ceil = {}
for b in batch:
    ceil[(b['code'], b['term'])] = set(b['ceiling_codes'])

print("batch len:", len(batch), "result len:", len(res))
assert len(res) == 45, "length mismatch"

yes=no=unc=0
srcs=set()
for r in res:
    key=(r['code'], r['term'])
    assert key in ceil, f"unknown term {key}"
    ss = r['site_specific']
    if ss=='Yes':
        yes+=1
        sub=set(r['site_subset_codes'])
        c=ceil[key]
        assert sub, f"empty subset for Yes {key}"
        assert sub < c, f"NOT strict subset {key}: {sub} vs {c}"
        assert r['source'].startswith('http'), f"Yes without http source {key}"
        assert len(r['site_subset_codes'])==len(r['site_subset_labels']), f"len mismatch labels {key}"
        srcs.add(r['source'])
    elif ss=='No':
        no+=1
    elif ss=='Uncertain':
        unc+=1
    else:
        raise Exception("bad value "+ss)
    if r.get('source','').startswith('http'):
        srcs.add(r['source'])

# check every batch term present exactly
from collections import Counter
bc=Counter((b['code'],b['term']) for b in batch)
rc=Counter((r['code'],r['term']) for r in res)
assert bc==rc, "term set mismatch"

print(f"Yes={yes} No={no} Uncertain={unc}")
print(f"Unique http sources: {len(srcs)}")
for s in sorted(srcs):
    print(" ", s)
print("ALL VALIDATION PASSED")
