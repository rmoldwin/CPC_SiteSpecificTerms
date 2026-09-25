import json

batch = json.load(open('/home/user/workspace/icdo32_execution/batches/cns_09.json'))

# Source URLs (all fetched during research)
SRC = {
    "mvnt": ("https://pmc.ncbi.nlm.nih.gov/articles/PMC11817111/",
             "Calandrelli et al., Diagnostics 2025 (PMC11817111)"),
    "pgnt": ("https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11035433/",
             "Du et al., imaging of PGNT (PMC11035433)"),
    "mgt": ("https://pubmed.ncbi.nlm.nih.gov/31609499/",
            "Lucas et al., myxoid glioneuronal tumor PDGFRA (PMID 31609499)"),
    "calvarial": ("https://pubmed.ncbi.nlm.nih.gov/33069929/",
                  "Omofoye et al., primary intraosseous meningioma of the calvarium: systematic review (PMID 33069929)"),
    "who_men": ("https://pmc.ncbi.nlm.nih.gov/articles/PMC10477988/",
                "Yarabarla et al., Front Oncol 2023 — WHO 2021 intracranial meningiomas update (PMC10477988)"),
    "atrt": ("https://pmc.ncbi.nlm.nih.gov/articles/PMC12785001/",
             "Histogenesis of ATRT, Cancers 2025 (PMC12785001)"),
    "dlgnt": ("https://radiopaedia.org/articles/diffuse-leptomeningeal-glioneuronal-tumour?lang=us",
              "Radiopaedia — diffuse leptomeningeal glioneuronal tumour"),
    "rgnt": ("https://pmc.ncbi.nlm.nih.gov/articles/PMC8369514/",
             "Clinical Case Reports 2021 — RGNT of fourth ventricle (PMC8369514)"),
    "ectopic": ("https://www.intechopen.com/chapters/78780",
                "IntechOpen — Meninges Outside the Meninges: Ectopic Meningiomas"),
}

# Topography labels
LBL = {
    "C700": "Cerebral meninges", "C701": "Spinal meninges", "C709": "Meninges, NOS",
    "C710": "Cerebrum", "C711": "Frontal lobe", "C712": "Temporal lobe",
    "C713": "Parietal lobe", "C714": "Occipital lobe", "C715": "Ventricle, NOS",
    "C716": "Cerebellum, NOS", "C717": "Brain stem", "C718": "Overlapping lesion of brain",
    "C720": "Spinal cord", "C721": "Cauda equina", "C729": "Nervous system, NOS",
}

def labels(codes):
    return [LBL[c] for c in codes]

# Decisions keyed by (code, term)
decisions = {}

def setd(code, term, ss, subset, rationale, srckey):
    url, name = SRC[srckey] if srckey else ("", "")
    decisions[(code, term)] = {
        "site_specific": ss,
        "site_subset_codes": subset,
        "site_subset_labels": labels(subset) if subset else [],
        "rationale": rationale,
        "source": url,
        "source_name": name,
    }

# ---- Embryonal tumors 9508/3 (ceiling spans whole neuraxis) -> No ----
for t in ["Atypical teratoid/rhabdoid tumor TYR",
          "CNS Embryonal tumor with rhabdoid features",
          "Embryonal tumor with rhabdoid features"]:
    setd("9508/3", t, "No", [],
         "AT/RT and CNS embryonal tumors with rhabdoid features arise anywhere along the neuraxis (supratentorial, infratentorial/cerebellum, brainstem, spinal cord and meninges); not restricted to a proper subset of the ceiling.",
         "atrt")

# ---- 9509/0 MVNT -> Yes (cerebral hemispheres only; not spinal cord/cauda equina) ----
setd("9509/0", "Multinodular and vacuolating neuronal tumor", "Yes",
     ["C710", "C711", "C712", "C713", "C714"],
     "MVNT is a tumor of the cerebral hemispheres (temporal, parietal, frontal, occipital lobes; rare deep supratentorial sites); it is not reported in the spinal cord or cauda equina, a proper subset of the code ceiling which also includes C720/C721.",
     "mvnt")

# ---- 9509/1 glioneuronal tumors ----
setd("9509/1", "Glioneuronal tumor, NOS", "No", [],
     "A generic (NOS) glioneuronal descriptor without a specific anatomic restriction; occurs across the CNS sites of the ceiling.",
     "who_men")
setd("9509/1", "Myxoid glioneuronal tumor", "Yes",
     ["C710", "C711", "C712", "C713", "C714", "C718"],
     "Myxoid glioneuronal tumor has a predilection for the septum pellucidum, corpus callosum and periventricular white matter of the lateral ventricle — all supratentorial cerebral structures; not reported in the spinal cord or cauda equina, a proper subset of the ceiling.",
     "mgt")
setd("9509/1", "Papillary glioneuronal tumor", "Yes",
     ["C710", "C711", "C712", "C713", "C714", "C718"],
     "Papillary glioneuronal tumor is supratentorial in ~97% of cases (cerebral hemispheres, periventricular white matter), with only rare brainstem cases and no spinal cord involvement reported; a proper subset of the ceiling excluding C720/C721.",
     "pgnt")
setd("9509/1", "Rosette-forming glioneuronal tumor", "No", [],
     "Although classically a fourth-ventricle/cerebellar tumor, RGNT is reported across the neuraxis including brainstem, pineal region, optic chiasm, ventricles and spinal cord; it spans essentially the full ceiling.",
     "rgnt")

