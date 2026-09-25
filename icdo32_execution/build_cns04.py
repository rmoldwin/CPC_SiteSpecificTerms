import json

batch = json.load(open('/home/user/workspace/icdo32_execution/batches/cns_04.json'))

LBL = {
 "C700":"Cerebral meninges","C701":"Spinal meninges","C709":"Meninges NOS",
 "C710":"Cerebrum","C711":"Frontal lobe","C712":"Temporal lobe","C713":"Parietal lobe",
 "C714":"Occipital lobe","C715":"Ventricle","C716":"Cerebellum","C717":"Brain stem",
 "C718":"Overlapping brain","C719":"Brain NOS","C720":"Spinal cord","C721":"Cauda equina",
 "C722":"Olfactory nerve","C723":"Optic nerve","C724":"Acoustic nerve","C725":"Cranial nerve NOS",
 "C728":"Overlapping CNS","C729":"Nervous system NOS","C751":"Pituitary gland",
 "C752":"Craniopharyngeal duct","C753":"Pineal gland",
}

# Sources
SRC_CRANIO = "https://www.ncbi.nlm.nih.gov/books/NBK538819/"
SRC_CRANIO_NAME = "Endotext: Craniopharyngiomas (NBK538819)"
SRC_PINEAL = "https://pmc.ncbi.nlm.nih.gov/articles/PMC8036741/"
SRC_PINEAL_NAME = "Pineal Gland Tumors: A Review, PMC8036741"
SRC_SUBEP = "https://pmc.ncbi.nlm.nih.gov/articles/PMC4618470/"
SRC_SUBEP_NAME = "Neurological Research subependymoma series, PMC4618470"

def labels(codes):
    return [LBL[c] for c in codes]

def obj(code, term, ss, subset=None, rationale="", source="", source_name=""):
    d = {"code":code, "term":term, "site_specific":ss}
    if ss == "Yes":
        d["site_subset_codes"] = subset
        d["site_subset_labels"] = labels(subset)
    else:
        d["site_subset_codes"] = []
        d["site_subset_labels"] = []
    d["rationale"] = rationale
    d["source"] = source
    d["source_name"] = source_name
    return d

# Decision map keyed by (code, term)
def decide(code, term, ceiling):
    t = term.lower()
    # 9350/1, 9351/1 craniopharyngioma family -> sellar/craniopharyngeal duct (C751,C752)
    if code in ("9350/1","9351/1"):
        subset = [c for c in ["C751","C752"] if c in ceiling]
        return ("Yes", subset,
            "Craniopharyngiomas (incl. adamantinomatous and Rathke pouch origin) arise almost exclusively along the craniopharyngeal duct/Rathke pouch in the sellar-suprasellar (pituitary) region, not diffusely in the cerebral lobes that the code's ceiling also permits.",
            SRC_CRANIO, SRC_CRANIO_NAME)
    # 9362/3 pineal parenchymal tumors -> pineal gland (C753)
    if code == "9362/3":
        subset = [c for c in ["C753"] if c in ceiling]
        return ("Yes", subset,
            "Pineal parenchymal tumors (pineocytoma/pineoblastoma spectrum and mixed/transitional pineal tumors) arise from pineocytes in the pineal gland, a proper subset of the ceiling, which also includes cranial nerves (C722-C725).",
            SRC_PINEAL, SRC_PINEAL_NAME)
    # 9383/1 subependymoma family -> ventricular system + spinal cord/central canal
    if code == "9383/1":
        subset = [c for c in ["C715","C720","C721"] if c in ceiling]
        return ("Yes", subset,
            "Subependymomas (and synonyms subependymal astrocytoma/glioma, and mixed subependymoma-ependymoma) arise in the ependymal-lined ventricular system (esp. 4th and lateral ventricles) and the spinal cord central canal, not within cerebral-lobe parenchyma; this is a proper subset of the code's ceiling.",
            SRC_SUBEP, SRC_SUBEP_NAME)
    return None

results = []
for c in batch:
    code = c["code"]; term = c["term"]; ceiling = c["ceiling_codes"]
    d = decide(code, term, ceiling)
    if d:
        ss, subset, rat, src, srcname = d
        # sanity: subset must be non-empty strict subset
        assert subset and set(subset).issubset(set(ceiling)) and len(subset) < len(ceiling), (code, term, subset)
        results.append(obj(code, term, ss, subset, rat, src, srcname))
    else:
        # Default No with rationale by category
        if code == "9131/0":
            rat = "Cutaneous/soft-tissue vascular lesion (hemangioma/pyogenic granuloma variant) whose usual sites are not within the CNS ceiling assigned to this code; no literature restricts it to a proper subset of the code's CNS ceiling, so not site-specific within the ceiling."
        elif code == "9161/1" and "lung" in term.lower():
            rat = "This is described as a lung tumor (hemangioblastoma-like clear cell stromal tumor of lung); its site (lung) is not among the CNS ceiling codes, so no valid proper subset of the ceiling can be reported."
        elif code == "9161/1":
            rat = "Hemangioblastoma/angioblastoma occurs throughout the CNS (cerebellum, brainstem, spinal cord, supratentorial, meninges, cranial nerves); a predilection for cerebellum/spinal cord is not an anatomic restriction, so it is not confined to a proper subset of the ceiling."
        elif code == "9380/1" or code == "9380/3":
            rat = "Generic glioma descriptor (NOS / grade / low- or high-grade) with no specific anatomic restriction; gliomas occur across the CNS sites in the ceiling."
        elif code == "9381/3":
            rat = "Gliomatosis cerebri denotes a diffuse, widely infiltrative growth pattern involving multiple CNS regions rather than a restricted single subsite; not confined to a proper subset of the ceiling."
        elif code == "9384/1":
            rat = "Retinal astrocytoma / astrocytic hamartoma of retina is a retinal (eye, C69) lesion; the retina is not among this code's CNS ceiling codes, so no valid proper subset of the ceiling can be reported."
        else:
            rat = "No published evidence restricts this term to a proper subset of the code's ceiling sites."
        results.append(obj(code, term, "No", None, rat, "", ""))

# validate length
assert len(results) == len(batch) == 45, len(results)

# validate every Yes has source + strict subset
for r in results:
    if r["site_specific"] == "Yes":
        assert r["source"].startswith("http"), r
        assert r["site_subset_codes"], r

import collections
cnt = collections.Counter(r["site_specific"] for r in results)
print("Counts:", dict(cnt))
srcs = set(r["source"] for r in results if r["source"])
print("Distinct source URLs:", len(srcs))

json.dump(results, open('/home/user/workspace/icdo32_execution/results/cns_04.json','w'), indent=1)
print("written", len(results))
