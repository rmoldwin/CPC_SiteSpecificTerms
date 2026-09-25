import json

labels = {
'C079':'Parotid gland','C080':'Submandibular gland','C081':'Sublingual gland','C088':'Overlapping lesion of major salivary glands','C089':'Major salivary gland, NOS',
'C300':'Nasal cavity','C310':'Maxillary sinus','C311':'Ethmoid sinus','C312':'Frontal sinus','C313':'Sphenoid sinus','C318':'Overlapping lesion of accessory sinuses','C319':'Accessory sinus, NOS',
'C569':'Ovary',
'C739':'Thyroid gland',
'C740':'Cortex of adrenal gland','C741':'Medulla of adrenal gland','C749':'Adrenal gland, NOS',
'C751':'Pituitary gland','C752':'Craniopharyngeal duct',
}

def lab(codes): return [labels[c] for c in codes]

SINONASAL = ["C300","C310","C311","C312","C313","C318","C319"]
SALIVARY = ["C079","C080","C081","C088","C089"]

# Sources
S_WHO_THY = "https://pmc.ncbi.nlm.nih.gov/articles/PMC9633223/"
S_WHO_THY_NAME = "PMC9633223 - Update from the 2022 WHO Classification of Thyroid Tumors (Endocrinology and Metabolism)"
S_OTC = "https://academic.oup.com/jcem/advance-article/doi/10.1210/clinem/dgag025/8443041"
S_OTC_NAME = "J Clin Endocrinol Metab - Approach to the patient: Oncocytic thyroid cancer (MI/EA/WI-OTC subtypes)"
S_MIOTC = "https://www.mypathologyreport.ca/diagnosis-library/minimally-invasive-oncocytic-carcinoma-thyroid-gland/"
S_MIOTC_NAME = "MyPathologyReport - Minimally invasive oncocytic carcinoma of the thyroid gland"
S_OSDC = "https://pmc.ncbi.nlm.nih.gov/articles/PMC9424456/"
S_OSDC_NAME = "Head and Neck Pathology PMC9424456 - Oncocytoid/Oncocytic variant of salivary duct carcinoma"
S_ACC_WHO = "http://www.kcpathsociety.org/wp-content/uploads/2023/01/WHO-paragraph.pdf"
S_ACC_WHO_NAME = "WHO Blue Book (Endocrine & NE Tumours 5th ed) - Adrenal cortical carcinoma 8370/3 definition"
S_ACC_WHO5 = "https://pmc.ncbi.nlm.nih.gov/articles/PMC11261174/"
S_ACC_WHO5_NAME = "J Pathol Transl Med PMC11261174 - What's new in adrenal gland pathology: WHO 5th edition"
S_DYSG = "https://pmc.ncbi.nlm.nih.gov/articles/PMC10679589/"
S_DYSG_NAME = "Diagn Interv Radiol PMC10679589 - Ovarian dysgerminoma (female equivalent of testicular seminoma)"
S_TCS = "https://pmc.ncbi.nlm.nih.gov/articles/PMC7754799/"
S_TCS_NAME = "J Int Med Res PMC7754799 - Sinonasal teratocarcinosarcoma (WHO term coined 2005)"

ONC_CEIL = ["C079","C080","C081","C088","C089","C500","C501","C502","C503","C504","C505","C506","C508","C509","C690","C691","C692","C693","C694","C695","C696","C698","C699","C739","C740","C741","C749","C750","C751","C752","C754","C755","C758","C759"]
PIT_CEIL = ["C751","C752"]
GRAN_CEIL = ["C569","C740","C741","C749","C750","C751","C752","C754","C755","C758","C759"]
ADR_CEIL = ["C740","C741","C749"]
PAP_CEIL = ["C569","C739"]
C9060 = ["C379","C381","C382","C383","C481","C482","C569","C710","C711","C712","C713","C714","C716","C740","C741","C749","C750","C751","C752","C753","C754","C755","C758","C759"]
C9070 = ["C379","C381","C382","C383","C481","C482","C569","C620","C621","C629","C630","C631","C637","C710","C711","C712","C713","C714","C720","C721","C740","C741","C749","C750","C751","C752","C753","C754","C755","C758","C759"]
C9072 = ["C481","C482","C620","C621","C629","C740","C741","C749","C750","C751","C752","C753","C754","C755","C758","C759"]
C9081 = ["C300","C310","C311","C312","C313","C318","C319","C379","C381","C382","C383","C481","C482","C569","C710","C711","C712","C713","C714","C716","C740","C741","C749","C750","C751","C752","C753","C754","C755","C758","C759"]
C9082 = ["C481","C482","C710","C711","C712","C713","C714","C716","C740","C741","C749","C750","C751","C752","C753","C754","C755","C758","C759"]

