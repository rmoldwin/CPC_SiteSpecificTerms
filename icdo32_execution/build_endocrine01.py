import json

batch = json.load(open('/home/user/workspace/icdo32_execution/batches/endocrine_01.json'))

LAB = {
    "C751": "Pituitary gland",
    "C752": "Craniopharyngeal duct",
    "C753": "Pineal gland",
    "C529": "Vagina",
    "C530": "Endocervix",
    "C531": "Exocervix",
    "C538": "Overlapping lesion of cervix uteri",
    "C539": "Cervix uteri, NOS",
}

# WHO Blue Book Endocrine & Neuroendocrine Tumours 5th ed contents page
WHO_URL = "https://whobluebooks.iarc.who.int/structures/endocrine-and-neuroendocrine-tumours/"
WHO_NAME = "WHO Classification of Tumours 5th ed, Endocrine and Neuroendocrine Tumours (pituitary gland section)"
STATPEARLS_URL = "https://www.ncbi.nlm.nih.gov/books/NBK554451/"
STATPEARLS_NAME = "Pituitary Adenoma, StatPearls (NCBI Bookshelf)"
WHO_PIT_REV_URL = "https://pubmed.ncbi.nlm.nih.gov/35291028/"
WHO_PIT_REV_NAME = "Overview of the 2022 WHO Classification of Pituitary Tumors, PubMed PMID 35291028"
EYEWIKI_URL = "https://eyewiki.org/Pituitary_Adenoma"
EYEWIKI_NAME = "Pituitary Adenoma, EyeWiki (AAO) - acidophil/basophil/chromophobe tinctorial classification"
PITBLAST_URL = "https://pmc.ncbi.nlm.nih.gov/articles/PMC4129448/"
PITBLAST_NAME = "Pituitary blastoma: DICER1 syndrome, Acta Neuropathologica (PMC4129448)"
GCC_URL = "https://pmc.ncbi.nlm.nih.gov/articles/PMC8799286/"
GCC_NAME = "Glassy cell carcinoma of cervix, Translational Cancer Research (PMC8799286)"

# Pituitary gland (C751) rationale: anterior pituitary/adenohypophysis; craniopharyngeal
# duct (C752) is a distinct structure where craniopharyngioma, not pituitary adenoma, arises.
PIT_SUBSET = ["C751"]
PIT_LABELS = ["Pituitary gland"]

def pit_result(code, term, source, sname, rat):
    return {
        "code": code, "term": term, "site_specific": "Yes",
        "site_subset_codes": PIT_SUBSET, "site_subset_labels": PIT_LABELS,
        "rationale": rat, "source": source, "source_name": sname,
    }

def no_result(code, term, rat):
    return {
        "code": code, "term": term, "site_specific": "No",
        "site_subset_codes": [], "site_subset_labels": [],
        "rationale": rat, "source": "", "source_name": "",
    }

# Map (code, term) -> decision
pit_rat = ("A pituitary neuroendocrine tumour/adenoma of the adenohypophysis (anterior pituitary gland, C751); "
           "the craniopharyngeal duct (C752) in the code ceiling is a distinct structure that gives rise to "
           "craniopharyngioma, not to this entity, so use is restricted to the pituitary gland proper.")

acidophil_rat = ("Acidophil/eosinophil adenoma is a classic tinctorial category of anterior-pituitary (adenohypophyseal, "
                 "C751) adenomas (e.g. somatotroph/lactotroph tumours); it is not a craniopharyngeal-duct (C752) entity, "
                 "so it is restricted to the pituitary gland within the ceiling.")

chromophobe_rat = ("Chromophobe adenoma/carcinoma is a classic tinctorial category of anterior-pituitary "
                   "(adenohypophyseal, C751) tumours; it is not a craniopharyngeal-duct (C752) lesion, so it is "
                   "restricted to the pituitary gland within the ceiling.")

pitblast_rat = ("Pituitary blastoma is a rare early-childhood tumour of the pituitary gland (C751) associated with "
                "DICER1; it does not arise from the craniopharyngeal duct (C752), so it is restricted to the pituitary "
                "gland within the ceiling. 'Pituitary embryoma' is a synonym.")

decisions = {}

# 8005/0 Clear cell tumor, NOS -- generic descriptor
decisions[("8005/0","Clear cell tumor, NOS")] = no_result("8005/0","Clear cell tumor, NOS",
    "Generic non-specific morphologic descriptor ('clear cell tumor, NOS') with no literature evidence restricting it to a proper subset of its two-site endocrine ceiling.")

