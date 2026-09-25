import json

batch = json.load(open("/home/user/workspace/icdo32_execution/batches/respiratory_01.json"))

# Label lookup
LBL = {
    "C300":"Nasal cavity","C310":"Maxillary sinus","C311":"Ethmoid sinus",
    "C312":"Frontal sinus","C313":"Sphenoid sinus","C318":"Overlapping lesion of accessory sinuses",
    "C319":"Accessory sinus, NOS","C339":"Trachea","C340":"Main bronchus","C341":"Upper lobe, lung",
    "C342":"Middle lobe, lung","C343":"Lower lobe, lung","C348":"Overlapping lesion of lung",
    "C349":"Lung, NOS","C390":"Upper respiratory tract, NOS","C569":"Ovary",
    "C529":"Vagina, NOS","C530":"Endocervix","C531":"Exocervix","C538":"Overlapping lesion of cervix uteri",
    "C539":"Cervix uteri, NOS","C379":"Thymus","C380":"Heart, mediastinum, and pleura"
}

SINONASAL = ["C300","C310","C311","C312","C313","C318","C319"]
THORACIC_8044 = ["C339","C340","C341","C342","C343","C348","C349","C390"]
LUNG_8333 = ["C340","C341","C342","C343","C348","C349"]
CERVIX = ["C530","C531","C538","C539"]  # will refine below

def labels(codes):
    return [LBL.get(c,c) for c in codes]

# Sources
SRC_SINONASAL = ("https://pmc.ncbi.nlm.nih.gov/articles/PMC12078905/",
    "PubMed PMC12078905 (Head Neck Pathol 2025) citing WHO Head & Neck Tumours 5th ed")
SRC_OVARY = ("https://www.jcancer.org/v10p0223.htm",
    "PubMed / J Cancer 2019 (SCCOHT review); WHO Female Genital Tumours")
SRC_OVARY_NG = ("https://pmc.ncbi.nlm.nih.gov/articles/PMC4332808/",
    "Nature Genetics 2014 (PMC4332808) SMARCA4 in SCCOHT")
SRC_THORACIC = ("https://academic.oup.com/jjco/article/54/3/265/7479745",
    "Jpn J Clin Oncol 2024 citing WHO Classification of Thoracic Tumours 5th ed 2021")
SRC_HMSC = ("https://lesterthompsonmd.com/pdf/HNPJ-2022-03_Update%20From%20the%20ENT%205th%20Edition%20From%20the%20WHO.pdf",
    "Thompson & Bishop, Head Neck Pathol 2022 — WHO Head & Neck 5th ed update")
SRC_HPV_CERVIX = ("https://www.iccr-cancer.org/wp-content/uploads/2023/10/ICCR-Cervix-5th-ed-v5.0-bookmark-1.pdf",
    "ICCR Carcinoma of the Cervix Reporting Guide 5th ed (WHO Female Genital Tumours)")
SRC_FETAL = ("https://whobluebooks.iarc.who.int/structures/thoracic-tumours/",
    "WHO Blue Books — Thoracic Tumours 5th ed (Fetal adenocarcinoma of the lung)")
SRC_INTERMED = ("https://training.seer.cancer.gov/lung/abstract-code-stage/morphology.html",
    "SEER Training — Lung morphology (small cell/intermediate cell lung cancer)")

def yes(codes, rationale, src):
    return {"site_specific":"Yes","site_subset_codes":codes,
            "site_subset_labels":labels(codes),"rationale":rationale,
            "source":src[0],"source_name":src[1]}
def no(rationale, src=None):
    d={"site_specific":"No","site_subset_codes":[],"site_subset_labels":[],
       "rationale":rationale,"source":src[0] if src else "","source_name":src[1] if src else ""}
    return d
def unc(rationale, src=None):
    d={"site_specific":"Uncertain","site_subset_codes":[],"site_subset_labels":[],
       "rationale":rationale,"source":src[0] if src else "","source_name":src[1] if src else ""}
    return d

# Decision map keyed by (code, term)
D = {}

# --- 8044/3 ovary ---
D[("8044/3","SMARCA4-deficient carcinoma of ovary")] = yes(["C569"],
  "Term explicitly names the ovary; SMARCA4-deficient ovarian carcinoma (SCCOHT) is an ovarian entity in WHO Female Genital Tumours, restricted to the ovary within the ceiling.", SRC_OVARY_NG)

