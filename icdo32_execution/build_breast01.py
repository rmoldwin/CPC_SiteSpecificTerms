import json

BATCH = "/home/user/workspace/icdo32_execution/batches/breast_01.json"
OUT = "/home/user/workspace/icdo32_execution/results/breast_01.json"

with open(BATCH) as f:
    cands = json.load(f)

# Label lookups
LBL = {
    "C079": "Parotid gland",
    "C080": "Submandibular gland",
    "C081": "Sublingual gland",
    "C088": "Overlapping lesion of major salivary glands",
    "C089": "Major salivary gland, NOS",
    "C250": "Head of pancreas", "C251": "Body of pancreas", "C252": "Tail of pancreas",
    "C253": "Pancreatic duct", "C254": "Islets of Langerhans", "C257": "Other pancreas",
    "C258": "Overlapping lesion of pancreas", "C259": "Pancreas, NOS",
    "C500": "Nipple", "C501": "Central portion of breast", "C502": "Upper-inner quadrant",
    "C503": "Lower-inner quadrant", "C504": "Upper-outer quadrant", "C505": "Lower-outer quadrant",
    "C506": "Axillary tail of breast", "C508": "Overlapping lesion of breast", "C509": "Breast, NOS",
    "C510": "Labium majus", "C511": "Labium minus", "C512": "Clitoris",
    "C518": "Overlapping lesion of vulva", "C519": "Vulva, NOS",
    "C619": "Prostate gland",
}

SALIVARY = ["C079", "C080", "C081", "C088", "C089"]
VULVA = ["C510", "C511", "C512", "C518", "C519"]

def breast_codes(ceiling):
    return [c for c in ceiling if c.startswith("C50")]

# Sources
SRC_LGCCC = ("https://pmc.ncbi.nlm.nih.gov/articles/PMC10293154/",
             "WHO Head and Neck Tumours 5th ed / Skalova & Hyrcza, Head Neck Pathol 2023 (PMC10293154)")
SRC_IDC = ("https://pmc.ncbi.nlm.nih.gov/articles/PMC10293154/",
           "WHO Head and Neck Tumours 5th ed / Skalova & Hyrcza, Head Neck Pathol 2023 (PMC10293154)")
SRC_CHC = ("https://pubmed.ncbi.nlm.nih.gov/24121179/",
           "D'Alfonso et al., PubMed PMID 24121179 (cystic hypersecretory carcinoma = breast DCIS variant)")
SRC_DCISMALE = ("https://pmc.ncbi.nlm.nih.gov/articles/PMC9581867/",
                "Breast Cancer Res Treat 2022, DCIS of the male breast (PMC9581867)")
SRC_AGMLG = ("https://pubmed.ncbi.nlm.nih.gov/38711196/",
             "Adenocarcinoma of anogenital mammary gland type, vulvar tumor, PubMed PMID 38711196")
SRC_AMGT = ("https://pmc.ncbi.nlm.nih.gov/articles/PMC11831014/",
            "Primary Vulvar Adenocarcinoma of Mammary Gland Type, Int J Womens Health 2025 (PMC11831014)")

# Decision map keyed by (code, term)
def mk(ss, codes, rat, src):
    return {"site_specific": ss,
            "site_subset_codes": codes,
            "rationale": rat,
            "source": src[0],
            "source_name": src[1]}

decisions = {}

# --- 8314/3 Lipid-rich carcinoma: breast-only ceiling -> No (spans all breast subsites)
decisions[("8314/3","Lipid-rich carcinoma")] = mk("No", [],
    "Code 8314/3 is SMVL-valid only at breast subsites (C500-C509); lipid-rich carcinoma is a breast IBC-NST morphologic variant occurring across the whole breast, so it is not restricted to a proper subset of its ceiling.",
    ("https://pmc.ncbi.nlm.nih.gov/articles/PMC9119809/","Muller et al., J Pathol Transl Med 2022, WHO Breast 5th ed (PMC9119809)"))

# --- 8315/3 Glycogen-rich carcinoma & Glycogen-rich clear cell carcinoma: breast-only ceiling -> No
for t in ["Glycogen-rich carcinoma","Glycogen-rich clear cell carcinoma"]:
    decisions[("8315/3",t)] = mk("No", [],
        "Code 8315/3 is SMVL-valid only at breast subsites (C500-C509); glycogen-rich (clear cell) carcinoma is a breast IBC-NST morphologic variant used across all breast subsites, so no proper subset restriction applies within its ceiling.",
        ("https://pmc.ncbi.nlm.nih.gov/articles/PMC9119809/","Muller et al., J Pathol Transl Med 2022, WHO Breast 5th ed (PMC9119809)"))

