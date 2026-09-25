import json

batch = json.load(open("/home/user/workspace/icdo32_execution/batches/heme_01.json"))

# Sources used
SEER_HL = "https://seer.cancer.gov/seertools/hemelymph/51f6cf57e3e27c3994bd5372/"
SEER_HCD = "https://seer.cancer.gov/seertools/hemelymph/51f6cf59e3e27c3994bd5486/"
WHO5 = "https://pmc.ncbi.nlm.nih.gov/articles/PMC9214472/"
STATPEARLS = "https://www.ncbi.nlm.nih.gov/books/NBK499969/"

def hl_rationale(term):
    return ("Hodgkin lymphoma subtypes are nodal-family neoplasms; SEER Hematopoietic rules assign the full "
            "lymph node region range C770-C779 as primary sites. Anatomic preferences (e.g. mediastinal/cervical for "
            "nodular sclerosis) are tendencies, not exclusions, so the term is not restricted to a proper subset of "
            "its lymph-node-region ceiling.")

results = []
for obj in batch:
    code = obj["code"]
    term = obj["term"]
    ceiling = obj["ceiling_codes"]

    if code in ("9650/3","9651/3","9652/3","9653/3","9655/3","9659/3","9663/3"):
        results.append({
            "code": code, "term": term,
            "site_specific": "No",
            "site_subset_codes": [],
            "site_subset_labels": [],
            "rationale": hl_rationale(term),
            "source": SEER_HL,
            "source_name": "SEER Hematopoietic ICD-O-3 database (Nodular sclerosis CHL entry) / WHO Classification of Tumours 5th ed (Haematolymphoid)"
        })
    elif code == "9688/3":
        results.append({
            "code": code, "term": term,
            "site_specific": "No",
            "site_subset_codes": [],
            "site_subset_labels": [],
            "rationale": ("T-cell/histiocyte-rich large B-cell lymphoma and related large B-cell entities under this code are "
                          "nodal-family lymphomas with the full lymph node region range (C770-C779) as their ceiling; the literature "
                          "does not restrict them to a proper subset of specific nodal regions."),
            "source": WHO5,
            "source_name": "WHO Classification of Tumours 5th ed, Haematolymphoid (Leukemia 2022 overview) / SEER Hematopoietic database"
        })
    elif code == "9762/3":
        # Heavy chain diseases. Ceiling = C421 (bone marrow) + C770-C779 (lymph node regions).
        # Literature-supported restriction (alpha HCD -> GI/small intestine) lies OUTSIDE the ceiling,
        # so it cannot be expressed as a proper subset of ceiling codes. Gamma HCD and NOS are disseminated.
        results.append({
            "code": code, "term": term,
            "site_specific": "No",
            "site_subset_codes": [],
            "site_subset_labels": [],
            "rationale": ("Heavy chain diseases are systemic plasma-cell/lymphoplasmacytic processes; per SEER, gamma (Franklin) HCD "
                          "is disseminated across lymph nodes, Waldeyer ring, marrow, liver and spleen, while alpha HCD is centered on the "
                          "GI tract/small intestine (sites not in this code's ceiling). Within the code's bone-marrow-plus-nodal ceiling, no "
                          "literature restricts the term to a demonstrable proper subset, so it is not site-specific."),
            "source": SEER_HCD,
            "source_name": "SEER Hematopoietic ICD-O-3 database (Heavy chain diseases entry)"
        })
    else:
        results.append({
            "code": code, "term": term,
            "site_specific": "No",
            "site_subset_codes": [],
            "site_subset_labels": [],
            "rationale": "No literature evidence of restriction to a proper subset of the code ceiling.",
            "source": SEER_HL,
            "source_name": "SEER Hematopoietic ICD-O-3 database"
        })

# validate subsets
for r in results:
    obj = next(o for o in batch if o["code"]==r["code"] and o["term"]==r["term"])
    assert set(r["site_subset_codes"]).issubset(set(obj["ceiling_codes"])), r

json.dump(results, open("/home/user/workspace/icdo32_execution/results/heme_01.json","w"), indent=1)
print("len:", len(results))
from collections import Counter
print(Counter(r["site_specific"] for r in results))