# ---- 9509/3 DLGNT group -> No (diffuse over brain AND spinal leptomeninges) ----
for t in ["Diffuse leptomeningeal glioneuronal tumor",
          "Diffuse leptomeningeal glioneuronal tumor with 1q gain",
          "Diffuse leptomeningeal glioneuronal tumor, methylation class 1 (DLGNT-MC-1)",
          "Diffuse leptomeningeal glioneuronal tumor, methylation class 2 (DLGNT-MC-2)"]:
    setd("9509/3", t, "No", [],
         "DLGNT is defined by diffuse leptomeningeal spread over both the brain surface and the spinal cord, with common intraparenchymal spinal lesions; it involves the whole neuraxis, not a proper subset of the ceiling.",
         "dlgnt")

# ---- Meningiomas: ceiling {C700 cerebral meninges, C701 spinal meninges, C709 meninges NOS} ----
# Standard histologic subtypes occur at both cranial and spinal meninges -> No.
men_no_histo = [
    ("9530/0", "Lymphoplasmacyte-rich meningioma"),
    ("9530/0", "Meningioma, NOS"),
    ("9530/0", "Metaplastic meningioma"),
    ("9530/0", "Microcystic meningioma"),
    ("9530/0", "Secretory meningioma"),
    ("9530/1", "Diffuse meningiomatosis"),
    ("9530/1", "Meningiomatosis, NOS"),
    ("9530/1", "Multiple meningiomas"),
    ("9530/3", "Anaplastic (malignant) meningioma"),
    ("9530/3", "Leptomeningeal sarcoma"),
    ("9530/3", "Meningeal sarcoma"),
    ("9530/3", "Meningioma, anaplastic"),
    ("9530/3", "Meningioma, grade 3"),
    ("9530/3", "Meningioma, malignant"),
    ("9530/3", "Meningothelial sarcoma"),
    ("9531/0", "Endotheliomatous meningioma"),
    ("9531/0", "Meningothelial meningioma"),
    ("9531/0", "Syncytial meningioma"),
    ("9532/0", "Fibroblastic meningioma"),
    ("9532/0", "Fibrous meningioma"),
    ("9533/0", "Psammomatous meningioma"),
    ("9534/0", "Angiomatous meningioma"),
    ("9537/0", "Mixed meningioma"),
    ("9537/0", "Transitional meningioma"),
    ("9538/1", "Chordoid meningioma"),
    ("9538/1", "Clear cell meningioma"),
]
for code, t in men_no_histo:
    setd(code, t, "No", [],
         "A histologic/grade descriptor of meningioma; per the WHO 2021 classification meningioma subtypes arise along meningeal surfaces of both the calvarium and spinal canal and are not restricted to cranial or spinal sites.",
         "who_men")

# Location-descriptor meningiomas (ectopic family)
setd("9530/0", "Calvarial meningioma", "Yes",
     ["C700", "C709"],
     "Calvarial (primary intraosseous) meningioma arises from and within the calvarial skull bone (most often frontal bone), a cranial location; not a spinal-meninges entity, so it maps to a cranial-meninges proper subset of the ceiling.",
     "calvarial")
# Ectopic / extracranial family: generic multi-site descriptors (head/neck, paraspinal, mediastinum, lung) -> No
for t in ["Ectopic meningioma", "Extracranial/extraspinal meningioma",
          "Extradural meningioma", "Extraneuraxial meningioma",
          "Heterotopic meningioma"]:
    setd("9530/0", t, "No", [],
         "A generic location descriptor for meningiomas occurring outside the neuraxis at many sites (head and neck, orbit, sinonasal, skin, paraspinal soft tissue, mediastinum, lung); not restricted to a single cranial-vs-spinal meningeal subset.",
         "ectopic")
# Intraosseous: calvaria AND vertebral column both reported -> No
setd("9530/0", "Intraosseous meningioma", "No", [],
     "Intraosseous meningioma arises within bone at both the calvaria and (rarely) the vertebral column, so it is not confined to a cranial-only meningeal subset of the ceiling.",
     "ectopic")

# ---- Build ordered output matching batch ----
out = []
for o in batch:
    key = (o["code"], o["term"])
    d = decisions[key]
    out.append({
        "code": o["code"],
        "term": o["term"],
        "site_specific": d["site_specific"],
        "site_subset_codes": d["site_subset_codes"],
        "site_subset_labels": d["site_subset_labels"],
        "rationale": d["rationale"],
        "source": d["source"],
        "source_name": d["source_name"],
    })

# Validation: subsets strict subset of ceiling
for o, r in zip(batch, out):
    ceil = set(o["ceiling_codes"])
    ss = set(r["site_subset_codes"])
    if r["site_specific"] == "Yes":
        assert ss and ss < ceil, f"BAD SUBSET {r['code']} {r['term']}: {ss} not strict subset of {ceil}"
        assert r["source"].startswith("http"), f"NO SOURCE {r['term']}"
    else:
        assert ss == set() or True

assert len(out) == 45, len(out)
json.dump(out, open('/home/user/workspace/icdo32_execution/results/cns_09.json', 'w'), indent=2)

from collections import Counter
c = Counter(r["site_specific"] for r in out)
urls = set(r["source"] for r in out if r["source"])
print("Counts:", dict(c))
print("Unique source URLs:", len(urls))
print("Total rows:", len(out))