# 8010/0 Epithelial tumor, benign -- generic
decisions[("8010/0","Epithelial tumor, benign")] = no_result("8010/0","Epithelial tumor, benign",
    "Generic non-specific descriptor for a benign epithelial neoplasm; no literature basis for restricting it to a proper subset of the ceiling.")

# 8011/3 Epithelioma NOS / malignant -- generic multi-site
decisions[("8011/3","Epithelioma, NOS")] = no_result("8011/3","Epithelioma, NOS",
    "Generic synonym for carcinoma/epithelial malignancy used across many organs; not restricted to any proper subset of the 19-site ceiling.")
decisions[("8011/3","Epithelioma, malignant")] = no_result("8011/3","Epithelioma, malignant",
    "Generic synonym for malignant epithelial neoplasm used across many organs; not restricted to any proper subset of the 19-site ceiling.")

# 8015/3 Glassy cell carcinoma -> Yes, female genital subset present in ceiling
decisions[("8015/3","Glassy cell carcinoma")] = {
    "code":"8015/3","term":"Glassy cell carcinoma","site_specific":"Yes",
    "site_subset_codes":["C529","C530","C531","C538","C539"],
    "site_subset_labels":["Vagina","Endocervix","Exocervix","Overlapping lesion of cervix uteri","Cervix uteri, NOS"],
    "rationale":("Glassy cell carcinoma is defined in the literature as a rare poorly-differentiated adenosquamous "
                 "carcinoma of the female genital tract, overwhelmingly the uterine cervix (rarely endometrium/vagina). "
                 "Within its broad 24-site ceiling only the female-genital codes apply, i.e. cervix and vagina, a proper subset."),
    "source":GCC_URL,"source_name":GCC_NAME}

# 8140/0 group -- ceiling {C751,C752}
c8140_0 = {
 "Adenoma, NOS":"Generic descriptor 'adenoma, NOS'; no literature restricting it to a proper subset of the endocrine ceiling.",
 "Bartholin gland adenoma":"Bartholin gland adenoma is a vulvar (Bartholin gland) lesion; its literature site (vulva) is not within the endocrine ceiling (C751/C752), so no supported restriction to a proper subset of the ceiling can be asserted.",
 "Bronchiolar adenoma":"Bronchiolar adenoma is a peripheral lung tumour; its literature site (lung) is not within the endocrine ceiling, so no supported restriction to a proper subset of the ceiling can be asserted.",
 "Bronchiolar adenoma/ciliated muconodular papillary tumor":"Bronchiolar adenoma / ciliated muconodular papillary tumour is a peripheral lung entity; its literature site (lung) is not within the endocrine ceiling, so no supported restriction to a proper subset of the ceiling.",
 "Chief cell-predominant polyp, NOS":"Chief cell-predominant polyp is a gastric fundic/oxyntic-gland lesion; its literature site (stomach) is not within the endocrine ceiling, so no supported restriction to a proper subset of the ceiling.",
 "Chief cell-predominant polyp, low-grade":"Chief cell-predominant polyp is a gastric fundic/oxyntic-gland lesion; its literature site (stomach) is not within the endocrine ceiling, so no supported restriction to a proper subset of the ceiling.",
 "Ciliated muconodular papillary tumor":"Ciliated muconodular papillary tumour is a peripheral lung entity; its literature site (lung) is not within the endocrine ceiling, so no supported restriction to a proper subset of the ceiling.",
 "Oxyntic gland adenoma, NOS":"Oxyntic gland adenoma is a gastric (fundus/body) neoplasm; its literature site (stomach) is not within the endocrine ceiling, so no supported restriction to a proper subset of the ceiling.",
 "Oxyntic gland adenoma, low-grade":"Oxyntic gland adenoma is a gastric neoplasm; its literature site (stomach) is not within the endocrine ceiling, so no supported restriction to a proper subset of the ceiling.",
 "Oxyntic gland polyp, NOS":"Oxyntic gland polyp is a gastric fundus/body lesion; its literature site (stomach) is not within the endocrine ceiling, so no supported restriction to a proper subset of the ceiling.",
 "Oxyntic gland polyp, low-grade":"Oxyntic gland polyp is a gastric fundus/body lesion; its literature site (stomach) is not within the endocrine ceiling, so no supported restriction to a proper subset of the ceiling.",
 "Parathyroid adenoma":"Parathyroid adenoma arises in the parathyroid gland (C750), which is not within this code's ceiling (C751/C752); no restriction to a proper subset of the ceiling itself can be supported.",
 "Pyloric gland adenoma":"Pyloric gland adenoma is a gastrointestinal (gastric/duodenal/biliary) neoplasm; its literature sites are not within the endocrine ceiling, so no supported restriction to a proper subset of the ceiling.",
 "Pyloric gland adenoma, low-grade":"Pyloric gland adenoma is a gastrointestinal neoplasm; its literature sites are not within the endocrine ceiling, so no supported restriction to a proper subset of the ceiling.",
 "Pyloric gland intracystic papillary neoplasm, NOS":"Pyloric-gland intracystic papillary neoplasm is a pancreatobiliary/gastric entity; its literature sites are not within the endocrine ceiling, so no supported restriction to a proper subset of the ceiling.",
 "Pyloric gland intracystic papillary neoplasm, low-grade":"Pyloric-gland intracystic papillary neoplasm is a pancreatobiliary/gastric entity; its literature sites are not within the endocrine ceiling, so no supported restriction to a proper subset of the ceiling.",
 "Pyloric gland tubular adenoma, NOS":"Pyloric-gland tubular adenoma is a gastrointestinal neoplasm; its literature sites are not within the endocrine ceiling, so no supported restriction to a proper subset of the ceiling.",
 "Pyloric gland tubular adenoma, low-grade":"Pyloric-gland tubular adenoma is a gastrointestinal neoplasm; its literature sites are not within the endocrine ceiling, so no supported restriction to a proper subset of the ceiling.",
 "Pyloric gland-type adenoma, NOS":"Pyloric-gland-type adenoma is a gastrointestinal neoplasm; its literature sites are not within the endocrine ceiling, so no supported restriction to a proper subset of the ceiling.",
 "Pyloric gland-type adenoma, low grade":"Pyloric-gland-type adenoma is a gastrointestinal neoplasm; its literature sites are not within the endocrine ceiling, so no supported restriction to a proper subset of the ceiling.",
 "Sclerosing polycystic adenoma":"Sclerosing polycystic adenoma is a salivary-gland lesion; its literature site (salivary glands) is not within the endocrine ceiling, so no supported restriction to a proper subset of the ceiling.",
}
for term, rat in c8140_0.items():
    decisions[("8140/0",term)] = no_result("8140/0",term,rat)

