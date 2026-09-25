import json

# Ceiling reference:
# testis codes: C620 (undescended), C621 (descended), C629 (testis NOS)
# C630 epididymis, C631 spermatic cord, C637 overlapping male genital
# C379 thymus, C381/C382/C383 mediastinum

TESTIS = ["C620", "C621", "C629"]
TESTIS_LABELS = ["Undescended testis", "Descended testis", "Testis, NOS"]

results = []

def add(code, term, ss, subset=None, labels=None, rationale="", source="", source_name=""):
    o = {"code": code, "term": term, "site_specific": ss}
    if ss == "Yes":
        o["site_subset_codes"] = subset
        o["site_subset_labels"] = labels
    o["rationale"] = rationale
    o["source"] = source
    o["source_name"] = source_name
    results.append(o)

# --- 8640/3 Sertoli cell (ceiling = 3 testis codes only) ---
# All three ceiling codes are testis (undescended/descended/NOS). A testicular
# term covers all of them, so no proper subset is possible -> No.
for term in ["Sertoli cell carcinoma", "Sertoli cell tumor, malignant"]:
    add("8640/3", term, "No",
        rationale="Sertoli cell tumors arise in the testis; the code's ceiling (C620/C621/C629) is entirely testis, so the term occupies the whole ceiling and no proper anatomic subset exists.",
        source="https://uroweb.org/guidelines/testicular-cancer/chapter/rare-adult-para-and-testicular-tumours",
        source_name="EAU Guidelines on Testicular Cancer (rare para/testicular tumours)")

# --- 8650/3 Leydig / interstitial cell tumor (ceiling = 6 codes) ---
# Predominantly testicular but literature documents extratesticular/paratesticular
# Leydig cell tumors in spermatic cord (C631) and epididymis (C630), both in the
# ceiling. So the term is not restricted to a proper subset -> No.
for term in ["Interstitial cell tumor, malignant", "Leydig cell tumor, malignant", "Malignant Leydig cell tumor"]:
    add("8650/3", term, "No",
        rationale="Leydig (interstitial) cell tumors are chiefly testicular but a recognized minority (~2-3%) are extratesticular/paratesticular, arising in the spermatic cord and epididymis, which are both within the code's ceiling; thus the term is not confined to a proper subset.",
        source="https://meridian.allenpress.com/aplm/article/131/2/311/460139/An-In-Depth-Look-at-Leydig-Cell-Tumor-of-the",
        source_name="Al-Agha & Axiotis, Arch Pathol Lab Med 2007 (An In-Depth Look at Leydig Cell Tumor of the Testis)")

# --- 9061/2 (ceiling = 3 testis codes only) ---
for term in ["Intratubular seminoma", "Intratubular trophoblast"]:
    add("9061/2", term, "No",
        rationale="An intratubular (within seminiferous tubules) lesion is inherently testicular; the ceiling (C620/C621/C629) is entirely testis, so no proper subset is possible.",
        source="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6789349/",
        source_name="Testicular germ cell tumors: the changing role of the pathologist, PMC6789349")

# --- 9061/3 (ceiling = 10 codes: thymus/mediastinum + testis + epididymis/cord) ---
# Germinoma of testis: name restricts to testis -> Yes, subset = testis codes.
add("9061/3", "Germinoma of testis", "Yes", TESTIS, TESTIS_LABELS,
    rationale="The named entity 'germinoma of testis' is by definition confined to the testis, a proper subset of the code's ceiling, which also spans extragonadal sites (thymus C379, mediastinum C381-C383) and paratesticular sites (epididymis C630, spermatic cord C631).",
    source="https://pubmed.ncbi.nlm.nih.gov/10355653/",
    source_name="Weidner N, Germ-cell tumors of the mediastinum, PMID 10355653 (establishes seminoma/germinoma family also occurs extragonadally)")
# Seminoma with syncytiotrophoblast(ic) cells + Seminoma NOS: occur extragonadally
for term in ["Seminoma with syncytiotrophoblast cells", "Seminoma with syncytiotrophoblastic cells", "Seminoma, NOS"]:
    add("9061/3", term, "No",
        rationale="Seminoma (including the syncytiotrophoblast-containing variant) occurs both in the testis and at extragonadal sites (mediastinum/thymus) as well as paratesticular sites, spanning essentially the whole ceiling; it is not restricted to a proper subset.",
        source="https://pubmed.ncbi.nlm.nih.gov/10355653/",
        source_name="Weidner N, Germ-cell tumors of the mediastinum, PMID 10355653")

