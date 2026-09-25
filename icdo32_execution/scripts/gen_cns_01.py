import json

batch = json.load(open('/home/user/workspace/icdo32_execution/batches/cns_01.json'))

# Sources
SRC_WHO_LEPTO = "https://www.por-journal.com/journals/pathology-and-oncology-research/articles/10.3389/pore.2023.1611482/full"
SRC_WHO_LEPTO_NAME = "WHO CNS5 (2021) primary leptomeningeal melanocytic tumors / Pathol Oncol Res 2023"
SRC_MELANOCYTOMA = "https://pmc.ncbi.nlm.nih.gov/articles/PMC11274408/"
SRC_MELANOCYTOMA_NAME = "Cancers 2024, Primary Meningeal Melanocytic Tumors of the CNS (WHO CNS5)"
SRC_SFT = "https://pmc.ncbi.nlm.nih.gov/articles/PMC8057625/"
SRC_SFT_NAME = "Brain Pathology 2011 / WHO CNS classification - Solitary Fibrous Tumors and Hemangiopericytomas of the Meninges"

MEN = ["C700", "C701", "C709"]
MEN_LABELS = ["Cerebral meninges", "Spinal meninges", "Meninges, NOS"]

def obj(code, term, ss, codes=None, labels=None, rationale="", source="", source_name=""):
    return {
        "code": code,
        "term": term,
        "site_specific": ss,
        "site_subset_codes": codes or [],
        "site_subset_labels": labels or [],
        "rationale": rationale,
        "source": source,
        "source_name": source_name,
    }

# Decision map keyed by (code, term)
decisions = {}

# ---- Generic NOS descriptors (8000/8001) -> No ----
generic_8000 = [
    ("8000/0", "Neoplasm, benign"),
    ("8000/0", "Tumor, benign"),
    ("8000/0", "Unclassified tumor, benign"),
    ("8000/1", "Neoplasm, NOS"),
    ("8000/1", "Neoplasm, uncertain whether benign or malignant"),
    ("8000/1", "Tumor, NOS"),
    ("8000/1", "Unclassified tumor, borderline malignancy"),
    ("8000/1", "Unclassified tumor, uncertain whether benign or malignant"),
    ("8001/0", "Tumor cells, benign"),
    ("8001/1", "Tumor cells, NOS"),
    ("8001/1", "Tumor cells, uncertain whether benign or malignant"),
]
for code, term in generic_8000:
    decisions[(code, term)] = obj(code, term, "No",
        rationale="Generic non-specific neoplasm/tumor descriptor applicable to any tumor type; not tied to any anatomic subsite and used across the entire code ceiling.")

# ---- 8728 melanocytic ----
decisions[("8728/0", "Diffuse melanocytosis")] = obj(
    "8728/0", "Diffuse melanocytosis", "Yes", MEN, MEN_LABELS,
    rationale="Primary diffuse leptomeningeal melanocytosis is a diffuse melanocytic proliferation arising from and confined to the leptomeninges (arachnoid/pia); restricted to the meningeal codes rather than the spinal-cord/cranial-nerve codes in the ceiling.",
    source=SRC_WHO_LEPTO, source_name=SRC_WHO_LEPTO_NAME)
decisions[("8728/0", "Meningeal melanocytosis")] = obj(
    "8728/0", "Meningeal melanocytosis", "Yes", MEN, MEN_LABELS,
    rationale="Meningeal (leptomeningeal) melanocytosis is a diffuse neoplasm of leptomeningeal melanocytes confined to the meninges; a proper subset of the 9-code ceiling that also lists spinal cord and cranial nerves.",
    source=SRC_MELANOCYTOMA, source_name=SRC_MELANOCYTOMA_NAME)