# 8146/0 Monomorphic adenoma -- salivary gland term
decisions[("8146/0","Monomorphic adenoma")] = no_result("8146/0","Monomorphic adenoma",
    "Monomorphic adenoma is a salivary-gland adenoma category; its literature site (salivary glands) is not within the endocrine ceiling (C751/C752), so no restriction to a proper subset of the ceiling can be supported.")

# 8260/0 group -- ceiling {C751,C752}
c8260 = {
 "Glandular papilloma":"Glandular papilloma is a bronchial/tracheobronchial papilloma; its literature site (lung/airway) is not within the endocrine ceiling, so no supported restriction to a proper subset of the ceiling.",
 "Papillary adenoma, NOS":"Generic descriptor 'papillary adenoma, NOS'; no literature restricting it to a proper subset of the endocrine ceiling.",
 "Renal papillary adenoma":"Renal papillary adenoma is a kidney tumour (C64); its literature site is not within the endocrine ceiling (C751/C752), so no restriction to a proper subset of the ceiling can be supported.",
 "Renal tubulopapillary adenoma":"Renal tubulopapillary adenoma is a kidney tumour (C64); its literature site is not within the endocrine ceiling, so no restriction to a proper subset of the ceiling can be supported.",
 "Tubulopapillary adenoma":"Generic/renal-associated 'tubulopapillary adenoma'; no literature restricting it to a proper subset of the endocrine ceiling.",
}
for term, rat in c8260.items():
    decisions[("8260/0",term)] = no_result("8260/0",term,rat)

# 8270/0 Chromophobe adenoma -> pituitary
decisions[("8270/0","Chromophobe adenoma")] = pit_result("8270/0","Chromophobe adenoma", EYEWIKI_URL, EYEWIKI_NAME, chromophobe_rat)
# 8270/3 group -> pituitary
decisions[("8270/3","Chromophobe adenocarcinoma")] = pit_result("8270/3","Chromophobe adenocarcinoma", EYEWIKI_URL, EYEWIKI_NAME, chromophobe_rat)
decisions[("8270/3","Chromophobe adenoma of pituitary")] = pit_result("8270/3","Chromophobe adenoma of pituitary", WHO_URL, WHO_NAME,
    "Explicitly a chromophobe adenoma of the pituitary gland (adenohypophysis, C751); does not arise from the craniopharyngeal duct (C752), so it is restricted to the pituitary gland within the ceiling.")