# --- 8500/2 terms ---
# Salivary-specific IDC subtypes (intercalated duct, oncocytic) -> Yes (salivary)
salivary_yes_2 = {
    "Intercalated duct carcinoma": "intercalated duct type of salivary gland intraductal carcinoma",
    "Intercalated duct intraductal carcinoma": "intercalated duct subtype of salivary intraductal carcinoma",
    "Intraductal carcinoma, intercalated duct": "intercalated duct subtype of salivary intraductal carcinoma",
    "Oncocytic intraductal carcinoma": "oncocytic subtype of salivary gland intraductal carcinoma",
    "Intraductal carcinoma, oncocytic": "oncocytic subtype of salivary gland intraductal carcinoma",
    "Low grade cribriform cystadenocarcinoma (LGCCC)": "salivary gland intraductal carcinoma (historically low-grade cribriform cystadenocarcinoma)",
}
for t, desc in salivary_yes_2.items():
    decisions[("8500/2",t)] = mk("Yes", SALIVARY,
        f"The {desc} is a WHO-defined salivary gland entity; within the 8500/2 ceiling (salivary + breast + prostate) it is restricted to the major salivary glands.",
        SRC_IDC)

# Apocrine intraductal carcinoma -> Uncertain (apocrine intraductal/DCIS occurs in both salivary and breast)
for t in ["Apocrine intraductal carcinoma","Intraductal carcinoma, apocrine"]:
    decisions[("8500/2",t)] = mk("Uncertain", [],
        "Apocrine intraductal carcinoma is a named salivary IDC subtype, but apocrine ductal carcinoma in situ is equally well described in the breast; evidence does not clearly restrict the term to a proper subset of its salivary+breast+prostate ceiling.",
        SRC_IDC)

# Breast-specific in situ terms -> Yes (breast subset)
bc2 = breast_codes(cands[3]["ceiling_codes"]) if False else None  # placeholder; compute per item

breast_yes_2 = {
    "Cystic hypersecretory carcinoma, intraductal": ("Cystic hypersecretory carcinoma is a WHO/literature-recognized variant of ductal carcinoma in situ of the breast, not described in salivary gland or prostate.", SRC_CHC),
    "DCIS of high nuclear grade": ("Ductal carcinoma in situ (DCIS) graded by nuclear grade is a breast-specific in situ carcinoma classification.", SRC_CHC),
    "DCIS of intermediate nuclear grade": ("Ductal carcinoma in situ (DCIS) graded by nuclear grade is a breast-specific in situ carcinoma classification.", SRC_CHC),
    "DCIS of low nuclear grade": ("Ductal carcinoma in situ (DCIS) graded by nuclear grade is a breast-specific in situ carcinoma classification.", SRC_CHC),
    "DIN 3": ("Ductal intraepithelial neoplasia grade 3 (DIN 3) is a breast-specific grading synonym for high-grade DCIS.", SRC_CHC),
    "Ductal intraepithelial neoplasia 3": ("Ductal intraepithelial neoplasia grade 3 is a breast-specific grading synonym for high-grade DCIS.", SRC_CHC),
    "Mammary carcinoma, in situ": ("In situ mammary (breast) carcinoma is by definition a breast entity.", SRC_CHC),
    "Non-invasive mammary carcinoma": ("Non-invasive mammary (breast) carcinoma is by definition a breast entity.", SRC_CHC),
    "Carcinoma in situ of male breast": ("Carcinoma in situ of the male breast is a breast entity localized to breast subsites (C50); male breast tissue is still coded to C50.", SRC_DCISMALE),
}
for t,(rat,src) in breast_yes_2.items():
    bc = breast_codes(next(c["ceiling_codes"] for c in cands if c["code"]=="8500/2" and c["term"]==t))
    decisions[("8500/2",t)] = mk("Yes", bc, rat, src)

# Generic multi-site NOS / mixed descriptors under 8500/2 -> No
generic_no_2 = [
    "DCIS, NOS",
    "Ductal carcinoma in situ, NOS",
    "Intraductal adenocarcinoma, noninfiltrating, NOS",
    "Intraductal carcinoma, NOS",
    "Intraductal carcinoma, mixed",
    "Intraductal carcinoma, noninfiltrating, NOS",
    "Mixed intraductal carcinoma",
]
for t in generic_no_2:
    decisions[("8500/2",t)] = mk("No", [],
        "Generic non-infiltrating/intraductal carcinoma descriptor applied across all sites of the 8500/2 ceiling (salivary, breast, prostate); not restricted to a proper subset.",
        ("https://pmc.ncbi.nlm.nih.gov/articles/PMC10293154/","WHO classifications; term is a generic multi-site intraductal descriptor (PMC10293154)"))

# --- 8500/3 terms ---
# Salivary-specific
decisions[("8500/3","Basal-like salivary duct carcinoma")] = mk("Yes", SALIVARY,
    "Salivary duct carcinoma (including its basal-like variant) is a WHO-defined salivary gland malignancy resembling high-grade breast ductal carcinoma; within the 8500/3 ceiling it is restricted to the major salivary glands.",
    ("https://pmc.ncbi.nlm.nih.gov/articles/PMC7541685/","Nakaguro et al., Cancer Cytopathol 2020, salivary duct carcinoma variants (PMC7541685)"))

