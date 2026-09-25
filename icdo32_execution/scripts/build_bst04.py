import json

batch_path = "/home/user/workspace/icdo32_execution/batches/bone_soft_tissue_04.json"
out_path = "/home/user/workspace/icdo32_execution/results/bone_soft_tissue_04.json"

with open(batch_path) as f:
    batch = json.load(f)

labels = {
"C300":"Nasal cavity","C310":"Maxillary sinus","C311":"Ethmoid sinus","C312":"Frontal sinus","C313":"Sphenoid sinus","C318":"Overlapping accessory sinus","C319":"Accessory sinus NOS",
"C340":"Main bronchus","C341":"Upper lobe lung","C342":"Middle lobe lung","C343":"Lower lobe lung","C348":"Overlapping lung","C349":"Lung NOS",
"C380":"Heart","C480":"Retroperitoneum","C488":"Overlapping retroperitoneum/peritoneum",
"C490":"Connective/soft tissue head & neck","C491":"Connective/soft tissue upper limb","C492":"Connective/soft tissue lower limb","C493":"Connective/soft tissue thorax","C494":"Connective/soft tissue abdomen","C495":"Connective/soft tissue pelvis","C496":"Connective/soft tissue trunk NOS","C498":"Overlapping connective/soft tissue","C499":"Connective/soft tissue NOS",
"C569":"Ovary","C620":"Undescended testis","C621":"Descended testis","C629":"Testis NOS",
}

def lab(codes):
    return [labels.get(c, c) for c in codes]

# Decisions keyed by (code, term)
YES = {}

# 9084/3 Testicular NET prepubertal-type -> testis
YES[("9084/3","Testicular neuroendocrine tumor, prepubertal-type")] = {
    "subset": ["C620","C621","C629"],
    "rationale": "WHO 5th ed classifies 'prepubertal-type testicular neuroendocrine tumour' as a testis-specific germ-cell-derived entity (a specialized form of prepubertal-type teratoma arising in the testis); it is a named testicular tumour, restricting it to testis within the broad germ-cell ceiling.",
    "source": "https://onlinelibrary.wiley.com/doi/10.1111/his.14675",
    "source_name": "WHO 5th ed testicular tumours (Histopathology, Wiley) — 'prepubertal type testicular neuroendocrine tumour'",
}
# 9084/3 Well-differentiated NET (monodermal teratoma) -> gonads (ovary + testis)
YES[("9084/3","Well-differentiated neuroendocrine tumor (monodermal teratoma)")] = {
    "subset": ["C569","C620","C621","C629"],
    "rationale": "Well-differentiated neuroendocrine tumour arising as a monodermal teratoma (carcinoid) is a gonadal germ-cell entity: most commonly ovarian (struma/strumal carcinoid) and testicular (prepubertal-type). It is restricted to the gonads within the broad germ-cell ceiling.",
    "source": "https://pmc.ncbi.nlm.nih.gov/articles/PMC11238806/",
    "source_name": "Monodermal teratoma review (World J Clin Cases) — most common in ovaries, followed by testes",
}

# 9133/3 IVBAT variants -> lung
lung = ["C340","C341","C342","C343","C348","C349"]
for term in ["Intravascular bronchial alveolar tumor","Intravascular bronchioloalveolar tumor"]:
    YES[("9133/3",term)] = {
        "subset": lung,
        "rationale": "Intravascular bronchioloalveolar tumor (IVBAT) is the historical name for pulmonary epithelioid hemangioendothelioma — a tumour defined specifically in the lung. The term restricts the entity to lung within the multi-site EHE ceiling.",
        "source": "https://pubmed.ncbi.nlm.nih.gov/6282146/",
        "source_name": "Bhagavan et al., IVBAT: low-grade sclerosing angiosarcoma of lung (PubMed PMID 6282146)",
    }

# 9137/3 Pulmonary artery intimal sarcoma -> pulmonary artery (thorax) + heart
YES[("9137/3","Pulmonary artery intimal sarcoma")] = {
    "subset": ["C380","C493"],
    "rationale": "Pulmonary artery intimal sarcoma is restricted to the pulmonary artery/pulmonary trunk (coded to thorax connective tissue C493 per SEER) and may involve cardiac structures/right ventricular outflow (C380). It does not occur at the limb/pelvic/abdominal soft-tissue sites in the code ceiling.",
    "source": "https://seer.cancer.gov/seer-inquiry/inquiry-detail/20150052/",
    "source_name": "SEER Inquiry 20150052 — code pulmonary artery intimal sarcoma to pulmonary artery C493",
}
# 9137/3 Intimal sarcoma (generic) -> great vessels + heart
YES[("9137/3","Intimal sarcoma")] = {
    "subset": ["C380","C493","C494"],
    "rationale": "Intimal sarcoma is defined as arising within the lumen of large vessels of the pulmonary (pulmonary artery -> thorax C493) or systemic circulation (thoracic aorta C493 / abdominal aorta C494) or within the heart cavities (C380). It is restricted to great-vessel/cardiac sites, not the general limb/pelvic soft tissue in the ceiling.",
    "source": "https://curesarcoma.org/sarcoma-subtypes/intimal-sarcoma/",
    "source_name": "Sarcoma Foundation of America / WHO — intimal sarcoma essential criteria (large vessels of pulmonary/systemic circulation or heart)",
}