decisions[("8270/3","Chromophobe carcinoma")] = pit_result("8270/3","Chromophobe carcinoma", EYEWIKI_URL, EYEWIKI_NAME, chromophobe_rat)

# 8271/0 Prolactinoma -> pituitary
decisions[("8271/0","Prolactinoma")] = pit_result("8271/0","Prolactinoma", WHO_PIT_REV_URL, WHO_PIT_REV_NAME,
    "Prolactinoma (lactotroph PitNET/adenoma) is a well-differentiated tumour of anterior-pituitary (adenohypophyseal, C751) cells; it does not arise from the craniopharyngeal duct (C752), so it is restricted to the pituitary gland within the ceiling.")

# 8272/0 Pituitary adenoma NOS -> pituitary
decisions[("8272/0","Pituitary adenoma, NOS")] = pit_result("8272/0","Pituitary adenoma, NOS", STATPEARLS_URL, STATPEARLS_NAME,
    "Pituitary adenoma (PitNET) is by definition a neoplasm of the anterior pituitary gland (adenohypophysis, C751); it does not arise from the craniopharyngeal duct (C752), so it is restricted to the pituitary gland within the ceiling.")

# 8273/3 Pituitary blastoma / embryoma -> pituitary
decisions[("8273/3","Pituitary blastoma")] = pit_result("8273/3","Pituitary blastoma", PITBLAST_URL, PITBLAST_NAME, pitblast_rat)
decisions[("8273/3","Pituitary embryoma")] = pit_result("8273/3","Pituitary embryoma", PITBLAST_URL, PITBLAST_NAME, pitblast_rat)

# 8280/0 Acidophil / Eosinophil adenoma -> pituitary
decisions[("8280/0","Acidophil adenoma")] = pit_result("8280/0","Acidophil adenoma", EYEWIKI_URL, EYEWIKI_NAME, acidophil_rat)
decisions[("8280/0","Eosinophil adenoma")] = pit_result("8280/0","Eosinophil adenoma", EYEWIKI_URL, EYEWIKI_NAME, acidophil_rat)
# 8280/3 group -> pituitary
decisions[("8280/3","Acidophil adenocarcinoma")] = pit_result("8280/3","Acidophil adenocarcinoma", EYEWIKI_URL, EYEWIKI_NAME, acidophil_rat)
decisions[("8280/3","Acidophil adenoma")] = pit_result("8280/3","Acidophil adenoma", EYEWIKI_URL, EYEWIKI_NAME, acidophil_rat)
decisions[("8280/3","Acidophil carcinoma")] = pit_result("8280/3","Acidophil carcinoma", EYEWIKI_URL, EYEWIKI_NAME, acidophil_rat)

# Build in batch order
out = []
missing = []
for item in batch:
    key = (item["code"], item["term"])
    if key not in decisions:
        missing.append(key)
        continue
    out.append(decisions[key])

if missing:
    raise SystemExit("MISSING decisions for: %r" % missing)

# Validate subsets are within ceiling
cmap = {(i["code"], i["term"]): set(i["ceiling_codes"]) for i in batch}
for i, d in enumerate(out):
    key = (d["code"], d["term"])
    ceil = cmap[key]
    sub = set(d["site_subset_codes"])
    if d["site_specific"] == "Yes":
        assert sub, "Yes must have subset: %r" % (key,)
        assert sub < ceil, "subset must be STRICT subset of ceiling: %r sub=%r ceil=%r" % (key, sub, ceil)
        assert d["source"].startswith("http"), "Yes needs http source: %r" % (key,)
    # length of labels matches codes
    assert len(d["site_subset_codes"]) == len(d["site_subset_labels"]), "label/code mismatch %r" % (key,)

assert len(out) == 45, "length %d != 45" % len(out)

import collections
c = collections.Counter(d["site_specific"] for d in out)
srcs = set(d["source"] for d in out if d["source"])
json.dump(out, open('/home/user/workspace/icdo32_execution/results/endocrine_01.json','w'), indent=1)
print("len", len(out))
print("counts", dict(c))
print("unique sources", len(srcs))
for s in sorted(srcs):
    print("  ", s)
