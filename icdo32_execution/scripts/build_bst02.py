import json, os

BATCH="/home/user/workspace/icdo32_execution/batches/bone_soft_tissue_02.json"
OUT="/home/user/workspace/icdo32_execution/results/bone_soft_tissue_02.json"

batch=json.load(open(BATCH))
by=lambda i:batch[i]

def ceil(i): return batch[i]['ceiling_codes']

# Label map for C-codes we use
LABELS={
 'C400':'Long bones of upper limb','C401':'Short bones of upper limb','C402':'Long bones of lower limb',
 'C403':'Short bones of lower limb','C408':'Overlapping bones/joints of limbs','C409':'Bone of limb, NOS',
 'C410':'Bones of skull and face','C411':'Mandible','C412':'Vertebral column','C413':'Rib/sternum/clavicle',
 'C414':'Pelvic bones/sacrum/coccyx','C418':'Overlapping bones/joints','C419':'Bone, NOS',
 'C480':'Retroperitoneum','C488':'Overlapping peritoneum/retroperitoneum',
 'C490':'Connective tissue head/neck','C491':'Connective tissue upper limb','C492':'Connective tissue lower limb',
 'C493':'Connective tissue thorax','C494':'Connective tissue abdomen','C495':'Connective tissue pelvis',
 'C496':'Connective tissue trunk','C498':'Overlapping connective tissue','C499':'Connective tissue, NOS',
 'C649':'Kidney, NOS',
}
def labels(codes): return [LABELS.get(c,c) for c in codes]

# Default all "No"
results=[]
for o in batch:
    results.append({
        "code":o['code'],"term":o['term'],"site_specific":"No",
        "site_subset_codes":[],"site_subset_labels":[],
        "rationale":"Generic soft tissue/bone sarcoma morphology used across all anatomic sites in the code's ceiling; no literature-supported restriction to a proper subset.",
        "source":"","source_name":""
    })

BONE=['C400','C401','C402','C403','C408','C409','C410','C411','C412','C413','C414','C418','C419']

# --- 8830/3 index 6: UPS of bone -> Yes (bone) ---
i=6; c=ceil(i); sub=[x for x in BONE if x in c]
results[i].update({
 "site_specific":"Yes","site_subset_codes":sub,"site_subset_labels":labels(sub),
 "rationale":"'Undifferentiated high-grade pleomorphic sarcoma of bone' is the renamed 'malignant fibrous histiocytoma of bone' and is classified specifically among mesenchymal tumours of bone in the WHO 5th ed bone volume; the term is defined as a primary bone entity, a proper subset of the code's ceiling (which also spans skin and soft tissue).",
 "source":"https://radiopaedia.org/articles/who-classification-of-tumours-of-bone",
 "source_name":"WHO Classification of Tumours of Bone 5th ed (Radiopaedia summary); JSTAGE J Oral Dis Maxillofac review"
})

# --- 8963/3 rhabdoid group. ceiling: C480,C488,C49*,C649 ---
# index 40 ATRT of kidney -> Yes kidney
i=40; c=ceil(i); sub=['C649']
results[i].update({
 "site_specific":"Yes","site_subset_codes":sub,"site_subset_labels":labels(sub),
 "rationale":"Term is explicitly the kidney rhabdoid entity (rhabdoid tumour of the kidney, RTK); restricted to kidney (C649), a proper subset of the ceiling which also includes retroperitoneum/peritoneum and soft tissue.",
 "source":"https://pmc.ncbi.nlm.nih.gov/articles/PMC6087667/",
 "source_name":"Geller et al., Biology and Treatment of Rhabdoid Tumor, PMC6087667"
})
# index 41 Extrarenal rhabdoid tumor -> Yes non-kidney soft tissue
i=41; c=ceil(i); sub=[x for x in c if x!='C649']
results[i].update({
 "site_specific":"Yes","site_subset_codes":sub,"site_subset_labels":labels(sub),
 "rationale":"By definition 'extrarenal' rhabdoid tumour arises outside the kidney, in soft tissue/retroperitoneum/peritoneum; excludes the kidney (C649), i.e. a proper subset of the ceiling.",
 "source":"https://pmc.ncbi.nlm.nih.gov/articles/PMC6087667/",
 "source_name":"Geller et al., Biology and Treatment of Rhabdoid Tumor, PMC6087667"
})
# index 42 Malignant rhabdoid tumor (NOS) -> No (all sites incl kidney & soft tissue)
results[42]['rationale']="Generic malignant rhabdoid tumour occurs across renal, retroperitoneal, peritoneal and soft-tissue sites; not restricted to a proper subset of the ceiling."
results[42]['source']="https://pmc.ncbi.nlm.nih.gov/articles/PMC6087667/"
results[42]['source_name']="Geller et al., Biology and Treatment of Rhabdoid Tumor, PMC6087667"
# index 43 Malignant rhabdoid tumor of the kidney -> Yes kidney
i=43; sub=['C649']
results[i].update({
 "site_specific":"Yes","site_subset_codes":sub,"site_subset_labels":labels(sub),
 "rationale":"Term is explicitly the kidney form (rhabdoid tumour of the kidney); restricted to kidney (C649), a proper subset of the ceiling which also spans retroperitoneum/peritoneum and soft tissue.",
 "source":"https://pmc.ncbi.nlm.nih.gov/articles/PMC6087667/",
 "source_name":"Geller et al., Biology and Treatment of Rhabdoid Tumor, PMC6087667"
})
# index 44 Rhabdoid sarcoma -> No (generic synonym)

# --- 8842/3 pulmonary myxoid sarcoma terms (indices 11-15): lung-specific but lung NOT in ceiling ---
ppms_idx=[11,12,13,14,15]
for i in ppms_idx:
    results[i].update({
     "site_specific":"Uncertain",
     "site_subset_codes":[],"site_subset_labels":[],
     "rationale":"Primary pulmonary myxoid sarcoma is a lung-specific mesenchymal neoplasm (WHO 2021 Thoracic Tumours), but the code's SMVL ceiling contains only connective/soft-tissue sites (C49*) and no lung code, so the literature-supported lung restriction cannot be expressed as a subset of this ceiling.",
     "source":"https://pmc.ncbi.nlm.nih.gov/articles/PMC12885817/",
     "source_name":"AME Case Reports 2026 (PPMS, WHO 2021 lung-specific mesenchymal neoplasm)"
    })
# index 10 Ossifying fibromyxoid tumor malignant -> No (soft tissue, spans C49 ceiling)

os.makedirs(os.path.dirname(OUT),exist_ok=True)
json.dump(results,open(OUT,'w'),indent=2)

# validate subsets
for r in results:
    if r['site_specific']=="Yes":
        cc=next(o['ceiling_codes'] for o in batch if o['code']==r['code'] and o['term']==r['term'])
        assert set(r['site_subset_codes']).issubset(set(cc)), r['term']
        assert set(r['site_subset_codes'])!=set(cc), "not proper subset: "+r['term']
        assert r['source'].startswith('http'), r['term']
        assert len(r['site_subset_codes'])>0, r['term']

from collections import Counter
cnt=Counter(r['site_specific'] for r in results)
srcs=set(r['source'] for r in results if r['source'])
print("LEN",len(results))
print(cnt)
print("unique sources:",len(srcs))
for i,r in enumerate(results):
    if r['site_specific']!="No": print(i,r['site_specific'],r['code'],r['term'],r['site_subset_codes'])