for t in ["Small cell carcinoma of the ovary, hypercalcemic type",
          "Small cell carcinoma of the ovary, hypercalcemic type, large cell subtype",
          "Small cell carcinoma, hypercalcemic type",
          "Small cell carcinoma, hypercalcemic type, large cell subtype",
          "Small cell carcinoma, large cell subtype",
          "Small cell carcinoma, large cell variant"]:
    D[("8044/3",t)] = yes(["C569"],
      "Hypercalcemic-type small cell carcinoma (SCCOHT), including its large-cell/rhabdoid variant, is definitionally an ovarian tumor per WHO Female Genital Tumours; restricted to the ovary within the ceiling.", SRC_OVARY)

# --- 8044/3 sinonasal ---
for t in ["SMARCA4-deficient sinonasal carcinoma",
          "SMARCA4-deficient undifferentiated sinonasal carcinoma",
          "SMARCB1-deficient sinonasal adenocarcinoma",
          "SMARCB1-deficient sinonasal carcinoma",
          "SMARCB1-deficient undifferentiated sinonasal carcinoma",
          "SWI/SNF complex-deficient sinonasal carcinoma"]:
    D[("8044/3",t)] = yes(SINONASAL,
      "SWI/SNF (SMARCB1/SMARCA4)-deficient sinonasal carcinoma is defined as a sinonasal tract entity in WHO Head & Neck Tumours 5th ed; restricted to nasal cavity and paranasal sinuses within the ceiling.", SRC_SINONASAL)

# --- 8044/3 thoracic ---
for t in ["Thoracic SMARCA4-deficient undifferentiated tumor"]:
    D[("8044/3",t)] = yes(THORACIC_8044,
      "Thoracic SMARCA4-deficient undifferentiated tumor is defined in WHO Thoracic Tumours 5th ed (2021) as a thoracic/lung entity under 'other epithelial tumours of the lung'; restricted to the thoracic/respiratory codes within the ceiling.", SRC_THORACIC)

# ambiguous
D[("8044/3","SMARCA4-deficient undifferentiated tumor")] = unc(
  "Without a site qualifier this term is used for both the thoracic (lung) entity and other SMARCA4-deficient undifferentiated tumors; the name alone does not restrict it to a specific proper subset of the ceiling.", SRC_THORACIC)

D[("8044/3","Small cell carcinoma, intermediate cell")] = yes(THORACIC_8044,
  "'Intermediate cell' small cell carcinoma is a small cell lung cancer morphologic descriptor (SEER lists intermediate cell carcinoma among small cell lung cancers); used in the lower respiratory tract, not the ovary/sinonasal, so restricted to the thoracic/respiratory codes within the ceiling.", SRC_INTERMED)

# --- 8046/3 ---
D[("8046/3","Non-small cell carcinoma")] = no(
  "Generic descriptor; its ceiling is entirely lung (C340-C349), so it is used across all of its valid sites and is not restricted to a proper subset.")

# --- 8250/2 (lung-only ceiling) ---
for t in ["Adenocarcinoma in situ of lung, non-mucinous","Adenocarcinoma in situ, non-mucinous"]:
    D[("8250/2",t)] = no(
      "Adenocarcinoma in situ (non-mucinous) is a lung entity and its ceiling is entirely lung (C340-C349); covers all of the ceiling, so not a proper subset.")

# --- 8250/3 (ceiling C339,C34x,C390) lung parenchyma adeno patterns ---
for t in ["Alveolar cell carcinoma","Bronchiolar adenocarcinoma","Bronchiolar carcinoma",
          "Bronchiolo-alveolar adenocarcinoma, NOS","Bronchiolo-alveolar carcinoma, NOS",
          "Lepidic adenocarcinoma"]:
    D[("8250/3",t)] = no(
      "Lepidic/bronchiolo-alveolar adenocarcinoma patterns are pulmonary adenocarcinomas spanning the lung/respiratory ceiling; no literature restricts the term to a smaller proper subset within the ceiling.")

# --- 8253/2 ---
for t in ["Adenocarcinoma in situ of lung, mucinous","Adenocarcinoma in situ, mucinous"]:
    D[("8253/2",t)] = no(
      "Mucinous adenocarcinoma in situ is a lung entity and its ceiling is entirely lung (C340-C349); covers all of the ceiling, not a proper subset.")

# --- 8253/3 ---
for t in ["Adenocarcinoma of lung, mucinous","Bronchiolo-alveolar carcinoma, goblet cell type",
          "Bronchiolo-alveolar carcinoma, mucinous","Invasive mucinous adenocarcinoma",
          "Mucinous carcinoma of lung"]:
    D[("8253/3",t)] = no(
      "Invasive mucinous (bronchiolo-alveolar) adenocarcinoma is a pulmonary adenocarcinoma spanning the lung/respiratory ceiling; no literature restricts it to a smaller proper subset.")