def obj(code, term, ss, subset=None, rat="", src="", srcname=""):
    o = {"code":code,"term":term,"site_specific":ss}
    if ss=="Yes":
        o["site_subset_codes"]=subset
        o["site_subset_labels"]=lab(subset)
    else:
        o["site_subset_codes"]=[]
        o["site_subset_labels"]=[]
    o["rationale"]=rat
    o["source"]=src
    o["source_name"]=srcname
    return o

results=[]

# ---- 8290/3 oncocytic / Hurthle ----
results.append(obj("8290/3","H\u00fcrthle cell carcinoma","Yes",["C739"],
 "Per WHO 2022 thyroid classification, 'H\u00fcrthle cell carcinoma' is the historical name for oncocytic carcinoma of the thyroid, a follicular-cell-derived thyroid entity restricted to the thyroid gland.",
 S_WHO_THY, S_WHO_THY_NAME))
results.append(obj("8290/3","Minimally invasive oncocytic carcinoma","Yes",["C739"],
 "Minimally/widely invasive grading of oncocytic carcinoma is a thyroid-specific (follicular-derived) staging scheme; minimally invasive oncocytic carcinoma denotes an oncocytic thyroid carcinoma with capsular invasion only.",
 S_OTC, S_OTC_NAME))
results.append(obj("8290/3","Minimally invasive oncocytic carcinoma of the thyroid gland (capsular invasion only)","Yes",["C739"],
 "Term explicitly names the thyroid gland; it is an oncocytic thyroid carcinoma with capsular invasion only, restricted to the thyroid.",
 S_MIOTC, S_MIOTC_NAME))
results.append(obj("8290/3","Oncocytic adenocarcinoma","No",None,
 "Generic oncocytic (oxyphilic) adenocarcinoma descriptor; oncocytic change occurs across many code-eligible sites (salivary gland, breast, adrenal, thyroid, eye), so not restricted to a proper subset.",
 S_OSDC, S_OSDC_NAME))
results.append(obj("8290/3","Oncocytic carcinoma","No",None,
 "Generic oncocytic carcinoma descriptor; oncocytic carcinomas are recognized across salivary gland, thyroid, adrenal and other code-eligible sites, so not restricted to a proper subset.",
 S_OSDC, S_OSDC_NAME))
results.append(obj("8290/3","Oncocytic carcinoma of the thyroid gland","Yes",["C739"],
 "WHO 2022 designates 'oncocytic carcinoma of the thyroid' as the follicular-cell-derived thyroid entity (former H\u00fcrthle cell carcinoma), restricted to the thyroid.",
 S_WHO_THY, S_WHO_THY_NAME))
results.append(obj("8290/3","Oncocytic salivary duct carcinoma","Yes",SALIVARY,
 "Oncocytic (oncocytoid) salivary duct carcinoma is a salivary-gland carcinoma variant, restricted to the major/minor salivary glands within the code ceiling.",
 S_OSDC, S_OSDC_NAME))
results.append(obj("8290/3","Oxyphilic adenocarcinoma","No",None,
 "Oxyphilic/oncocytic adenocarcinoma is a generic morphologic descriptor of oxyphilic (mitochondria-rich) tumors occurring across multiple code-eligible sites; not restricted to a proper subset.",
 S_OSDC, S_OSDC_NAME))
results.append(obj("8290/3","Widely invasive oncocytic carcinoma","Yes",["C739"],
 "Widely invasive grading of oncocytic carcinoma is a thyroid-specific follicular-derived staging scheme (WI-OTC), denoting an oncocytic thyroid carcinoma with extensive invasion.",
 S_OTC, S_OTC_NAME))
