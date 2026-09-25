import json, os

batch_path = "/home/user/workspace/icdo32_execution/batches/endocrine_02.json"
out_path = "/home/user/workspace/icdo32_execution/results/endocrine_02.json"

with open(batch_path) as f:
    batch = json.load(f)

# Sources
SRC_ONCO_THYROID = "https://www.ncbi.nlm.nih.gov/books/NBK568736/"
SRC_ONCO_THYROID_NAME = "StatPearls: Oncocytic (Hürthle Cell) Thyroid Carcinoma (NCBI Bookshelf NBK568736)"
SRC_EAOTC = "https://www.mypathologyreport.ca/diagnosis-library/oncocytic-carcinoma-of-the-thyroid-gland/"
SRC_EAOTC_NAME = "MyPathologyReport: Oncocytic Carcinoma of the Thyroid Gland (WHO 2022 subtypes)"

results = []

for obj in batch:
    code = obj["code"]
    term = obj["term"]
    ceiling = obj["ceiling_codes"]
    r = {
        "code": code,
        "term": term,
        "site_specific": "No",
        "site_subset_codes": [],
        "site_subset_labels": [],
        "rationale": "",
        "source": "",
        "source_name": "",
    }

    if code == "8290/3":
        # All terms are thyroid oncocytic / Hurthle cell carcinoma entities.
        # Ceiling includes C739 (thyroid) among 34 codes (salivary, breast, eye,
        # thyroid, adrenal, pituitary, paraganglia, endocrine NOS).
        # These entities are exclusively thyroid follicular-cell derived tumors.
        r["site_specific"] = "Yes"
        r["site_subset_codes"] = ["C739"]
        r["site_subset_labels"] = ["Thyroid gland"]
        if "encapsulated angioinvasive" in term.lower():
            r["rationale"] = ("Encapsulated angioinvasive oncocytic carcinoma is a WHO 2022 "
                              "invasion subtype of oncocytic carcinoma of the thyroid gland, a "
                              "follicular-cell-derived thyroid malignancy; it does not arise at the "
                              "other ceiling sites (salivary, breast, eye, adrenal, pituitary), so it "
                              "is restricted to the thyroid (C739).")
            r["source"] = SRC_EAOTC
            r["source_name"] = SRC_EAOTC_NAME
        else:
            r["rationale"] = ("Hürthle cell (oncocytic) carcinoma / oncocytic follicular carcinoma is a "
                              "rare thyroid cancer originating from oncocytic (Hürthle) follicular "
                              "thyroid cells; it is not described at the other ceiling sites, so it is "
                              "restricted to the thyroid (C739).")
            r["source"] = SRC_ONCO_THYROID
            r["source_name"] = SRC_ONCO_THYROID_NAME
    else:
        # 8280/3, 8281/0, 8281/3, 8290/0 -> ceiling is {C751, C752} (pituitary region).
        # PitNET / pituitary adenoma variants and pituitary oncocytic entities span the
        # pituitary ceiling; thyroid/parathyroid-named oncocytic terms under 8290/0 have
        # no valid thyroid/parathyroid code within the {C751,C752} ceiling, so no proper
        # subset can be expressed -> not flagged as site-specific.
        r["site_specific"] = "No"
        r["rationale"] = ("Code ceiling is limited to the pituitary region (C751 pituitary gland, "
                          "C752 craniopharyngeal duct); the term is not restricted to a proper subset "
                          "of these two codes based on the literature, so it is not site-specific within "
                          "its ceiling.")
        r["source"] = ""
        r["source_name"] = ""

    results.append(r)

os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

# Summary
from collections import Counter
c = Counter(r["site_specific"] for r in results)
print("length:", len(results))
print(dict(c))
# validate subsets
for r in results:
    if r["site_specific"] == "Yes":
        orig = next(o for o in batch if o["code"]==r["code"] and o["term"]==r["term"])
        assert set(r["site_subset_codes"]).issubset(set(orig["ceiling_codes"])), r
        assert len(r["site_subset_codes"]) < len(orig["ceiling_codes"]), r
        assert r["source"].startswith("http"), r
print("validation OK")