decisions[("8728/1", "Meningeal melanocytoma")] = obj(
    "8728/1", "Meningeal melanocytoma", "Yes", MEN, MEN_LABELS,
    rationale="Meningeal (leptomeningeal) melanocytoma is a circumscribed neoplasm arising from leptomeningeal melanocytes and is defined as a meningeal tumor; restricted to the meningeal codes, a proper subset of the ceiling.",
    source=SRC_MELANOCYTOMA, source_name=SRC_MELANOCYTOMA_NAME)
decisions[("8728/3", "Meningeal melanomatosis")] = obj(
    "8728/3", "Meningeal melanomatosis", "No",
    rationale="Meningeal melanomatosis is a leptomeningeal entity, but this code's ceiling already consists solely of the three meningeal codes (C700/C701/C709); the term matches the entire ceiling, so no proper anatomic subset exists.")

# ---- 8800/0 soft tissue tumor benign -> No ----
decisions[("8800/0", "Soft tissue tumor, benign")] = obj(
    "8800/0", "Soft tissue tumor, benign", "No",
    rationale="Generic benign soft-tissue (mesenchymal) descriptor with no anatomic restriction; applicable across the code's full CNS ceiling.")

# ---- 8815 solitary fibrous tumor / hemangiopericytoma -> Yes (meninges) ----
sft_terms = [
    "Fat-forming (lipomatous) solitary fibrous tumor",
    "Giant cell\u2013rich solitary fibrous tumor",
    "Hemangiopericytic meningioma",
    "Hemangiopericytoma, NOS",
    "Lipomatous solitary fibrous tumor",
    "Localized fibrous tumor",
    "Solitary fibrous tumor, NOS",
    "Solitary fibrous tumor, fat-forming",
    "Solitary fibrous tumor, giant cell-rich",
    "Solitary fibrous tumor, grade 2",
    "Solitary fibrous tumor, lipomatous",
    "Solitary fibrous tumor/Hemangiopericytoma, grade 2",
]
for term in sft_terms:
    decisions[("8815/1", term)] = obj(
        "8815/1", term, "Yes", MEN, MEN_LABELS,
        rationale="Within the CNS, solitary fibrous tumor / hemangiopericytoma is a dura-based, non-meningothelial mesenchymal MENINGEAL neoplasm arising from the meninges/dura; it is not an intraparenchymal brain tumor, so it is restricted to the meningeal codes (a proper subset of the 21-code ceiling).",
        source=SRC_SFT, source_name=SRC_SFT_NAME)

# ---- 8850/0 lipoma variants ----
LIP_SRC_SIALO = "https://pmc.ncbi.nlm.nih.gov/articles/PMC3714831/"
LIP_SRC_SIALO_NAME = "Dental Research Journal - Sialolipoma of salivary glands"
LIP_SRC_THYMO = "https://radiopaedia.org/articles/thymolipoma?lang=us"
LIP_SRC_THYMO_NAME = "Radiopaedia - Thymolipoma (anterior mediastinum/thymus)"

decisions[("8850/0", "Lipoadenoma, oncocytic")] = obj(
    "8850/0", "Lipoadenoma, oncocytic", "Uncertain",
    rationale="Oncocytic lipoadenoma is described in the literature as a salivary-gland (and parathyroid) lesion, i.e. outside this code's entirely CNS ceiling; no CNS anatomic subsite can be substantiated, so a valid subset within the ceiling cannot be asserted.",
    source=LIP_SRC_SIALO, source_name=LIP_SRC_SIALO_NAME)
decisions[("8850/0", "Oncocytic lipoadenoma")] = obj(
    "8850/0", "Oncocytic lipoadenoma", "Uncertain",
    rationale="Oncocytic lipoadenoma is a salivary-gland/parathyroid lesion in the literature, outside the code's CNS-only ceiling; no CNS subsite is supportable, so restriction to a proper subset of the ceiling cannot be established.",
    source=LIP_SRC_SIALO, source_name=LIP_SRC_SIALO_NAME)