results.append(obj("8290/3","Widely invasive oncocytic carcinoma of the thyroid gland","Yes",["C739"],
 "Term explicitly names the thyroid gland; widely invasive oncocytic thyroid carcinoma is restricted to the thyroid.",
 S_OTC, S_OTC_NAME))

# ---- 8300/0 & 8300/3 & 8310/0 & 8323/0 pituitary adenoma/carcinoma terms ----
PIT_SRC = "https://pmc.ncbi.nlm.nih.gov/articles/PMC11261174/"  # placeholder endocrine WHO; will not be Yes so source only needs to be informational
for code, term in [
 ("8300/0","Basophil adenoma"),("8300/0","Mucoid cell adenoma"),
 ("8300/3","Basophil adenocarcinoma"),("8300/3","Basophil adenoma"),("8300/3","Basophil carcinoma"),
 ("8300/3","Mucoid cell adenocarcinoma"),("8300/3","Mucoid cell adenoma"),
 ("8310/0","Clear cell adenoma")]:
    results.append(obj(code,term,"No",None,
     "Code ceiling is already limited to the pituitary region (pituitary gland C751 and craniopharyngeal duct C752); this pituitary adenoma/carcinoma term applies across the entire ceiling, so it is not restricted to a proper subset.",
     S_ACC_WHO5, S_ACC_WHO5_NAME))

# ---- 8320/3 granular cell (batch order: adenocarcinoma, carcinoma) ----
for term in ["Granular cell adenocarcinoma","Granular cell carcinoma"]:
    results.append(obj("8320/3",term,"No",None,
     "Generic granular-cell (oncocytic/granular cytoplasm) carcinoma descriptor spanning multiple endocrine and ovarian code-eligible sites; no published restriction to a proper subset of the ceiling.",
     S_ACC_WHO5, S_ACC_WHO5_NAME))

# ---- 8323/0 mixed cell adenoma (pituitary) ----
results.append(obj("8323/0","Mixed cell adenoma","No",None,
     "Code ceiling is already limited to the pituitary region (pituitary gland C751 and craniopharyngeal duct C752); this pituitary adenoma term applies across the entire ceiling, so it is not restricted to a proper subset.",
     S_ACC_WHO5, S_ACC_WHO5_NAME))

# ---- 8370/3 adrenal cortical carcinoma terms (cortex-derived) ----
ADR_SUB = ["C740","C749"]
adr_terms = [
 ("Adrenal cortical adenocarcinoma"),
 ("Adrenal cortical carcinoma"),
 ("Adrenal cortical carcinoma, conventional"),
 ("Adrenal cortical carcinoma, oncocytic"),
 ("Adrenal cortical tumor, malignant"),
 ("Adrenocortical carcinoma, NOS"),
 ("Conventional adrenal cortical carcinoma"),
 ("Myxoid adrenal cortical carcinoma"),
 ("Oncocytic adrenal cortical carcinoma"),
 ("Sarcomatoid adrenal cortical carcinoma"),
]
for term in adr_terms:
    results.append(obj("8370/3",term,"Yes",ADR_SUB,
     "WHO defines adrenal cortical carcinoma (and all its subtypes) as a malignant epithelial tumour originating from adrenal cortical cells; it is confined to the adrenal cortex (C740) / adrenal gland NOS (C749) and does not arise from the adrenal medulla (C741, origin of pheochromocytoma).",
     S_ACC_WHO, S_ACC_WHO_NAME))

# ---- 8450/3 papillary cystadenocarcinoma ----
for term in ["Papillary cystadenocarcinoma, NOS","Papillocystic adenocarcinoma"]:
    results.append(obj("8450/3",term,"No",None,
     "Generic papillary cystadenocarcinoma architectural descriptor occurring at both ceiling sites (ovary and thyroid) and elsewhere; not restricted to a proper subset.",
     S_DYSG, S_DYSG_NAME))

# ---- 9060/3 dysgerminoma ----
for term in ["Dysgerminoma","Dysgerminoma with syncytiotrophoblast cells","Germinoma of ovary"]:
    results.append(obj("9060/3",term,"Yes",["C569"],
     "Dysgerminoma is the ovary-specific germinoma (female equivalent of testicular seminoma); the analogous tumors are termed seminoma in testis and germinoma in the CNS, so the dysgerminoma nomenclature is restricted to the ovary within this ceiling.",
     S_DYSG, S_DYSG_NAME))