# Anogenital mammary-like / mammary gland type -> vulva
decisions[("8500/3","Adenocarcinoma of anogenital mammary-like glands")] = mk("Yes", VULVA,
    "Adenocarcinoma of anogenital mammary-like glands arises in the vulva/anogenital region from anogenital mammary-like glands; within the 8500/3 ceiling it maps to the vulvar subsites.",
    SRC_AGMLG)
decisions[("8500/3","Adenocarcinoma of mammary gland type")] = mk("Yes", VULVA,
    "Adenocarcinoma of mammary gland type is the vulvar (anogenital mammary-like gland) carcinoma showing breast-type morphology; within the 8500/3 ceiling it is restricted to the vulvar subsites.",
    SRC_AMGT)

# Male / breast NST specific
decisions[("8500/3","Invasive breast carcinoma of no special type")] = mk("Yes", breast_codes(cands[0]["ceiling_codes"]) if False else breast_codes(next(c["ceiling_codes"] for c in cands if c["code"]=="8500/3" and c["term"]=="Invasive breast carcinoma of no special type")),
    "Invasive breast carcinoma of no special type is by name a breast entity; within the multi-organ 8500/3 ceiling it is restricted to the breast subsites.",
    ("https://en.wikipedia.org/wiki/Invasive_carcinoma_of_no_special_type","WHO Breast 5th ed terminology; invasive breast carcinoma NST is breast-specific"))
decisions[("8500/3","Invasive breast carcinoma, NOS")] = mk("Yes", breast_codes(next(c["ceiling_codes"] for c in cands if c["code"]=="8500/3" and c["term"]=="Invasive breast carcinoma, NOS")),
    "Invasive breast carcinoma, NOS is by name a breast entity; within the multi-organ 8500/3 ceiling it is restricted to the breast subsites.",
    ("https://pmc.ncbi.nlm.nih.gov/articles/PMC3683948/","WHO Breast classification; invasive breast carcinoma NST/NOS is breast-specific (PMC3683948)"))
decisions[("8500/3","Invasive carcinoma of male breast")] = mk("Yes", breast_codes(next(c["ceiling_codes"] for c in cands if c["code"]=="8500/3" and c["term"]=="Invasive carcinoma of male breast")),
    "Invasive carcinoma of the male breast is a breast entity localized to breast subsites (C50); male breast tissue is coded to C50.",
    ("https://www.cancer.org/cancer/types/breast-cancer-in-men.html","American Cancer Society, breast cancer in men (invasive ductal carcinoma of the breast)"))

# Generic 8500/3 duct/adenocarcinoma descriptors -> No (multi-site)
generic_no_3 = [
    "Basal-like carcinoma, NOS",
    "Duct adenocarcinoma, NOS",
    "Duct carcinoma, NOS",
    "Duct cell adenocarcinoma",
    "Duct cell carcinoma",
    "Ductal adenocarcinoma",
    "Ductal carcinoma, NOS",
    "Infiltrating duct adenocarcinoma",
    "Infiltrating duct carcinoma, NOS",
    "Infiltrating ductal carcinoma, NOS",
    "Invasive carcinoma",
    "Invasive carcinoma of no special type",
]
for t in generic_no_3:
    decisions[("8500/3",t)] = mk("No", [],
        "Generic ductal/invasive adenocarcinoma descriptor used across the multiple organs in the 8500/3 ceiling (salivary, pancreas, breast, vulva, prostate); not restricted to a proper subset.",
        ("https://pmc.ncbi.nlm.nih.gov/articles/PMC3683948/","WHO classifications; generic multi-site duct/invasive carcinoma descriptor (PMC3683948)"))

# Build output preserving order
out = []
for c in cands:
    key = (c["code"], c["term"])
    d = decisions[key]
    obj = {"code": c["code"], "term": c["term"], "site_specific": d["site_specific"]}
    codes = d["site_subset_codes"]
    obj["site_subset_codes"] = codes
    obj["site_subset_labels"] = [LBL[x] for x in codes]
    obj["rationale"] = d["rationale"]
    obj["source"] = d["source"]
    obj["source_name"] = d["source_name"]
    # validate subset
    if d["site_specific"] == "Yes":
        assert set(codes).issubset(set(c["ceiling_codes"])), f"NOT subset: {key} {codes}"
        assert set(codes) != set(c["ceiling_codes"]), f"not proper subset: {key}"
        assert len(codes) > 0
    out.append(obj)

assert len(out) == 45, len(out)

with open(OUT, "w") as f:
    json.dump(out, f, indent=1)

from collections import Counter
cnt = Counter(o["site_specific"] for o in out)
print("counts:", dict(cnt), "total:", len(out))
srcs = set(o["source"] for o in out if o["site_specific"]=="Yes")
print("distinct Yes sources:", len(srcs))
for o in out:
    print(o["code"], "|", o["term"][:45], "|", o["site_specific"], "|", o["site_subset_codes"])
