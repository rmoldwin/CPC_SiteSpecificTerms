import json

with open('/home/user/workspace/icdo32_execution/results/bone_soft_tissue_01.json') as f:
    res = json.load(f)
with open('/home/user/workspace/icdo32_execution/batches/bone_soft_tissue_01.json') as f:
    batch = json.load(f)

print("results len:", len(res), "batch len:", len(batch))

# build ceiling lookup by (code, term)
ceil = {}
for b in batch:
    ceil[(b['code'], b['term'])] = set(b['ceiling_codes'])

counts = {'Yes':0,'No':0,'Uncertain':0}
errors = []
for i,(r,b) in enumerate(zip(res,batch)):
    if r['code']!=b['code'] or r['term']!=b['term']:
        errors.append(f"[{i}] mismatch: {r['code']}|{r['term']} vs {b['code']}|{b['term']}")
    counts[r['site_specific']] = counts.get(r['site_specific'],0)+1
    c = set(b['ceiling_codes'])
    sub = set(r['site_subset_codes'])
    if r['site_specific']=='Yes':
        if not r['source'].startswith('http'):
            errors.append(f"[{i}] Yes without http source: {r['term']}")
        if not sub:
            errors.append(f"[{i}] Yes with empty subset: {r['term']}")
        if not sub.issubset(c):
            errors.append(f"[{i}] subset NOT within ceiling: {r['term']} extra={sub-c}")
        if sub==c:
            errors.append(f"[{i}] subset equals full ceiling (not proper): {r['term']}")
        if len(r['site_subset_codes'])!=len(r['site_subset_labels']):
            errors.append(f"[{i}] codes/labels length mismatch: {r['term']}")
    else:
        if sub:
            errors.append(f"[{i}] non-Yes has subset codes: {r['term']}")

print("counts:", counts)
urls = set(r['source'] for r in res if r['source'].startswith('http'))
print("unique http sources:", len(urls))
if errors:
    print("ERRORS:")
    for e in errors: print(" ", e)
else:
    print("NO ERRORS - all checks passed")