decisions[("8850/0", "Sialolipoma")] = obj(
    "8850/0", "Sialolipoma", "Uncertain",
    rationale="Sialolipoma is a defined salivary-gland neoplasm (major/minor salivary glands), outside this code's CNS-only ceiling; no CNS subset can be substantiated from the literature.",
    source=LIP_SRC_SIALO, source_name=LIP_SRC_SIALO_NAME)
decisions[("8850/0", "Thymolipoma")] = obj(
    "8850/0", "Thymolipoma", "Uncertain",
    rationale="Thymolipoma is an anterior-mediastinal/thymic lipomatous tumor, outside this code's CNS-only ceiling; no CNS anatomic subset can be supported.",
    source=LIP_SRC_THYMO, source_name=LIP_SRC_THYMO_NAME)
decisions[("8850/0", "Lipomatous hypertrophy of atrial septum")] = obj(
    "8850/0", "Lipomatous hypertrophy of atrial septum", "Uncertain",
    rationale="Lipomatous hypertrophy of the atrial septum is a cardiac lesion, outside this code's CNS-only ceiling; no CNS anatomic subset can be substantiated.",
    source=LIP_SRC_THYMO, source_name="Radiopaedia - lipomatous lesion terminology reference")
decisions[("8850/0", "Lipoma, NOS")] = obj(
    "8850/0", "Lipoma, NOS", "No",
    rationale="Generic lipoma descriptor; intracranial and spinal lipomas occur across the meninges, brain and spinal cord, so the term is not restricted to a proper subset of the CNS ceiling.")

# ---- 8890/1 leiomyomatosis -> No (2-code NOS ceiling) ----
leio_terms = [
    "Diffuse leiomyomatosis",
    "Disseminated peritoneal leiomyomatosis",
    "Intravascular leiomyomatosis",
    "Intravenous leiomyomatosis",
    "Leiomyomatosis peritonealis disseminata",
    "Leiomyomatosis, NOS",
    "Leiomyomatosis, diffuse",
]
for term in leio_terms:
    decisions[("8890/1", term)] = obj(
        "8890/1", term, "No",
        rationale="The code ceiling comprises only two generic non-specific CNS codes (C728 overlapping lesion of brain/CNS, C729 nervous system NOS); no substantive pathology basis distinguishes one from the other, so no meaningful proper anatomic subset can be defined.")

# ---- 9080/0 teratoma -> No (distributed across ceiling) ----
tera_terms = [
    "Adult cystic teratoma",
    "Adult teratoma, NOS",
    "Cystic teratoma, NOS",
    "Mature cystic teratoma",
]
for term in tera_terms:
    decisions[("9080/0", term)] = obj(
        "9080/0", term, "No",
        rationale="Generic mature-teratoma descriptor; intracranial germ-cell teratomas, though midline-predominant (pineal/suprasellar), also arise in brain parenchyma (basal ganglia, thalamus, ventricles, cerebrum) and spinal cord, spanning essentially all of the code's CNS ceiling, so no proper subset restriction is supported.")

# Build ordered results matching batch order
results = []
for item in batch:
    key = (item["code"], item["term"])
    if key not in decisions:
        raise SystemExit(f"Missing decision for {key}")
    d = decisions[key]
    # verify subset
    for c in d["site_subset_codes"]:
        assert c in item["ceiling_codes"], f"{c} not in ceiling for {key}"
    results.append(d)

assert len(results) == 45, len(results)
out = '/home/user/workspace/icdo32_execution/results/cns_01.json'
json.dump(results, open(out, 'w'), indent=1, ensure_ascii=False)

yes = sum(1 for r in results if r["site_specific"] == "Yes")
no = sum(1 for r in results if r["site_specific"] == "No")
unc = sum(1 for r in results if r["site_specific"] == "Uncertain")
urls = set(r["source"] for r in results if r["source"])
print(f"Total={len(results)} Yes={yes} No={no} Uncertain={unc}")
print(f"Unique source URLs fetched: {len(urls)}")
for u in urls:
    print(" ", u)