# 9180/3 Osteosarcoma, extraosseus -> soft tissue + sinonasal, NOT bone
extra = ["C300","C310","C311","C312","C313","C318","C319","C480","C488","C490","C491","C492","C493","C494","C495","C496","C498","C499"]
YES[("9180/3","Osteosarcoma, extraosseus")] = {
    "subset": extra,
    "rationale": "Extraskeletal (extraosseous) osteosarcoma is by definition a soft-tissue tumour arising WITHOUT attachment to bone/periosteum (thigh, extremities, retroperitoneum, trunk, rarely sinonasal). It therefore excludes the bone topography codes (C400-C419) that are part of the code ceiling.",
    "source": "https://curesarcoma.org/sarcoma-subtypes/extraskeletal-osteosarcoma/",
    "source_name": "Sarcoma Foundation of America — extraskeletal osteosarcoma forms bone in soft tissues without bone involvement",
}

results = []
for item in batch:
    code = item["code"]
    term = item["term"]
    ceiling = item["ceiling_codes"]
    key = (code, term)
    if key in YES:
        d = YES[key]
        subset = d["subset"]
        # verify strict subset
        assert set(subset).issubset(set(ceiling)), f"NOT subset: {key} {set(subset)-set(ceiling)}"
        assert set(subset) != set(ceiling), f"equals ceiling: {key}"
        assert len(subset) >= 1
        results.append({
            "code": code, "term": term, "site_specific": "Yes",
            "site_subset_codes": subset,
            "site_subset_labels": lab(subset),
            "rationale": d["rationale"],
            "source": d["source"],
            "source_name": d["source_name"],
        })
    else:
        # default No
        results.append({
            "code": code, "term": term, "site_specific": "No",
            "site_subset_codes": [],
            "site_subset_labels": [],
            "rationale": "Generic germ-cell/teratoma/mixed germ-cell or multi-site sarcoma descriptor with no literature evidence restricting it to a proper subset of the code's validated sites; entity occurs across essentially all sites in the ceiling (gonadal and extragonadal midline germ-cell sites, or multi-site soft tissue/bone/visceral for EHE and osteosarcoma).",
            "source": "",
            "source_name": "",
        })

# Attach specific No-rationales / sources for the researched multi-site groups
NO_SRC = {}
# EHE generic variants -> multi-site (liver, lung, bone, soft tissue)
ehe_terms = [
 "Epithelioid hemangioendothelioma with WWTR1-CAMTA1 fusion",
 "Epithelioid hemangioendothelioma with WWTR1::CAMTA1 fusion",
 "Epithelioid hemangioendothelioma with YAP1-TFE3 fusion",
 "Epithelioid hemangioendothelioma with YAP1::TFE3 fusion",
 "Epithelioid hemangioendothelioma, NOS",
 "Epithelioid hemangioendothelioma, malignant",
]
for t in ehe_terms:
    NO_SRC[("9133/3",t)] = {
        "rationale": "Epithelioid hemangioendothelioma (all molecular subtypes and NOS/malignant) arises across many anatomic sites — liver, lung, bone, and soft tissue of head/neck, trunk and extremities, plus skin and heart — spanning essentially the entire code ceiling; not restricted to a proper subset.",
        "source": "https://pubmed.ncbi.nlm.nih.gov/24986479/",
        "source_name": "Sardaro/Errani-type series; PMID 24986479 — EHE occurs at various anatomic sites (soft tissue, bone, lung, liver)",
    }
# GLI1-altered soft tissue tumor -> multi-site within its GI/soft-tissue/skin ceiling
for t in ["GL1-altered soft tissue tumor","GLI1-altered soft tissue tumor"]:
    NO_SRC[("9150/3",t)] = {
        "rationale": "GLI1-altered mesenchymal tumours, while first codified in head & neck, occur broadly including the GI tract (stomach), soft tissue and genitourinary sites, covering the GI/soft-tissue/skin/eye sites present in this code's ceiling; not restricted to a proper subset within the ceiling.",
        "source": "https://pmc.ncbi.nlm.nih.gov/articles/PMC9018467/",
        "source_name": "GLI1 gene alterations in GU/GI neoplasms (Am J Surg Pathol, PMC9018467)",
    }
# Osteosarcoma generic bone+extraskeletal
for t in ["Osteoblastic sarcoma","Osteochondrosarcoma","Osteogenic sarcoma, NOS","Osteosarcoma, NOS"]:
    NO_SRC[("9180/3",t)] = {
        "rationale": "Generic osteosarcoma/osteogenic sarcoma descriptor. Osteosarcoma arises predominantly in bone but also as extraskeletal osteosarcoma in soft tissue and sinonasal sites; the term is not anatomically restricted to a proper subset of this code's bone+soft-tissue ceiling.",
        "source": "https://www.cancer.gov/types/bone/hp/osteosarcoma-treatment-pdq",
        "source_name": "NCI PDQ Osteosarcoma treatment — conventional and extraskeletal osteosarcoma sites",
    }

for r in results:
    key = (r["code"], r["term"])
    if r["site_specific"] == "No" and key in NO_SRC:
        r["rationale"] = NO_SRC[key]["rationale"]
        r["source"] = NO_SRC[key]["source"]
        r["source_name"] = NO_SRC[key]["source_name"]

assert len(results) == 45, len(results)
with open(out_path,"w") as f:
    json.dump(results, f, indent=1)

from collections import Counter
c = Counter(r["site_specific"] for r in results)
print("counts", dict(c))
print("length", len(results))
for r in results:
    if r["site_specific"]=="Yes":
        print("YES:", r["code"], r["term"], "->", r["site_subset_codes"])
