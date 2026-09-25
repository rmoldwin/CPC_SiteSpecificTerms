import json

batch = json.load(open('/home/user/workspace/icdo32_execution/batches/skin_01.json'))

# Map ceiling for validation
ceil = {}
for o in batch:
    ceil[o['code']] = set(o['ceiling_codes'])

# Breast subset codes
BREAST = ["C500","C501","C502","C503","C504","C505","C506","C508","C509"]
BREAST_LABEL = "Breast"

# Sources
SRC_THYROID = "https://pmc.ncbi.nlm.nih.gov/articles/PMC9633223/"
SRC_THYROID_NAME = "Endocrinol Metab 2022 (Jung et al.) — Update from the 2022 WHO Classification of Thyroid Neoplasms"
SRC_DCIS = "https://www.cancer.org/cancer/diagnosis-staging/tests/biopsy-and-cytology-tests/understanding-your-pathology-report/breast-pathology/ductal-carcinoma-in-situ.html"
SRC_DCIS_NAME = "American Cancer Society — Understanding Your Pathology Report: Ductal Carcinoma In Situ (DCIS)"

# Decisions keyed by (code, term)
YES = {}
UNCERTAIN = {}

# 8201/3 Cribriform morular thyroid carcinoma -> thyroid, but C739 is NOT in the ceiling
# Per the locked rule, the reported subset must be a strict subset of ceiling_codes and we
# must NEVER expand beyond the ceiling. Thyroid (C739) is absent from this code's ceiling,
# so the term's true anatomic home cannot be represented -> Uncertain.
UNCERTAIN[("8201/3","Cribriform morular thyroid carcinoma")] = {
    "rationale":"The 2022 WHO Classification of Endocrine Tumours defines cribriform morular thyroid carcinoma (8201/3) as a distinct thyroid tumour, so the entity is anatomically restricted to the thyroid (C739). However C739 is not present in this code's SMVL ceiling, so the literature-supported restriction falls entirely outside the allowed sites and no valid in-ceiling subset can be reported.",
    "source":SRC_THYROID,"source_name":SRC_THYROID_NAME}

# 8201/2 Ductal carcinoma in situ, cribriform type -> breast
YES[("8201/2","Ductal carcinoma in situ, cribriform type")] = {
    "site_subset_codes":BREAST,
    "site_subset_labels":[BREAST_LABEL]*len(BREAST),
    "rationale":"Ductal carcinoma in situ (intraductal carcinoma) is, by definition, a non-invasive carcinoma confined to the breast ducts/lobules; the 'ductal' cribriform-type in situ entity is a breast lesion, a proper subset of this code's ceiling which also spans skin and eye.",
    "source":SRC_DCIS,"source_name":SRC_DCIS_NAME}

# 8230/2 Ductal carcinoma in situ, solid type -> breast
YES[("8230/2","Ductal carcinoma in situ, solid type")] = {
    "site_subset_codes":BREAST,
    "site_subset_labels":[BREAST_LABEL]*len(BREAST),
    "rationale":"Ductal carcinoma in situ, solid type is by definition a breast entity (malignant cells confined within breast ducts/lobules); it is anatomically restricted to the breast, a proper subset of this code's ceiling that also includes skin and thyroid.",
    "source":SRC_DCIS,"source_name":SRC_DCIS_NAME}

# 8230/2 Intraductal carcinoma, solid type -> breast (synonym of DCIS)
YES[("8230/2","Intraductal carcinoma, solid type")] = {
    "site_subset_codes":BREAST,
    "site_subset_labels":[BREAST_LABEL]*len(BREAST),
    "rationale":"Intraductal carcinoma is the direct synonym of ductal carcinoma in situ, a breast-duct-confined entity; the solid-type intraductal carcinoma is restricted to the breast, a proper subset of this code's ceiling that also includes skin and thyroid.",
    "source":SRC_DCIS,"source_name":SRC_DCIS_NAME}

# Uncertain: 8201/2 Cribriform carcinoma in situ (no 'ductal' qualifier; ceiling includes eye/skin)
UNCERTAIN[("8201/2","Cribriform carcinoma in situ")] = {
    "rationale":"Without a 'ductal' qualifier, 'cribriform carcinoma in situ' can denote an in-situ cribriform lesion of breast, cutaneous adnexal, or conjunctival/eye origin; published literature does not clearly restrict this exact term to a single organ within the code's skin+breast+eye ceiling.",
    "source":SRC_DCIS,"source_name":SRC_DCIS_NAME}

WHO_SKIN = "https://whobluebooks.iarc.who.int/structures/skintumours/"
WHO_SKIN_NAME = "WHO Classification of Tumours, 5th ed — Skin Tumours (IARC), Appendageal tumours chapter"

out = []
for o in batch:
    key = (o['code'], o['term'])
    if key in YES:
        d = YES[key]
        # validate subset
        assert set(d['site_subset_codes']).issubset(ceil[o['code']]), f"subset violation {key}: {set(d['site_subset_codes'])-ceil[o['code']]}"
        rec = {"code":o['code'],"term":o['term'],"site_specific":"Yes",
               "site_subset_codes":d['site_subset_codes'],
               "site_subset_labels":d['site_subset_labels'],
               "rationale":d['rationale'],"source":d['source'],"source_name":d['source_name']}
    elif key in UNCERTAIN:
        d = UNCERTAIN[key]
        rec = {"code":o['code'],"term":o['term'],"site_specific":"Uncertain",
               "site_subset_codes":[],"site_subset_labels":[],
               "rationale":d['rationale'],"source":d['source'],"source_name":d['source_name']}
    else:
        # No — skin adnexal tumor used across its skin-bearing ceiling, or generic descriptor
        rec = {"code":o['code'],"term":o['term'],"site_specific":"No",
               "site_subset_codes":[],"site_subset_labels":[],
               "rationale":"WHO 5th ed Skin Tumours defines this as a cutaneous appendageal (adnexal) carcinoma; the term is applied across all skin-bearing sites in this code's ceiling (skin +/- lip/genital skin/breast) rather than a proper anatomic subset. Generic/growth-pattern descriptors are likewise not site-restricted.",
               "source":WHO_SKIN,"source_name":WHO_SKIN_NAME}
    out.append(rec)

assert len(out)==45, len(out)
json.dump(out, open('/home/user/workspace/icdo32_execution/results/skin_01.json','w'), indent=2)

from collections import Counter
c = Counter(r['site_specific'] for r in out)
print("counts:", dict(c))
print("length:", len(out))
