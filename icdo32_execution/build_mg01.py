import json

batch = json.load(open('/home/user/workspace/icdo32_execution/batches/male_genital_01.json'))

# Decision overrides keyed by (code, term). Default = No with generic rationale.
YES = {}
UNC = {}

# 8620/3 granulosa cell tumor. Ceiling = C569 ovary + C620/C621/C629 testis.
gct_src = "https://pmc.ncbi.nlm.nih.gov/articles/PMC12891927/"
gct_srcname = "Ricci et al., Histopathology 2025 (PMC12891927), WHO 5th ed male genital tumours"
YES[("8620/3","Adult granulosa cell tumor of ovary")] = {
  "site_subset_codes":["C569"],"site_subset_labels":["Ovary"],
  "rationale":"'Adult granulosa cell tumor of ovary' names the ovarian entity specifically; the literature treats ovarian AGCT (FOXL2 p.Cys134Trp-driven, most common ovarian sex cord-stromal tumour) as distinct from the testicular counterpart in the code's ceiling, restricting this named term to the ovary (a proper subset of ovary+testis).",
  "source":gct_src,"source_name":gct_srcname}
YES[("8620/3","Granulosa cell tumor of ovary, NOS")] = {
  "site_subset_codes":["C569"],"site_subset_labels":["Ovary"],
  "rationale":"The qualifier 'of ovary' anatomically restricts this term to the ovary; ovarian granulosa cell tumour is a distinct entity separate from the testicular counterpart, so the term maps to a proper subset (ovary) of the code's ovary+testis ceiling.",
  "source":gct_src,"source_name":gct_srcname}

# Adult granulosa cell tumor of adrenal gland -> adrenal (C74) is OUTSIDE ceiling {ovary,testis}
adr_src = "https://pmc.ncbi.nlm.nih.gov/articles/PMC10212836/"
UNC[("8620/3","Adult granulosa cell tumor of adrenal gland")] = {
  "rationale":"Primary granulosa cell tumour of the adrenal gland is a rare documented extraovarian variant, but the adrenal gland (C74) is not among this code's ceiling codes (ovary C569, testis C620/C621/C629). Its literature-defined site does not intersect the ceiling, so it cannot be mapped to a proper subset of the allowed sites.",
  "source":adr_src,"source_name":"El Fadli et al., Int Cancer Conf J 2023 (PMC10212836) - extraovarian/adrenal GCT"}

out = []
for item in batch:
    code = item["code"]; term = item["term"]; ceil = item["ceiling_codes"]
    key = (code, term)
    if key in YES:
        d = YES[key]
        # verify subset
        assert set(d["site_subset_codes"]).issubset(set(ceil)) and set(d["site_subset_codes"]) != set(ceil), key
        out.append({"code":code,"term":term,"site_specific":"Yes",
                    "site_subset_codes":d["site_subset_codes"],
                    "site_subset_labels":d["site_subset_labels"],
                    "rationale":d["rationale"],"source":d["source"],"source_name":d["source_name"]})
    elif key in UNC:
        d = UNC[key]
        out.append({"code":code,"term":term,"site_specific":"Uncertain",
                    "site_subset_codes":[],"site_subset_labels":[],
                    "rationale":d["rationale"],"source":d["source"],"source_name":d["source_name"]})
    else:
        # Default No. Provide group-appropriate rationale.
        if code == "8620/3":
            rat = "Granulosa cell tumour (this generic/adult-type/sarcomatoid/carcinoma variant) occurs in both the ovary and the testis, spanning essentially the full ovary+testis ceiling of this code, so it is not restricted to a proper subset."
        elif code == "8640/3":
            rat = "Malignant Sertoli cell tumour's ceiling here is testis-only (C620/C621/C629, a single organ); there is no literature-supported anatomic subset within testicular subsites, so it is not site-specific relative to its ceiling."
        elif code == "8054/3":
            rat = "Warty/condylomatous carcinoma's ceiling here is penis-only (C600-C609); it is not restricted to a proper subset of penile subsites in the literature, so it is not site-specific relative to its ceiling."
        elif code == "8083/2":
            rat = "Basaloid squamous cell carcinoma in situ is a generic HPV-associated squamous entity arising across anal, penile and other lower-genital/male-genital squamous sites in the ceiling; it is not restricted to a proper subset."
        else:
            # BCC family 8090-8097
            rat = "This basal cell carcinoma descriptor is a generic morphologic/architectural variant of a skin tumour that can arise at any hair-bearing squamous site in the ceiling (anal margin, vulva, penis, scrotum); it is not anatomically restricted to a proper subset."
        out.append({"code":code,"term":term,"site_specific":"No",
                    "site_subset_codes":[],"site_subset_labels":[],
                    "rationale":rat,"source":"","source_name":""})

assert len(out) == 45, len(out)
import os
os.makedirs('/home/user/workspace/icdo32_execution/results', exist_ok=True)
json.dump(out, open('/home/user/workspace/icdo32_execution/results/male_genital_01.json','w'), indent=1)
y=sum(1 for o in out if o["site_specific"]=="Yes")
n=sum(1 for o in out if o["site_specific"]=="No")
u=sum(1 for o in out if o["site_specific"]=="Uncertain")
print("len",len(out),"Yes",y,"No",n,"Uncertain",u)