# --- 9063/3 Spermatocytic tumor family (ceiling = 6 codes) ---
# Spermatocytic tumor occurs EXCLUSIVELY in testis; no extragonadal counterpart.
# Ceiling includes epididymis(C630), spermatic cord(C631), overlapping(C637) ->
# testis-only is a proper subset -> Yes.
for term in ["Spermatocytic seminoma", "Spermatocytic tumor",
             "Spermatocytic tumor with sarcomatous differentiation", "Spermatocytoma"]:
    add("9063/3", term, "Yes", TESTIS, TESTIS_LABELS,
        rationale="WHO/EAU and pathology literature establish that spermatocytic tumor occurs exclusively in the testis with no extragonadal or paratesticular counterpart; this excludes epididymis (C630), spermatic cord (C631) and overlapping male-genital (C637) sites in the ceiling, leaving only the testis codes.",
        source="https://uroweb.org/guidelines/testicular-cancer/chapter/rare-adult-para-and-testicular-tumours",
        source_name="EAU Guidelines on Testicular Cancer: 'Spermatocytic tumours ... occur exclusively in the testis'")

# --- 9064/2 GCNIS family (ceiling = 3 testis codes only) ---
for term in ["Germ cell neoplasia in situ", "Intratubular germ cell neoplasia",
             "Intratubular germ cell neoplasia (male gonadal)", "Intratubular malignant germ cells",
             "Specific forms of intratubular germ cell neoplasia"]:
    add("9064/2", term, "No",
        rationale="GCNIS/intratubular germ cell neoplasia is defined by neoplastic germ cells within the seminiferous tubules of the testis; the ceiling (C620/C621/C629) is entirely testis, so no proper subset is possible.",
        source="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6789349/",
        source_name="Testicular germ cell tumors: the changing role of the pathologist, PMC6789349 (GCNIS localized within seminiferous tubules)")

# --- 9070/2 Intratubular embryonal carcinoma (ceiling = 3 testis) ---
add("9070/2", "Intratubular embryonal carcinoma", "No",
    rationale="An intratubular embryonal carcinoma is by definition within the testicular seminiferous tubules; the ceiling is entirely testis (C620/C621/C629), so no proper subset exists.",
    source="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6789349/",
    source_name="Testicular germ cell tumors: the changing role of the pathologist, PMC6789349")

# --- 9071/2 Intratubular yolk-sac tumor (ceiling = 3 testis) ---
add("9071/2", "Intratubular yolk-sac tumor", "No",
    rationale="An intratubular yolk-sac tumor is confined to testicular seminiferous tubules; the ceiling is entirely testis (C620/C621/C629), so no proper subset exists.",
    source="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6789349/",
    source_name="Testicular germ cell tumors: the changing role of the pathologist, PMC6789349")

# --- 9080/2 Intratubular teratoma (ceiling = 3 testis) ---
add("9080/2", "Intratubular teratoma", "No",
    rationale="An intratubular teratoma is within testicular seminiferous tubules; the ceiling is entirely testis (C620/C621/C629), so no proper subset exists.",
    source="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6789349/",
    source_name="Testicular germ cell tumors: the changing role of the pathologist, PMC6789349")

# Verify order/length against batch
batch = json.load(open("/home/user/workspace/icdo32_execution/batches/male_genital_02.json"))
assert len(results) == len(batch) == 23, (len(results), len(batch))
for r, b in zip(results, batch):
    assert r["code"] == b["code"] and r["term"] == b["term"], (r["term"], b["term"])
    if r["site_specific"] == "Yes":
        for c in r["site_subset_codes"]:
            assert c in b["ceiling_codes"], (r["term"], c)
        assert set(r["site_subset_codes"]) != set(b["ceiling_codes"]), r["term"]  # strict subset

json.dump(results, open("/home/user/workspace/icdo32_execution/results/male_genital_02.json", "w"), indent=1)

from collections import Counter
c = Counter(r["site_specific"] for r in results)
print("Counts:", dict(c))
print("Total:", len(results))
