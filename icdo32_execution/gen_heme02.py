import json

merck = "https://www.merckmanuals.com/professional/hematology-and-oncology/plasma-cell-disorders/heavy-chain-diseases"
merck_name = "Merck Manual Professional Edition - Heavy Chain Diseases"

batch = json.load(open("/home/user/workspace/icdo32_execution/batches/heme_02.json"))

results = []
for item in batch:
    code = item["code"]
    term = item["term"]

    if code == "9762/3":
        # Heavy chain diseases / IPSID. Ceiling = blood (C421) + lymph nodes (C770-779)
        rationale = ("Heavy chain diseases (including IPSID/Mediterranean lymphoma and mu heavy chain disease) are systemic "
                     "lymphoplasmacytic disorders involving blood and lymph nodes; literature shows involvement across blood "
                     "and abdominal/peripheral lymph node compartments rather than a single code-mappable lymph node subset, "
                     "so no strict proper-subset restriction of the ceiling is supported.")
        source = merck
        source_name = merck_name
    else:
        # Leukemia/MDS codes: ceiling = C421 (blood) + C424 (bone marrow) only
        rationale = ("This is a systemic myeloid/leukemic hematopoietic neoplasm diagnosed in bone marrow with peripheral "
                     "blood involvement; its two ceiling sites (blood and bone marrow) are both intrinsic to the disease, so "
                     "no proper-subset anatomic restriction applies.")
        source = merck
        source_name = merck_name

    results.append({
        "code": code,
        "term": term,
        "site_specific": "No",
        "site_subset_codes": [],
        "site_subset_labels": [],
        "rationale": rationale,
        "source": source,
        "source_name": source_name
    })

assert len(results) == 36, len(results)
import os
os.makedirs("/home/user/workspace/icdo32_execution/results", exist_ok=True)
json.dump(results, open("/home/user/workspace/icdo32_execution/results/heme_02.json","w"), indent=1)
print("wrote", len(results), "objects")
print(sum(1 for r in results if r["site_specific"]=="No"), "No")