# --- 8254/3 ---
for t in ["Adenocarcinoma of lung, mixed mucinous and non-mucinous",
          "Bronchiolo-alveolar carcinoma, Clara cell and goblet cell type",
          "Bronchiolo-alveolar carcinoma, indeterminate type",
          "Bronchiolo-alveolar carcinoma, mixed mucinous and non-mucinous",
          "Bronchiolo-alveolar carcinoma, type II pneumocyte and goblet cell type",
          "Mixed invasive mucinous and non-mucinous adenocarcinoma"]:
    D[("8254/3",t)] = no(
      "Mixed mucinous/non-mucinous (bronchiolo-alveolar) adenocarcinoma is a pulmonary adenocarcinoma spanning the lung/respiratory ceiling; no literature restricts it to a smaller proper subset.")

# --- 8256/3, 8257/3 (lung-only ceiling) ---
D[("8256/3","Minimally invasive adenocarcinoma, non-mucinous")] = no(
  "Minimally invasive adenocarcinoma is a lung entity and its ceiling is entirely lung (C340-C349); covers all of the ceiling, not a proper subset.")
D[("8257/3","Minimally invasive adenocarcinoma, mucinous")] = no(
  "Minimally invasive adenocarcinoma (mucinous) is a lung entity and its ceiling is entirely lung (C340-C349); covers all of the ceiling, not a proper subset.")

# --- 8333/3 fetal adenocarcinoma ---
D[("8333/3","Fetal adenocarcinoma")] = yes(LUNG_8333,
  "Fetal adenocarcinoma (8333/3) is defined as a lung tumor ('fetal adenocarcinoma of the lung') in WHO Thoracic Tumours 5th ed; restricted to lung, excluding the thyroid (C739) code in the ceiling.", SRC_FETAL)

# --- 8483/3 ---
D[("8483/3","Adenocarcinoma, HPV-associated")] = yes(["C530","C531","C538","C539"],
  "'Adenocarcinoma, HPV-associated' (8483/3) is the HPV-associated endocervical adenocarcinoma of WHO Female Genital Tumours, valid for uterine cervix; restricted to the cervix codes within the ceiling.", SRC_HPV_CERVIX)
for t in ["HPV-associated multiphenotypic sinonasal carcinoma","HPV-related multiphenotypic sinonasal carcinoma"]:
    D[("8483/3",t)] = yes(SINONASAL,
      "HPV-related multiphenotypic sinonasal carcinoma is described in WHO Head & Neck Tumours 5th ed as seemingly restricted to the sinonasal tract; restricted to nasal cavity and paranasal sinuses within the ceiling.", SRC_HMSC)

# --- 8580/3 intrapulmonary thymoma ---
D[("8580/3","Intrapulmonary thymoma")] = unc(
  "Intrapulmonary thymoma arises from ectopic thymic tissue in the lung, but the ceiling only contains thymus (C379) and mediastinum/heart/pleura (C380); no literature cleanly restricts it to a proper subset of these two mediastinal codes.")

# Build output preserving order & ceiling validation
out=[]
for obj in batch:
    key=(obj["code"],obj["term"])
    dec=D[key]
    codes=dec["site_subset_codes"]
    # validate subset
    ceil=set(obj["ceiling_codes"])
    assert set(codes).issubset(ceil), f"NOT SUBSET: {key} {codes} not in {ceil}"
    if dec["site_specific"]=="Yes":
        assert len(codes)>0 and len(codes)<len(ceil), f"NOT PROPER SUBSET {key}"
        assert dec["source"].startswith("http"), f"NO SOURCE {key}"
    row={"code":obj["code"],"term":obj["term"],"site_specific":dec["site_specific"],
         "site_subset_codes":codes,"site_subset_labels":dec["site_subset_labels"],
         "rationale":dec["rationale"],"source":dec["source"],"source_name":dec["source_name"]}
    out.append(row)

assert len(out)==45, len(out)
import os
os.makedirs("/home/user/workspace/icdo32_execution/results",exist_ok=True)
json.dump(out,open("/home/user/workspace/icdo32_execution/results/respiratory_01.json","w"),indent=1)

from collections import Counter
c=Counter(r["site_specific"] for r in out)
srcs={r["source"] for r in out if r["source"]}
print("counts",c)
print("n_sources",len(srcs))
print("total",len(out))