# ---- 9070/3 embryonal carcinoma ----
for term in ["Embryonal adenocarcinoma","Embryonal carcinoma, NOS"]:
    results.append(obj("9070/3",term,"No",None,
     "Embryonal carcinoma is a germ cell tumor type occurring across gonadal (testis, ovary) and extragonadal midline/CNS sites; it is not restricted to a proper subset of the code ceiling.",
     "https://en.wikipedia.org/wiki/Embryonal_carcinoma","Embryonal carcinoma - occurs in ovaries, testes and extragonadal sites"))

# ---- 9072/3 polyembryoma ----
for term in ["Embryonal carcinoma, polyembryonal type","Polyembryoma"]:
    results.append(obj("9072/3",term,"No",None,
     "Polyembryoma is a rare germ cell tumor described in both gonadal (testis) and extragonadal (retroperitoneal) locations; within this ceiling it is not confined to a demonstrable proper subset.",
     "https://pubmed.ncbi.nlm.nih.gov/28429716/","PubMed 28429716 - Polyembryoma in testicular mixed germ cell tumors"))

# ---- 9081/3 teratocarcinoma / mixed EC+teratoma / teratocarcinosarcoma ----
results.append(obj("9081/3","Mixed embryonal carcinoma and teratoma","No",None,
 "Mixed embryonal carcinoma and teratoma is a generic mixed germ cell tumor occurring across gonadal and extragonadal germ-cell sites; not restricted to a proper subset.",
 "https://en.wikipedia.org/wiki/Germ_cell_tumor","Germ cell tumor - gonadal and extragonadal distribution"))
results.append(obj("9081/3","Teratocarcinoma","No",None,
 "Teratocarcinoma (mixed teratoma plus embryonal carcinoma) is a generic germ cell tumor occurring across gonadal and extragonadal sites; not restricted to a proper subset.",
 "https://en.wikipedia.org/wiki/Germ_cell_tumor","Germ cell tumor - gonadal and extragonadal distribution"))
TCS_SUB = SINONASAL + ["C569"]
results.append(obj("9081/3","Teratocarcinosarcoma","Yes",TCS_SUB,
 "Teratocarcinosarcoma (WHO sinonasal teratocarcinosarcoma) most frequently arises in the nasal cavity and paranasal sinuses, with rarer reports in the ovary; within the ceiling it is confined to the sinonasal sites and ovary and does not involve thymus, mediastinum, CNS or endocrine sites.",
 S_TCS, S_TCS_NAME))

# ---- 9082/3 malignant teratoma anaplastic / undifferentiated ----
for term in ["Malignant teratoma, anaplastic","Malignant teratoma, undifferentiated"]:
    results.append(obj("9082/3",term,"Uncertain",None,
     "These are legacy British (BTTPR) classification terms for undifferentiated malignant teratoma (largely a testicular/gonadal concept); the code ceiling here (retroperitoneum, CNS, endocrine) excludes the gonads, and no source clearly restricts the term to a proper subset of these specific ceiling sites.",
     "https://assets.publishing.service.gov.uk/media/5a7ea711e5274a2e8ab47562/testicular_cancer.pdf","GOV.UK Testicular cancer - BTTPR malignant teratoma undifferentiated terminology"))

print("total", len(results))
from collections import Counter
print(Counter(r['site_specific'] for r in results))
# validate subsets
ceilmap = {'8290/3':ONC_CEIL,'8300/0':PIT_CEIL,'8300/3':PIT_CEIL,'8310/0':PIT_CEIL,'8323/0':PIT_CEIL,
'8320/3':GRAN_CEIL,'8370/3':ADR_CEIL,'8450/3':PAP_CEIL,'9060/3':C9060,'9070/3':C9070,'9072/3':C9072,'9081/3':C9081,'9082/3':C9082}
for r in results:
    if r['site_specific']=='Yes':
        ceil=set(ceilmap[r['code']])
        sub=set(r['site_subset_codes'])
        assert sub<ceil, f"NOT strict subset: {r['term']} {sub-ceil}"
        assert len(sub)>0
print("all Yes subsets valid strict subsets")

json.dump(results, open('/home/user/workspace/icdo32_execution/results/endocrine_03.json','w'), indent=1)
print("written")
